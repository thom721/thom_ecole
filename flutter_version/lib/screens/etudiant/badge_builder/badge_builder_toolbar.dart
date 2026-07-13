import 'package:flutter/material.dart';

import '../../../models/badge_layout.dart';
import '../../../theme/app_theme.dart';

/// Libellés affichés pour chaque jeton de `kBadgePlaceholderTokens` —
/// mêmes jetons, juste un texte lisible dans le menu "Champ dynamique".
const _fieldLabels = {
  '{{nom}}': 'Nom',
  '{{prenom}}': 'Prénom',
  '{{classe}}': 'Classe',
  '{{identifiant}}': 'Identifiant',
  '{{expiration}}': 'Expiration',
  '{{salle}}': 'Salle',
};

/// Colonne d'outils de l'éditeur de badge — ajout d'éléments, champs
/// dynamiques liés aux données de l'étudiant, image de fond, actions sur
/// l'élément sélectionné (dupliquer/supprimer/ordre).
class BadgeBuilderToolbar extends StatelessWidget {
  const BadgeBuilderToolbar({
    super.key,
    required this.onAddText,
    required this.onAddField,
    required this.onAddShape,
    required this.onAddPhotoPlaceholder,
    required this.onAddQrPlaceholder,
    required this.onAddImage,
    required this.onPickBackground,
    required this.hasSelection,
    required this.onDuplicate,
    required this.onDelete,
    required this.onBringToFront,
    required this.onSendToBack,
    required this.penActive,
    required this.onTogglePen,
  });

  final VoidCallback onAddText;
  final ValueChanged<String> onAddField;
  final VoidCallback onAddShape;
  final VoidCallback onAddPhotoPlaceholder;
  final VoidCallback onAddQrPlaceholder;
  final VoidCallback onAddImage;
  final VoidCallback onPickBackground;
  final bool hasSelection;
  final VoidCallback onDuplicate;
  final VoidCallback onDelete;
  final VoidCallback onBringToFront;
  final VoidCallback onSendToBack;
  final bool penActive;
  final VoidCallback onTogglePen;

  @override
  Widget build(BuildContext context) {
    // Le tracé au clic exige un état ininterrompu (points déjà posés) —
    // les autres actions sont désactivées pendant que la plume est
    // active pour éviter de le corrompre (ex. supprimer l'élément
    // sélectionné pendant qu'on dessine).
    final disabledWhileDrawing = penActive;
    return Container(
      width: 60,
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      // Défile plutôt que de déborder (RenderFlex overflow) quand la
      // fenêtre est basse ou que le bandeau de la plume réduit l'espace
      // vertical disponible — la colonne d'outils a une hauteur fixe de
      // contenu qui peut dépasser la hauteur allouée.
      child: SingleChildScrollView(
        child: Column(
          children: [
            _ToolButton(
              icon: Icons.text_fields,
              tooltip: 'Ajouter du texte libre',
              onPressed: disabledWhileDrawing ? null : onAddText,
            ),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Tooltip(
                message:
                    'Ajouter un champ dynamique (nom, classe, identifiant…)',
                child: PopupMenuButton<String>(
                  icon: Icon(
                    Icons.data_object,
                    size: 20,
                    color: disabledWhileDrawing
                        ? AppColors.textMuted.withValues(alpha: 0.35)
                        : null,
                  ),
                  onSelected: disabledWhileDrawing ? null : onAddField,
                  itemBuilder: (context) => [
                    for (final token in kBadgePlaceholderTokens)
                      PopupMenuItem(
                        value: token,
                        child: Text(_fieldLabels[token] ?? token),
                      ),
                    const PopupMenuDivider(),
                    const PopupMenuItem(
                      value: kBadgeCustomFieldToken,
                      child: Text('Personnalisé'),
                    ),
                  ],
                ),
              ),
            ),
            _ToolButton(
              icon: Icons.crop_square_outlined,
              tooltip: 'Ajouter une forme',
              onPressed: disabledWhileDrawing ? null : onAddShape,
            ),
            _ToolButton(
              icon: Icons.person_outline,
              tooltip: 'Emplacement photo',
              onPressed: disabledWhileDrawing ? null : onAddPhotoPlaceholder,
            ),
            _ToolButton(
              icon: Icons.qr_code_2,
              tooltip: 'Emplacement QR code',
              onPressed: disabledWhileDrawing ? null : onAddQrPlaceholder,
            ),
            _ToolButton(
              icon: Icons.add_photo_alternate_outlined,
              tooltip: 'Ajouter une image (logo, signature...)',
              onPressed: disabledWhileDrawing ? null : onAddImage,
            ),
            _ToolButton(
              icon: Icons.draw_outlined,
              tooltip: penActive
                  ? 'Plume active — cliquez pour poser un point, glissez pour le courber'
                  : 'Outil plume (tracer une forme libre)',
              onPressed: onTogglePen,
              color: penActive ? AppColors.accent : null,
            ),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 6),
              child: Divider(height: 1),
            ),
            _ToolButton(
              icon: Icons.image_outlined,
              tooltip: 'Image de fond',
              onPressed: disabledWhileDrawing ? null : onPickBackground,
            ),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 6),
              child: Divider(height: 1),
            ),
            _ToolButton(
              icon: Icons.copy_outlined,
              tooltip: 'Dupliquer',
              onPressed: (hasSelection && !disabledWhileDrawing)
                  ? onDuplicate
                  : null,
            ),
            _ToolButton(
              icon: Icons.delete_outline,
              tooltip: 'Supprimer',
              onPressed: (hasSelection && !disabledWhileDrawing)
                  ? onDelete
                  : null,
              color: AppColors.danger,
            ),
            _ToolButton(
              icon: Icons.flip_to_front_outlined,
              tooltip: 'Premier plan',
              onPressed: (hasSelection && !disabledWhileDrawing)
                  ? onBringToFront
                  : null,
            ),
            _ToolButton(
              icon: Icons.flip_to_back_outlined,
              tooltip: 'Arrière-plan',
              onPressed: (hasSelection && !disabledWhileDrawing)
                  ? onSendToBack
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}

class _ToolButton extends StatelessWidget {
  const _ToolButton({
    required this.icon,
    required this.tooltip,
    required this.onPressed,
    this.color,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback? onPressed;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Tooltip(
        message: tooltip,
        child: IconButton(
          icon: Icon(icon, size: 20),
          color: onPressed == null
              ? AppColors.textMuted.withValues(alpha: 0.35)
              : (color ?? AppColors.textPrimary),
          onPressed: onPressed,
        ),
      ),
    );
  }
}
