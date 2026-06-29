import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/auth_state.dart';
import '../../../state/parametres_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

String _fmt(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

/// Onglet "Années" — équivalent du tab `annees` de Parametres.vue : liste
/// paginée v1/anneeAcademique + modale Début/Fin/Statut (school_client:
/// Helper/Components/annee_academique.py).
class AnneesTab extends StatelessWidget {
  const AnneesTab({super.key});

  Future<void> _confirmDelete(
      BuildContext context, AnneeAcademiqueRecord a, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer l\'année académique "${a.anneeAcademique}" ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;
    final error = await state.deleteAnnee(a.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, AnneeAcademiqueRecord a) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Année Académique'),
        content: ParamDetailTable(rows: [
          ('Année', a.anneeAcademique),
          ('Début', a.dateDebut),
          ('Fin', a.dateFin),
          ('Statut', a.status ? 'Actif' : 'Inactif'),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Fermer')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    final subs = context.watch<AuthState>().visibleSubItems('settings');
    final canAjouter = subs == null || subs.contains('ajouter');
    final canModifier = subs == null || subs.contains('modifier');
    final canSupprimer = subs == null || subs.contains('supprimer');
    final canVoir = subs == null || subs.contains('voir');

    return ParamTabCard(
      title: 'Années Académiques',
      subtitle: 'Définissez les périodes scolaires actives',
      canAdd: canAjouter,
      onAdd: () => showDialog(context: context, builder: (_) => const _AnneeFormDialog()),
      isLoading: state.anneeLoading,
      error: state.anneeError,
      emptyLabel: 'Aucune année académique',
      emptyIcon: Icons.calendar_today_outlined,
      currentPage: state.anneeCurrentPage,
      lastPage: state.anneeLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadAnnees(page: page),
      columns: const [
        DataColumn(label: Text('DÉBUT')),
        DataColumn(label: Text('FIN')),
        DataColumn(label: Text('ANNÉE ACADÉMIQUE')),
        DataColumn(label: Text('STATUT')),
        DataColumn(label: Text('')),
      ],
      rows: state.annees.map((a) {
        return DataRow(cells: [
          DataCell(Text(a.dateDebut, style: TextStyle(color: AppColors.textMuted))),
          DataCell(Text(a.dateFin, style: TextStyle(color: AppColors.textMuted))),
          DataCell(Text(a.anneeAcademique,
              style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600))),
          DataCell(BadgePill(
            label: a.status ? 'Actif' : 'Inactif',
            colorKey: a.status ? 'emerald' : 'cyan',
            dot: true,
          )),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (canVoir)
                IconButton(
                  tooltip: 'Voir',
                  icon: const Icon(Icons.remove_red_eye_outlined, size: 16, color: Color(0xFF34D399)),
                  onPressed: () => _showDetail(context, a),
                ),
              if (canModifier)
                IconButton(
                  tooltip: 'Modifier',
                  icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.accentLight),
                  onPressed: () =>
                      showDialog(context: context, builder: (_) => _AnneeFormDialog(record: a)),
                ),
              if (canSupprimer)
                IconButton(
                  tooltip: 'Supprimer',
                  icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                  onPressed: () => _confirmDelete(context, a, state),
                ),
            ],
          )),
        ]);
      }).toList(),
    );
  }
}

class _AnneeFormDialog extends StatefulWidget {
  const _AnneeFormDialog({this.record});

  final AnneeAcademiqueRecord? record;

  @override
  State<_AnneeFormDialog> createState() => _AnneeFormDialogState();
}

class _AnneeFormDialogState extends State<_AnneeFormDialog> {
  DateTime? _dateDebut;
  DateTime? _dateFin;
  bool? _status;
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _dateDebut = DateTime.tryParse(r.dateDebut);
      _dateFin = DateTime.tryParse(r.dateFin);
      _status = r.status;
    }
  }

  Future<void> _pickDate({required bool isDebut}) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: (isDebut ? _dateDebut : _dateFin) ?? DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => isDebut ? _dateDebut = picked : _dateFin = picked);
    }
  }

  Future<void> _submit() async {
    if (_dateDebut == null || _dateFin == null || _status == null) {
      setState(() => _error = 'Tous les champs sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitAnnee(
          id: widget.record?.id,
          dateDebut: _fmt(_dateDebut!),
          dateFin: _fmt(_dateFin!),
          status: _status!,
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
    final state = context.watch<ParametresState>();
    return ParamDialogShell(
      title: 'Année Académique',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _DatePickerField(label: 'Début', value: _dateDebut, onTap: () => _pickDate(isDebut: true)),
          const SizedBox(height: 12),
          _DatePickerField(label: 'Fin', value: _dateFin, onTap: () => _pickDate(isDebut: false)),
          const SizedBox(height: 12),
          DropdownButtonFormField<bool>(
            initialValue: _status,
            decoration: const InputDecoration(labelText: 'Statut'),
            items: const [
              DropdownMenuItem(value: true, child: Text('Actif')),
              DropdownMenuItem(value: false, child: Text('Inactif')),
            ],
            onChanged: (v) => setState(() => _status = v),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.anneeSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}

class _DatePickerField extends StatelessWidget {
  const _DatePickerField({required this.label, required this.value, required this.onTap});

  final String label;
  final DateTime? value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: InputDecorator(
        decoration:
            InputDecoration(labelText: label, suffixIcon: const Icon(Icons.calendar_today_outlined, size: 16)),
        child: Text(
          value == null ? '' : _fmt(value!),
          style: TextStyle(color: AppColors.textPrimary),
        ),
      ),
    );
  }
}
