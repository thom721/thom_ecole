import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/note.dart';
import '../../models/student.dart' show Niveau;
import '../../state/note_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';

const _sessionOptions = ['1ère', '2ème'];

/// Équivalent du flux en 2 étapes show_dialog_for_notes() →
/// show_data_after_search_for_insert_notes() (school_client,
/// Controllers/Main.py:10456-10827) : recherche des étudiants par
/// niveau/cours/classe/année (+ faculté/session pour Universitaire/
/// Technique), puis grille de saisie des notes. Reproduit ici comme une
/// page dédiée (pas une modale) : sur le web, `NoteForm.vue` est une vraie
/// page routée (`/admin/ajouter-notes`) qui passe de
/// `InsertNotesComponents` à la grille via `v-if="!isdata"`, exactement le
/// même principe qu'on a déjà appliqué à Cours/Programme
/// (CoursFormScreen/ProgrammeFormScreen).
class NoteEntryScreen extends StatefulWidget {
  const NoteEntryScreen({super.key});

  @override
  State<NoteEntryScreen> createState() => _NoteEntryScreenState();
}

class _NoteEntryScreenState extends State<NoteEntryScreen> {
  int _step = 1;
  String? _error;

  // Étape 1
  String? _niveauId;
  String? _coursId;
  String? _classeId;
  String? _anneeId;
  String? _faculteId;
  String? _session;

  // Étape 2
  NoteSearchResult? _result;
  String? _currentCoursId;
  String _currentCoursNom = '';
  String _currentTypeMatiere = '';
  double? _currentCoefficients;
  double? _currentNoteDePassage;
  String _currentProfesseurId = '';
  String? _evaluationMonth;
  String? _evaluationControle;

