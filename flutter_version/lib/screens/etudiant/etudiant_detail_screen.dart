import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/print_gate.dart';
import '../../models/student.dart';
import '../../models/student_detail.dart';
import '../../state/reference_data_state.dart';
import '../../state/students_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';

enum _Tab { inscription, responsable, documents, details }

class _DocumentRow {
  String type = '';
  String numero = '';
  DateTime? dateExpiration;
  String? imageDataUri;
}

const _documentTypes = [
  'Attestation', 'Certificat', 'Certificat de naissance',
  "Carte d'identité", 'Diplôme', 'Relevé de notes',
  "Photo d'identité", 'Autre',
];

/// Équivalent de Ajout_etudiant.vue (ecole_nginx/frontend) — utilisé pour
/// "Nouvel étudiant", "Modifier" ET "Voir détails" (les 3 routes du web
/// pointent vers le même composant ; ici aussi, seul l'onglet "Détails" est
/// strictement en lecture, les 3 autres restent éditables même en
/// consultation, par fidélité). Absent de school_client (formulaire simple,
/// sans onglets ni parcours académique) — repris ici sur demande explicite.
class EtudiantDetailScreen extends StatefulWidget {
  const EtudiantDetailScreen({super.key, this.student});

  final Student? student;

  @override
  State<EtudiantDetailScreen> createState() => _EtudiantDetailScreenState();
}

class _EtudiantDetailScreenState extends State<EtudiantDetailScreen> {
  _Tab _tab = _Tab.inscription;

  final _nom = TextEditingController();
  final _prenom = TextEditingController();
  final _telephone = TextEditingController();
  final _email = TextEditingController();
  final _adresse = TextEditingController();
  final _lieuDeNaissance = TextEditingController();
  final _religion = TextEditingController();
  final _nisu = TextEditingController();
  final _dernierEtablissement = TextEditingController();

  final _nomResponsable = TextEditingController();
  final _prenomResponsable = TextEditingController();
  final _telephoneResponsable = TextEditingController();
  final _emailResponsable = TextEditingController();
  final _adresseResponsable = TextEditingController();
  final _metierResponsable = TextEditingController();
  String? _relationResponsable;
  String? _sexeResponsable;

  String _sexe = 'M';
  DateTime? _dateDeNaissance;
  String? _niveauId;
  String? _classeId;
  String? _anneeId;
  String? _faculteId;
  String _aideFinanciere = 'Aucune';

  final List<_DocumentRow> _documents = [_DocumentRow()];

  bool _saving = false;
  String? _error;
  bool _loadedOnce = false;

  bool get _isExisting => widget.student != null;

