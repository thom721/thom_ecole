import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/auth_state.dart';
import '../../../state/parametres_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

/// Onglet "Facultés" — équivalent du tab `facultes` de Parametres.vue.
class FacultesTab extends StatelessWidget {
  const FacultesTab({super.key});

  Future<void> _confirmDelete(BuildContext context, FaculteRecord f, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer la faculté "${f.nom}" ?'),
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
    final error = await state.deleteFaculte(f.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, FaculteRecord f) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Faculté'),
        content: ParamDetailTable(rows: [
          ('Nom', f.nom),
          ('Nbre sessions', f.nbAnnee),
          ('Statut', f.status ? 'Actif' : 'Inactif'),
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
      title: 'Facultés / Professions',
      subtitle: "Gérez les domaines d'étude disponibles",
      canAdd: canAjouter,
      onAdd: () => showDialog(context: context, builder: (_) => const _FaculteFormDialog()),
      isLoading: state.faculteLoading,
      error: state.faculteError,
      emptyLabel: 'Aucune faculté enregistrée',
      emptyIcon: Icons.school_outlined,
      currentPage: state.faculteCurrentPage,
      lastPage: state.faculteLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadFacultes(page: page),
      columns: const [
        DataColumn(label: Text('NOM')),
        DataColumn(label: Text('NBRE SESSIONS')),
        DataColumn(label: Text('STATUT')),
        DataColumn(label: Text('')),
      ],
      rows: state.facultesList.map((f) {
        return DataRow(cells: [
          DataCell(Text(f.nom, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600))),
          DataCell(Text(f.nbAnnee, style: TextStyle(color: AppColors.textMuted))),
          DataCell(BadgePill(
            label: f.status ? 'Actif' : 'Inactif',
            colorKey: f.status ? 'emerald' : 'cyan',
            dot: true,
          )),
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
                      showDialog(context: context, builder: (_) => _FaculteFormDialog(record: f)),
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

class _FaculteFormDialog extends StatefulWidget {
  const _FaculteFormDialog({this.record});

  final FaculteRecord? record;

  @override
  State<_FaculteFormDialog> createState() => _FaculteFormDialogState();
}

class _FaculteFormDialogState extends State<_FaculteFormDialog> {
  late final TextEditingController _nomController;
  late final TextEditingController _nbAnneeController;
  String? _error;

  @override
  void initState() {
    super.initState();
    _nomController = TextEditingController(text: widget.record?.nom ?? '');
    _nbAnneeController = TextEditingController(text: widget.record?.nbAnnee ?? '');
  }

  @override
  void dispose() {
    _nomController.dispose();
    _nbAnneeController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_nomController.text.trim().length < 4 || _nbAnneeController.text.trim().length < 4) {
      setState(() => _error = "Le nom et le nombre de sessions doivent contenir au moins 4 caractères.");
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitFaculte(
          nom: _nomController.text.trim(),
          nbAnnee: _nbAnneeController.text.trim(),
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
      title: 'Facultés / Profession',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _nomController,
            decoration: const InputDecoration(labelText: "Domaine d'étude", hintText: 'Ex: Infirmière'),
            autofocus: true,
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _nbAnneeController,
            decoration: const InputDecoration(labelText: 'Nbre de sessions', hintText: 'Ex: 4 ans'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
              isEdit: false, submitting: state.faculteSubmitting, onSubmit: _submit),
        ],
      ),
    );
  }
}
