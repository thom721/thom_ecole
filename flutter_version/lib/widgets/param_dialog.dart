import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Coquille commune des modales de création/édition de la page Paramètres —
/// équivalent de StyleModal.vue (ecole_nginx/frontend/src/components), même
/// fond panelBg, mêmes coins arrondis, même croix de fermeture rouge.
class ParamDialogShell extends StatelessWidget {
  const ParamDialogShell({super.key, required this.title, required this.child, this.width = 540});

  final String title;
  final Widget child;
  final double width;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.panelBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: width, maxHeight: 720),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(title,
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: AppColors.danger, size: 18),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                child,
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Table clé/valeur pour les dialogues de détail des onglets Paramètres.
class ParamDetailTable extends StatelessWidget {
  const ParamDetailTable({super.key, required this.rows});
  final List<(String, String)> rows;

  @override
  Widget build(BuildContext context) {
    return Table(
      columnWidths: const {0: IntrinsicColumnWidth(), 1: FlexColumnWidth()},
      children: rows.map((r) {
        return TableRow(children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
            child: Text(r.$1, style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
            child: Text(r.$2,
                style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w500, fontSize: 13)),
          ),
        ]);
      }).toList(),
    );
  }
}

/// Ligne d'actions "Fermer" / "Enregistrer ou Modifier" — identique dans
/// chaque modale de Parametres.vue (DangerButton + PrimaryButton).
class ParamDialogActions extends StatelessWidget {
  const ParamDialogActions({
    super.key,
    required this.isEdit,
    required this.submitting,
    required this.onSubmit,
  });

  final bool isEdit;
  final bool submitting;
  final VoidCallback? onSubmit;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 18),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
            child: const Text('Fermer'),
          ),
          const SizedBox(width: 8),
          FilledButton(
            onPressed: submitting ? null : onSubmit,
            child: submitting
                ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : Text(isEdit ? 'Modifier' : 'Enregistrer'),
          ),
        ],
      ),
    );
  }
}
