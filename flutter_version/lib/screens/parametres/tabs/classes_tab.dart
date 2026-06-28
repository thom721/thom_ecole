import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
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

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    return ParamTabCard(
      title: 'Classes',
      subtitle: 'Organisez les classes par cycle',
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
          DataCell(
            IconButton(
              icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.textMuted),
              onPressed: () => showDialog(context: context, builder: (_) => _ClasseFormDialog(record: c)),
            ),
          ),
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
  final _nomController = TextEditingController();
  String? _error;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _niveauId = r.niveauId;
      _nomController.text = r.nomClasse;
    }
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
