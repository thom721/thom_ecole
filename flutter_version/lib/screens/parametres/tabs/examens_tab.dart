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

  Future<void> _confirmDelete(BuildContext context, ParamExamRecord e, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le paramètre "${e.niveauName} — ${e.anneeAcademique}" ?'),
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
    final error = await state.deleteExamen(e.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, ParamExamRecord e) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Paramètre Examen'),
        content: ParamDetailTable(rows: [
          ('Cycle', e.niveauName),
          ('Évaluation', _evaluationLabels[e.evaluationPar] ?? e.evaluationPar),
          ('Année académique', e.anneeAcademique),
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
    final auth = context.watch<AuthState>();
    final subs = auth.visibleSubItems('settings');
    final canWrite = auth.roles.contains('admin');
    final canAjouter = canWrite && (subs == null || subs.contains('ajouter'));
    final canModifier = canWrite && (subs == null || subs.contains('modifier'));
    final canSupprimer = canWrite && (subs == null || subs.contains('supprimer'));
    final canVoir = subs == null || subs.contains('voir');

    return ParamTabCard(
      title: 'Paramètres des Examens',
      subtitle: "Configurez les méthodes d'évaluation par cycle et année",
      canAdd: canAjouter,
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
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (canVoir)
                IconButton(
                  tooltip: 'Voir',
                  icon: const Icon(Icons.remove_red_eye_outlined, size: 16, color: Color(0xFF34D399)),
                  onPressed: () => _showDetail(context, e),
                ),
              if (canModifier)
                IconButton(
                  tooltip: 'Modifier',
                  icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.accentLight),
                  onPressed: () => showDialog(context: context, builder: (_) => _ExamenFormDialog(record: e)),
                ),
              if (canSupprimer)
                IconButton(
                  tooltip: 'Supprimer',
                  icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                  onPressed: () => _confirmDelete(context, e, state),
                ),
            ],
          )),
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

