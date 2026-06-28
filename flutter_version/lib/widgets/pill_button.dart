import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Bouton pilule translucide — reprend .btn-emerald/.btn-sky/.btn-amber/
/// .btn-violet/.btn-custum-sky (ecole_nginx/frontend/src/assets/main.css) :
/// fond teinté à 10%, bordure teintée à 20%, texte coloré, hover plus opaque.
class PillButton extends StatelessWidget {
  const PillButton({
    super.key,
    required this.label,
    required this.colorKey,
    this.onPressed,
    this.icon,
  });

  final String label;
  final String colorKey;
  final VoidCallback? onPressed;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final palette = AppColors.cardPalette[colorKey] ?? AppColors.cardPalette['blue']!;
    return TextButton.icon(
      onPressed: onPressed,
      icon: icon != null ? Icon(icon, size: 15, color: palette.text) : const SizedBox.shrink(),
      label: Text(label, style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w500, color: palette.text)),
      style: ButtonStyle(
        backgroundColor: WidgetStateProperty.resolveWith((states) {
          return palette.bar.withValues(alpha: states.contains(WidgetState.hovered) ? 0.25 : 0.1);
        }),
        side: WidgetStatePropertyAll(BorderSide(color: palette.bar.withValues(alpha: 0.25))),
        shape: WidgetStatePropertyAll(RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
        padding: const WidgetStatePropertyAll(EdgeInsets.symmetric(horizontal: 16, vertical: 12)),
      ),
    );
  }
}
