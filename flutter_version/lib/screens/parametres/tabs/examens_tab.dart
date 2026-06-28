import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/parametres_state.dart';
import '../../../state/reference_data_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

const _evaluationOptions = ['mois', 'session', 'semestre', 'Trimestre', 'Controle'];
const _evaluationLabels = {
  'mois': 'Mois',
  'session': 'Session',
  'semestre': 'Semestre',
  'Trimestre': 'Trimestre',
  'Controle': 'Contrôle',
};

/// Onglet "Examens" — équivalent du tab `exams` de Parametres.vue : liste
/// paginée v1/paramsExam + modale Évaluation/Année/Cycle (school_client:
/// Helper/Components/Exam_params.py).
class ExamensTab extends StatelessWidget {
  const ExamensTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    return ParamTabCard(
      title: 'Paramètres des Examens',
      subtitle: "Configurez les méthodes d'évaluation par cycle et année",
      onAdd: () => showDialog(context: context, builder: (_) => const _ExamenFormDialog()),
      isLoading: state.examenLoading,
      error: state.examenError,
      emptyLabel: 'Aucun paramètre configuré',
      emptyIcon: Icons.fact_check_outlined,
      currentPage: state.examenCurrentPage,
      lastPage: state.examenLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadExamens(page: page),
      columns: const [
        DataColumn(label: Text('CYCLE')),
        DataColumn(label: Text('ÉVALUATION')),
        DataColumn(label: Text('ANNÉE ACADÉMIQUE')),
        DataColumn(label: Text('')),
      ],
      rows: state.examensList.map((e) {
        return DataRow(cells: [
          DataCell(Text(e.niveauName,
              style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600))),
          DataCell(BadgePill(label: _evaluationLabels[e.evaluationPar] ?? e.evaluationPar, colorKey: 'sky')),
          DataCell(Text(e.anneeAcademique, style: TextStyle(color: AppColors.textMuted))),
          DataCell(
            IconButton(
              icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.textMuted),
              onPressed: () => showDialog(context: context, builder: (_) => _ExamenFormDialog(record: e)),
            ),
          ),
        ]);
      }).toList(),
    );
  }
}

class _ExamenFormDialog extends StatefulWidget {
  const _ExamenFormDialog({this.record});

  final ParamExamRecord? record;

  @override
  State<_ExamenFormDialog> createState() => _ExamenFormDialogState();
}

class _ExamenFormDialogState extends State<_ExamenFormDialog> {
  String? _evaluationPar;
  String? _anneeAcademiqueId;
  String? _niveauId;
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _evaluationPar = r.evaluationPar;
      _anneeAcademiqueId = r.anneeAcademiqueId;
      _niveauId = r.niveauId;
    }
  }

  Future<void> _submit() async {
    if (_evaluationPar == null || _anneeAcademiqueId == null || _niveauId == null) {
      setState(() => _error = 'Tous les champs sont requis.');
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitExamen(
          id: widget.record?.id,
          niveauId: _niveauId!,
          anneeAcademiqueId: _anneeAcademiqueId!,
          evaluationPar: _evaluationPar!,
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
      title: 'Paramètres des Examens',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _evaluationPar,
            decoration: const InputDecoration(labelText: 'Évaluation / Examen par'),
            items: _evaluationOptions
                .map((v) => DropdownMenuItem(value: v, child: Text(_evaluationLabels[v]!)))
                .toList(),
            onChanged: (v) => setState(() => _evaluationPar = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _anneeAcademiqueId,
            decoration: const InputDecoration(labelText: 'Année Académique'),
            items: ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
            onChanged: (v) => setState(() => _anneeAcademiqueId = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            decoration: const InputDecoration(labelText: 'Cycle'),
            items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
            onChanged: (v) => setState(() => _niveauId = v),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.examenSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
