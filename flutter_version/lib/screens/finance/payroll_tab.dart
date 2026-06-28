import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/payroll.dart';
import '../../state/payroll_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';

/// Versements de salaire aux Professeurs/Personnel — fonctionnalité ajoutée
/// sur demande explicite, sans référence bureau/web (voir
/// lib/state/payroll_state.dart). Liste + "Verser un salaire" ; chaque ligne
/// "En attente" peut être marquée "Payé".
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

  Future<void> _markPaid(PayrollRecord payroll) async {
    final error = await context.read<PayrollState>().markPaid(payroll.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
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
                    DataColumn(label: Text('MONTANT')),
                    DataColumn(label: Text('PÉRIODE')),
                    DataColumn(label: Text('MÉTHODE')),
                    DataColumn(label: Text('STATUT')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((p) {
                    final isPaying = state.payingId == p.id;
                    final isDeleting = state.deletingId == p.id;
                    final isPending = p.statut == 'En attente';
                    return DataRow(
                      cells: [
                        DataCell(Text(p.user)),
                        DataCell(Text(p.montant.toStringAsFixed(2))),
                        DataCell(Text('${p.mois} ${p.annee}')),
                        DataCell(Text(p.methodePaiement)),
                        DataCell(_StatusBadge(statut: p.statut)),
                        DataCell(Text(p.date)),
                        DataCell(
                          isPaying || isDeleting
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : Row(
                                  children: [
                                    if (isPending)
                                      TextButton(
                                        onPressed: () => _markPaid(p),
                                        child: const Text('Marquer payé'),
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
    final isPending = statut == 'En attente';
    final color = isPending ? AppColors.accent : const Color(0xFF34D399);
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
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PayrollState>().loadUserOptions();
    });
  }

  @override
  void dispose() {
    _amountController.dispose();
    _anneeController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text.trim());
    final annee = _anneeController.text.trim();

    if (_userId == null ||
        amount == null ||
        amount <= 0 ||
        _mois == null ||
        annee.length != 4) {
      setState(
        () => _error =
            'Employé, montant (> 0), mois et année (4 chiffres) sont requis.',
      );
      return;
    }
    setState(() => _error = null);
    final error = await context.read<PayrollState>().create(
      userId: _userId!,
      montant: amount,
      mois: _mois!,
      annee: annee,
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

    return ParamDialogShell(
      title: 'Verser un salaire',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          state.isLoadingUserOptions
              ? const Padding(
                  padding: EdgeInsets.symmetric(vertical: 14),
                  child: LinearProgressIndicator(minHeight: 2),
                )
              : DropdownButtonFormField<String>(
                  initialValue: _userId,
                  decoration: const InputDecoration(
                    labelText: 'Professeur / Personnel',
                  ),
                  items: state.userOptions
                      .map(
                        (u) => DropdownMenuItem(
                          value: u.id,
                          child: Text(u.fullName),
                        ),
                      )
                      .toList(),
                  onChanged: (v) => setState(() => _userId = v),
                ),
          const SizedBox(height: 12),
          TextField(
            controller: _amountController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Montant'),
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
