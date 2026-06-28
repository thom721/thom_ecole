import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/loan.dart';
import '../../state/loan_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';

/// Équivalent de tab_loans()/loans_form()/sauvegarder_loans()/
/// to_loans_repayments() (school_client, Controllers/Main.py:4871-4972).
class LoanTab extends StatefulWidget {
  const LoanTab({super.key});

  @override
  State<LoanTab> createState() => _LoanTabState();
}

class _LoanTabState extends State<LoanTab> {
  Future<void> _openCreateForm() async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => const _LoanFormDialog(),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Prêt accordé.')));
    }
  }

  Future<void> _openRepayForm(LoanRecord loan) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _RepayFormDialog(loan: loan),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Remboursement enregistré.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<LoanState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            PillButton(
              label: 'Accorder un prêt',
              colorKey: 'violet',
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
                    context.read<LoanState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('UTILISATEUR')),
                    DataColumn(label: Text('MONTANT')),
                    DataColumn(label: Text('REMBOURSÉ')),
                    DataColumn(label: Text('ÉCHÉANCE')),
                    DataColumn(label: Text('STATUT')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((l) {
                    return DataRow(
                      cells: [
                        DataCell(Text(l.user ?? '—')),
                        DataCell(Text(l.amount.toStringAsFixed(2))),
                        DataCell(_RepaymentProgress(loan: l)),
                        DataCell(Text('${l.termMonths} Mois')),
                        DataCell(_StatusBadge(status: l.status)),
                        DataCell(Text(l.date)),
                        DataCell(
                          TextButton(
                            onPressed: l.status == 'paid'
                                ? null
                                : () => _openRepayForm(l),
                            child: const Text('Rembourser'),
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

/// Équivalent de la barre de progression "Remboursé" de Tresorerie.vue
/// (ecole_nginx/frontend, onglet Prêts) — calcule le pourcentage réellement
/// remboursé (montant - solde restant) / montant, contrairement au web qui
/// affiche par erreur `amount / (amount + remaining)` (toujours ≥ 50% dès
/// la création d'un prêt, `statut` au lieu de `status` pour la couleur du
/// badge) : on reprend ici la mise en forme (barre + %), pas le calcul
/// erroné.
class _RepaymentProgress extends StatelessWidget {
  const _RepaymentProgress({required this.loan});

  final LoanRecord loan;

  @override
  Widget build(BuildContext context) {
    final repaid = loan.amount - loan.remainingBalance;
    final pct = loan.amount > 0
        ? (repaid / loan.amount * 100).clamp(0, 100).round()
        : 0;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 70,
          height: 6,
          decoration: BoxDecoration(
            color: AppColors.hoverOverlay,
            borderRadius: BorderRadius.circular(4),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: pct / 100,
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.accent,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$pct%',
          style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
        ),
      ],
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final isPending = status == 'pending';
    final color = isPending ? AppColors.accent : const Color(0xFF34D399);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        status,
        style: TextStyle(
          fontSize: 11.5,
          fontWeight: FontWeight.w500,
          color: color,
        ),
      ),
    );
  }
}

/// Champ verrouillé reproduisant un QLineEdit `readOnly=true` du bureau
/// (Approuvé par/Date d'approbation/Date de déblocage/Solde restant/Date de
/// création/Dernière mise à jour, main_school1.ui:17320-17524) : jamais
/// renseigné à la création (aucun flux d'approbation/déblocage n'existe
/// côté bureau ni serveur), donc affiché mais désactivé plutôt qu'omis.
class _LockedField extends StatelessWidget {
  const _LockedField({required this.label, this.value});

  final String label;
  final String? value;

  @override
  Widget build(BuildContext context) {
    return InputDecorator(
      decoration: InputDecoration(labelText: label, enabled: false),
      child: Text(
        value?.isNotEmpty == true ? value! : '—',
        style: TextStyle(color: AppColors.textMuted, fontSize: 13.5),
      ),
    );
  }
}

class _LoanFormDialog extends StatefulWidget {
  const _LoanFormDialog();

  @override
  State<_LoanFormDialog> createState() => _LoanFormDialogState();
}

class _LoanFormDialogState extends State<_LoanFormDialog> {
  String? _userId;
  final _amountController = TextEditingController();
  final _termController = TextEditingController(text: '1');
  final _interestController = TextEditingController(text: '0');
  final _monthlyPaymentController = TextEditingController();
  String _status = LoanState.statusOptions.first;
  String? _error;

  @override
  void initState() {
    super.initState();
    _amountController.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _amountController.dispose();
    _termController.dispose();
    _interestController.dispose();
    _monthlyPaymentController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text.trim());
    final term = int.tryParse(_termController.text.trim());
    final interest = double.tryParse(_interestController.text.trim()) ?? 0;
    final monthlyPayment = double.tryParse(
      _monthlyPaymentController.text.trim(),
    );

    if (_userId == null ||
        amount == null ||
        amount <= 0 ||
        term == null ||
        term <= 0 ||
        monthlyPayment == null ||
        monthlyPayment < 0) {
      setState(
        () => _error =
            'Utilisateur, montant (> 0), durée en mois (> 0) et mensualité sont requis.',
      );
      return;
    }
    setState(() => _error = null);
    final error = await context.read<LoanState>().createLoan(
      userId: _userId!,
      amount: amount,
      termMonths: term,
      interestRate: interest,
      monthlyPayment: monthlyPayment,
      status: _status,
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
    final state = context.watch<LoanState>();

    final amount = _amountController.text.trim();

    return ParamDialogShell(
      title: 'Accorder un prêt',
      width: 640,
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
                    labelText: 'Identifiant utilisateur / nom',
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
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(labelText: 'Montant'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _termController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Durée (mois)'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _interestController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: "Taux d'intérêt (%)",
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _monthlyPaymentController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(labelText: 'Mensualité'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _status,
                  decoration: const InputDecoration(labelText: 'Statut'),
                  items: LoanState.statusOptions
                      .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                      .toList(),
                  onChanged: (v) => setState(() => _status = v ?? _status),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Row(
            children: [
              Expanded(child: _LockedField(label: 'Approuvé par')),
              SizedBox(width: 12),
              Expanded(child: _LockedField(label: "Date d'approbation")),
              SizedBox(width: 12),
              Expanded(child: _LockedField(label: 'Date de déblocage')),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _LockedField(
                  label: 'Solde restant',
                  value: amount.isEmpty ? null : amount,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(child: _LockedField(label: 'Date de création')),
              const SizedBox(width: 12),
              const Expanded(
                child: _LockedField(label: 'Dernière mise à jour'),
              ),
            ],
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

class _RepayFormDialog extends StatefulWidget {
  const _RepayFormDialog({required this.loan});

  final LoanRecord loan;

  @override
  State<_RepayFormDialog> createState() => _RepayFormDialogState();
}

class _RepayFormDialogState extends State<_RepayFormDialog> {
  final _amountController = TextEditingController();
  final _methodController = TextEditingController();
  String? _error;

  @override
  void dispose() {
    _amountController.dispose();
    _methodController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final amount = double.tryParse(_amountController.text.trim());
    if (amount == null || amount <= 0) {
      setState(() => _error = 'Le montant remboursé doit être supérieur à 0.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<LoanState>().repay(
      loansId: widget.loan.id,
      paidAmount: amount,
      paymentMethod: _methodController.text.trim().isEmpty
          ? null
          : _methodController.text.trim(),
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
    final state = context.watch<LoanState>();
    final repayments = widget.loan.repayments;

    return ParamDialogShell(
      title: 'Remboursement — ${widget.loan.user ?? ''}',
      width: 680,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Équivalent de "Historique des paiements" (tab_rembousement,
          // main_school1.ui:17632-17673) — absente côté serveur jusqu'ici
          // car on n'affichait que le formulaire de remboursement.
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Historique des paiements',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 320,
                  child: repayments.isEmpty
                      ? Center(
                          child: Text(
                            'Aucun remboursement enregistré.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 12,
                              color: AppColors.textMuted,
                            ),
                          ),
                        )
                      : ListView.separated(
                          itemCount: repayments.length,
                          separatorBuilder: (_, _) => Divider(
                            height: 10,
                            color: AppColors.borderSubtle,
                          ),
                          itemBuilder: (context, index) {
                            final r = repayments[index];
                            return Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 8,
                              ),
                              decoration: BoxDecoration(
                                color: AppColors.cardBg,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          r.paidAmount.toStringAsFixed(2),
                                          style: TextStyle(
                                            fontSize: 13,
                                            fontWeight: FontWeight.w500,
                                            color: AppColors.textPrimary,
                                          ),
                                        ),
                                        Text(
                                          r.paymentMethod ?? 'Non précisé',
                                          style: TextStyle(
                                            fontSize: 11,
                                            color: AppColors.textMuted,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Text(
                                    r.createdAt,
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: AppColors.textMuted,
                                    ),
                                  ),
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
                Text(
                  'Faire un remboursement',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                _LockedField(
                  label: 'Paiement mensuel',
                  value: widget.loan.monthlyPayment.toStringAsFixed(2),
                ),
                const SizedBox(height: 12),
                _LockedField(
                  label: "Taux d'intérêt",
                  value: widget.loan.interestRate.toStringAsFixed(2),
                ),
                const SizedBox(height: 12),
                _LockedField(
                  label: 'Solde restant',
                  value: widget.loan.remainingBalance.toStringAsFixed(2),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _methodController,
                  decoration: const InputDecoration(
                    labelText: 'Méthode de paiement',
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Montant à payer',
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style: const TextStyle(
                      color: AppColors.danger,
                      fontSize: 12,
                    ),
                  ),
                ],
                ParamDialogActions(
                  isEdit: false,
                  submitting: state.isSubmitting,
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
