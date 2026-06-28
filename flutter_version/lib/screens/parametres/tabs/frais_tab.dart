import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/parametres_state.dart';
import '../../../state/reference_data_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

/// Onglet "Frais" — équivalent du tab `frais` de Parametres.vue, qui
/// n'affiche QUE les frais d'inscription (Frais Divers existe côté backend
/// mais n'est rendu nulle part dans ce fichier réellement routé — vérifié,
/// donc pas reproduit ici). Pas de pagination affichée côté web non plus
/// (frais_paginate ne garde que `.data`, sans `<Pagination>`).
class FraisTab extends StatelessWidget {
  const FraisTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    return ParamTabCard(
      title: "Frais d'inscription",
      subtitle: "Tarifs d'inscription par cycle et année",
      onAdd: () => showDialog(context: context, builder: (_) => const _FraisFormDialog()),
      isLoading: state.fraisLoading,
      error: state.fraisError,
      emptyLabel: "Aucun frais d'inscription",
      emptyIcon: Icons.receipt_long_outlined,
      columns: const [
        DataColumn(label: Text('CYCLE')),
        DataColumn(label: Text('ANNÉE ACADÉMIQUE')),
        DataColumn(label: Text('PRIX')),
        DataColumn(label: Text('')),
      ],
      rows: state.fraisList.map((f) {
        return DataRow(cells: [
          DataCell(BadgePill(label: f.niveauName, colorKey: 'purple')),
          DataCell(Text(f.anneeAcademique, style: TextStyle(color: AppColors.textMuted))),
          DataCell(Text('${f.prix}',
              style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w700, fontFamily: 'monospace'))),
          DataCell(
            IconButton(
              icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.textMuted),
              onPressed: () => showDialog(context: context, builder: (_) => _FraisFormDialog(record: f)),
            ),
          ),
        ]);
      }).toList(),
    );
  }
}

class _FraisFormDialog extends StatefulWidget {
  const _FraisFormDialog({this.record});

  final FraisInscriptionRecord? record;

  @override
  State<_FraisFormDialog> createState() => _FraisFormDialogState();
}

class _FraisFormDialogState extends State<_FraisFormDialog> {
  String? _niveauId;
  String? _anneeAcId;
  final _prixController = TextEditingController();
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _niveauId = r.niveauId;
      _anneeAcId = r.anneeAc;
      _prixController.text = '${r.prix}';
    }
  }

  @override
  void dispose() {
    _prixController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final prix = num.tryParse(_prixController.text.replaceAll(',', '.'));
    if (_niveauId == null || _anneeAcId == null || prix == null || prix <= 0) {
      setState(() => _error = 'Tous les champs sont requis (prix > 0).');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitFrais(
          id: widget.record?.id,
          niveauId: _niveauId!,
          anneeAc: _anneeAcId!,
          prix: prix,
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
      title: "Frais d'inscription",
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            decoration: const InputDecoration(labelText: 'Cycle'),
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
            controller: _prixController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Prix'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.fraisSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
