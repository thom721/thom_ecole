import 'dart:async';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

/// Capture une photo TEST (jamais enregistrée sur un étudiant, jamais
/// persistée dans le gabarit) qui sert uniquement à calibrer visuellement
/// les réglages de luminosité/contraste/saturation/centrage/zoom d'un
/// emplacement photo pendant la conception — voir
/// badge_builder_property_panel.dart. Volontairement plus simple que le
/// flux caméra complet de badge_screen.dart (pas de caméra IP) mais avec
/// le même rebalayage périodique (une caméra branchée après ouverture du
/// dialogue doit quand même apparaître dans le sélecteur).
Future<Uint8List?> showBadgeTestPhotoCaptureDialog(BuildContext context) {
  return showDialog<Uint8List>(
    context: context,
    builder: (context) => const _TestPhotoCaptureDialog(),
  );
}

class _TestPhotoCaptureDialog extends StatefulWidget {
  const _TestPhotoCaptureDialog();

  @override
  State<_TestPhotoCaptureDialog> createState() =>
      _TestPhotoCaptureDialogState();
}

class _TestPhotoCaptureDialogState extends State<_TestPhotoCaptureDialog> {
  List<CameraDescription> _cameras = [];
  CameraDescription? _selectedCamera;
  CameraController? _controller;
  bool _initializing = false;
  String? _error;
  Timer? _scanTimer;

  @override
  void initState() {
    super.initState();
    _loadCameras();
    _scanTimer = Timer.periodic(
      const Duration(seconds: 2),
      (_) => _rescanCameras(),
    );
  }

  /// Rebalayage périodique (voir badge_screen.dart::_loadCameras) — met à
  /// jour la liste affichée dans le sélecteur SANS redémarrer l'aperçu
  /// actif : contrairement au premier chargement ([_loadCameras], qui
  /// sélectionne toujours la première caméra), ici on ne touche à
  /// [_selectedCamera]/[_controller] QUE si la caméra active a disparu
  /// (débranchée) — sinon, redémarrer le contrôleur toutes les 2 secondes
  /// ferait clignoter l'aperçu en continu.
  Future<void> _rescanCameras() async {
    try {
      final cams = await availableCameras();
      if (!mounted) return;
      setState(() => _cameras = cams);
      final stillPresent =
          _selectedCamera == null ||
          cams.any((c) => c.name == _selectedCamera!.name);
      if (stillPresent) return;
      if (cams.isNotEmpty) {
        await _selectCamera(cams.first);
      } else {
        await _controller?.dispose();
        if (!mounted) return;
        setState(() {
          _selectedCamera = null;
          _controller = null;
        });
      }
    } catch (_) {
      // Rebalayage silencieux : une erreur transitoire ne doit pas
      // remplacer une erreur déjà affichée ni interrompre un aperçu actif.
    }
  }

  Future<void> _loadCameras() async {
    setState(() {
      _initializing = true;
      _error = null;
    });
    try {
      final cams = await availableCameras();
      if (!mounted) return;
      setState(() => _cameras = cams);
      if (cams.isNotEmpty) {
        await _selectCamera(cams.first);
      } else {
        setState(() => _initializing = false);
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
      if (mounted) setState(() => _initializing = false);
    }
  }

  Future<void> _selectCamera(CameraDescription camera) async {
    await _controller?.dispose();
    setState(() {
      _selectedCamera = camera;
      _controller = null;
      _initializing = true;
      _error = null;
    });
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
        _controller = ctrl;
        _initializing = false;
      });
    } catch (e) {
      await ctrl.dispose();
      if (mounted) {
        setState(() {
          _error = e.toString();
          _initializing = false;
        });
      }
    }
  }

  Future<void> _capture() async {
    final ctrl = _controller;
    if (ctrl == null || !ctrl.value.isInitialized) return;
    try {
      final file = await ctrl.takePicture();
      final bytes = await file.readAsBytes();
      if (mounted) Navigator.of(context).pop(Uint8List.fromList(bytes));
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  void dispose() {
    _scanTimer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Photo test'),
      content: SizedBox(
        width: 480,
        height: 400,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Sert à régler l\'apparence (luminosité, contraste, cadrage) — jamais '
              'sauvegardée dans le gabarit ; peut ensuite être enregistrée sur la '
              'fiche d\'un étudiant prévisualisé via "Enregistrer la photo".',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            if (_cameras.length > 1)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: DropdownButtonFormField<CameraDescription>(
                  initialValue: _selectedCamera,
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: 'Caméra',
                    isDense: true,
                  ),
                  items: _cameras
                      .map(
                        (c) => DropdownMenuItem(value: c, child: Text(c.name)),
                      )
                      .toList(),
                  onChanged: (c) {
                    if (c != null) _selectCamera(c);
                  },
                ),
              ),
            Expanded(child: _buildPreview()),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Annuler'),
        ),
        FilledButton(
          onPressed: (_controller?.value.isInitialized ?? false)
              ? _capture
              : null,
          child: const Text('Capturer'),
        ),
      ],
    );
  }

  Widget _buildPreview() {
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Text(
            'Caméra indisponible : $_error',
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.red),
          ),
        ),
      );
    }
    if (_initializing || _controller == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: CameraPreview(_controller!),
    );
  }
}
