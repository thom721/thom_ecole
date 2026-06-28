import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Pastille colorée utilisée dans les tableaux de Parametres.vue (ex:
/// `bg-emerald-500/10 text-emerald-400 border border-emerald-500/20` pour un
/// statut "Actif", `bg-sky-500/10 ...` pour une méthode d'évaluation, etc.)
class BadgePill extends StatelessWidget {
  const BadgePill({
    super.key,
    required this.label,
    required this.colorKey,
    this.dot = false,
    this.showBorder = true,
  });

  final String label;
  final String colorKey;
  final bool dot;

  /// `false` réduit le contour à une simple bordure très discrète au lieu du
  /// `withValues(alpha: 0.2)` habituel — utile dans les grilles denses
  /// (rôles/permissions) où la bordure de chaque pastille ajoute du bruit
  /// visuel inutile une fois la couleur de fond déjà présente.
  final bool showBorder;

  @override
  Widget build(BuildContext context) {
    final color = AppColors.cardPalette[colorKey]?.text ?? AppColors.textMuted;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: showBorder
            ? Border.all(color: color.withValues(alpha: 0.2))
            : null,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (dot) ...[
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 6),
          ],
          Flexible(
            child: Text(
              label,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
