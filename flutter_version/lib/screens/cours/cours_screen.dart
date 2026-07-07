import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/print_gate.dart';
import '../../core/print_permission.dart';
import '../../models/cours.dart';
import '../../models/programme.dart';
import '../../state/cours_state.dart';
import '../../state/programme_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';
import 'cours_form_screen.dart';
import 'programme_form_screen.dart';

/// Équivalent de cours_page()/go_to_cours_page() ET programme_index()
/// (school_client, Controllers/Main.py: 9625-10227 pour Cours,
/// 9714-10227/10116 pour Programme) — un même onglet "Cours" sur bureau
/// regroupe les deux sections (Matières et Programme), structure reprise
/// ici avec un sélecteur d'onglet (motif de profile_screen.dart). Voir
/// CoursState/ProgrammeState pour le contrat API exact.
class CoursScreen extends StatefulWidget {
  const CoursScreen({super.key});

  @override
  State<CoursScreen> createState() => _CoursScreenState();
}

enum _Tab { cours, programmes }

class _CoursScreenState extends State<CoursScreen> {
  _Tab _tab = _Tab.cours;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReferenceDataState>().loadOnce();
      context.read<CoursState>().load();
    });
  }

  void _select(_Tab tab) {
    setState(() => _tab = tab);
    if (tab == _Tab.programmes) {
      context.read<ProgrammeState>().load();
      context.read<ProgrammeState>().loadCombos();
    }
  }

  Future<void> _openImprimerHoraire() async {
    if (!canPrintNonReceipt(context)) return;
    if (!canPrintPermission(context, 'Imprimer rapport pedagogique')) return;
    await context.read<ProgrammeState>().loadCombos();
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => const _ImprimerHoraireDialog(),
    );
  }

  Future<void> _openChargeEnseignement() async {
    if (!canPrintNonReceipt(context)) return;
    if (!canPrintPermission(context, 'Imprimer rapport pedagogique')) return;
    await context.read<ProgrammeState>().loadCombos();
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => const _ChargeEnseignementDialog(),
    );
  }

  Widget _buildSwitcher() {
    Widget pill(_Tab value, String label, IconData icon) {
      final selected = _tab == value;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: selected ? AppColors.hoverOverlay : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => _select(value),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(icon, size: 15, color: selected ? AppColors.accentLight : AppColors.textMuted),
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: selected ? AppColors.textPrimary : AppColors.textMuted,
                    ),
                  ),
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
          pill(_Tab.cours, 'Matières', Icons.menu_book_outlined),
          pill(_Tab.programmes, 'Programme', Icons.calendar_view_week_outlined),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Cours',
            subtitle: 'Gestion des matières et du programme par niveau',
            icon: Icons.menu_book_outlined,
            colorKey: 'sky',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildSwitcher(),
              const Spacer(),
              PillButton(
                label: 'Imprimer horaire',
                colorKey: 'sky',
                icon: Icons.print_outlined,
                onPressed: _openImprimerHoraire,
              ),
              const SizedBox(width: 10),
              PillButton(
                label: "Charge d'enseignement",
                colorKey: 'blue',
                icon: Icons.summarize_outlined,
                onPressed: _openChargeEnseignement,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: switch (_tab) {
              _Tab.cours => const _CoursTabView(),
              _Tab.programmes => const _ProgrammeTabView(),
            },
          ),
        ],
      ),
    );
  }
}

class _CoursTabView extends StatefulWidget {
  const _CoursTabView();

  @override
  State<_CoursTabView> createState() => _CoursTabViewState();
}

