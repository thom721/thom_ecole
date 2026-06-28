import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../state/parametres_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

/// Onglet "Facultés" — équivalent du tab `facultes` de Parametres.vue.
/// Création seulement : dans le frontend réel, les boutons éditer/supprimer
/// de ce tableau n'ont aucun gestionnaire @click câblé (vérifié dans le
/// fichier source), donc pas reproduits ici — seul "Ajouter" est fonctionnel.
class FacultesTab extends StatelessWidget {
  const FacultesTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    return ParamTabCard(
      title: 'Facultés / Professions',
      subtitle: "Gérez les domaines d'étude disponibles",
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
        ]);
      }).toList(),
    );
  }
}

class _FaculteFormDialog extends StatefulWidget {
  const _FaculteFormDialog();

  @override
  State<_FaculteFormDialog> createState() => _FaculteFormDialogState();
}

class _FaculteFormDialogState extends State<_FaculteFormDialog> {
  final _nomController = TextEditingController();
  final _nbAnneeController = TextEditingController();
  String? _error;

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
          ParamDialogActions(isEdit: false, submitting: state.faculteSubmitting, onSubmit: _submit),
        ],
      ),
    );
  }
}
