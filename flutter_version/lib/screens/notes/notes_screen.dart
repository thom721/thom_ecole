import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/note.dart';
import '../../state/note_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';
import 'note_entry_screen.dart';

/// Équivalent de notes_page() (school_client, Controllers/Main.py:10296+) —
/// liste paginée des coursEtudiant + entrée "Ajouter / Modifier notes"
/// (show_dialog_for_notes → show_data_after_search_for_insert_notes →
/// enregistrer_notes) + impression de bulletin (par étudiant et par classe).
///
/// Volontairement omis (fonctionnalités mortes côté bureau, voir
/// note_state.dart) : la saisie par Contrôle/Trimestre, "Voir notes"
/// (action_on_notes → voir_notes, appelle une route avec la mauvaise
/// méthode HTTP et sans les champs nécessaires), et Modifier/Supprimer
/// depuis la liste (boutons jamais connectés sur le bureau).
class NotesScreen extends StatefulWidget {
  const NotesScreen({super.key});

  @override
  State<NotesScreen> createState() => _NotesScreenState();
}

class _NotesScreenState extends State<NotesScreen> {
  final _searchController = TextEditingController();
  final Map<String, String?> _periodeSelection = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReferenceDataState>().loadOnce();
      context.read<NoteState>().load();
      context.read<NoteState>().loadCoursCombo();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openEntryDialog() async {
    final saved = await Navigator.of(
      context,
    ).push<bool>(MaterialPageRoute(builder: (_) => const NoteEntryScreen()));
    if (saved == true && mounted) {
      context.read<NoteState>().load(page: 1);
    }
  }

  Future<void> _printRow(CoursEtudiantRecord row) async {
    final selection = _periodeSelection[row.id];
    if (selection == null) return;
    final isUniversitaire = row.niveauName == 'Universitaire';
    final error = await context.read<NoteState>().printBulletin(
      row.id,
      mois: isUniversitaire ? null : selection,
      session: isUniversitaire ? selection : null,
    );
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  List<DropdownMenuItem<String>> _periodeOptions(CoursEtudiantRecord row) {
    if (row.niveauName == 'Universitaire') {
      return const [
        DropdownMenuItem(value: '1ère session', child: Text('1ère session')),
        DropdownMenuItem(value: '2ème session', child: Text('2ème session')),
      ];
    }
    return [
      const DropdownMenuItem(value: 'all', child: Text('Annuel')),
      ...NoteState.moisAnneeScolaire.map(
        (m) => DropdownMenuItem(value: m, child: Text(m)),
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<NoteState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Notes & Évaluations',
            subtitle: 'Saisie et gestion des résultats académiques',
            icon: Icons.edit_note_outlined,
            colorKey: 'emerald',
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              PillButton(
                label: 'Ajouter / Modifier notes',
                colorKey: 'emerald',
                icon: Icons.edit_outlined,
                onPressed: _openEntryDialog,
              ),
              const SizedBox(width: 8),
              PillButton(
                label: 'Bulletin',
                colorKey: 'sky',
                icon: Icons.menu_book_outlined,
                onPressed: () => showDialog(
                  context: context,
                  builder: (_) => const _MassBulletinDialog(),
                ),
              ),
              const Spacer(),
              SizedBox(
                width: 260,
                child: TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search, size: 18),
                    hintText: 'Rechercher un étudiant...',
                    isDense: true,
                  ),
                  onSubmitted: (v) =>
                      context.read<NoteState>().load(page: 1, search: v),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.errorMessage != null)
            Expanded(
              child: Center(
                child: Text(
                  state.errorMessage!,
                  style: TextStyle(color: AppColors.textPrimary),
                ),
              ),
            )
          else
            Expanded(
              child: SingleChildScrollView(
                child: DataTableCard(
                  currentPage: state.currentPage,
                  lastPage: state.lastPage,
                  onPageChange: (page) =>
                      context.read<NoteState>().load(page: page),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('IDENTIFIANT')),
                      DataColumn(label: Text('NOM')),
                      DataColumn(label: Text('PRÉNOM')),
                      DataColumn(label: Text('CLASSE')),
                      DataColumn(label: Text('CYCLE')),
                      DataColumn(label: Text('ANNÉE')),
                      DataColumn(label: Text('PÉRIODE')),
                      DataColumn(label: Text('')),
                    ],
                    rows: state.items.map((r) {
                      final isPrinting = state.printingId == r.id;
                      return DataRow(
                        cells: [
                          DataCell(Text(r.identifiant)),
                          DataCell(Text(r.fname)),
                          DataCell(Text(r.lname)),
                          DataCell(Text(r.nomClasse ?? '—')),
                          DataCell(Text(r.niveauName ?? '—')),
                          DataCell(Text(r.anneeAcademique)),
                          DataCell(
                            SizedBox(
                              width: 150,
                              child: DropdownButtonFormField<String>(
                                initialValue: _periodeSelection[r.id],
                                decoration: const InputDecoration(
                                  isDense: true,
                                  hintText: 'Période',
                                ),
                                items: _periodeOptions(r),
                                onChanged: (v) =>
                                    setState(() => _periodeSelection[r.id] = v),
                              ),
                            ),
                          ),
                          DataCell(
                            isPrinting
                                ? const SizedBox(
                                    height: 14,
                                    width: 14,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : IconButton(
                                    tooltip: 'Imprimer le bulletin',
                                    icon: Icon(
                                      Icons.picture_as_pdf_outlined,
                                      size: 17,
                                      color: AppColors.accentLight,
                                    ),
                                    onPressed: _periodeSelection[r.id] == null
                                        ? null
                                        : () => _printRow(r),
                                  ),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _MassBulletinDialog extends StatefulWidget {
  const _MassBulletinDialog();

  @override
  State<_MassBulletinDialog> createState() => _MassBulletinDialogState();
}

class _MassBulletinDialogState extends State<_MassBulletinDialog> {
  String? _anneeNom;
  String? _classeId;
  String? _mois;
  String? _error;

  Future<void> _submit() async {
    if (_anneeNom == null || _mois == null || _classeId == null) {
      setState(() => _error = 'Année, mois et classe sont requis.');
      return;
    }
    final error = await context.read<NoteState>().printMassBulletin(
      anneeAcademiqueNom: _anneeNom!,
      classeId: _classeId!,
      mois: _mois!,
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<NoteState>();
    final refData = context.watch<ReferenceDataState>();

    return ParamDialogShell(
      title: 'Bulletin de classe',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _anneeNom,
            decoration: const InputDecoration(labelText: 'Année académique'),
            items: refData.annees
                .map((a) => DropdownMenuItem(value: a.nom, child: Text(a.nom)))
                .toList(),
            onChanged: (v) => setState(() => _anneeNom = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _mois,
            decoration: const InputDecoration(labelText: 'Mois'),
            items: [
              const DropdownMenuItem(value: 'Annuel', child: Text('Annuel')),
              ...NoteState.moisAnneeScolaire.map(
                (m) => DropdownMenuItem(value: m, child: Text(m)),
              ),
            ],
            onChanged: (v) => setState(() => _mois = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _classeId,
            decoration: const InputDecoration(labelText: 'Classe'),
            items: refData.classes
                .map(
                  (c) =>
                      DropdownMenuItem(value: c.id, child: Text(c.nomClasse)),
                )
                .toList(),
            onChanged: (v) => setState(() => _classeId = v),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Annuler'),
              ),
              const SizedBox(width: 8),
              FilledButton(
                onPressed: state.isPrintingMass ? null : _submit,
                child: state.isPrintingMass
                    ? const SizedBox(
                        height: 16,
                        width: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Imprimer'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
