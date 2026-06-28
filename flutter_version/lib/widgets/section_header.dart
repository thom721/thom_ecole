import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Bandeau de titre de page — icône colorée + titre + sous-titre. Reprend le
/// motif répété en haut de chaque page du frontend web (ecole_nginx/frontend,
/// ex: Paiements.vue, Dashboard.vue) : icône dans un carré 36x36 teinté à 10%
/// avec bordure à 20%, titre 15px gras, sous-titre 12px muet.
class SectionHeader extends StatelessWidget {
  const SectionHeader({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    this.colorKey = 'blue',
    this.trailing,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final String colorKey;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final palette = AppColors.cardPalette[colorKey] ?? AppColors.cardPalette['blue']!;
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: palette.bar.withValues(alpha: 0.1),
            border: Border.all(color: palette.bar.withValues(alpha: 0.2)),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, size: 18, color: palette.text),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: TextStyle(
                      fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              Text(subtitle, style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
            ],
          ),
        ),
        ?trailing,
      ],
    );
  }
}
