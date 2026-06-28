import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/programme.dart';
import '../../models/student.dart' show Niveau;
import '../../state/programme_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';

const _joursOptions = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
const _sessionOptions = ['1ère', '2ème'];

class _ProgRow {
  _ProgRow({
    this.id,
    this.niveauId,
    this.coursId,
    this.professeurId,
    this.classeId,
    this.anneeId,
    this.faculteId,
    this.jours,
    String heure = '',
    String coefficients = '',
    this.session,
    String noteDePassage = '',
  })  : heure = TextEditingController(text: heure),
        coefficients = TextEditingController(text: coefficients),
        noteDePassage = TextEditingController(text: noteDePassage);

  factory _ProgRow.fromProgramme(Programme p) => _ProgRow(
        id: p.id,
        niveauId: p.niveauId,
        coursId: p.coursId,
        professeurId: p.professeurId,
        classeId: p.classeId,
        anneeId: p.anneeAcademiqueId,
        faculteId: p.faculteId,
        jours: p.jours,
        heure: p.heure ?? '',
        coefficients: p.coefficients?.toString() ?? '',
        session: p.session,
        noteDePassage: p.noteDePassage?.toString() ?? '',
      );

  final String? id;
  String? niveauId;
  String? coursId;
  String? professeurId;
  String? classeId;
  String? anneeId;
  String? faculteId;
  String? jours;
  final TextEditingController heure;
  final TextEditingController coefficients;
  String? session;
  final TextEditingController noteDePassage;

  void dispose() {
    heure.dispose();
    coefficients.dispose();
    noteDePassage.dispose();
  }
}

/// Équivalent de add_programme_page()/add_programme_line()/
/// enregistrer_programme() (school_client, Controllers/Main.py:9714-9905,
/// 10058-10082) : une page dédiée (pas une modale) où l'on peut ajouter
/// plusieurs lignes de programme dynamiquement et les enregistrer toutes en
/// un seul envoi (POST v1/programme, {"programmeCoursObject": [...]}). En
/// édition, la page s'ouvre avec UNE ligne préremplie (équivalent du
/// routeur de réponses asynchrones sur `v1/programme/{id}`) ; on peut
/// ajouter d'autres lignes vierges dans le même envoi. "Supprimer de la
/// base" (ligne existante) appelle réellement GET v1/delete-programme/{id}.
class ProgrammeFormScreen extends StatefulWidget {
  const ProgrammeFormScreen({super.key, this.initial});

  final Programme? initial;

  @override
  State<ProgrammeFormScreen> createState() => _ProgrammeFormScreenState();
}

class _ProgrammeFormScreenState extends State<ProgrammeFormScreen> {
  late final List<_ProgRow> _rows = [
    if (widget.initial != null) _ProgRow.fromProgramme(widget.initial!) else _ProgRow(),
  ];
  String? _error;

