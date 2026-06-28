import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/dual_auth.dart';
import '../../models/student.dart';
import '../../models/transaction.dart';
import '../../state/transaction_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';

/// Équivalent de autre_transaction()/set_table_refresh_data_other_transac()
/// (school_client, Controllers/Main.py:5013-5119) — transactions diverses
/// (badge perdu, relevé de notes, diplôme...) liées ou non à un élève.
class TransactionTab extends StatefulWidget {
  const TransactionTab({super.key});

  @override
  State<TransactionTab> createState() => _TransactionTabState();
}

class _TransactionTabState extends State<TransactionTab> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openForm({OtherTransactionRecord? transaction}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _TransactionFormDialog(initial: transaction),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            transaction == null
                ? 'Transaction enregistrée.'
                : 'Transaction modifiée.',
          ),
        ),
      );
    }
  }

  Future<void> _confirmDelete(OtherTransactionRecord transaction) async {
    final raison = await showReasonDialog(
      context: context,
      title: 'Supprimer cette transaction ?',
      message:
          'Supprimer la transaction "${transaction.displayDescription}" ? Indiquez la raison de la suppression.',
      confirmLabel: 'Supprimer',
    );
    if (raison == null || !mounted) return;
    final error = await runWithPinApproval(
      context: context,
      permission: 'Supprimer transaction',
      action: ({approvalToken}) => context.read<TransactionState>().delete(
        transaction.id,
        raison: raison,
        approvalToken: approvalToken,
      ),
    );
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<TransactionState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Nouvelle transaction',
              colorKey: 'sky',
              icon: Icons.add,
              onPressed: () => _openForm(),
            ),
            const Spacer(),
            SizedBox(
              width: 260,
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 18),
                  hintText: 'Rechercher une transaction...',
                  isDense: true,
                ),
                onSubmitted: (v) =>
                    context.read<TransactionState>().load(page: 1, search: v),
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
                    context.read<TransactionState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('UTILISATEUR')),
                    DataColumn(label: Text('DESCRIPTION')),
                    DataColumn(label: Text('ÉLÈVE')),
                    DataColumn(label: Text('MONTANT')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((t) {
                    final isDeleting = state.deletingId == t.id;
                    return DataRow(
                      cells: [
                        DataCell(Text(t.utilisateur ?? '—')),
                        DataCell(Text(t.displayDescription)),
                        DataCell(Text(t.etudiantLabel)),
                        DataCell(Text(t.montant.toStringAsFixed(2))),
                        DataCell(Text(t.date)),
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
                                    IconButton(
                                      tooltip: 'Modifier',
                                      icon: Icon(
                                        Icons.edit_outlined,
                                        size: 17,
                                        color: AppColors.accentLight,
                                      ),
                                      onPressed: () =>
                                          _openForm(transaction: t),
                                    ),
                                    IconButton(
                                      tooltip: 'Supprimer',
                                      icon: const Icon(
                                        Icons.delete_outline,
                                        size: 17,
                                        color: AppColors.danger,
                                      ),
                                      onPressed: () => _confirmDelete(t),
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

class _TransactionFormDialog extends StatefulWidget {
  const _TransactionFormDialog({this.initial});

  final OtherTransactionRecord? initial;

  @override
  State<_TransactionFormDialog> createState() => _TransactionFormDialogState();
}

class _TransactionFormDialogState extends State<_TransactionFormDialog> {
  late String _description =
      widget.initial?.description ?? TransactionState.descriptionOptions.first;
  late final _descriptionSuppController = TextEditingController(
    text: widget.initial?.descriptionSupplementaire ?? '',
  );
  late final _montantController = TextEditingController(
    text: widget.initial?.montant.toString() ?? '',
  );
  late final _studentSearchController = TextEditingController(
    text: widget.initial?.etudiantLabel == '—'
        ? ''
        : widget.initial?.etudiantLabel ?? '',
  );
  String? _identifiant;
  String? _error;

  @override
  void initState() {
    super.initState();
    _identifiant = widget.initial?.etudiantId;
  }

  @override
  void dispose() {
    _descriptionSuppController.dispose();
    _montantController.dispose();
    _studentSearchController.dispose();
    super.dispose();
  }

  void _selectStudent(Student s) {
    setState(() {
      _identifiant = s.id;
      _studentSearchController.text = '${s.nom} ${s.prenom}';
    });
    context.read<TransactionState>().searchStudents('');
  }

  Future<void> _submit() async {
    final montant = double.tryParse(_montantController.text.trim());
    final descriptionSupp = _descriptionSuppController.text.trim();

    if (montant == null || montant <= 0) {
      setState(() => _error = 'Le montant doit être supérieur à 0.');
      return;
    }
    if (_description == 'Autre' && descriptionSupp.isEmpty) {
      setState(
        () =>
            _error = 'La description supplémentaire est requise pour "Autre".',
      );
      return;
    }
    setState(() => _error = null);
    final error = await runWithPinApproval(
      context: context,
      permission: 'Modifier transaction',
      action: ({approvalToken}) => context.read<TransactionState>().save(
        id: widget.initial?.id,
        description: _description,
        descriptionSupplementaire: descriptionSupp.isEmpty
            ? null
            : descriptionSupp,
        identifiant: _identifiant,
        montant: montant,
        approvalToken: approvalToken,
      ),
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
    final state = context.watch<TransactionState>();

    return ParamDialogShell(
      title: widget.initial == null
          ? 'Nouvelle transaction'
          : 'Modifier la transaction',
      width: 460,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _studentSearchController,
            decoration: const InputDecoration(
              labelText: 'Identifiant (élève, optionnel)',
              prefixIcon: Icon(Icons.search, size: 18),
              isDense: true,
            ),
            onChanged: (v) {
              if (_identifiant != null) {
                setState(() => _identifiant = null);
              }
              context.read<TransactionState>().searchStudents(v);
            },
          ),
          if (state.liveSearchResults.isNotEmpty)
            Container(
              margin: const EdgeInsets.only(top: 6),
              constraints: const BoxConstraints(maxHeight: 160),
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                border: Border.all(color: AppColors.borderHover),
                borderRadius: BorderRadius.circular(10),
              ),
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: state.liveSearchResults.length,
                itemBuilder: (context, index) {
                  final s = state.liveSearchResults[index];
                  return ListTile(
                    dense: true,
                    title: Text(
                      '${s.nom} ${s.prenom}',
                      style: TextStyle(
                        fontSize: 12.5,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    subtitle: Text(
                      s.identifiant,
                      style: TextStyle(
                        fontSize: 11,
                        color: AppColors.textMuted,
                      ),
                    ),
                    onTap: () => _selectStudent(s),
                  );
                },
              ),
            ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _description,
            decoration: const InputDecoration(labelText: 'Description'),
            items: TransactionState.descriptionOptions
                .map((d) => DropdownMenuItem(value: d, child: Text(d)))
                .toList(),
            onChanged: (v) => setState(() => _description = v ?? _description),
          ),
          if (_description == 'Autre') ...[
            const SizedBox(height: 12),
            TextField(
              controller: _descriptionSuppController,
              decoration: const InputDecoration(
                labelText: 'Description supplémentaire',
              ),
            ),
          ],
          const SizedBox(height: 12),
          TextField(
            controller: _montantController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Montant'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          ParamDialogActions(
            isEdit: widget.initial != null,
            submitting: state.isSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
