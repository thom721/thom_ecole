import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/dual_auth.dart';
import '../../models/depense.dart';
import '../../state/depense_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';

/// Équivalent de depense_page()/enregistrer_depense()/delete_depense()
/// (school_client, Controllers/Main.py:5122-5295).
class DepenseTab extends StatefulWidget {
  const DepenseTab({super.key});

  @override
  State<DepenseTab> createState() => _DepenseTabState();
}

class _DepenseTabState extends State<DepenseTab> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openForm({DepenseRecord? depense}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _DepenseFormDialog(initial: depense),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            depense == null ? 'Dépense ajoutée.' : 'Dépense modifiée.',
          ),
        ),
      );
    }
  }

  Future<void> _confirmDelete(DepenseRecord depense) async {
    final raison = await showReasonDialog(
      context: context,
      title: 'Supprimer cette dépense ?',
      message:
          'Supprimer la dépense "${depense.description}" ? Indiquez la raison de la suppression.',
      confirmLabel: 'Supprimer',
    );
    if (raison == null || !mounted) return;
    final error = await runWithPinApproval(
      context: context,
      permission: 'Supprimer paiement',
      action: ({approvalToken}) => context.read<DepenseState>().delete(
        depense.id,
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
    final state = context.watch<DepenseState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Ajouter une dépense',
              colorKey: 'rose',
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
                  hintText: 'Rechercher une dépense...',
                  isDense: true,
                ),
                onSubmitted: (v) =>
                    context.read<DepenseState>().load(page: 1, search: v),
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
                    context.read<DepenseState>().load(page: page),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('DESCRIPTION')),
                    DataColumn(label: Text('PRIX')),
                    DataColumn(label: Text('UTILISATEUR')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((d) {
                    final isDeleting = state.deletingId == d.id;
                    return DataRow(
                      cells: [
                        DataCell(Text(d.description)),
                        DataCell(Text(d.prix.toStringAsFixed(2))),
                        DataCell(Text(d.userName ?? '—')),
                        DataCell(Text(d.date)),
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
                                      onPressed: () => _openForm(depense: d),
                                    ),
                                    IconButton(
                                      tooltip: 'Supprimer',
                                      icon: const Icon(
                                        Icons.delete_outline,
                                        size: 17,
                                        color: AppColors.danger,
                                      ),
                                      onPressed: () => _confirmDelete(d),
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

class _DepenseFormDialog extends StatefulWidget {
  const _DepenseFormDialog({this.initial});

  final DepenseRecord? initial;

  @override
  State<_DepenseFormDialog> createState() => _DepenseFormDialogState();
}

class _DepenseFormDialogState extends State<_DepenseFormDialog> {
  late final _descController = TextEditingController(
    text: widget.initial?.description ?? '',
  );
  late final _prixController = TextEditingController(
    text: widget.initial?.prix.toString() ?? '',
  );
  String? _error;

  @override
  void dispose() {
    _descController.dispose();
    _prixController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final description = _descController.text.trim();
    final prix = double.tryParse(_prixController.text.trim());
    if (description.length < 3 || prix == null || prix <= 0) {
      setState(
        () => _error =
            'Description (3 caractères min.) et prix (> 0) sont requis.',
      );
      return;
    }
    setState(() => _error = null);
    final error = await runWithPinApproval(
      context: context,
      permission: 'Modifier paiement',
      action: ({approvalToken}) => context.read<DepenseState>().save(
        id: widget.initial?.id,
        description: description,
        prix: prix,
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
    final state = context.watch<DepenseState>();

    return ParamDialogShell(
      title: widget.initial == null
          ? 'Ajouter une dépense'
          : 'Modifier la dépense',
      width: 440,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _descController,
            decoration: const InputDecoration(labelText: 'Description'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _prixController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Prix'),
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
