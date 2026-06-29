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

/// Onglet "Classes" — équivalent du tab `classes` de Parametres.vue : liste
/// paginée v1/classes + modale Cycle/Classe (school_client: Helper/
/// Components/Add_classes.py).
class ClassesTab extends StatelessWidget {
  const ClassesTab({super.key});

  Future<void> _confirmDelete(
      BuildContext context, ClasseRecord c, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer la classe "${c.nomClasse}" ?'),
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
    final error = await state.deleteClasse(c.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, ClasseRecord c) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Classe'),
        content: ParamDetailTable(rows: [
          ('Cycle / Niveau', c.niveauName),
          ('Classe', c.nomClasse),
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
      title: 'Classes',
      subtitle: 'Organisez les classes par cycle',
      canAdd: canAjouter,
      onAdd: () => showDialog(context: context, builder: (_) => const _ClasseFormDialog()),
      isLoading: state.classeLoading,
      error: state.classeError,
      emptyLabel: 'Aucune classe enregistrée',
      emptyIcon: Icons.apartment_outlined,
      currentPage: state.classeCurrentPage,
      lastPage: state.classeLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadClasses(page: page),
      columns: const [
        DataColumn(label: Text('CYCLE / NIVEAU')),
        DataColumn(label: Text('CLASSE')),
        DataColumn(label: Text('')),
      ],
      rows: state.classesList.map((c) {
        return DataRow(cells: [
          DataCell(BadgePill(label: c.niveauName, colorKey: 'purple')),
          DataCell(Text(c.nomClasse,
              style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600))),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (canVoir)
                IconButton(
                  tooltip: 'Voir',
                  icon: const Icon(Icons.remove_red_eye_outlined, size: 16, color: Color(0xFF34D399)),
                  onPressed: () => _showDetail(context, c),
                ),
              if (canModifier)
                IconButton(
                  tooltip: 'Modifier',
                  icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.accentLight),
                  onPressed: () =>
                      showDialog(context: context, builder: (_) => _ClasseFormDialog(record: c)),
                ),
              if (canSupprimer)
                IconButton(
                  tooltip: 'Supprimer',
                  icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                  onPressed: () => _confirmDelete(context, c, state),
                ),
            ],
          )),
        ]);
      }).toList(),
    );
  }
}

class _ClasseFormDialog extends StatefulWidget {
  const _ClasseFormDialog({this.record});

  final ClasseRecord? record;

  @override
  State<_ClasseFormDialog> createState() => _ClasseFormDialogState();
}

class _ClasseFormDialogState extends State<_ClasseFormDialog> {
  String? _niveauId;
  late final TextEditingController _nomController;
  String? _error;

  @override
  void initState() {
    super.initState();
    _nomController = TextEditingController(text: widget.record?.nomClasse ?? '');
    _niveauId = widget.record?.niveauId;
  }

  @override
  void dispose() {
    _nomController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_niveauId == null || _nomController.text.trim().length < 3) {
      setState(() => _error = "Choisissez un cycle et un nom de classe d'au moins 3 caractères.");
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitClasse(
          id: widget.record?.id,
          niveauId: _niveauId!,
          nomClasse: _nomController.text.trim(),
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
    final niveaux = context.watch<ReferenceDataState>().niveaux;
    return ParamDialogShell(
      title: 'Classe',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            decoration: const InputDecoration(labelText: 'Cycle'),
            items: niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
            onChanged: (v) => setState(() => _niveauId = v),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _nomController,
            decoration: const InputDecoration(labelText: 'Classe', hintText: 'Ex: 6ème A, Terminale S...'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.classeSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
