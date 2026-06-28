import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Pagination numérotée — reprend Pagination.vue (ecole_nginx/frontend) :
/// chevrons précédent/suivant, pages affichées avec ellipses autour de la
/// page courante (delta=2), page active en fond plein accent.
class NumberedPager extends StatelessWidget {
  const NumberedPager({
    super.key,
    required this.currentPage,
    required this.lastPage,
    required this.onPageChange,
  });

  final int currentPage;
  final int lastPage;
  final ValueChanged<int> onPageChange;

  List<Object> _displayedPages() {
    const delta = 2;
    final range = <int>[];
    for (var i = 1; i <= lastPage; i++) {
      if (i == 1 || i == lastPage || (i >= currentPage - delta && i <= currentPage + delta)) {
        range.add(i);
      }
    }
    final withDots = <Object>[];
    int? last;
    for (final i in range) {
      if (last != null) {
        if (i - last == 2) {
          withDots.add(last + 1);
        } else if (i - last != 1) {
          withDots.add('...');
        }
      }
      withDots.add(i);
      last = i;
    }
    return withDots;
  }

  @override
  Widget build(BuildContext context) {
    if (lastPage <= 1) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        color: AppColors.panelBg,
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _ChevronButton(
            icon: Icons.chevron_left,
            onPressed: currentPage > 1 ? () => onPageChange(currentPage - 1) : null,
          ),
          for (final page in _displayedPages())
            if (page is int)
              _PageButton(
                label: '$page',
                active: page == currentPage,
                onPressed: () => onPageChange(page),
              )
            else
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 8),
                child: Text('…', style: TextStyle(color: AppColors.textMuted)),
              ),
          _ChevronButton(
            icon: Icons.chevron_right,
            onPressed: currentPage < lastPage ? () => onPageChange(currentPage + 1) : null,
          ),
        ],
      ),
    );
  }
}

class _ChevronButton extends StatelessWidget {
  const _ChevronButton({required this.icon, required this.onPressed});
  final IconData icon;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(icon, size: 20),
      color: onPressed != null ? AppColors.accentLight : AppColors.textMuted,
      onPressed: onPressed,
    );
  }
}

class _PageButton extends StatelessWidget {
  const _PageButton({required this.label, required this.active, required this.onPressed});
  final String label;
  final bool active;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: active ? AppColors.accent : Colors.transparent,
      borderRadius: BorderRadius.circular(6),
      child: InkWell(
        borderRadius: BorderRadius.circular(6),
        onTap: onPressed,
        child: Container(
          width: 34,
          height: 34,
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: active ? Colors.white : AppColors.accentLight,
            ),
          ),
        ),
      ),
    );
  }
}
