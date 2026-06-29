import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/auth_state.dart';
import '../../../state/parametres_state.dart';
import '../../../state/reference_data_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

/// Onglet "Frais Divers" — feature 100% bureau (school_client:
/// Helper/Components/Frais_divers.py), absente du frontend web.
class FraisDiversTab extends StatelessWidget {
  const FraisDiversTab({super.key});

  Future<void> _confirmDelete(
      BuildContext context, FraisDiversRecord f, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le frais divers "${f.niveauName} — ${f.anneeAcademique}" ?'),
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
    final error = await state.deleteFraisDivers(f.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, FraisDiversRecord f) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Frais Divers'),
        content: ParamDetailTable(rows: [
          ('Cycle', f.niveauName),
          ('Année académique', f.anneeAcademique),
          ('Description', f.description.isEmpty ? '—' : f.description),
          ('Prix', '${f.prix}'),
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
      title: 'Frais Divers',
      subtitle: 'Frais ponctuels par cycle et année (uniforme, carte, etc.)',
      canAdd: canAjouter,
      onAdd: () => showDialog(context: context, builder: (_) => const _FraisDiversFormDialog()),
      isLoading: state.fraisDiversLoading,
      error: state.fraisDiversError,
      emptyLabel: 'Aucun frais divers',
      emptyIcon: Icons.receipt_outlined,
      currentPage: state.fraisDiversCurrentPage,
      lastPage: state.fraisDiversLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadFraisDivers(page: page),
      columns: const [
        DataColumn(label: Text('CYCLE')),
        DataColumn(label: Text('ANNÉE ACADÉMIQUE')),
        DataColumn(label: Text('DESCRIPTION')),
        DataColumn(label: Text('PRIX')),
        DataColumn(label: Text('')),
      ],
      rows: state.fraisDiversList.map((f) {
        return DataRow(cells: [
          DataCell(BadgePill(label: f.niveauName, colorKey: 'purple')),
          DataCell(Text(f.anneeAcademique, style: TextStyle(color: AppColors.textMuted))),
          DataCell(Text(f.description.isEmpty ? '—' : f.description,
              style: TextStyle(color: AppColors.textMuted))),
          DataCell(Text('${f.prix}',
              style: TextStyle(
                  color: AppColors.textPrimary, fontWeight: FontWeight.w700, fontFamily: 'monospace'))),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (canVoir)
                IconButton(
                  tooltip: 'Voir',
                  icon: const Icon(Icons.remove_red_eye_outlined, size: 16, color: Color(0xFF34D399)),
                  onPressed: () => _showDetail(context, f),
                ),
              if (canModifier)
                IconButton(
                  tooltip: 'Modifier',
                  icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.accentLight),
                  onPressed: () =>
                      showDialog(context: context, builder: (_) => _FraisDiversFormDialog(record: f)),
                ),
              if (canSupprimer)
                IconButton(
                  tooltip: 'Supprimer',
                  icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                  onPressed: () => _confirmDelete(context, f, state),
                ),
            ],
          )),
        ]);
      }).toList(),
    );
  }
}

class _FraisDiversFormDialog extends StatefulWidget {
  const _FraisDiversFormDialog({this.record});

  final FraisDiversRecord? record;

  @override
  State<_FraisDiversFormDialog> createState() => _FraisDiversFormDialogState();
}

class _FraisDiversFormDialogState extends State<_FraisDiversFormDialog> {
  String? _niveauId;
  String? _anneeAcId;
  late final TextEditingController _descriptionController;
  late final TextEditingController _prixController;
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    _niveauId = r?.niveauId;
    _anneeAcId = r?.anneeAcId;
    _descriptionController = TextEditingController(text: r?.description ?? '');
    _prixController = TextEditingController(text: r == null ? '' : '${r.prix}');
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    _prixController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final prix = num.tryParse(_prixController.text.replaceAll(',', '.'));
    if (_niveauId == null || _anneeAcId == null || prix == null || prix <= 0) {
      setState(() => _error = 'Cycle, année et prix (> 0) sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitFraisDivers(
          id: widget.record?.id,
          niveauId: _niveauId!,
          anneeAc: _anneeAcId!,
          prix: prix,
          description: _descriptionController.text.trim(),
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
    final ref = context.watch<ReferenceDataState>();
    return ParamDialogShell(
      title: 'Frais divers',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            decoration: const InputDecoration(labelText: 'Cycle / Section / Niveau'),
            items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
            onChanged: (v) => setState(() => _niveauId = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _anneeAcId,
            decoration: const InputDecoration(labelText: 'Année Académique'),
            items: ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
            onChanged: (v) => setState(() => _anneeAcId = v),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _descriptionController,
            decoration: const InputDecoration(labelText: 'Description'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _prixController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Prix', hintText: 'Ex: 1000gdes'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.fraisDiversSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
