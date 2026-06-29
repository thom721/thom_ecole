import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'numbered_pager.dart';

/// Carte d'un onglet de la page Paramètres — reprend exactement la structure
/// de chaque section de Parametres.vue (ecole_nginx/frontend) : carte
/// `bg-[#161b26]` avec un en-tête (titre+sous-titre+bouton "Ajouter"), un
/// tableau, et une pagination en pied de carte.
class ParamTabCard extends StatelessWidget {
  const ParamTabCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onAdd,
    required this.columns,
    required this.rows,
    this.canAdd = true,
    this.currentPage,
    this.lastPage,
    this.onPageChange,
    this.isLoading = false,
    this.error,
    this.emptyLabel = 'Aucune donnée',
    this.emptyIcon = Icons.inbox_outlined,
  });

  final String title;
  final String subtitle;
  final VoidCallback onAdd;
  final bool canAdd;
  final List<DataColumn> columns;
  final List<DataRow> rows;
  final int? currentPage;
  final int? lastPage;
  final ValueChanged<int>? onPageChange;
  final bool isLoading;
  final String? error;
  final String emptyLabel;
  final IconData emptyIcon;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                      const SizedBox(height: 2),
                      Text(subtitle, style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                    ],
                  ),
                ),
                if (canAdd)
                  TextButton.icon(
                    onPressed: onAdd,
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text('Ajouter'),
                    style: TextButton.styleFrom(
                      backgroundColor: AppColors.accent.withValues(alpha: 0.15),
                      foregroundColor: AppColors.accentLight,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
              ],
            ),
          ),
          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (error != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 40),
              child: Center(child: Text(error!, style: TextStyle(color: AppColors.textPrimary))),
            )
          else if (rows.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Column(
                  children: [
                    Icon(emptyIcon, size: 36, color: AppColors.textMuted.withValues(alpha: 0.4)),
                    const SizedBox(height: 8),
                    Text(emptyLabel, style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  ],
                ),
              ),
            )
          else
            LayoutBuilder(
              builder: (context, constraints) {
                return SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: ConstrainedBox(
                    constraints: BoxConstraints(minWidth: constraints.maxWidth),
                    child: DataTable(showCheckboxColumn: false, columns: columns, rows: rows),
                  ),
                );
              },
            ),
          if (currentPage != null && lastPage != null && onPageChange != null && rows.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Align(
                alignment: Alignment.centerRight,
                child: NumberedPager(
                  currentPage: currentPage!,
                  lastPage: lastPage!,
                  onPageChange: onPageChange!,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
