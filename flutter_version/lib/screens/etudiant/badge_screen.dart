import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../core/print_gate.dart';
import '../../models/student.dart';
import '../../services/template_store.dart';
import '../../state/profile_state.dart';
import '../../state/students_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/badge_renderer.dart';
import '../../widgets/section_header.dart';

const _salles = {'A': 'Salle A', 'B': 'Salle B', 'C': 'Salle C', 'D': 'Salle D'};

const _moisNoms = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
];

/// Équivalent de combo_template (Main.py:637-640) : un simple sélecteur —
/// l'upload est aussi possible directement ici (bouton "Choisir template",
/// sur demande explicite) en plus de la page Profil ("Template badge 1/2",
/// lib/screens/profile/profile_screen.dart) — les deux écrans partagent le
/// même stockage local (TemplateStore).
const _templates = {'template_badge_1': 'Template 1', 'template_badge_2': 'Template 2'};

/// Équivalent de ABadge (Resources/main_school1.ui:5457-6456) — page
/// "Badge / Carte d'identité" — et de make_an_identity_card()/
/// generate_badge()/generate_badge_and_save() (school_client, Controllers/
/// Main.py:5594, 5602-6280) : aperçu du badge, recherche d'étudiant, flux
/// caméra (USB ou IP, comme toggle_camera()/active_camera_ip()) avec
/// capture, chargement de photo, sélection de template/salle, et les deux
/// actions de génération (avec ou sans synchronisation de la photo).
///
/// Différences disclosées par rapport au bureau :
/// - Liste/flux caméra USB : `camera_macos` (AVFoundation) au lieu de
///   QMediaDevices + OpenCV — même résultat (sélection du périphérique,
///   aperçu live, capture d'une image), implémentation différente.
/// - Caméra IP (téléphone) : le bureau ouvre un flux vidéo MJPEG continu
///   (cv2.VideoCapture('http://ip:8080/video')) ; ici l'aperçu "live" est
///   obtenu par interrogation répétée (toutes les ~700 ms) de l'endpoint
///   photo de l'app IP Webcam (http://ip:8080/photo.jpg) — même source,
///   fréquence de rafraîchissement plus faible qu'un vrai flux vidéo.
/// - Vérification de l'IP : un GET HTTP court (au lieu d'un `ping` ICMP,
///   qui nécessiterait des permissions élevées côté macOS sandboxé) —
///   même intention (confirmer que l'IP répond) via un moyen accessible.
/// - Date d'expiration : codée en dur ("Juin 2026") côté bureau (le champ
///   `date_dexp` correspondant existe dans le .ui mais reste un QLabel
///   toujours caché, jamais relié à une saisie) — ici sélectionnable
///   (mois + année), sur demande explicite.
///
/// Important : il N'EXISTE PAS, côté bureau, de fonctionnalité de
/// positionnement personnalisé des éléments du badge (pas de glisser-
/// déposer, pas de coordonnées configurables) — generate_badge() (Main.py:
/// 6144-6280) dessine à des coordonnées 100% fixes. Un fichier
/// `badge_config.json` existe dans le dépôt mais n'est lu nulle part (mort).
/// Des éditeurs avec positionnement glissable existent (Badge.py, Badge2.py,
/// input.py/BadgeEditorWidget) mais ne sont PAS intégrés à cette page —
/// vérifié explicitement. Les coordonnées reprises ici sont déjà la copie
/// fidèle des QRect/drawText réels du bureau.
class BadgeScreen extends StatefulWidget {
  /// [initialStudent] : pré-sélectionne un étudiant si ouvert depuis la
  /// ligne de la liste (icône badge par étudiant) — équivalent de
  /// on_row_clicked_badge() (school_client, Main.py), qui ouvrait directement
  /// la page badge avec l'étudiant cliqué déjà chargé.
  const BadgeScreen({super.key, this.initialStudent});

  final Student? initialStudent;

  @override
  State<BadgeScreen> createState() => _BadgeScreenState();
}