  bool get _isEdit => widget.initial != null;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ProgrammeState>().loadCombos();
    });
  }

  @override
  void dispose() {
    for (final r in _rows) {
      r.dispose();
    }
    super.dispose();
  }

  void _addRow() => setState(() => _rows.add(_ProgRow()));

  void _removeRow(_ProgRow row) {
    setState(() {
      _rows.remove(row);
      row.dispose();
    });
  }

  bool _isUniOuTech(String name) => name == 'Universitaire' || name == 'Technique';

  Future<void> _deleteFromDb(_ProgRow row) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: const Text('Supprimer définitivement cette ligne du programme ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<ProgrammeState>().delete(row.id!);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
      return;
    }
    _removeRow(row);
  }

  /// Équivalent (simplifié, en superset sûr) des validations de
  /// store_programme() (RProgramme.py:276-341), appliquées à chaque ligne.
  Future<void> _submit(List<Niveau> niveaux) async {
    final items = <Map<String, dynamic>>[];
    for (final row in _rows) {
      if (row.niveauId == null || row.coursId == null || row.professeurId == null || row.classeId == null || row.anneeId == null) {
        setState(() => _error = 'Niveau, cours, professeur, classe et année académique sont requis pour chaque ligne.');
        return;
      }
      final niveauName = niveaux.firstWhere((n) => n.id == row.niveauId, orElse: () => Niveau(id: '', name: '')).name;

      if (_isUniOuTech(niveauName)) {
        if (row.faculteId == null || row.noteDePassage.text.trim().isEmpty || row.jours == null || row.heure.text.trim().isEmpty) {
          setState(() => _error = 'Faculté, note de passage, jours et heure sont obligatoires pour le niveau $niveauName.');
          return;
        }
        if (niveauName == 'Universitaire' && (row.session == null || row.session!.isEmpty)) {
          setState(() => _error = 'La session est obligatoire pour le niveau Universitaire.');
          return;
        }
      } else if (niveauName == 'Primaire' || niveauName == 'Secondaire') {
        if (row.coefficients.text.trim().isEmpty) {
          setState(() => _error = 'Les coefficients sont obligatoires pour ce niveau.');
          return;
        }
        if (niveauName == 'Secondaire' && (row.jours == null || row.heure.text.trim().isEmpty)) {
          setState(() => _error = 'Jours et heure sont obligatoires pour le niveau Secondaire.');
          return;
        }
      }

      items.add({
        if (row.id != null) 'id': row.id,
        'cours_id': row.coursId,
        'professeur_id': row.professeurId,
        'class': row.classeId,
        'niveau_id': row.niveauId,
        'annee_academique': row.anneeId,
        'faculte_id': row.faculteId,
        'jours': row.jours,
        'heure': row.heure.text.trim().isEmpty ? null : row.heure.text.trim(),
        'session': row.session,
        'coefficients': row.coefficients.text.trim().isEmpty ? null : double.tryParse(row.coefficients.text.trim()),
        'note_de_passage': row.noteDePassage.text.trim().isEmpty ? null : double.tryParse(row.noteDePassage.text.trim()),
      });
    }

    setState(() => _error = null);
    final error = await context.read<ProgrammeState>().save(items);
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final progState = context.watch<ProgrammeState>();
    final refData = context.watch<ReferenceDataState>();
    final niveaux = refData.niveaux;

    return Scaffold(
      backgroundColor: AppColors.appBg,
      appBar: AppBar(
        backgroundColor: AppColors.appBg,
        elevation: 0,
        title: Text(_isEdit ? 'Modifier le programme' : 'Ajouter au programme'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Vous pouvez ajouter plusieurs lignes pour enregistrer plusieurs entrées de programme à la fois.',
              style: TextStyle(fontSize: 12.5, color: AppColors.textMuted),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: AppColors.sidebarBg,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      for (final row in _rows) ...[
                        _buildRow(row, niveaux, progState, refData),
                        Divider(height: 24, color: AppColors.borderSubtle),
                      ],
                      TextButton.icon(
                        onPressed: _addRow,
                        icon: const Icon(Icons.add, size: 16),
                        label: const Text('Ajouter une ligne'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12.5)),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${_rows.length} entrée${_rows.length > 1 ? 's' : ''}',
                    style: TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
                FilledButton(
                  onPressed: progState.isSubmitting ? null : () => _submit(niveaux),
                  child: progState.isSubmitting
                      ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : Text(_isEdit ? 'Modifier' : 'Enregistrer tout'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Disposition en grille de 4 colonnes, comme le formulaire web
  /// (AddProgramme.vue:150, `grid-cols-4`) — tous les champs s'enchaînent
  /// dans le même ordre que là-bas : Niveau, Cours, Professeur,
  /// Coefficients (toujours visible, pas conditionnel), puis Faculté
  /// (Universitaire/Technique), Session et Note de passage (Universitaire
  /// uniquement), puis Classe, Année académique, Jours, Heure.
  Widget _buildRow(_ProgRow row, List<Niveau> niveaux, ProgrammeState progState, ReferenceDataState refData) {
    final niveauName = niveaux.firstWhere((n) => n.id == row.niveauId, orElse: () => Niveau(id: '', name: '')).name;
    final isUniOuTech = row.niveauId != null && _isUniOuTech(niveauName);
    final isUniversitaire = row.niveauId != null && niveauName == 'Universitaire';
    final classes = refData.classesForNiveau(row.niveauId);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Align(
          alignment: Alignment.topRight,
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            IconButton(
              tooltip: 'Supprimer cette ligne',
              icon: Icon(Icons.close, size: 18, color: AppColors.textMuted),
              onPressed: _rows.length > 1 ? () => _removeRow(row) : null,
            ),
            if (row.id != null)
              IconButton(
                tooltip: 'Supprimer de la base',
                icon: const Icon(Icons.delete_forever_outlined, size: 18, color: AppColors.danger),
                onPressed: () => _deleteFromDb(row),
              ),
          ]),
        ),
        _FieldGrid(fields: [
          DropdownButtonFormField<String>(
            initialValue: row.niveauId,
            decoration: const InputDecoration(labelText: 'Niveau'),
            items: niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
            onChanged: (v) => setState(() {
              row.niveauId = v;
              row.classeId = null;
            }),
          ),
          progState.isLoadingCombos
              ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
              : DropdownButtonFormField<String>(
                  initialValue: progState.cours.any((c) => c.id == row.coursId) ? row.coursId : null,
                  decoration: const InputDecoration(labelText: 'Cours'),
                  items: progState.cours.map((c) => DropdownMenuItem(value: c.id, child: Text(c.coursNom))).toList(),
                  onChanged: (v) => setState(() => row.coursId = v),
                ),
          progState.isLoadingCombos
              ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
              : DropdownButtonFormField<String>(
                  initialValue: progState.professeurs.any((p) => p.id == row.professeurId) ? row.professeurId : null,
                  decoration: const InputDecoration(labelText: 'Professeur'),
                  items: progState.professeurs.map((p) => DropdownMenuItem(value: p.id, child: Text(p.fullName))).toList(),
                  onChanged: (v) => setState(() => row.professeurId = v),
                ),
          TextField(controller: row.coefficients, decoration: const InputDecoration(labelText: 'Coefficients')),
          if (isUniOuTech)
            DropdownButtonFormField<String>(
              initialValue: refData.facultes.any((f) => f.id == row.faculteId) ? row.faculteId : null,
              decoration: const InputDecoration(labelText: 'Faculté / Option'),
              items: refData.facultes.map((f) => DropdownMenuItem(value: f.id, child: Text(f.nom))).toList(),
              onChanged: (v) => setState(() => row.faculteId = v),
            ),
          if (isUniversitaire)
            DropdownButtonFormField<String>(
              initialValue: _sessionOptions.contains(row.session) ? row.session : null,
              decoration: const InputDecoration(labelText: 'Session'),
              items: _sessionOptions.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (v) => setState(() => row.session = v),
            ),
          if (isUniversitaire)
            TextField(controller: row.noteDePassage, decoration: const InputDecoration(labelText: 'Note de passage')),
          DropdownButtonFormField<String>(
            initialValue: classes.any((c) => c.id == row.classeId) ? row.classeId : null,
            decoration: const InputDecoration(labelText: 'Classe'),
            items: classes.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))).toList(),
            onChanged: (v) => setState(() => row.classeId = v),
          ),
          DropdownButtonFormField<String>(
            initialValue: row.anneeId,
            decoration: const InputDecoration(labelText: 'Année académique'),
            items: refData.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
            onChanged: (v) => setState(() => row.anneeId = v),
          ),
          DropdownButtonFormField<String>(
            initialValue: row.jours,
            decoration: const InputDecoration(labelText: 'Jours'),
            items: _joursOptions.map((j) => DropdownMenuItem(value: j, child: Text(j))).toList(),
            onChanged: (v) => setState(() => row.jours = v),
          ),
          TextField(controller: row.heure, decoration: const InputDecoration(labelText: 'Heure')),
        ]),
      ],
    );
  }
}

/// Grille responsive à 4 colonnes (web : `grid-cols-4`) — chaque champ
/// occupe un quart de la largeur disponible, et s'enchaîne naturellement à
/// la ligne suivante (les champs conditionnels en moins ne laissent donc
/// jamais de trou).
class _FieldGrid extends StatelessWidget {
  const _FieldGrid({required this.fields});

  final List<Widget> fields;

  static const _columns = 4;
  static const _spacing = 12.0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final itemWidth = (constraints.maxWidth - _spacing * (_columns - 1)) / _columns;
        return Wrap(
          spacing: _spacing,
          runSpacing: 12,
          children: fields.map((f) => SizedBox(width: itemWidth, child: f)).toList(),
        );
      },
    );
  }
}
