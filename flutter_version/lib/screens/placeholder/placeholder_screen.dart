import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

/// Page pas encore reproduite depuis school_client — chaque page sera
/// remplacée par son propre écran au fur et à mesure (voir Resources/
/// main_school1.ui pour la liste complète des pages d'origine).
class PlaceholderScreen extends StatelessWidget {
  const PlaceholderScreen({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.construction, size: 48, color: AppColors.textMuted),
          const SizedBox(height: 12),
          Text(
            '$title — pas encore reproduit',
            style: TextStyle(fontSize: 16, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}