class _BadgeScreenState extends State<BadgeScreen> {
  final _searchController = TextEditingController();
  final _ipController = TextEditingController();
  final _ipDio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 3), receiveTimeout: const Duration(seconds: 3)));

  Student? _selected;
  Uint8List? _photoBytes;
  String _salle = 'A';
  String _template = 'template_badge_1';
  final Map<String, Uint8List?> _templateBytes = {};
  bool _generating = false;
  bool _uploadingTemplate = false;
  String? _error;

  // Date d'expiration ("Juin 2026" sur le bureau, codée en dur) — ici
  // sélectionnable (mois + année), ajouté sur demande explicite.
  int _expMonth = DateTime.now().month;
  int _expYear = DateTime.now().year;

  // ── Caméra USB (camera — cross-platform : macOS + Windows + Linux) ─────
  List<CameraDescription> _cameras = [];
  CameraDescription? _selectedCamera;
  CameraController? _cameraController;
  bool _cameraInitialized = false;
  bool _previewRunning = false;

  // ── Rescan auto des périphériques (stop_search_cam, Main.py:5665) ──────
  Timer? _scanTimer;
  bool _scanActive = true;

  // ── Caméra IP (active_camera_ip, Main.py:5744) ──────────────────────────
  bool _isIpCamera = false;
  bool _checkingIp = false;
  Uint8List? _ipPreviewBytes;
  Timer? _ipPollTimer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final profile = context.read<ProfileState>();
      if (profile.profile == null) profile.load();
      // Pré-sélection si ouvert depuis la liste étudiant avec un étudiant donné.
      if (widget.initialStudent != null) _selectStudent(widget.initialStudent!);
    });
    _loadCameras();
    _scanTimer = Timer.periodic(const Duration(seconds: 2), (_) => _loadCameras());
    _loadTemplates();
  }

  Future<void> _loadTemplates() async {
    for (final key in _templates.keys) {
      final bytes = await TemplateStore.instance.read(key);
      if (mounted) setState(() => _templateBytes[key] = bytes);
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _ipController.dispose();
    _scanTimer?.cancel();
    _ipPollTimer?.cancel();
    _cameraController?.dispose();
    super.dispose();
  }

  /// Équivalent de listDevices() (camera_macos) — utilise le package
  /// cross-platform `camera` (macOS + Windows + Linux).
  Future<void> _loadCameras() async {
    try {
      final cameras = await availableCameras();
      if (!mounted) return;
      setState(() {
        _cameras = cameras;
        // Si la caméra sélectionnée a disparu (débranché), réinitialiser.
        if (_selectedCamera != null &&
            !_cameras.any((c) => c.name == _selectedCamera!.name)) {
          _selectedCamera = null;
          _cameraController?.dispose();
          _cameraController = null;
          _cameraInitialized = false;
          _previewRunning = false;
        }
      });
    } catch (_) {
      // Aucune permission ou aucun périphérique : le sélecteur reste vide.
    }
  }

  /// Équivalent de stop_populate_camera() (Main.py:5665) — le texte est
  /// volontairement inversé par rapport à l'état du timer, fidèle au bureau.
  void _toggleScan() {
    setState(() => _scanActive = !_scanActive);
    if (_scanActive) {
      _scanTimer = Timer.periodic(const Duration(seconds: 2), (_) => _loadCameras());
    } else {
      _scanTimer?.cancel();
    }
  }

  /// Démarre l'aperçu USB via CameraController (camera package).
  Future<void> _startUsbPreview() async {
    final camera = _selectedCamera!;
    final ctrl = CameraController(
      camera,
      ResolutionPreset.medium,
      enableAudio: false,
    );
    try {
      await ctrl.initialize();
      if (!mounted) {
        await ctrl.dispose();
        return;
      }
      setState(() {
        _cameraController = ctrl;
        _cameraInitialized = true;
        _previewRunning = true;
      });
    } catch (e) {
      await ctrl.dispose();
      if (mounted) setState(() => _error = 'Impossible d\'initialiser la caméra : $e');
    }
  }

  Future<void> _selectStudent(Student s) async {
    setState(() {
      _selected = s;
      _photoBytes = null;
      _error = null;
    });
    context.read<StudentsState>().searchLive('');
    await context.read<StudentsState>().loadDetail(s.id);
  }

  Future<void> _pickPhoto() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    final bytes = result?.files.single.bytes;
    if (bytes != null) setState(() => _photoBytes = bytes);
  }

  /// Le sélecteur "Template" choisit parmi les templates uploadés (depuis
  /// ici ou depuis la page Profil, TemplateStore est commun aux deux).
  void _onTemplateChanged(String? value) {
    if (value == null) return;
    if (value == 'template_badge_2' && _templateBytes['template_badge_2'] == null) {
      setState(() => _error = 'Aucun "Template badge 2" importé — utilisez le bouton "Choisir template".');
      return;
    }
    setState(() {
      _template = value;
      _error = null;
    });
  }

  /// Permet d'importer/remplacer directement le template actuellement
  /// sélectionné (équivalent template_badge_1()/template_badge_2(),
  /// Main.py:6817-6947) — disponible ici en plus de la page Profil.
  Future<void> _pickTemplateForCurrent() async {
    setState(() => _uploadingTemplate = true);
    final error = await TemplateStore.instance.pickAndSave(_template);
    if (!mounted) return;
    if (error != null) {
      setState(() {
        _error = error;
        _uploadingTemplate = false;
      });
      return;
    }
    final bytes = await TemplateStore.instance.read(_template);
    if (!mounted) return;
    setState(() {
      _templateBytes[_template] = bytes;
      _error = null;
      _uploadingTemplate = false;
    });
  }

  String _formatExpiration() => '${_moisNoms[_expMonth - 1]} $_expYear';

  /// Équivalent de active_camera_ip() (Main.py:5744) : vérifie que l'IP
  /// répond avant d'activer le flux (ping côté bureau, GET HTTP court ici).
  Future<void> _toggleIpCamera(bool enable) async {
    if (!enable) {
      setState(() {
        _isIpCamera = false;
        _ipPreviewBytes = null;
        if (_previewRunning) _previewRunning = false;
      });
      _ipPollTimer?.cancel();
      return;
    }
    final ip = _ipController.text.trim();
    if (ip.isEmpty) {
      setState(() => _error = "Entrez l'adresse IP du téléphone.");
      return;
    }
    setState(() => _checkingIp = true);
    try {
      await _ipDio.get('http://$ip:8080/');
      if (!mounted) return;
      setState(() {
        _isIpCamera = true;
        _error = null;
        _selectedCamera = null;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = "Caméra IP injoignable à $ip:8080.");
    } finally {
      if (mounted) setState(() => _checkingIp = false);
    }
  }

  void _startIpPolling() {
    _ipPollTimer?.cancel();
    _ipPollTimer = Timer.periodic(const Duration(milliseconds: 700), (_) async {
      final ip = _ipController.text.trim();
      if (ip.isEmpty) return;
      try {
        final response = await _ipDio.get<List<int>>(
          'http://$ip:8080/photo.jpg',
          options: Options(responseType: ResponseType.bytes),
        );
        if (mounted) setState(() => _ipPreviewBytes = Uint8List.fromList(response.data!));
      } catch (_) {
        // Frame manquée : on garde la précédente, comme un flux vidéo réel.
      }
    });
  }

  /// Équivalent de toggle_camera() (Main.py:5817) : un même bouton démarre
  /// l'aperçu, puis capture une image une fois l'aperçu actif.
  Future<void> _onCaptureButton() async {
    if (!_previewRunning) {
      if (_isIpCamera) {
        setState(() => _previewRunning = true);
        _startIpPolling();
      } else if (_selectedCamera != null) {
        await _startUsbPreview();
      } else {
        setState(() => _error = 'Sélectionnez une caméra.');
      }
      return;
    }

    // Capture (equivalent capture_photo(), Main.py:5898).
    if (_isIpCamera) {
      _ipPollTimer?.cancel();
      setState(() {
        _photoBytes = _ipPreviewBytes;
        _previewRunning = false;
      });
    } else if (_cameraController != null && _cameraInitialized) {
      final file = await _cameraController!.takePicture();
      final bytes = await file.readAsBytes();
      await _cameraController!.dispose();
      setState(() {
        _photoBytes = Uint8List.fromList(bytes);
        _previewRunning = false;
        _cameraController = null;
        _cameraInitialized = false;
      });
    }
  }

  Uint8List? _currentPhotoBytes(StudentsState state) {
    if (_photoBytes != null) return _photoBytes;
    final base64Photo = state.currentDetail?.photoBase64;
    if (base64Photo == null || base64Photo.isEmpty) return null;
    final raw = base64Photo.contains(',') ? base64Photo.split(',').last : base64Photo;
    try {
      return base64Decode(raw);
    } catch (_) {
      return null;
    }
  }

  Future<Uint8List?> _generate({required bool sync}) async {
    final state = context.read<StudentsState>();
    final detail = state.currentDetail;
    final selected = _selected;
    if (selected == null || detail == null) return null;

    final photoBytes = _currentPhotoBytes(state);
    if (photoBytes == null) {
      setState(() => _error = 'Photo de l’étudiant manquante : capturez ou choisissez un fichier.');
      return null;
    }

    setState(() {
      _generating = true;
      _error = null;
    });

    try {
      final schoolName = context.read<ProfileState>().profile?.nom ?? '';
      final responsable = (detail.adresseResponsable?.isNotEmpty ?? false)
          ? '${detail.adresseResponsable} \n ${detail.telephoneResponsable ?? ''}'
          : 'responsable info';

      final png = await renderBadgePng(
        schoolName: schoolName,
        fullName: '${detail.nom} ${detail.prenom}',
        classeName: detail.classeActuelle?.nomClasse ?? '',
        identifiant: detail.identifiant,
        salleLabel: _salles[_salle] ?? '',
        expirationLabel: _formatExpiration(),
        photoBytes: photoBytes,
        qrData: responsable,
        templateBytes: _templateBytes[_template],
      );

      final file = File('${Directory.systemTemp.path}/badge_${detail.identifiant}.png');
      await file.writeAsBytes(png);
      if (Platform.isMacOS) {
        await Process.run('open', [file.path]);
      } else if (Platform.isWindows) {
        await Process.run('cmd', ['/c', 'start', '', file.path]);
      } else if (Platform.isLinux) {
        await Process.run('xdg-open', [file.path]);
      }

      if (sync) {
        final dataUri = 'data:image/jpeg;base64,${base64Encode(photoBytes)}';
        final error = await state.saveBadgePhoto(studentId: selected.id, photoBase64: dataUri);
        if (error != null && mounted) {
          setState(() => _error = error);
        }
      }
      return png;
    } finally {
      if (mounted) setState(() => _generating = false);
    }
  }

  Future<void> _onGenerer() async {
    if (!canPrintNonReceipt(context)) return;
    final png = await _generate(sync: false);
    if (!mounted || png == null) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Badge généré et ouvert.')));
  }

  Future<void> _onEnregistrer() async {
    final png = await _generate(sync: true);
    if (!mounted || png == null) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Badge généré ; photo synchronisée sur la fiche de l’étudiant.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StudentsState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Badge / Carte d’identité',
            subtitle: 'Composez et imprimez la carte d’identité scolaire',
            icon: Icons.badge_outlined,
            colorKey: 'rose',
          ),
          const SizedBox(height: 16),
          Expanded(child: SingleChildScrollView(child: _buildBody(state))),
        ],
      ),
    );
  }

  Widget _buildBody(StudentsState state) {
    final detail = _selected != null ? state.currentDetail : null;
    final photoBytes = _currentPhotoBytes(state);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // ── Ligne du haut : aperçu badge + recherche (frame_108/frame_109) ──
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              flex: 3,
              child: _BadgePreview(
                templateBytes: _templateBytes[_template],
                photoBytes: photoBytes,
                fullName: detail != null ? '${detail.nom} ${detail.prenom}' : 'Full Name',
                classeName: detail?.classeActuelle?.nomClasse ?? 'Classe',
                identifiant: detail?.identifiant ?? 'Id Card',
                salleLabel: _salles[_salle] ?? '',
                expirationLabel: _formatExpiration(),
                qrData: (detail?.adresseResponsable?.isNotEmpty ?? false)
                    ? '${detail!.adresseResponsable} \n ${detail.telephoneResponsable ?? ''}'
                    : 'responsable info',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              flex: 2,
              child: _buildSearchPanel(state),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (_error != null) ...[
          Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          const SizedBox(height: 12),
        ],
        // ── Ligne du bas : aperçu caméra + contrôles (widget_19) ────────────
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(flex: 3, child: _buildCameraPreview()),
            const SizedBox(width: 16),
            Expanded(flex: 2, child: _buildControls(state)),
          ],
        ),
      ],
    );
  }

  Widget _buildSearchPanel(StudentsState state) {
    return Container(
      height: 290,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _searchController,
            decoration: const InputDecoration(
              labelText: "Identifiant de l'etudiant",
              prefixIcon: Icon(Icons.search, size: 18),
            ),
            onChanged: (v) {
              if (_selected != null) setState(() => _selected = null);
              context.read<StudentsState>().searchLive(v);
            },
          ),
          const SizedBox(height: 10),
          Expanded(
            child: state.isSearchingLive
                ? const Center(child: CircularProgressIndicator())
                : ListView.separated(
                    itemCount: state.liveSearchResults.length,
                    separatorBuilder: (_, _) => Divider(height: 1, color: AppColors.borderSubtle),
                    itemBuilder: (context, index) {
                      final s = state.liveSearchResults[index];
                      final active = _selected?.id == s.id;
                      return ListTile(
                        dense: true,
                        selected: active,
                        title: Text('${s.nom} ${s.prenom}', style: TextStyle(color: AppColors.textPrimary, fontSize: 13)),
                        subtitle: Text(s.identifiant, style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                        onTap: () => _selectStudent(s),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildCameraPreview() {
    Widget content;
    if (_isIpCamera && _previewRunning) {
      content = _ipPreviewBytes != null
          ? Image.memory(_ipPreviewBytes!, fit: BoxFit.contain, gaplessPlayback: true)
          : const Center(child: CircularProgressIndicator());
    } else if (_previewRunning && _cameraController != null && _cameraInitialized) {
      content = CameraPreview(_cameraController!);
    } else {
      content = Center(
        child: Icon(Icons.videocam_off_outlined, color: AppColors.textMuted, size: 32),
      );
    }

    return Container(
      height: 240,
      decoration: BoxDecoration(
        color: Colors.black,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      clipBehavior: Clip.antiAlias,
      child: content,
    );
  }

  Widget _buildControls(StudentsState state) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ipController,
                  decoration: const InputDecoration(
                    labelText: 'Entrer l’adresse ip du téléphone',
                    isDense: true,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              _checkingIp
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                  : OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _isIpCamera ? const Color(0xFF34A853) : const Color(0xFFFCBC05),
                      ),
                      onPressed: () => _toggleIpCamera(!_isIpCamera),
                      child: Text(_isIpCamera ? 'IP active' : 'Ip desactive', style: const TextStyle(fontSize: 11)),
                    ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _template,
                  decoration: const InputDecoration(labelText: 'Template', isDense: true),
                  items: _templates.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
                  onChanged: _onTemplateChanged,
                ),
              ),
              const SizedBox(width: 8),
              _uploadingTemplate
                  ? const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 12),
                      child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
                    )
                  : IconButton(
                      tooltip: 'Choisir template',
                      icon: const Icon(Icons.upload_outlined, size: 18),
                      onPressed: _pickTemplateForCurrent,
                    ),
              const SizedBox(width: 2),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _salle,
                  decoration: const InputDecoration(labelText: 'Salle', isDense: true),
                  items: _salles.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
                  onChanged: (v) => setState(() => _salle = v ?? _salle),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _expMonth,
                  decoration: const InputDecoration(labelText: 'Mois d’expiration', isDense: true),
                  items: [
                    for (var m = 1; m <= 12; m++) DropdownMenuItem(value: m, child: Text(_moisNoms[m - 1])),
                  ],
                  onChanged: (v) => setState(() => _expMonth = v ?? _expMonth),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _expYear,
                  decoration: const InputDecoration(labelText: 'Année d’expiration', isDense: true),
                  items: [
                    for (var y = DateTime.now().year; y <= DateTime.now().year + 5; y++)
                      DropdownMenuItem(value: y, child: Text('$y')),
                  ],
                  onChanged: (v) => setState(() => _expYear = v ?? _expYear),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _isIpCamera ? 'ip' : _selectedCamera?.name,
                  decoration: const InputDecoration(labelText: 'Choisir La camera', isDense: true),
                  items: [
                    ..._cameras.map((c) => DropdownMenuItem(
                          value: c.name,
                          child: Text(c.name, overflow: TextOverflow.ellipsis),
                        )),
                    if (_isIpCamera) const DropdownMenuItem(value: 'ip', child: Text('Camera ip')),
                  ],
                  onChanged: (v) {
                    if (v == 'ip') return;
                    _cameraController?.dispose();
                    setState(() {
                      _selectedCamera = _cameras.firstWhere((c) => c.name == v);
                      _cameraController = null;
                      _cameraInitialized = false;
                      _previewRunning = false;
                    });
                  },
                ),
              ),
              const SizedBox(width: 10),
              TextButton(
                onPressed: _toggleScan,
                child: Text(
                  _scanActive ? 'Arrêté' : 'Relancé',
                  style: TextStyle(fontSize: 12, color: _scanActive ? AppColors.danger : AppColors.accentLight),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              TextButton(
                onPressed: _onCaptureButton,
                child: Text(
                  _previewRunning ? 'Capturer' : 'Prendre Photo',
                  style: TextStyle(color: _previewRunning ? const Color(0xFF34A853) : const Color(0xFFFCBC05)),
                ),
              ),
              const SizedBox(width: 12),
              TextButton(
                onPressed: _pickPhoto,
                child: const Text('Charger Photo', style: TextStyle(color: Color(0xFF1A73E8))),
              ),
              const Spacer(),
              OutlinedButton(
                style: OutlinedButton.styleFrom(foregroundColor: AppColors.danger, side: const BorderSide(color: AppColors.danger)),
                onPressed: _generating ? null : _onGenerer,
                child: const Text('Générer le Badge'),
              ),
            ],
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF34A853),
                side: const BorderSide(color: Color(0xFF34A853)),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              onPressed: _generating ? null : _onEnregistrer,
              child: _generating
                  ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Générer le Badge et enregistrer la photo'),
            ),
          ),
        ],
      ),
    );
  }
}

