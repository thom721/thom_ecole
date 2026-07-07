import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/loan.dart';
import '../../models/parametre_payroll.dart';
import '../../models/payroll.dart';
import '../../state/parametre_payroll_state.dart';
import '../../state/payroll_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/searchable_dropdown_field.dart';

/// Versements de salaire aux Professeurs/Personnel — fonctionnalité ajoutée
/// sur demande explicite, sans référence bureau/web (voir
/// lib/state/payroll_state.dart). Deux modes : salaire fixe (montant saisi/
/// pré-rempli depuis Professeur.salaireFixe) ou horaire (montant dû calculé
/// à partir des heures saisies × taux configuré par cours/année dans
/// ParametrePayroll, "Gérer les taux horaires"). Les versements peuvent
/// être partiels — montant dû / versé / solde restant, mirror du module
/// Prêts (loan_tab.dart).
class PayrollTab extends StatefulWidget {
  const PayrollTab({super.key});

  @override
  State<PayrollTab> createState() => _PayrollTabState();
}

class _PayrollTabState extends State<PayrollTab> {
  Future<void> _openCreateForm() async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => const _PayrollFormDialog(),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Versement enregistré.')));
    }
  }

  void _openTauxDialog() {
    showDialog<void>(
      context: context,
      builder: (_) => const _ParametrePayrollDialog(),
    );
  }

  void _openBilanMensuel() {
    showDialog<void>(
      context: context,
      builder: (_) => const _BilanMensuelDialog(),
    );
  }

  Future<void> _openVerserForm(PayrollRecord payroll) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _VerserFormDialog(payroll: payroll),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Versement enregistré.')));
    }
  }

  Future<void> _confirmDelete(PayrollRecord payroll) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text(
          'Supprimer le versement de ${payroll.user} (${payroll.mois} ${payroll.annee}) ?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<PayrollState>().delete(payroll.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PayrollState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            PillButton(
              label: 'Verser un salaire',
              colorKey: 'cyan',
              icon: Icons.add,
              onPressed: _openCreateForm,
            ),
            const SizedBox(width: 10),
            PillButton(
              label: 'Gérer les taux horaires',
              colorKey: 'blue',
              icon: Icons.schedule,
              onPressed: _openTauxDialog,
            ),
            const SizedBox(width: 10),
            PillButton(
              label: 'Bilan mensuel',
              colorKey: 'violet',
              icon: Icons.fact_check_outlined,
              onPressed: _openBilanMensuel,
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
                    context.read<PayrollState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('EMPLOYÉ')),
                    DataColumn(label: Text('MONTANT DÛ')),
                    DataColumn(label: Text('VERSÉ')),
                    DataColumn(label: Text('SOLDE')),
                    DataColumn(label: Text('PÉRIODE')),
                    DataColumn(label: Text('MÉTHODE')),
                    DataColumn(label: Text('STATUT')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((p) {
                    final isDeleting = state.deletingId == p.id;
                    final montantDu = p.montantDu ?? p.montant;
                    final solde = p.remainingBalance ?? 0;
                    final verse = montantDu - solde;
                    final isPaye = p.statut == 'Payé';
                    return DataRow(
                      cells: [
                        DataCell(Text(p.user)),
                        DataCell(Text(montantDu.toStringAsFixed(2))),
                        DataCell(Text(verse.toStringAsFixed(2))),
                        DataCell(Text(solde.toStringAsFixed(2))),
                        DataCell(Text('${p.mois} ${p.annee}')),
                        DataCell(Text(p.methodePaiement)),
                        DataCell(_StatusBadge(statut: p.statut)),
                        DataCell(
                          isDeleting
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : Row(
                                  children: [
                                    if (!isPaye)
                                      TextButton(
                                        onPressed: () => _openVerserForm(p),
                                        child: const Text('Verser'),
                                      ),
                                    IconButton(
                                      tooltip: 'Supprimer',
                                      icon: const Icon(
                                        Icons.delete_outline,
                                        size: 17,
                                        color: AppColors.danger,
                                      ),
                                      onPressed: () => _confirmDelete(p),
                                    ),
                                  ],
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
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.statut});

  final String statut;

  @override
  Widget build(BuildContext context) {
    final color = switch (statut) {
      'Payé' => AppColors.cardPalette['emerald']!.text,
      'Partiel' => AppColors.cardPalette['amber']!.text,
      _ => AppColors.accent,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        statut,
        style: TextStyle(
          fontSize: 11.5,
          fontWeight: FontWeight.w500,
          color: color,
        ),
      ),
    );
  }
}

/// Dialog CRUD des taux horaires par cours/année (ParametrePayroll) —
/// liste + petit formulaire d'ajout, mirror du style liste+form des
/// onglets Paramètres (ex. examens_tab.dart).
class _ParametrePayrollDialog extends StatefulWidget {
  const _ParametrePayrollDialog();

  @override
  State<_ParametrePayrollDialog> createState() => _ParametrePayrollDialogState();
}

class _ParametrePayrollDialogState extends State<_ParametrePayrollDialog> {
  String? _coursId;
  String? _anneeId;
  final _tauxController = TextEditingController();
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ParametrePayrollState>().load();
      context.read<ParametrePayrollState>().loadAllCours();
      context.read<ReferenceDataState>().loadOnce();
    });
  }

  @override
  void dispose() {
    _tauxController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final taux = double.tryParse(_tauxController.text.trim());
    if (_coursId == null || _anneeId == null || taux == null || taux <= 0) {
      setState(() => _error = 'Cours, année académique et taux (> 0) sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametrePayrollState>().create(
          coursId: _coursId!,
          tauxHoraire: taux,
          anneeAcademique: _anneeId!,
        );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      _tauxController.clear();
      setState(() => _coursId = null);
    }
  }

  Future<void> _confirmDelete(ParametrePayroll p) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le taux horaire de ${p.coursNom} ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    await context.read<ParametrePayrollState>().delete(p.id);
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametrePayrollState>();
    final refData = context.watch<ReferenceDataState>();

    return ParamDialogShell(
      title: 'Taux horaires par cours',
      width: 640,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            height: 220,
            child: state.isLoading
                ? const Center(child: CircularProgressIndicator())
                : state.items.isEmpty
                    ? Center(
                        child: Text('Aucun taux configuré.',
                            style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                      )
                    : ListView.separated(
                        itemCount: state.items.length,
                        separatorBuilder: (_, _) => Divider(height: 8, color: AppColors.borderSubtle),
                        itemBuilder: (context, index) {
                          final p = state.items[index];
                          return Row(
                            children: [
                              Expanded(
                                child: Text('${p.coursNom} — ${p.anneeAcademiqueLabel}',
                                    style: TextStyle(color: AppColors.textPrimary, fontSize: 13)),
                              ),
                              Text('${p.tauxHoraire.toStringAsFixed(2)} / h',
                                  style: TextStyle(color: AppColors.textMuted, fontSize: 12.5)),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                                onPressed: state.deletingId == p.id ? null : () => _confirmDelete(p),
                              ),
                            ],
                          );
                        },
                      ),
          ),
          const Divider(height: 20),
          Text('Ajouter un taux', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          const SizedBox(height: 10),
          SearchableDropdownField<(String, String)>(
            key: ValueKey('cours-taux-${state.coursOptionsForDropdown.length}'),
            options: state.coursOptionsForDropdown,
            idOf: (c) => c.$1,
            displayStringForOption: (c) => c.$2,
            selectedId: _coursId,
            labelText: 'Cours',
            onSelected: (c) => setState(() => _coursId = c.$1),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _anneeId,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Année académique'),
                  items: refData.annees
                      .map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom, overflow: TextOverflow.ellipsis)))
                      .toList(),
                  onChanged: (v) => setState(() => _anneeId = v),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextField(
                  controller: _tauxController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Taux / heure'),
                ),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Align(
              alignment: Alignment.centerRight,
              child: FilledButton(
                onPressed: state.isSubmitting ? null : _submit,
                child: state.isSubmitting
                    ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Ajouter'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// "Bilan mensuel" (demande explicite) : pour un mois/année donné, montre
/// d'un coup d'œil tous les professeurs avec leur Payroll du mois — montant
/// dû/versé/solde/statut — ou "Aucun" si rien n'a encore été enregistré.
class _BilanMensuelDialog extends StatefulWidget {
  const _BilanMensuelDialog();

  @override
  State<_BilanMensuelDialog> createState() => _BilanMensuelDialogState();
}

class _BilanMensuelDialogState extends State<_BilanMensuelDialog> {
  late String _mois = PayrollState.moisOptions[DateTime.now().month - 1];
  late final _anneeController = TextEditingController(text: '${DateTime.now().year}');

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  @override
  void dispose() {
    _anneeController.dispose();
    super.dispose();
  }

  void _load() {
    context.read<PayrollState>().loadBilanMensuel(
          mois: _mois,
          annee: _anneeController.text.trim(),
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PayrollState>();

    return ParamDialogShell(
      title: 'Bilan mensuel — professeurs',
      width: 720,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _mois,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Mois'),
                  items: PayrollState.moisOptions
                      .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                      .toList(),
                  onChanged: (v) {
                    setState(() => _mois = v ?? _mois);
                    _load();
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _anneeController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Année'),
                  onSubmitted: (_) => _load(),
                ),
              ),
              const SizedBox(width: 12),
              IconButton(
                tooltip: 'Actualiser',
                icon: const Icon(Icons.refresh),
                onPressed: _load,
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (state.isLoadingBilan)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 30),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (state.bilanError != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Text(state.bilanError!, style: const TextStyle(color: AppColors.danger)),
            )
          else
            SizedBox(
              height: 400,
              child: SingleChildScrollView(
                child: DataTableCard(
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('PROFESSEUR')),
                      DataColumn(label: Text('MONTANT DÛ')),
                      DataColumn(label: Text('VERSÉ')),
                      DataColumn(label: Text('SOLDE')),
                      DataColumn(label: Text('STATUT')),
                    ],
                    rows: state.bilanMensuel.map((r) {
                      return DataRow(cells: [
                        DataCell(Text(r.nom)),
                        DataCell(Text(r.montantDu?.toStringAsFixed(2) ?? '—')),
                        DataCell(Text(r.montantVerse?.toStringAsFixed(2) ?? '—')),
                        DataCell(Text(r.soldeRestant?.toStringAsFixed(2) ?? '—')),
                        DataCell(_StatusBadge(statut: r.statut)),
                      ]);
                    }).toList(),
                  ),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Fermer'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PayrollFormDialog extends StatefulWidget {
  const _PayrollFormDialog();

  @override
  State<_PayrollFormDialog> createState() => _PayrollFormDialogState();
}

class _PayrollFormDialogState extends State<_PayrollFormDialog> {
  String? _userId;
  final _amountController = TextEditingController();
  String? _mois;
  late final _anneeController = TextEditingController(
    text: '${DateTime.now().year}',
  );
  String _methodePaiement = PayrollState.methodeOptions.first;
  String? _anneeAcademiqueId;
  final Map<String, TextEditingController> _heuresControllers = {};
  String? _error;
  // Personnel avec casquette enseignante (salaire fixe Personnel + fiche
  // Professeur liée) : false = payer la fiche professeur (horaire/fixe
  // selon sa config), true = payer le salaire fixe Personnel à la place.
  bool _payAsPersonnel = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PayrollState>().loadUserOptions();
      context.read<ReferenceDataState>().loadOnce();
    });
  }

  @override
  void dispose() {
    _amountController.dispose();
    _anneeController.dispose();
    for (final c in _heuresControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _onUserChanged(String? userId) async {
    setState(() {
      _userId = userId;
      _anneeAcademiqueId = null;
      _heuresControllers.clear();
      _payAsPersonnel = false;
    });
    if (userId == null) return;
    await context.read<PayrollState>().loadProfesseurInfo(userId);
    if (!mounted) return;
    final state = context.read<PayrollState>();
    if (state.selectedTypePaiement == 'fixe' && state.selectedSalaireFixe != null) {
      _amountController.text = state.selectedSalaireFixe!.toStringAsFixed(2);
    }
    setState(() {});
  }

  Future<void> _onAnneeAcademiqueChanged(String? anneeId) async {
    setState(() => _anneeAcademiqueId = anneeId);
    if (anneeId == null) return;
    final state = context.read<PayrollState>();
    await state.loadCoursOptions(anneeAcademique: anneeId);
    final moisIndex = PayrollState.moisOptions.indexOf(_mois ?? '');
    final annee = int.tryParse(_anneeController.text.trim());
    if (moisIndex >= 0 && annee != null) {
      await state.loadHeuresPointees(mois: moisIndex + 1, annee: annee);
    }
    if (!mounted) return;
    setState(() {
      for (final c in state.coursOptions) {
        _heuresControllers.putIfAbsent(c.coursId, () => TextEditingController());
      }
    });
  }

  double get _totalHoraire {
    final state = context.read<PayrollState>();
    double total = 0;
    for (final c in state.coursOptions) {
      final heures = double.tryParse(_heuresControllers[c.coursId]?.text.trim() ?? '') ?? 0;
      if (c.tauxHoraire != null) total += heures * c.tauxHoraire!;
    }
    return total;
  }

  Future<void> _submit() async {
    final state = context.read<PayrollState>();
    final annee = _anneeController.text.trim();

    if (_userId == null || _mois == null || annee.length != 4) {
      setState(() => _error = 'Employé, mois et année (4 chiffres) sont requis.');
      return;
    }

    String? errorResult;
    if (!_payAsPersonnel && state.selectedIsProfesseur && state.selectedTypePaiement == 'horaire') {
      if (_anneeAcademiqueId == null) {
        setState(() => _error = 'Année académique requise pour un calcul horaire.');
        return;
      }
      final details = <Map<String, dynamic>>[];
      for (final c in state.coursOptions) {
        final heures = double.tryParse(_heuresControllers[c.coursId]?.text.trim() ?? '');
        if (heures == null || heures <= 0) continue;
        if (c.tauxHoraire == null) {
          setState(() => _error = 'Aucun taux configuré pour « ${c.coursNom} ». Configurez-le avant de continuer.');
          return;
        }
        details.add({'cours_id': c.coursId, 'heures': heures});
      }
      if (details.isEmpty) {
        setState(() => _error = 'Saisissez au moins un nombre d\'heures pour un cours.');
        return;
      }
      setState(() => _error = null);
      errorResult = await state.create(
        userId: _userId!,
        mois: _mois!,
        annee: annee,
        methodePaiement: _methodePaiement,
        typeCalcul: 'horaire',
        detailsHoraires: details,
      );
    } else {
      final amount = double.tryParse(_amountController.text.trim());
      if (amount == null || amount <= 0) {
        setState(() => _error = 'Veuillez saisir un montant valide.');
        return;
      }
      setState(() => _error = null);
      errorResult = await state.create(
        userId: _userId!,
        mois: _mois!,
        annee: annee,
        methodePaiement: _methodePaiement,
        typeCalcul: 'fixe',
        montant: amount,
      );
    }

    if (!mounted) return;
    if (errorResult != null) {
      setState(() => _error = errorResult);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PayrollState>();
    final refData = context.watch<ReferenceDataState>();
    final isHoraire = !_payAsPersonnel && state.selectedIsProfesseur && state.selectedTypePaiement == 'horaire';

    return ParamDialogShell(
      title: 'Verser un salaire',
      width: 680,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          state.isLoadingUserOptions
              ? const Padding(
                  padding: EdgeInsets.symmetric(vertical: 14),
                  child: LinearProgressIndicator(minHeight: 2),
                )
              : Autocomplete<LoanUserOption>(
                  displayStringForOption: (u) => u.fullName,
                  optionsBuilder: (value) {
                    if (value.text.isEmpty) return state.userOptions;
                    final q = value.text.toLowerCase();
                    return state.userOptions.where((u) => u.fullName.toLowerCase().contains(q));
                  },
                  onSelected: (u) => _onUserChanged(u.id),
                  fieldViewBuilder: (context, controller, focusNode, onSubmit) => TextField(
                    controller: controller,
                    focusNode: focusNode,
                    decoration: const InputDecoration(labelText: 'Professeur / Personnel'),
                  ),
                ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _mois,
                  decoration: const InputDecoration(labelText: 'Mois'),
                  items: PayrollState.moisOptions
                      .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                      .toList(),
                  onChanged: (v) => setState(() => _mois = v),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _anneeController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Année'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _methodePaiement,
            decoration: const InputDecoration(labelText: 'Méthode de paiement'),
            items: PayrollState.methodeOptions
                .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                .toList(),
            onChanged: (v) =>
                setState(() => _methodePaiement = v ?? _methodePaiement),
          ),
          if (state.isLoadingProfesseurInfo) ...[
            const SizedBox(height: 12),
            const LinearProgressIndicator(minHeight: 2),
          ],
          if (state.selectedHasLinkedProfesseur) ...[
            const SizedBox(height: 12),
            Text('Cette personne a un salaire fixe (Personnel) ET une fiche professeur '
                '(casquette enseignante) — choisissez lequel payer :',
                style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
            const SizedBox(height: 8),
            SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: false, label: Text('Professeur')),
                ButtonSegment(value: true, label: Text('Personnel (fixe)')),
              ],
              selected: {_payAsPersonnel},
              onSelectionChanged: (selection) => setState(() {
                _payAsPersonnel = selection.first;
                if (_payAsPersonnel) {
                  _amountController.text = state.selectedPersonnelSalaireFixe?.toStringAsFixed(2) ?? '';
                } else if (state.selectedTypePaiement == 'fixe' && state.selectedSalaireFixe != null) {
                  _amountController.text = state.selectedSalaireFixe!.toStringAsFixed(2);
                }
              }),
            ),
          ],
          if (isHoraire) ...[
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              // DropdownButtonFormField ne relit initialValue qu'à sa
              // création — sans cette Key liée à _userId, changer
              // d'employé (qui remet _anneeAcademiqueId à null) laissait
              // le champ affiché bloqué sur l'ancienne sélection visuelle
              // pendant que la vraie valeur était déjà null, d'où l'erreur
              // "Année académique requise" malgré un champ qui semblait
              // rempli.
              key: ValueKey('annee-academique-$_userId'),
              initialValue: _anneeAcademiqueId,
              decoration: const InputDecoration(labelText: 'Année académique'),
              items: refData.annees
                  .map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom)))
                  .toList(),
              onChanged: _onAnneeAcademiqueChanged,
            ),
            if (state.heuresPointeesRef != null) ...[
              const SizedBox(height: 8),
              Text(
                'Heures pointées ce mois : ${state.heuresPointeesRef!.toStringAsFixed(1)} h (référence)',
                style: TextStyle(fontSize: 12, color: AppColors.textMuted),
              ),
            ],
            const SizedBox(height: 10),
            if (state.isLoadingCoursOptions)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 10),
                child: LinearProgressIndicator(minHeight: 2),
              )
            else if (_anneeAcademiqueId != null && state.coursOptions.isEmpty)
              Text('Aucun cours trouvé pour ce professeur sur cette année.',
                  style: TextStyle(fontSize: 12, color: AppColors.textMuted))
            else
              ...state.coursOptions.map((c) {
                final controller = _heuresControllers.putIfAbsent(c.coursId, () => TextEditingController());
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Text(c.coursNom, style: TextStyle(fontSize: 13, color: AppColors.textPrimary)),
                      ),
                      Expanded(
                        child: Text(
                          c.tauxHoraire != null ? '${c.tauxHoraire!.toStringAsFixed(2)} / h' : 'Taux non configuré',
                          style: TextStyle(
                            fontSize: 12,
                            color: c.tauxHoraire != null ? AppColors.textMuted : AppColors.danger,
                          ),
                        ),
                      ),
                      Expanded(
                        child: TextField(
                          controller: controller,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: const InputDecoration(labelText: 'Heures'),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                    ],
                  ),
                );
              }),
            if (state.coursOptions.isNotEmpty) ...[
              const SizedBox(height: 4),
              Align(
                alignment: Alignment.centerRight,
                child: Text(
                  'Montant dû : ${_totalHoraire.toStringAsFixed(2)}',
                  style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
              ),
            ],
          ] else ...[
            const SizedBox(height: 12),
            TextField(
              controller: _amountController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Montant'),
            ),
          ],
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          ParamDialogActions(
            isEdit: false,
            submitting: state.isSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}