  @override
  void initState() {
    super.initState();
    final s = widget.student;
    if (s != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _loadFullDetail(s.id));
    }
  }

  Future<void> _loadFullDetail(String id) async {
    await context.read<StudentsState>().loadDetail(id);
    if (!mounted) return;
    final d = context.read<StudentsState>().currentDetail;
    if (d != null) _applyDetail(d);
    setState(() => _loadedOnce = true);
  }

  void _applyDetail(StudentDetail d) {
    _nom.text = d.nom;
    _prenom.text = d.prenom;
    _telephone.text = d.telephone ?? '';
    _email.text = d.email ?? '';
    _adresse.text = d.adresse;
    _lieuDeNaissance.text = d.lieuDeNaissance ?? '';
    _sexe = d.sexe.isNotEmpty ? d.sexe : 'M';
    _dateDeNaissance = DateTime.tryParse(d.dateDeNaissance);
    _nomResponsable.text = d.nomResponsable ?? '';
    _prenomResponsable.text = d.prenomResponsable ?? '';
    _telephoneResponsable.text = d.telephoneResponsable ?? '';
    _emailResponsable.text = d.emailResponsable ?? '';
    _adresseResponsable.text = d.adresseResponsable ?? '';
    _metierResponsable.text = d.metierResponsable ?? '';
    _relationResponsable = d.relationResponsable;
    _sexeResponsable = d.sexeResponsable;
    final classeActuelle = d.classeActuelle;
    _niveauId = classeActuelle?.niveauId;
    _classeId = classeActuelle?.classesId;
    _anneeId = classeActuelle?.anneeAcademiqueId;
    setState(() {});
  }

  @override
  void dispose() {
    _nom.dispose();
    _prenom.dispose();
    _telephone.dispose();
    _email.dispose();
    _adresse.dispose();
    _lieuDeNaissance.dispose();
    _religion.dispose();
    _nisu.dispose();
    _dernierEtablissement.dispose();
    _nomResponsable.dispose();
    _prenomResponsable.dispose();
    _telephoneResponsable.dispose();
    _emailResponsable.dispose();
    _adresseResponsable.dispose();
    _metierResponsable.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _dateDeNaissance ?? DateTime(2010),
      firstDate: DateTime(1950),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _dateDeNaissance = picked);
  }

  Future<void> _pickDocumentDate(_DocumentRow doc) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: doc.dateExpiration ?? DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) setState(() => doc.dateExpiration = picked);
  }

  Future<void> _pickDocumentFile(_DocumentRow doc) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'pdf'],
      withData: true,
    );
    final file = result?.files.single;
    if (file?.bytes == null) return;
    final ext = (file!.extension ?? 'png').toLowerCase();
    final mime = ext == 'jpg' ? 'jpeg' : ext;
    setState(() => doc.imageDataUri = 'data:image/$mime;base64,${base64Encode(file.bytes!)}');
  }

  String _fmtDate(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  Future<void> _submit() async {
    if (_nom.text.trim().length < 3 ||
        _prenom.text.trim().length < 3 ||
        _lieuDeNaissance.text.trim().length < 3 ||
        _adresse.text.trim().length < 3 ||
        _dateDeNaissance == null) {
      setState(() {
        _tab = _Tab.inscription;
        _error = 'Nom, prénom, lieu de naissance, adresse (min. 3 caractères) et date de naissance sont obligatoires.';
      });
      return;
    }
    if (_niveauId == null || _classeId == null || _anneeId == null) {
      setState(() {
        _tab = _Tab.inscription;
        _error = 'Niveau, classe et année académique sont obligatoires.';
      });
      return;
    }

    setState(() {
      _saving = true;
      _error = null;
    });

    final documentss = _documents
        .where((d) => d.type.isNotEmpty)
        .map((d) => {
              'type_de_document': d.type,
              'document_numero': d.numero.trim().isEmpty ? null : d.numero.trim(),
              'document_date_dexpiration': d.dateExpiration != null ? _fmtDate(d.dateExpiration!) : null,
              'document_image': d.imageDataUri,
            })
        .toList();

    final payload = {
      if (widget.student != null) 'id': widget.student!.id,
      'nom': _nom.text.trim(),
      'prenom': _prenom.text.trim(),
      'sexe': _sexe,
      'date_de_naissance': _fmtDate(_dateDeNaissance!),
      'lieu_de_naissance': _lieuDeNaissance.text.trim(),
      'adresse': _adresse.text.trim(),
      'religion': _religion.text.trim().isEmpty ? null : _religion.text.trim(),
      'telephone': _telephone.text.trim().isEmpty ? null : _telephone.text.trim(),
      'email': _email.text.trim().isEmpty ? null : _email.text.trim(),
      'aide_financiere': _aideFinanciere,
      'nisu': _nisu.text.trim().isEmpty ? null : _nisu.text.trim(),
      'dernier_etablissement': _dernierEtablissement.text.trim().isEmpty ? null : _dernierEtablissement.text.trim(),
      'niveau_id': _niveauId,
      'classe_actuelle_id': _classeId,
      'annee_academique_id': _anneeId,
      'faculte_id': _faculteId,
      'nom_responsable': _nomResponsable.text.trim().isEmpty ? null : _nomResponsable.text.trim(),
      'prenom_responsable': _prenomResponsable.text.trim().isEmpty ? null : _prenomResponsable.text.trim(),
      'adresse_responsable': _adresseResponsable.text.trim().isEmpty ? null : _adresseResponsable.text.trim(),
      'email_responsable': _emailResponsable.text.trim().isEmpty ? null : _emailResponsable.text.trim(),
      'relation_responsable': _relationResponsable,
      'sexe_responsable': _sexeResponsable,
      'telephone_responsable': _telephoneResponsable.text.trim().isEmpty ? null : _telephoneResponsable.text.trim(),
      'metier_responsable': _metierResponsable.text.trim().isEmpty ? null : _metierResponsable.text.trim(),
      'documentss': documentss,
    };

    final error = await context.read<StudentsState>().save(payload);
    if (!mounted) return;
    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Étudiant enregistré.')));
      Navigator.of(context).pop(true);
    } else {
      setState(() {
        _saving = false;
        _error = error;
      });
    }
  }

  Future<void> _printRecu() async {
    final id = widget.student?.id;
    if (id == null) return;
    final error = await context.read<StudentsState>().printRecuInscription(id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  Future<void> _printFiche() async {
    if (!canPrintNonReceipt(context)) return;
    final id = widget.student?.id;
    if (id == null) return;
    final error = await context.read<StudentsState>().printStudentDetails(id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final students = context.watch<StudentsState>();

    if (_isExisting && !_loadedOnce) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: SectionHeader(
                  title: _isExisting ? "Modifier l'étudiant" : 'Nouvel étudiant',
                  subtitle: _isExisting ? 'ID : ${widget.student!.id}' : "Formulaire d'inscription",
                  icon: Icons.school_outlined,
                  colorKey: 'blue',
                ),
              ),
              if (_isExisting) ...[
                OutlinedButton.icon(
                  onPressed: students.isPrintingRecu ? null : _printRecu,
                  icon: students.isPrintingRecu
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.receipt_long_outlined, size: 16),
                  label: const Text('Reçu'),
                ),
                const SizedBox(width: 10),
                FilledButton.icon(
                  onPressed: students.isPrintingFiche ? null : _printFiche,
                  icon: students.isPrintingFiche
                      ? const SizedBox(
                          height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.print_outlined, size: 16),
                  label: const Text('Imprimer'),
                ),
              ],
            ],
          ),
          const SizedBox(height: 16),
          _buildTabBar(),
          const SizedBox(height: 16),
          if (_error != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.danger.withValues(alpha: 0.08),
                border: Border.all(color: AppColors.danger.withValues(alpha: 0.3)),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
            ),
            const SizedBox(height: 16),
          ],
          Expanded(
            child: SingleChildScrollView(
              child: switch (_tab) {
                _Tab.inscription => _buildInscriptionTab(),
                _Tab.responsable => _buildResponsableTab(),
                _Tab.documents => _buildDocumentsTab(),
                _Tab.details => _buildDetailsTab(students),
              },
            ),
          ),
          if (_tab != _Tab.details) ...[
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: FilledButton(
                onPressed: _saving ? null : _submit,
                child: _saving
                    ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                    : Text(_isExisting ? 'Sauvegarder les modifications' : "Enregistrer l'étudiant"),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    Widget pill(_Tab value, String label, IconData icon) {
      final selected = _tab == value;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: selected ? AppColors.hoverOverlay : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _tab = value),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(icon, size: 15, color: selected ? AppColors.accentLight : AppColors.textMuted),
                  const SizedBox(width: 8),
                  Text(label,
                      style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: selected ? AppColors.textPrimary : AppColors.textMuted)),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          pill(_Tab.inscription, 'Inscription', Icons.school_outlined),
          pill(_Tab.responsable, 'Responsable', Icons.person_outline),
          pill(_Tab.documents, 'Documents', Icons.attach_file),
          if (_isExisting) pill(_Tab.details, 'Détails', Icons.search_outlined),
        ],
      ),
    );
  }

  Widget _sectionCard(String title, IconData icon, Widget child) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(14),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(border: Border(bottom: BorderSide(color: AppColors.borderSubtle))),
            child: Row(
              children: [
                Icon(icon, size: 15, color: AppColors.textMuted),
                const SizedBox(width: 8),
                Text(title.toUpperCase(),
                    style: TextStyle(
                        fontSize: 11, letterSpacing: 0.6, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
              ],
            ),
          ),
          Padding(padding: const EdgeInsets.all(16), child: child),
        ],
      ),
    );
  }

  Widget _grid(List<Widget> children, {int minColWidth = 220}) {
    return LayoutBuilder(builder: (context, constraints) {
      final cols = (constraints.maxWidth / minColWidth).floor().clamp(1, 4);
      return Wrap(
        spacing: 12,
        runSpacing: 12,
        children: children
            .map((c) => SizedBox(width: (constraints.maxWidth - (cols - 1) * 12) / cols, child: c))
            .toList(),
      );
    });
  }

  Widget _buildInscriptionTab() {
    final ref = context.watch<ReferenceDataState>();
    final niveauName = ref.niveaux.where((n) => n.id == _niveauId).map((n) => n.name).firstOrNull;
    final showFaculte = niveauName == 'Universitaire' || niveauName == 'Technique';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _sectionCard(
          'Parcours scolaire',
          Icons.menu_book_outlined,
          _grid([
            DropdownButtonFormField<String>(
              initialValue: _niveauId,
              decoration: const InputDecoration(labelText: 'Niveau / Section'),
              items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
              onChanged: (v) => setState(() {
                _niveauId = v;
                _classeId = null;
                _faculteId = null;
              }),
            ),
            TextFormField(
              controller: _dernierEtablissement,
              decoration: const InputDecoration(labelText: 'Dernier établissement'),
            ),
            TextFormField(controller: _nisu, decoration: const InputDecoration(labelText: 'NISU')),
          ]),
        ),
        _sectionCard(
          'Identité',
          Icons.badge_outlined,
          _grid([
            TextFormField(controller: _nom, decoration: const InputDecoration(labelText: 'Nom')),
            TextFormField(controller: _prenom, decoration: const InputDecoration(labelText: 'Prénom')),
            DropdownButtonFormField<String>(
              initialValue: _sexe,
              decoration: const InputDecoration(labelText: 'Sexe'),
              items: const [
                DropdownMenuItem(value: 'F', child: Text('Féminin (F)')),
                DropdownMenuItem(value: 'M', child: Text('Masculin (M)')),
              ],
              onChanged: (v) => setState(() => _sexe = v ?? 'M'),
            ),
            InkWell(
              onTap: _pickDate,
              child: InputDecorator(
                decoration: const InputDecoration(labelText: 'Date de naissance'),
                child: Text(_dateDeNaissance == null ? '—' : _fmtDate(_dateDeNaissance!)),
              ),
            ),
            TextFormField(controller: _lieuDeNaissance, decoration: const InputDecoration(labelText: 'Lieu de naissance')),
            TextFormField(controller: _religion, decoration: const InputDecoration(labelText: 'Religion')),
          ]),
        ),
        _sectionCard(
          'Contact',
          Icons.contact_phone_outlined,
          _grid([
            TextFormField(controller: _adresse, decoration: const InputDecoration(labelText: 'Adresse')),
            TextFormField(controller: _telephone, decoration: const InputDecoration(labelText: 'Téléphone')),
            TextFormField(controller: _email, decoration: const InputDecoration(labelText: 'Courriel')),
          ]),
        ),
        _sectionCard(
          'Inscription académique',
          Icons.assignment_outlined,
          _grid([
            DropdownButtonFormField<String>(
              initialValue: _anneeId,
              decoration: const InputDecoration(labelText: 'Année académique'),
              items: ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
              onChanged: (v) => setState(() => _anneeId = v),
            ),
            if (showFaculte)
              DropdownButtonFormField<String>(
                initialValue: _faculteId,
                decoration: const InputDecoration(labelText: 'Faculté / Domaine'),
                items: ref.facultes.map((f) => DropdownMenuItem(value: f.id, child: Text(f.nom))).toList(),
                onChanged: (v) => setState(() => _faculteId = v),
              ),
            DropdownButtonFormField<String>(
              initialValue: _classeId,
              decoration: const InputDecoration(labelText: 'Classe'),
              items: ref.classesForNiveau(_niveauId).map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))).toList(),
              onChanged: (v) => setState(() => _classeId = v),
            ),
            DropdownButtonFormField<String>(
              initialValue: _aideFinanciere,
              decoration: const InputDecoration(labelText: 'Aide financière'),
              items: const [
                DropdownMenuItem(value: 'Aucune', child: Text('Aucune')),
                DropdownMenuItem(value: '1/4 Bourse', child: Text('1/4 Bourse')),
                DropdownMenuItem(value: 'Démie Bourse', child: Text('Demi-bourse')),
                DropdownMenuItem(value: 'Bourse', child: Text('Bourse complète')),
              ],
              onChanged: (v) => setState(() => _aideFinanciere = v ?? 'Aucune'),
            ),
          ]),
        ),
      ],
    );
  }

  Widget _buildResponsableTab() {
    return _sectionCard(
      'Informations du responsable',
      Icons.person_outline,
      _grid([
        TextFormField(controller: _nomResponsable, decoration: const InputDecoration(labelText: 'Nom')),
        TextFormField(controller: _prenomResponsable, decoration: const InputDecoration(labelText: 'Prénom')),
        DropdownButtonFormField<String>(
          initialValue: _sexeResponsable,
          decoration: const InputDecoration(labelText: 'Sexe'),
          items: const [
            DropdownMenuItem(value: 'F', child: Text('Féminin (F)')),
            DropdownMenuItem(value: 'M', child: Text('Masculin (M)')),
          ],
          onChanged: (v) => setState(() => _sexeResponsable = v),
        ),
        TextFormField(controller: _adresseResponsable, decoration: const InputDecoration(labelText: 'Adresse')),
        TextFormField(controller: _telephoneResponsable, decoration: const InputDecoration(labelText: 'Téléphone')),
        TextFormField(controller: _emailResponsable, decoration: const InputDecoration(labelText: 'Courriel')),
        TextFormField(controller: _metierResponsable, decoration: const InputDecoration(labelText: 'Métier')),
        TextFormField(
          initialValue: _relationResponsable,
          decoration: const InputDecoration(labelText: 'Relation', hintText: 'Père, Mère, Tuteur...'),
          onChanged: (v) => _relationResponsable = v,
        ),
      ]),
    );
  }

  Widget _buildDocumentsTab() {
    return _sectionCard(
      'Pièces soumises',
      Icons.attach_file,
      Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var i = 0; i < _documents.length; i++) ...[
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppColors.appBg,
                border: Border.all(color: AppColors.borderSubtle),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Text('Doc ${i + 1}', style: TextStyle(fontSize: 11, color: AppColors.textMuted, fontFamily: 'monospace')),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.close, size: 16),
                        onPressed: _documents.length == 1 ? null : () => setState(() => _documents.removeAt(i)),
                      ),
                    ],
                  ),
                  _grid([
                    DropdownButtonFormField<String>(
                      initialValue: _documents[i].type.isEmpty ? null : _documents[i].type,
                      decoration: const InputDecoration(labelText: 'Type'),
                      items: _documentTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                      onChanged: (v) => setState(() => _documents[i].type = v ?? ''),
                    ),
                    TextFormField(
                      initialValue: _documents[i].numero,
                      decoration: const InputDecoration(labelText: 'Numéro'),
                      onChanged: (v) => _documents[i].numero = v,
                    ),
                    InkWell(
                      onTap: () => _pickDocumentDate(_documents[i]),
                      child: InputDecorator(
                        decoration: const InputDecoration(labelText: 'Expiration'),
                        child: Text(_documents[i].dateExpiration == null ? '—' : _fmtDate(_documents[i].dateExpiration!)),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => _pickDocumentFile(_documents[i]),
                      icon: const Icon(Icons.upload_file_outlined, size: 16),
                      label: Text(_documents[i].imageDataUri != null ? 'Sélectionné ✓' : 'Choisir un fichier'),
                    ),
                  ]),
                ],
              ),
            ),
          ],
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: () => setState(() => _documents.add(_DocumentRow())),
              icon: const Icon(Icons.add, size: 16),
              label: const Text('Ajouter un document'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailsTab(StudentsState students) {
    final d = students.currentDetail;
    if (students.isLoadingDetail) return const Center(child: CircularProgressIndicator());
    if (d == null) {
      return Text(students.detailError ?? 'Profil indisponible.', style: TextStyle(color: AppColors.textMuted));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        LayoutBuilder(builder: (context, constraints) {
          final twoCols = constraints.maxWidth >= 700;
          final perso = _sectionCard(
            'Informations personnelles',
            Icons.badge_outlined,
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _infoRow('Identifiant', d.identifiant, mono: true),
                _infoRow('Nom complet', '${d.nom} ${d.prenom}'),
                _infoRow('Sexe', d.sexe),
                _infoRow('Date de naissance', d.dateDeNaissance),
                _infoRow('Lieu de naissance', d.lieuDeNaissance ?? ''),
                _infoRow('Adresse', d.adresse),
                _infoRow('Téléphone', d.telephone ?? ''),
                _infoRow('Courriel', d.email ?? ''),
                _infoRow('Classe actuelle', d.classeActuelle?.nomClasse ?? '', accent: true),
              ],
            ),
          );
          final right = Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (d.nomResponsable != null && d.nomResponsable!.isNotEmpty)
                _sectionCard(
                  'Responsable',
                  Icons.person_outline,
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _infoRow('Nom', '${d.nomResponsable} ${d.prenomResponsable ?? ''}'),
                      _infoRow('Sexe', d.sexeResponsable ?? ''),
                      _infoRow('Relation', d.relationResponsable ?? '', accent: true),
                      _infoRow('Métier', d.metierResponsable ?? ''),
                      _infoRow('Téléphone', d.telephoneResponsable ?? ''),
                      _infoRow('Courriel', d.emailResponsable ?? ''),
                      _infoRow('Adresse', d.adresseResponsable ?? ''),
                    ],
                  ),
                ),
              if (d.piecesSoumises.isNotEmpty)
                _sectionCard(
                  'Documents soumis (${d.piecesSoumises.length})',
                  Icons.attach_file,
                  Column(
                    children: d.piecesSoumises.map((p) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (p.imageBase64 != null && p.imageBase64!.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(right: 10),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.memory(
                                    base64Decode(p.imageBase64!.split(',').last),
                                    width: 40,
                                    height: 52,
                                    fit: BoxFit.cover,
                                    errorBuilder: (_, _, _) => const SizedBox.shrink(),
                                  ),
                                ),
                              ),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(p.typeDeDocument, style: TextStyle(fontSize: 13, color: AppColors.textPrimary)),
                                  if (p.documentNumero.isNotEmpty)
                                    _infoRow('Numéro', p.documentNumero),
                                  if (p.dateExpiration.isNotEmpty)
                                    _infoRow('Expiration', p.dateExpiration),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
            ],
          );
          if (!twoCols) return Column(children: [perso, right]);
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [Expanded(child: perso), const SizedBox(width: 16), Expanded(child: right)],
          );
        }),
        if (d.classesEtudiant.isNotEmpty)
          _sectionCard(
            'Parcours académique',
            Icons.trending_up,
            Column(
              children: d.classesEtudiant.map((p) => _ParcoursTile(student: d, entry: p)).toList(),
            ),
          ),
      ],
    );
  }

  Widget _infoRow(String label, String value, {bool mono = false, bool accent = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
          const Spacer(),
          Text(
            value.isEmpty ? '—' : value,
            textAlign: TextAlign.right,
            style: TextStyle(
              fontSize: 12,
              fontFamily: mono ? 'monospace' : null,
              color: accent ? AppColors.accentLight : const Color(0xFF8B949E),
              fontWeight: accent ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}

extension _FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull {
    final it = iterator;
    return it.moveNext() ? it.current : null;
  }
}

/// Une entrée du parcours académique — accordéon (toggleParcours(),
/// Ajout_etudiant.vue) : cours suivis, moyennes, suivi financier.
class _ParcoursTile extends StatefulWidget {
  const _ParcoursTile({required this.student, required this.entry});

  final StudentDetail student;
  final ClasseEtudiantEntry entry;

  @override
  State<_ParcoursTile> createState() => _ParcoursTileState();
}

class _ParcoursTileState extends State<_ParcoursTile> {
  bool _open = false;
  ParcoursDetails? _details;
  bool _loading = false;

  Future<void> _toggle() async {
    setState(() => _open = !_open);
    if (_open && _details == null) {
      setState(() => _loading = true);
      final details = await context.read<StudentsState>().loadParcoursDetails(
            studentId: widget.student.id,
            classeId: widget.entry.classesId,
            niveauId: widget.entry.niveauId,
            anneeId: widget.entry.anneeAcademiqueId,
          );
      if (!mounted) return;
      setState(() {
        _details = details;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        InkWell(
          onTap: _toggle,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(color: Color(0xFF3FB950), shape: BoxShape.circle),
                ),
                const SizedBox(width: 10),
                Text(widget.entry.anneeLabel, style: TextStyle(fontSize: 13, color: AppColors.textPrimary, fontWeight: FontWeight.w500)),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: AppColors.hoverOverlay, borderRadius: BorderRadius.circular(999)),
                  child: Text(widget.entry.nomClasse, style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                ),
                const Spacer(),
                Icon(_open ? Icons.expand_less : Icons.expand_more, size: 18, color: AppColors.textMuted),
              ],
            ),
          ),
        ),
        if (_open)
          Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: _loading
                ? const Padding(padding: EdgeInsets.all(16), child: Center(child: CircularProgressIndicator()))
                : _details == null
                    ? Text('Aucune donnée.', style: TextStyle(color: AppColors.textMuted, fontSize: 12))
                    : _buildParcoursContent(_details!),
          ),
      ],
    );
  }

  Widget _buildParcoursContent(ParcoursDetails details) {
    final analyse = details.analyses.isNotEmpty ? details.analyses.first : null;
    final versements = details.paiement.versements.where((v) => !v.isRetourne).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('NOTES ET MOYENNES',
            style: TextStyle(fontSize: 10.5, letterSpacing: 0.6, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        if (analyse == null)
          Padding(
            padding: EdgeInsets.only(bottom: 14),
            child: Text('Aucune note enregistrée', style: TextStyle(fontSize: 12, color: AppColors.textMuted, fontStyle: FontStyle.italic)),
          )
        else
          Container(
            margin: const EdgeInsets.only(bottom: 14),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.appBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Text('Moyenne générale', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                    const Spacer(),
                    Text('${analyse.moyenneGen}/10',
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: _moyenneColor(analyse.moyenneGen))),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: LinearProgressIndicator(
                    value: (analyse.moyenneGen / 10).clamp(0, 1),
                    minHeight: 6,
                    backgroundColor: AppColors.hoverOverlay,
                    valueColor: AlwaysStoppedAnimation(_moyenneColor(analyse.moyenneGen)),
                  ),
                ),
                if (analyse.topNom != null || analyse.lowNom != null) ...[
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      if (analyse.topNom != null)
                        Expanded(
                          child: Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                                color: const Color(0xFF3FB950).withValues(alpha: 0.08), borderRadius: BorderRadius.circular(10)),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('🏆 Meilleure matière', style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
                                Text(analyse.topNom!,
                                    style: const TextStyle(fontSize: 12, color: Color(0xFF3FB950), fontWeight: FontWeight.w600)),
                                Text('${analyse.topMoy}/10', style: const TextStyle(fontSize: 11, color: Color(0xFF3FB950))),
                              ],
                            ),
                          ),
                        ),
                      if (analyse.topNom != null && analyse.lowNom != null) const SizedBox(width: 10),
                      if (analyse.lowNom != null)
                        Expanded(
                          child: Container(
                            padding: const EdgeInsets.all(10),
                            decoration:
                                BoxDecoration(color: AppColors.danger.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(10)),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('⚠ À améliorer', style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
                                Text(analyse.lowNom!,
                                    style: const TextStyle(fontSize: 12, color: AppColors.danger, fontWeight: FontWeight.w600)),
                                Text('${analyse.lowMoy}/10', style: const TextStyle(fontSize: 11, color: AppColors.danger)),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        Text('SUIVI FINANCIER',
            style: TextStyle(fontSize: 10.5, letterSpacing: 0.6, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        if (versements.isEmpty)
          Text('Aucun versement enregistré.', style: TextStyle(fontSize: 12, color: AppColors.textMuted, fontStyle: FontStyle.italic))
        else
          Container(
            decoration: BoxDecoration(border: Border.all(color: AppColors.borderSubtle), borderRadius: BorderRadius.circular(10)),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: versements.map((v) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(border: Border(top: BorderSide(color: AppColors.borderSubtle))),
                  child: Row(
                    children: [
                      Expanded(flex: 3, child: Text(v.dateKey, style: TextStyle(fontSize: 11, color: AppColors.textMuted, fontFamily: 'monospace'))),
                      Expanded(flex: 2, child: Text(v.depot.toStringAsFixed(0), textAlign: TextAlign.center, style: TextStyle(fontSize: 12, color: AppColors.textPrimary))),
                      Expanded(
                          flex: 2,
                          child: Text(v.totalVerse.toStringAsFixed(0),
                              textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, color: Color(0xFF3FB950), fontWeight: FontWeight.w600))),
                      Expanded(
                          flex: 2,
                          child: Text(v.balance.toStringAsFixed(0),
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 12, color: v.balance > 0 ? AppColors.danger : const Color(0xFF3FB950)))),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
      ],
    );
  }

  Color _moyenneColor(double m) {
    if (m >= 9) return const Color(0xFF3FB950);
    if (m >= 7) return const Color(0xFFD29922);
    if (m >= 6) return AppColors.accentLight;
    return AppColors.danger;
  }
}
