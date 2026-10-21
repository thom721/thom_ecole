import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'numbered_pager.dart';
import 'scrollable_table.dart';

/// Conteneur de tableau — reprend DataTable.vue (ecole_nginx/frontend) :
/// fond cardBg (blanc en thème clair, #161b26 en sombre), bordure borderSubtle,
/// rayon 2xl (16px), padding 24px, plus la pagination numérotée (Pagination.vue).
class DataTableCard extends StatelessWidget {
  const DataTableCard({
    super.key,
    required this.child,
    this.currentPage,
    this.lastPage,
    this.onPageChange,
  });

  final Widget child;
  final int? currentPage;
  final int? lastPage;
  final ValueChanged<int>? onPageChange;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Pleine largeur + ascenseur horizontal visible (voir ScrollableTable).
          ScrollableTable(child: child),
          if (currentPage != null && lastPage != null && onPageChange != null) ...[
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: NumberedPager(
                currentPage: currentPage!,
                lastPage: lastPage!,
                onPageChange: onPageChange!,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