/// Versement (partiel ou intégral) contre un Payroll — mirror direct de
/// _RepayFormDialog (loan_tab.dart) : historique des versements à gauche,
/// formulaire à droite, montant pré-rempli au solde restant.
class _VerserFormDialog extends StatefulWidget {
  const _VerserFormDialog({required this.payroll});

  final PayrollRecord payroll;

  @override
  State<_VerserFormDialog> createState() => _VerserFormDialogState();
}

class _VerserFormDialogState extends State<_VerserFormDialog> {
  late final _amountController = TextEditingController(
    text: (widget.payroll.remainingBalance ?? widget.payroll.montant).toStringAsFixed(2),
  );
  String _methodePaiement = PayrollState.methodeOptions.first;
  String? _error;

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text.trim());
    if (amount == null || amount <= 0) {
      setState(() => _error = 'Le montant versé doit être supérieur à 0.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<PayrollState>().verser(
          payrollId: widget.payroll.id,
          montant: amount,
          methodePaiement: _methodePaiement,
        );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PayrollState>();
    final versements = widget.payroll.versements;
    final montantDu = widget.payroll.montantDu ?? widget.payroll.montant;
    final solde = widget.payroll.remainingBalance ?? 0;

    return ParamDialogShell(
      title: 'Versement — ${widget.payroll.user}',
      width: 680,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Historique des versements',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 280,
                  child: versements.isEmpty
                      ? Center(
                          child: Text(
                            'Aucun versement enregistré.',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 12, color: AppColors.textMuted),
                          ),
                        )
                      : ListView.separated(
                          itemCount: versements.length,
                          separatorBuilder: (_, _) => Divider(height: 10, color: AppColors.borderSubtle),
                          itemBuilder: (context, index) {
                            final v = versements[index];
                            return Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                              decoration: BoxDecoration(
                                color: AppColors.cardBg,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(v.montant.toStringAsFixed(2),
                                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
                                        Text(v.methodePaiement ?? 'Non précisé',
                                            style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                                      ],
                                    ),
                                  ),
                                  Text(v.dateVersement, style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
                                ],
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Faire un versement', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                const SizedBox(height: 8),
                InputDecorator(
                  decoration: const InputDecoration(labelText: 'Montant dû', enabled: false),
                  child: Text(montantDu.toStringAsFixed(2), style: TextStyle(color: AppColors.textMuted)),
                ),
                const SizedBox(height: 12),
                InputDecorator(
                  decoration: const InputDecoration(labelText: 'Solde restant', enabled: false),
                  child: Text(solde.toStringAsFixed(2), style: TextStyle(color: AppColors.textMuted)),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _methodePaiement,
                  decoration: const InputDecoration(labelText: 'Méthode de paiement'),
                  items: PayrollState.methodeOptions
                      .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                      .toList(),
                  onChanged: (v) => setState(() => _methodePaiement = v ?? _methodePaiement),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Montant à verser'),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
                ],
                ParamDialogActions(
                  isEdit: false,
                  submitting: state.payingId == widget.payroll.id,
                  onSubmit: _submit,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