/// Aperçu live approximatif du badge (frame_108) — les coordonnées sont les
/// mêmes que badge_renderer.dart (mises à l'échelle), qui reste la seule
/// source de vérité pour le PNG réellement enregistré.
class _BadgePreview extends StatelessWidget {
  const _BadgePreview({
    required this.templateBytes,
    required this.photoBytes,
    required this.fullName,
    required this.classeName,
    required this.identifiant,
    required this.salleLabel,
    required this.expirationLabel,
    required this.qrData,
  });

  final Uint8List? templateBytes;
  final Uint8List? photoBytes;
  final String fullName;
  final String classeName;
  final String identifiant;
  final String salleLabel;
  final String expirationLabel;
  final String qrData;

  static const _canvasW = 1013.0;
  static const _canvasH = 638.0;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: _canvasW / _canvasH,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final scale = constraints.maxWidth / _canvasW;
          return Container(
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(16),
              color: Colors.white,
            ),
            clipBehavior: Clip.antiAlias,
            child: Stack(
              children: [
                Positioned.fill(
                  child: templateBytes != null
                      ? Image.memory(templateBytes!, fit: BoxFit.cover)
                      : Image.asset('assets/badges/template_badge_1.jpg', fit: BoxFit.cover),
                ),
                Positioned(
                  left: 97 * scale,
                  top: 127 * scale,
                  width: 234 * scale,
                  height: 261 * scale,
                  child: Container(
                    decoration: BoxDecoration(border: Border.all(color: const Color(0xFF003366), width: 2)),
                    child: photoBytes != null
                        ? Image.memory(photoBytes!, fit: BoxFit.cover)
                        : Center(child: Text('Photo', style: TextStyle(color: AppColors.textMuted))),
                  ),
                ),
                // painter.drawText(100, 180, 1013, 200, AlignCenter, full_name) / (100, 220, 1013, 200, ..., classe).
                Positioned(
                  left: 100 * scale,
                  top: 180 * scale,
                  width: 1013 * scale,
                  height: 200 * scale,
                  child: Center(
                    child: Text(fullName,
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 24 * scale, fontWeight: FontWeight.bold, color: const Color(0xFF111827))),
                  ),
                ),
                Positioned(
                  left: 100 * scale,
                  top: 220 * scale,
                  width: 1013 * scale,
                  height: 200 * scale,
                  child: Center(
                    child: Text(classeName, textAlign: TextAlign.center, style: TextStyle(fontSize: 20 * scale, color: const Color(0xFF374151))),
                  ),
                ),
                // painter.drawText(x, y, text) : (x,y) = ligne de base.
                Positioned(
                  left: 62 * scale,
                  top: (475 - 18 * 0.8) * scale,
                  child: Text(identifiant, style: TextStyle(fontSize: 18 * scale, fontWeight: FontWeight.bold)),
                ),
                Positioned(
                  left: 300 * scale,
                  top: (480 - 17 * 0.8) * scale,
                  child: Text(expirationLabel, style: TextStyle(fontSize: 17 * scale)),
                ),
                Positioned(
                  left: 560 * scale,
                  top: (480 - 17 * 0.8) * scale,
                  child: Text(salleLabel, style: TextStyle(fontSize: 17 * scale)),
                ),
                Positioned(
                  left: 880 * scale,
                  top: 530 * scale,
                  width: 90 * scale,
                  height: 90 * scale,
                  child: QrImageView(data: qrData, padding: EdgeInsets.zero),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
