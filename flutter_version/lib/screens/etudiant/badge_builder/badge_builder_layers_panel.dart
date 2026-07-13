import 'package:flutter/material.dart';

import '../../../models/badge_layout.dart';
import '../../../theme/app_theme.dart';

/// Panneau des calques, style Adobe (Illustrator/Photoshop) — liste
/// [elements] du haut (premier plan, `zIndex` le plus élevé) vers le bas
/// (arrière-plan), chaque ligne avec une icône "œil" (`hidden`) et une
/// icône "cadenas" (`locked`) — voir leur doc dans models/badge_layout.dart
/// pour ce que ces deux champs affectent réellement (l'aperçu/l'export
/// pour `hidden`, la protection contre `bakeSubtraction` pour `locked`).
///
/// Sert aussi de motivation directe à `locked` : un fond coloré recouvert
/// par un élément qu'on veut découper serait, sans ce panneau, découpé EN
/// MÊME TEMPS que sa cible (aucune notion d'occlusion entre deux éléments
/// empilés, voir badge_builder_canvas.dart::bakeSubtraction) — verrouiller
/// ce fond le protège explicitement.
class BadgeBuilderLayersPanel extends StatelessWidget {
  const BadgeBuilderLayersPanel({
    super.key,
    required this.elements,
    required this.selectedId,
    required this.onSelect,
    required this.onToggleHidden,
    required this.onToggleLocked,
  });

  final List<BadgeElement> elements;
  final String? selectedId;
  final ValueChanged<String> onSelect;
  final ValueChanged<BadgeElement> onToggleHidden;
  final ValueChanged<BadgeElement> onToggleLocked;

  @override
  Widget build(BuildContext context) {
    final sorted = [...elements]..sort((a, b) => b.zIndex.compareTo(a.zIndex));

    // Pas de largeur fixe : ce panneau partage maintenant une seule
    // colonne, de largeur fixée par l'appelant, avec le panneau de
    // propriétés (badge_builder_screen.dart::_buildInspectorColumn) via un
    // sélecteur d'onglet "Propriétés"/"Calques" — les deux ne sont plus
    // affichés côte à côte (ça réduisait considérablement la place laissée
    // au canevas).
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Padding(
            padding: EdgeInsets.only(bottom: 8, left: 2),
            child: Text(
              'Calques',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),
          Expanded(
            child: sorted.isEmpty
                ? Center(
                    child: Text(
                      'Aucun élément.',
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 12,
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: sorted.length,
                    itemBuilder: (context, index) => _LayerRow(
                      key: ValueKey(sorted[index].id),
                      element: sorted[index],
                      selected: sorted[index].id == selectedId,
                      onSelect: () => onSelect(sorted[index].id),
                      onToggleHidden: () => onToggleHidden(sorted[index]),
                      onToggleLocked: () => onToggleLocked(sorted[index]),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

class _LayerRow extends StatelessWidget {
  const _LayerRow({
    super.key,
    required this.element,
    required this.selected,
    required this.onSelect,
    required this.onToggleHidden,
    required this.onToggleLocked,
  });

  final BadgeElement element;
  final bool selected;
  final VoidCallback onSelect;
  final VoidCallback onToggleHidden;
  final VoidCallback onToggleLocked;

  IconData get _typeIcon => switch (element.type) {
    BadgeElementType.text => Icons.text_fields,
    BadgeElementType.shape => Icons.category_outlined,
    BadgeElementType.photoPlaceholder => Icons.person_outline,
    BadgeElementType.qrPlaceholder => Icons.qr_code_2,
    BadgeElementType.staticImage => Icons.image_outlined,
  };

  String get _label => switch (element.type) {
    BadgeElementType.text =>
      (element.text?.isNotEmpty ?? false) ? element.text! : 'Texte',
    BadgeElementType.shape => 'Forme',
    BadgeElementType.photoPlaceholder => 'Photo',
    BadgeElementType.qrPlaceholder => 'QR code',
    BadgeElementType.staticImage => 'Image',
  };

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onSelect,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 2),
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.accentLight.withValues(alpha: 0.18)
              : null,
          borderRadius: BorderRadius.circular(6),
          border: selected ? Border.all(color: AppColors.accent) : null,
        ),
        child: Row(
          children: [
            Icon(
              _typeIcon,
              size: 15,
              color: element.hidden
                  ? AppColors.textMuted
                  : AppColors.textPrimary,
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                _label,
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
                style: TextStyle(
                  fontSize: 12,
                  color: element.hidden
                      ? AppColors.textMuted
                      : AppColors.textPrimary,
                  decoration: element.hidden
                      ? TextDecoration.lineThrough
                      : null,
                ),
              ),
            ),
            IconButton(
              iconSize: 16,
              visualDensity: VisualDensity.compact,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 26, minHeight: 26),
              tooltip: element.locked
                  ? 'Déverrouiller (autoriser la découpe)'
                  : 'Verrouiller (protéger contre la découpe)',
              onPressed: onToggleLocked,
              icon: Icon(
                element.locked ? Icons.lock_outline : Icons.lock_open_outlined,
                color: element.locked ? AppColors.accent : AppColors.textMuted,
              ),
            ),
            IconButton(
              iconSize: 16,
              visualDensity: VisualDensity.compact,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(minWidth: 26, minHeight: 26),
              tooltip: element.hidden ? 'Afficher' : 'Masquer',
              onPressed: onToggleHidden,
              icon: Icon(
                element.hidden
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                color: element.hidden
                    ? AppColors.textMuted
                    : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