class _CoursTabViewState extends State<_CoursTabView> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openForm({Cours? cours}) async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => CoursFormScreen(initial: cours)),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(cours == null ? 'Cours ajouté.' : 'Cours modifié.')),
      );
    }
  }

  Future<void> _confirmDelete(Cours cours) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le cours "${cours.coursNom}" ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<CoursState>().delete(cours.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<CoursState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Ajouter un cours',
              colorKey: 'sky',
              icon: Icons.add,
              onPressed: () => _openForm(),
            ),
            const Spacer(),
            SizedBox(
              width: 280,
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 18),
                  hintText: 'Rechercher un cours...',
                  isDense: true,
                ),
                onSubmitted: (v) => context.read<CoursState>().load(page: 1, search: v),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (state.isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (state.errorMessage != null)
          Expanded(child: Center(child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary))))
        else
          Expanded(
            child: SingleChildScrollView(
              child: DataTableCard(
                currentPage: state.currentPage,
                lastPage: state.lastPage,
                onPageChange: (page) => context.read<CoursState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('#')),
                    DataColumn(label: Text('NOM DU COURS')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.asMap().entries.map((entry) {
                    final i = entry.key;
                    final c = entry.value;
                    final isDeleting = state.deletingId == c.id;
                    return DataRow(cells: [
                      DataCell(Text('${i + 1}')),
                      DataCell(Text(c.coursNom)),
                      DataCell(
                        isDeleting
                            ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                            : Row(children: [
                                IconButton(
                                  tooltip: 'Modifier',
                                  icon: Icon(Icons.edit_outlined, size: 17, color: AppColors.accentLight),
                                  onPressed: () => _openForm(cours: c),
                                ),
                                IconButton(
                                  tooltip: 'Supprimer',
                                  icon: const Icon(Icons.delete_outline, size: 17, color: AppColors.danger),
                                  onPressed: () => _confirmDelete(c),
                                ),
                              ]),
                      ),
                    ]);
                  }).toList(),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Équivalent de programme_index() et de la grille de filtres associée
/// (school_client, Controllers/Main.py:10116+) — filtres niveau/classe/
/// année + recherche, table Cours/Professeur/Niveau/Classe/Année, CRUD
/// complet (le web n'avait, avant correction, ni Modifier ni Supprimer sur
/// cette table — corrigé aussi côté ecole_nginx/frontend/Cours.vue).
class _ProgrammeTabView extends StatefulWidget {
  const _ProgrammeTabView();

  @override
  State<_ProgrammeTabView> createState() => _ProgrammeTabViewState();
}

class _ProgrammeTabViewState extends State<_ProgrammeTabView> {
  final _searchController = TextEditingController();
  String? _niveauFilter;
  String? _classeFilter;
  String? _anneeFilter;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openForm({Programme? programme}) async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => ProgrammeFormScreen(initial: programme)),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(programme == null ? 'Programme ajouté.' : 'Programme modifié.')),
      );
    }
  }

  Future<void> _confirmDelete(Programme programme) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le programme "${programme.coursNom ?? ''}" ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<ProgrammeState>().delete(programme.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ProgrammeState>();
    final refData = context.watch<ReferenceDataState>();
    final niveaux = refData.niveaux;
    final annees = refData.annees;
    final classesForFilter = refData.classesForNiveau(_niveauFilter);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Ajouter au programme',
              colorKey: 'sky',
              icon: Icons.add,
              onPressed: () => _openForm(),
            ),
            const Spacer(),
            SizedBox(
              width: 240,
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 18),
                  hintText: 'Rechercher...',
                  isDense: true,
                ),
                onSubmitted: (v) => context.read<ProgrammeState>().load(page: 1, search: v),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _niveauFilter,
                decoration: const InputDecoration(labelText: 'Niveau', isDense: true),
                items: [
                  const DropdownMenuItem(value: null, child: Text('Tous les niveaux')),
                  ...niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))),
                ],
                onChanged: (v) {
                  setState(() {
                    _niveauFilter = v;
                    _classeFilter = null;
                  });
                  context.read<ProgrammeState>().load(page: 1, niveauId: v ?? '', classeId: '');
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _classeFilter,
                decoration: const InputDecoration(labelText: 'Classe', isDense: true),
                items: [
                  const DropdownMenuItem(value: null, child: Text('Toutes les classes')),
                  ...classesForFilter.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))),
                ],
                onChanged: (v) {
                  setState(() => _classeFilter = v);
                  context.read<ProgrammeState>().load(page: 1, classeId: v ?? '');
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _anneeFilter,
                decoration: const InputDecoration(labelText: 'Année académique', isDense: true),
                items: [
                  const DropdownMenuItem(value: null, child: Text('Toutes les années')),
                  ...annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))),
                ],
                onChanged: (v) {
                  setState(() => _anneeFilter = v);
                  context.read<ProgrammeState>().load(page: 1, anneeId: v ?? '');
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (state.isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (state.errorMessage != null)
          Expanded(child: Center(child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary))))
        else
          Expanded(
            child: SingleChildScrollView(
              child: DataTableCard(
                currentPage: state.currentPage,
                lastPage: state.lastPage,
                onPageChange: (page) => context.read<ProgrammeState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('COURS')),
                    DataColumn(label: Text('PROFESSEUR')),
                    DataColumn(label: Text('NIVEAU')),
                    DataColumn(label: Text('CLASSE')),
                    DataColumn(label: Text('ANNÉE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((p) {
                    final isDeleting = state.deletingId == p.id;
                    return DataRow(cells: [
                      DataCell(Text(p.coursNom ?? '—')),
                      DataCell(Text(p.professeurNom ?? '—')),
                      DataCell(Text(p.niveauName ?? '—')),
                      DataCell(Text(p.classeNom ?? '—')),
                      DataCell(Text(p.anneeAcademiqueNom ?? '—')),
                      DataCell(
                        isDeleting
                            ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                            : Row(children: [
                                IconButton(
                                  tooltip: 'Modifier',
                                  icon: Icon(Icons.edit_outlined, size: 17, color: AppColors.accentLight),
                                  onPressed: () => _openForm(programme: p),
                                ),
                                IconButton(
                                  tooltip: 'Supprimer',
                                  icon: const Icon(Icons.delete_outline, size: 17, color: AppColors.danger),
                                  onPressed: () => _confirmDelete(p),
                                ),
                              ]),
                      ),
                    ]);
                  }).toList(),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Modal "Imprimer horaire" — reconstruit fidèlement au modal du web
/// (Cours.vue), dont l'endpoint /print-horaire n'existait pas côté backend
/// (bouton mort). Mêmes champs : niveau → faculté (si niveau universitaire)
/// → classe + année académique.
class _ImprimerHoraireDialog extends StatefulWidget {
  const _ImprimerHoraireDialog();

  @override
  State<_ImprimerHoraireDialog> createState() => _ImprimerHoraireDialogState();
}

class _ImprimerHoraireDialogState extends State<_ImprimerHoraireDialog> {
  String? _niveauId;
  String? _faculteId;
  String? _classeId;
  String? _anneeId;
  String? _error;

  Future<void> _submit() async {
    if (_niveauId == null || _classeId == null || _anneeId == null) {
      setState(() => _error = 'Niveau, classe et année académique sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ProgrammeState>().printHoraire(
          niveauId: _niveauId!,
          classeId: _classeId!,
          anneeAcademiqueId: _anneeId!,
          faculteId: _faculteId,
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
    final refData = context.watch<ReferenceDataState>();
    final progState = context.watch<ProgrammeState>();
    final isUniversitaire = refData.niveaux
            .where((n) => n.id == _niveauId)
            .map((n) => n.name)
            .firstOrNull ==
        'Universitaire';
    final classes = refData.classesForNiveau(_niveauId);

    return ParamDialogShell(
      title: "Imprimer l'horaire",
      width: 560,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            isExpanded: true,
            decoration: const InputDecoration(labelText: "Niveau d'étude"),
            items: refData.niveaux
                .map((n) => DropdownMenuItem(value: n.id, child: Text(n.name)))
                .toList(),
            onChanged: (v) => setState(() {
              _niveauId = v;
              _classeId = null;
              _faculteId = null;
            }),
          ),
          if (isUniversitaire) ...[
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _faculteId,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Faculté / Option'),
              items: refData.facultes
                  .map((f) => DropdownMenuItem(value: f.id, child: Text(f.nom)))
                  .toList(),
              onChanged: (v) => setState(() => _faculteId = v),
            ),
          ],
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _classeId,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Classe'),
                  items: classes
                      .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                      .toList(),
                  onChanged: _niveauId == null ? null : (v) => setState(() => _classeId = v),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _anneeId,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Année académique'),
                  items: refData.annees
                      .map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom)))
                      .toList(),
                  onChanged: (v) => setState(() => _anneeId = v),
                ),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          Padding(
            padding: const EdgeInsets.only(top: 18),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: TextButton.styleFrom(foregroundColor: AppColors.danger),
                  child: const Text('Fermer'),
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  onPressed: progState.isPrintingHoraire ? null : _submit,
                  icon: progState.isPrintingHoraire
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.print_outlined, size: 16),
                  label: const Text('Imprimer'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Modal "Charge d'enseignement" — nouveau bouton (demande explicite) :
/// professeur + année académique → PDF listant ses cours/classes assignés
/// (Programme). Pas une durée en heures — voir RHoraireReport.py.
class _ChargeEnseignementDialog extends StatefulWidget {
  const _ChargeEnseignementDialog();

  @override
  State<_ChargeEnseignementDialog> createState() => _ChargeEnseignementDialogState();
}

class _ChargeEnseignementDialogState extends State<_ChargeEnseignementDialog> {
  String? _professeurId;
  String? _anneeId;
  String? _error;

  Future<void> _submit() async {
    if (_professeurId == null || _anneeId == null) {
      setState(() => _error = 'Professeur et année académique sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ProgrammeState>().printChargeEnseignement(
          professeurId: _professeurId!,
          anneeAcademiqueId: _anneeId!,
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
    final refData = context.watch<ReferenceDataState>();
    final progState = context.watch<ProgrammeState>();

    return ParamDialogShell(
      title: "Charge d'enseignement",
      width: 520,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _professeurId,
            isExpanded: true,
            decoration: const InputDecoration(labelText: 'Professeur'),
            items: progState.professeurs
                .map((p) => DropdownMenuItem(value: p.id, child: Text('${p.prenom} ${p.nom}')))
                .toList(),
            onChanged: (v) => setState(() => _professeurId = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _anneeId,
            isExpanded: true,
            decoration: const InputDecoration(labelText: 'Année académique'),
            items: refData.annees
                .map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom)))
                .toList(),
            onChanged: (v) => setState(() => _anneeId = v),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          Padding(
            padding: const EdgeInsets.only(top: 18),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: TextButton.styleFrom(foregroundColor: AppColors.danger),
                  child: const Text('Fermer'),
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  onPressed: progState.isPrintingCharge ? null : _submit,
                  icon: progState.isPrintingCharge
                      ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.print_outlined, size: 16),
                  label: const Text('Imprimer'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

