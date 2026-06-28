import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/parametres_state.dart';
import '../../../state/reference_data_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

/// Onglet "Frais Divers" — feature 100% bureau (school_client:
/// Helper/Components/Frais_divers.py, déclenchée par btn_frais_divers →
/// frais_divers_params_page(), Main.py:13424), absente du frontend web
/// (Parametres.vue n'a pas ce tab). Mêmes endpoints que le bureau réel :
/// v1/frais-divers-index (liste paginée) et v1/frais-divers-store (créer/
/// modifier). Colonne "Description" volontairement vide en pratique — voir
/// le commentaire sur FraisDiversRecord (lib/models/parametres.dart).
class FraisDiversTab extends StatelessWidget {
  const FraisDiversTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    return ParamTabCard(
      title: 'Frais Divers',
      subtitle: 'Frais ponctuels par cycle et année (uniforme, carte, etc.)',
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
              style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w700, fontFamily: 'monospace'))),
          DataCell(
            IconButton(
              icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.textMuted),
              onPressed: () => showDialog(context: context, builder: (_) => _FraisDiversFormDialog(record: f)),
            ),
          ),
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
  final _descriptionController = TextEditingController();
  final _prixController = TextEditingController();
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _niveauId = r.niveauId;
      _anneeAcId = r.anneeAcId;
      _descriptionController.text = r.description;
      _prixController.text = '${r.prix}';
    }
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