  Future<void> _submitSearch(List<Niveau> niveaux) async {
    if (_niveauId == null || _coursId == null || _classeId == null || _anneeId == null) {
      setState(() => _error = 'Niveau, cours, classe et année académique sont requis.');
      return;
    }
    final name = niveaux.firstWhere((n) => n.id == _niveauId, orElse: () => Niveau(id: '', name: '')).name;
    final isUniOuTech = name == 'Universitaire' || name == 'Technique';
    if (isUniOuTech && _faculteId == null) {
      setState(() => _error = 'La faculté / option est requise pour ce niveau.');
      return;
    }
    if (name == 'Universitaire' && (_session == null || _session!.isEmpty)) {
      setState(() => _error = 'La session est requise pour le niveau Universitaire.');
      return;
    }

    setState(() => _error = null);
    final (result: result, error: error) = await context.read<NoteState>().search(
          niveauId: _niveauId!,
          coursId: _coursId!,
          classeId: _classeId!,
          anneeAcademiqueId: _anneeId!,
          faculteId: isUniOuTech ? _faculteId : null,
          session: name == 'Universitaire' ? _session : null,
        );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
      return;
    }
    setState(() {
      _result = result;
      _currentCoursId = _coursId;
      _currentCoursNom = result!.cours.coursNom;
      _currentTypeMatiere = result.cours.typeMatiere ?? '';
      _currentCoefficients = result.cours.coefficients;
      _currentNoteDePassage = result.cours.noteDePassage;
      _currentProfesseurId = result.cours.professeurId ?? '';
      _step = 2;
    });
  }

  Future<void> _onCoursChange(String? coursId) async {
    final item = _result!.listCours.firstWhere((c) => c.id == coursId, orElse: () => _result!.listCours.first);
    setState(() {
      _currentCoursId = item.id;
      _currentCoursNom = item.coursNom;
      _currentTypeMatiere = item.typeMatiere ?? '';
      _currentCoefficients = item.coefficients;
      _currentNoteDePassage = item.noteDePassage;
      _currentProfesseurId = item.professeurId ?? '';
      for (final s in _result!.students) {
        s.note = null;
      }
    });
  }

  Future<void> _onEvaluationChange(String? month) async {
    setState(() => _evaluationMonth = month);
    if (month == null) return;
    final existing = await context.read<NoteState>().fetchExisting(
          coursNom: _currentCoursNom,
          examen: month,
          anneeAcademique: _result!.annee,
          typeMatiere: _currentTypeMatiere,
          students: _result!.students,
        );
    if (!mounted) return;
    setState(() {
      for (final s in _result!.students) {
        s.note = existing[s.id];
      }
    });
  }

  Future<void> _submitNotes({required bool exit}) async {
    final isUniversitaire = _result!.session != null;
    if (!isUniversitaire && (_evaluationMonth == null || _evaluationMonth!.isEmpty)) {
      setState(() => _error = "Vous devez choisir dans le champ Évaluation.");
      return;
    }
    if (isUniversitaire && (_evaluationControle == null || _evaluationControle!.isEmpty)) {
      setState(() => _error = 'Vous devez choisir entre Intra ou Finale.');
      return;
    }

    final error = await context.read<NoteState>().save(
          controle: isUniversitaire ? _evaluationControle! : 'mois',
          examen: isUniversitaire ? '' : _evaluationMonth!,
          coursNom: _currentCoursNom,
          typeMatiere: _currentTypeMatiere,
          coefficients: _currentCoefficients,
          session: _result!.session,
          noteDePassage: _currentNoteDePassage,
          professeurId: _currentProfesseurId,
          anneeAcademique: _result!.annee,
          students: _result!.students,
        );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
      return;
    }
    if (exit) {
      Navigator.of(context).pop(true);
    } else {
      setState(() {
        _error = null;
        for (final s in _result!.students) {
          s.note = 0;
        }
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Notes enregistrées.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final refData = context.watch<ReferenceDataState>();
    final noteState = context.watch<NoteState>();
    final niveaux = refData.niveaux;
    final niveauName = niveaux.firstWhere((n) => n.id == _niveauId, orElse: () => Niveau(id: '', name: '')).name;
    final isUniOuTech = _niveauId != null && (niveauName == 'Universitaire' || niveauName == 'Technique');
    final isUniversitaire = _niveauId != null && niveauName == 'Universitaire';

    return Scaffold(
      backgroundColor: AppColors.appBg,
      appBar: AppBar(
        backgroundColor: AppColors.appBg,
        elevation: 0,
        title: const Text('Ajouter / Modifier notes'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: _step == 1 ? _buildStep1(niveaux, refData, noteState, isUniOuTech, isUniversitaire) : _buildStep2(noteState),
      ),
    );
  }

  Widget _buildStep1(
    List<Niveau> niveaux,
    ReferenceDataState refData,
    NoteState noteState,
    bool isUniOuTech,
    bool isUniversitaire,
  ) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 680),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppColors.sidebarBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Rechercher des étudiants',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                const SizedBox(height: 20),
                Row(children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _niveauId,
                      decoration: const InputDecoration(labelText: 'Niveau / Section'),
                      items: niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
                      onChanged: (v) => setState(() {
                        _niveauId = v;
                        _classeId = null;
                        _faculteId = null;
                        _session = null;
                      }),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: noteState.isLoadingCombo
                        ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
                        : DropdownButtonFormField<String>(
                            initialValue: noteState.coursCombo.any((c) => c.id == _coursId) ? _coursId : null,
                            decoration: const InputDecoration(labelText: 'Cours / Matière'),
                            items: noteState.coursCombo
                                .map((c) => DropdownMenuItem(value: c.id, child: Text(c.coursNom)))
                                .toList(),
                            onChanged: (v) => setState(() => _coursId = v),
                          ),
                  ),
                ]),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _classeId,
                      decoration: const InputDecoration(labelText: 'Classe'),
                      items: refData
                          .classesForNiveau(_niveauId)
                          .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                          .toList(),
                      onChanged: (v) => setState(() => _classeId = v),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _anneeId,
                      decoration: const InputDecoration(labelText: 'Année académique'),
                      items: refData.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
                      onChanged: (v) => setState(() => _anneeId = v),
                    ),
                  ),
                ]),
                if (isUniOuTech) ...[
                  const SizedBox(height: 12),
                  Row(children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _faculteId,
                        decoration: const InputDecoration(labelText: 'Faculté / Option'),
                        items: refData.facultes.map((f) => DropdownMenuItem(value: f.id, child: Text(f.nom))).toList(),
                        onChanged: (v) => setState(() => _faculteId = v),
                      ),
                    ),
                    if (isUniversitaire) ...[
                      const SizedBox(width: 12),
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          initialValue: _session,
                          decoration: const InputDecoration(labelText: 'Session'),
                          items: _sessionOptions.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                          onChanged: (v) => setState(() => _session = v),
                        ),
                      ),
                    ],
                  ]),
                ],
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
                ],
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
                    const SizedBox(width: 8),
                    FilledButton(
                      onPressed: noteState.isSearching ? null : () => _submitSearch(niveaux),
                      child: noteState.isSearching
                          ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Text('Valider'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStep2(NoteState noteState) {
    final result = _result!;
    final isUniversitaire = result.session != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.sidebarBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          // Column plutôt qu'un Row title/contrôles côte à côte : sur une
          // fenêtre étroite, les deux SizedBox à largeur fixe (200+180)
          // n'avaient plus assez de place près du bloc titre/chips et
          // provoquaient un RenderFlex overflow.
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_currentCoursNom,
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.accentLight)),
              const SizedBox(height: 4),
              Text('${result.cours.nomClasse ?? ''} · ${result.annee}',
                  style: TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
              const SizedBox(height: 6),
              Wrap(spacing: 6, runSpacing: 6, children: [
                Chip(label: Text('Coeff. ${_currentCoefficients ?? '—'}')),
                Chip(label: Text('Passage ${_currentNoteDePassage ?? '—'}')),
                Chip(label: Text(_currentTypeMatiere)),
                Chip(label: Text('${result.students.length} étudiant${result.students.length > 1 ? 's' : ''}')),
              ]),
              const SizedBox(height: 14),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  SizedBox(
                    width: 200,
                    child: DropdownButtonFormField<String>(
                      initialValue: _currentCoursId,
                      decoration: const InputDecoration(labelText: 'Changer de matière', isDense: true),
                      items: result.listCours.map((c) => DropdownMenuItem(value: c.id, child: Text(c.coursNom))).toList(),
                      onChanged: _onCoursChange,
                    ),
                  ),
                  SizedBox(
                    width: 180,
                    child: isUniversitaire
                        ? Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text("Type d'évaluation", style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                              const SizedBox(height: 6),
                              SegmentedButton<String>(
                                segments: const [
                                  ButtonSegment(value: 'intra', label: Text('Intra')),
                                  ButtonSegment(value: 'finale', label: Text('Finale')),
                                ],
                                selected: {?_evaluationControle},
                                emptySelectionAllowed: true,
                                onSelectionChanged: (v) => setState(() => _evaluationControle = v.isEmpty ? null : v.first),
                              ),
                            ],
                          )
                        : DropdownButtonFormField<String>(
                            initialValue: _evaluationMonth,
                            decoration: const InputDecoration(labelText: 'Évaluation', isDense: true),
                            items: NoteState.moisAnneeScolaire.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                            onChanged: _onEvaluationChange,
                          ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        if (_error != null) Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
        const SizedBox(height: 8),
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              color: AppColors.sidebarBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(16),
            ),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(8),
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('#')),
                  DataColumn(label: Text('IDENTIFIANT')),
                  DataColumn(label: Text('NOM & PRÉNOM')),
                  DataColumn(label: Text('NOTE')),
                ],
                rows: result.students.asMap().entries.map((entry) {
                  final i = entry.key;
                  final s = entry.value;
                  return DataRow(cells: [
                    DataCell(Text('${i + 1}')),
                    DataCell(Text(s.identifiant)),
                    DataCell(Text('${s.nom} ${s.prenom}')),
                    DataCell(
                      SizedBox(
                        width: 80,
                        child: TextFormField(
                          key: ValueKey('${s.id}_${_evaluationMonth}_$_evaluationControle'),
                          initialValue: s.note?.toString() ?? '',
                          textAlign: TextAlign.center,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: const InputDecoration(isDense: true),
                          onChanged: (v) => s.note = double.tryParse(v),
                        ),
                      ),
                    ),
                  ]);
                }).toList(),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            TextButton(onPressed: () => setState(() => _step = 1), child: const Text('Retour')),
            Row(children: [
              OutlinedButton(
                onPressed: noteState.isSubmitting ? null : () => _submitNotes(exit: false),
                child: const Text('Enregistrer les notes'),
              ),
              const SizedBox(width: 8),
              FilledButton(
                onPressed: noteState.isSubmitting ? null : () => _submitNotes(exit: true),
                child: noteState.isSubmitting
                    ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Enregistrer et quitter'),
              ),
            ]),
          ],
        ),
      ],
    );
  }
}
