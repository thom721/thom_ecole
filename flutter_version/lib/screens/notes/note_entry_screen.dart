import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/note.dart';
import '../../models/programme.dart' show CoursCombo;
import '../../models/student.dart' show Niveau;
import '../../state/note_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/searchable_dropdown_field.dart';

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
  // Incrémenté à chaque rechargement authentique des notes affichées (choix
  // de cours ou d'évaluation, fin d'un fetchExisting). Inclus dans la Key
  // des TextFormField de la colonne Note : sans lui, deux mises à jour
  // successives de s.note sous la même évaluation (ex: le setState optimiste
  // puis celui qui applique fetchExisting) partagent la même Key → Flutter
  // réutilise l'Element existant et n'relit jamais le nouvel initialValue,
  // laissant afficher les notes d'une évaluation précédente.
  int _dataRevision = 0;

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
      // Les notes/évaluation affichées appartiennent au cours précédent —
      // on repart de zéro pour éviter d'associer par erreur une note saisie
      // pour un autre cours. Remettre _evaluationMonth/_evaluationControle
      // à null change aussi la Key des TextFormField de la colonne Note
      // (ci-dessous), ce qui force leur remount avec le initialValue vidé.
      _evaluationMonth = null;
      _evaluationControle = null;
      _dataRevision++;
      for (final s in _result!.students) {
        s.note = null;
      }
    });
  }

  Future<void> _onEvaluationChange(String? month) async {
    setState(() {
      _evaluationMonth = month;
      _dataRevision++;
      // Vider immédiatement : tant que fetchExisting n'a pas répondu, le
      // champ ne doit jamais laisser croire qu'une note de l'évaluation
      // précédente appartient à celle qu'on vient de choisir.
      for (final s in _result!.students) {
        s.note = null;
      }
    });
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
      _dataRevision++;
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
        _dataRevision++;
        for (final s in _result!.students) {
          s.note = null;
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
        child: _step == 1
            ? _buildStep1(niveaux, refData, noteState, isUniOuTech, isUniversitaire)
            : _buildStep2(noteState, isUniOuTech),
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
            color: AppColors.cardBg,
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
                        : SearchableDropdownField<CoursCombo>(
                            key: ValueKey('cours-matiere-${noteState.coursCombo.length}'),
                            options: noteState.coursCombo,
                            idOf: (c) => c.id,
                            displayStringForOption: (c) => c.coursNom,
                            selectedId: _coursId,
                            labelText: 'Cours / Matière',
                            onSelected: (c) => setState(() => _coursId = c.id),
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

  Widget _buildStep2(NoteState noteState, bool isUniOuTech) {
    final result = _result!;
    final isUniversitaire = result.session != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
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
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Wrap(spacing: 6, runSpacing: 6, children: [
                      Chip(label: Text('Coeff. ${_currentCoefficients ?? '—'}')),
                      // Note de passage : uniquement pertinente pour Technique/
                      // Universitaire (barème différent du Fondamental).
                      if (isUniOuTech) Chip(label: Text('Passage ${_currentNoteDePassage ?? '—'}')),
                      Chip(label: Text(_currentTypeMatiere)),
                      Chip(label: Text('${result.students.length} étudiant${result.students.length > 1 ? 's' : ''}')),
                    ]),
                  ),
                  const SizedBox(width: 12),
                  SizedBox(
                    width: 200,
                    child: SearchableDropdownField<NoteListCoursItem>(
                      options: result.listCours,
                      idOf: (c) => c.id,
                      displayStringForOption: (c) => c.coursNom,
                      selectedId: _currentCoursId,
                      labelText: 'Changer de matière',
                      isDense: true,
                      onSelected: (c) => _onCoursChange(c.id),
                    ),
                  ),
                  const SizedBox(width: 12),
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
                            // DropdownButtonFormField ne relit initialValue qu'à sa
                            // création : sans cette Key liée à _currentCoursId, la
                            // remise à null de _evaluationMonth dans _onCoursChange
                            // ne se reflète pas visuellement au changement de cours.
                            key: ValueKey('evaluation-mois-$_currentCoursId'),
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
              color: AppColors.cardBg,
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
                          key: ValueKey('${s.id}_${_evaluationMonth}_${_evaluationControle}_$_dataRevision'),
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
