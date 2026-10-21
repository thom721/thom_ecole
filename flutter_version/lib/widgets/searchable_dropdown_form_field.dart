import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Remplaçant direct de DropdownButtonFormField (mêmes paramètres :
/// initialValue, items, onChanged, decoration, isDense, isExpanded) dont le
/// menu ouvert affiche un champ de recherche au-dessus des options — pour
/// retrouver vite un cours, une classe, un professeur… dans une longue liste.
///
/// La recherche ignore la casse et les accents ("geometrie" trouve
/// "Géometrie"). Elle n'apparaît qu'à partir de [_searchThreshold] options :
/// sur Oui/Non, M/F… elle ne ferait qu'encombrer le menu.
///
/// Comme DropdownButtonFormField, [initialValue] n'est lu qu'à la création
/// du widget : les écrans existants changent sa Key pour forcer un remount
/// quand la valeur arrive en asynchrone, ce comportement est donc conservé.
class SearchableDropdownFormField<T> extends StatefulWidget {
  const SearchableDropdownFormField({
    super.key,
    required this.items,
    required this.onChanged,
    this.initialValue,
    this.decoration = const InputDecoration(),
    this.isDense = false,
    this.isExpanded = false,
  });

  final List<DropdownMenuItem<T>>? items;
  final ValueChanged<T?>? onChanged;
  final T? initialValue;
  final InputDecoration decoration;
  final bool isDense;

  /// Conservé pour la compatibilité d'API : le texte sélectionné est de
  /// toute façon tronqué (…) à la largeur du champ.
  final bool isExpanded;

  @override
  State<SearchableDropdownFormField<T>> createState() => _SearchableDropdownFormFieldState<T>();
}

const int _searchThreshold = 7;
const double _itemHeight = 44;
const double _searchHeight = 56;

class _SearchableDropdownFormFieldState<T> extends State<SearchableDropdownFormField<T>> {
  late T? _value = widget.initialValue;
  bool _open = false;

  List<DropdownMenuItem<T>> get _items => widget.items ?? const [];
  bool get _enabled => widget.onChanged != null && _items.isNotEmpty;

  DropdownMenuItem<T>? get _selectedItem {
    for (final item in _items) {
      if (item.value == _value) return item;
    }
    return null;
  }

  Future<void> _openMenu() async {
    if (!_enabled || _open) return;
    final box = context.findRenderObject() as RenderBox?;
    if (box == null || !box.hasSize) return;
    final navigator = Navigator.of(context);
    final overlayBox = navigator.overlay!.context.findRenderObject() as RenderBox;
    final rect = box.localToGlobal(Offset.zero, ancestor: overlayBox) & box.size;

    setState(() => _open = true);
    final result = await navigator.push(
      _SearchMenuRoute<T>(
        anchor: rect,
        items: _items,
        selectedValue: _value,
        barrierLabel: MaterialLocalizations.of(context).modalBarrierDismissLabel,
        capturedThemes: InheritedTheme.capture(from: context, to: navigator.context),
      ),
    );
    if (!mounted) return;
    setState(() => _open = false);
    if (result == null) return; // menu fermé sans choix
    setState(() => _value = result.value);
    widget.onChanged?.call(result.value);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final selected = _selectedItem;
    final decoration = widget.decoration
        .applyDefaults(theme.inputDecorationTheme)
        .copyWith(
          enabled: _enabled,
          isDense: widget.decoration.isDense ?? (widget.isDense ? true : null),
          suffixIcon: widget.decoration.suffixIcon ?? const Icon(Icons.arrow_drop_down),
        );

    return Semantics(
      button: true,
      enabled: _enabled,
      child: InkWell(
        onTap: _enabled ? _openMenu : null,
        canRequestFocus: _enabled,
        borderRadius: BorderRadius.circular(8),
        child: InputDecorator(
          decoration: decoration,
          isFocused: _open,
          isEmpty: selected == null,
          child: selected == null
              ? const SizedBox.shrink()
              : DefaultTextStyle.merge(
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: _enabled ? null : theme.disabledColor,
                  ),
                  child: selected.child,
                ),
        ),
      ),
    );
  }
}

/// Résultat du menu : distingue « fermé sans choix » (null) de « l'option
/// de valeur null a été choisie » (ex. « Tous les niveaux »).
class _Choice<T> {
  const _Choice(this.value);
  final T? value;
}

String _labelOf(DropdownMenuItem<Object?> item) {
  final child = item.child;
  if (child is Text) return child.data ?? child.textSpan?.toPlainText() ?? '';
  return item.value?.toString() ?? '';
}

const _accents = {
  'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a', 'ã': 'a',
  'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
  'î': 'i', 'ï': 'i', 'í': 'i', 'ì': 'i',
  'ô': 'o', 'ö': 'o', 'ó': 'o', 'ò': 'o', 'õ': 'o',
  'ù': 'u', 'û': 'u', 'ü': 'u', 'ú': 'u',
  'ç': 'c', 'ñ': 'n', 'ÿ': 'y',
};

String _normalize(String s) {
  final lower = s.toLowerCase();
  final buffer = StringBuffer();
  for (final rune in lower.runes) {
    final ch = String.fromCharCode(rune);
    buffer.write(_accents[ch] ?? ch);
  }
  return buffer.toString().trim();
}

class _SearchMenuRoute<T> extends PopupRoute<_Choice<T>> {
  _SearchMenuRoute({
    required this.anchor,
    required this.items,
    required this.selectedValue,
    required this.barrierLabel,
    required this.capturedThemes,
  });

  final Rect anchor;
  final List<DropdownMenuItem<T>> items;
  final T? selectedValue;
  final CapturedThemes capturedThemes;

  @override
  final String barrierLabel;

  @override
  Color? get barrierColor => null;

  @override
  bool get barrierDismissible => true;

  @override
  Duration get transitionDuration => const Duration(milliseconds: 120);

  @override
  Widget buildPage(BuildContext context, Animation<double> animation, Animation<double> secondaryAnimation) {
    return FadeTransition(
      opacity: animation,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final screen = constraints.biggest;
          final padding = MediaQuery.paddingOf(context);
          final keyboard = MediaQuery.viewInsetsOf(context).bottom;
          const margin = 8.0;

          final spaceBelow = screen.height - keyboard - padding.bottom - anchor.bottom - margin;
          final spaceAbove = anchor.top - padding.top - margin;
          final withSearch = items.length >= _searchThreshold;
          final wanted = items.length * _itemHeight + (withSearch ? _searchHeight : 0) + 16;
          final below = spaceBelow >= wanted.clamp(0, 320) || spaceBelow >= spaceAbove;
          final maxHeight = (below ? spaceBelow : spaceAbove).clamp(120.0, 420.0);

          final width = anchor.width.clamp(220.0, screen.width - 2 * margin);
          final left = anchor.left.clamp(margin, screen.width - width - margin);

          return Stack(
            children: [
              Positioned(
                left: left,
                width: width,
                top: below ? anchor.bottom + 4 : null,
                bottom: below ? null : screen.height - anchor.top + 4,
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxHeight: maxHeight),
                  child: capturedThemes.wrap(
                    _SearchMenu<T>(
                      items: items,
                      selectedValue: selectedValue,
                      withSearch: withSearch,
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _SearchMenu<T> extends StatefulWidget {
  const _SearchMenu({required this.items, required this.selectedValue, required this.withSearch});

  final List<DropdownMenuItem<T>> items;
  final T? selectedValue;
  final bool withSearch;

  @override
  State<_SearchMenu<T>> createState() => _SearchMenuState<T>();
}

class _SearchMenuState<T> extends State<_SearchMenu<T>> {
  late final List<String> _labels = [for (final item in widget.items) _normalize(_labelOf(item))];
  late List<int> _visible = List.generate(widget.items.length, (i) => i);
  late final ScrollController _scroll;
  // Option surlignée au clavier (flèches haut/bas), indice dans _visible.
  int _highlight = -1;

  @override
  void initState() {
    super.initState();
    final selectedIndex = widget.items.indexWhere((i) => i.value == widget.selectedValue);
    _highlight = selectedIndex;
    // Ouvre la liste positionnée sur l'option déjà choisie.
    _scroll = ScrollController(
      initialScrollOffset: selectedIndex > 2 ? (selectedIndex - 2) * _itemHeight : 0,
    );
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _filter(String query) {
    final q = _normalize(query);
    setState(() {
      _visible = [
        for (var i = 0; i < widget.items.length; i++)
          if (q.isEmpty || _labels[i].contains(q)) i,
      ];
      _highlight = _visible.isEmpty ? -1 : 0;
    });
    if (_scroll.hasClients) _scroll.jumpTo(0);
  }

  void _select(int itemIndex) {
    final item = widget.items[itemIndex];
    if (!item.enabled) return;
    item.onTap?.call();
    Navigator.of(context).pop(_Choice<T>(item.value));
  }

  void _moveHighlight(int delta) {
    if (_visible.isEmpty) return;
    final current = _visible.indexOf(_highlight);
    final next = ((current < 0 ? (delta > 0 ? -1 : 0) : current) + delta).clamp(0, _visible.length - 1);
    setState(() => _highlight = _visible[next]);
    if (_scroll.hasClients) {
      final top = next * _itemHeight;
      final viewport = _scroll.position.viewportDimension;
      if (top < _scroll.offset) {
        _scroll.jumpTo(top);
      } else if (top + _itemHeight > _scroll.offset + viewport) {
        _scroll.jumpTo(top + _itemHeight - viewport);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return CallbackShortcuts(
      bindings: {
        const SingleActivator(LogicalKeyboardKey.arrowDown): () => _moveHighlight(1),
        const SingleActivator(LogicalKeyboardKey.arrowUp): () => _moveHighlight(-1),
        const SingleActivator(LogicalKeyboardKey.enter): () {
          if (_visible.contains(_highlight)) {
            _select(_highlight);
          } else if (_visible.isNotEmpty) {
            _select(_visible.first);
          }
        },
        const SingleActivator(LogicalKeyboardKey.escape): () => Navigator.of(context).pop(),
      },
      child: Focus(
        autofocus: !widget.withSearch,
        child: Material(
          elevation: 8,
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(10),
          clipBehavior: Clip.antiAlias,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (widget.withSearch) ...[
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 8, 8, 4),
                  child: TextField(
                    autofocus: true,
                    onChanged: _filter,
                    textInputAction: TextInputAction.search,
                    decoration: const InputDecoration(
                      hintText: 'Rechercher…',
                      prefixIcon: Icon(Icons.search, size: 18),
                      isDense: true,
                    ),
                  ),
                ),
                Divider(height: 1, color: theme.dividerColor.withValues(alpha: 0.3)),
              ],
              Flexible(
                child: _visible.isEmpty
                    ? Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          'Aucun résultat',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: theme.hintColor),
                        ),
                      )
                    : Scrollbar(
                        controller: _scroll,
                        thumbVisibility: true,
                        child: ListView.builder(
                          controller: _scroll,
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          shrinkWrap: true,
                          itemExtent: _itemHeight,
                          itemCount: _visible.length,
                          itemBuilder: (context, i) {
                            final index = _visible[i];
                            final item = widget.items[index];
                            final isSelected = item.value == widget.selectedValue;
                            final isHighlighted = index == _highlight;
                            return Material(
                              color: isSelected
                                  ? scheme.primary.withValues(alpha: 0.10)
                                  : isHighlighted
                                      ? scheme.onSurface.withValues(alpha: 0.06)
                                      : Colors.transparent,
                              child: InkWell(
                                onTap: item.enabled ? () => _select(index) : null,
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 16),
                                  child: Align(
                                    alignment: AlignmentDirectional.centerStart,
                                    child: DefaultTextStyle.merge(
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: (theme.textTheme.titleMedium ?? const TextStyle()).copyWith(
                                        fontWeight: isSelected ? FontWeight.w600 : null,
                                        color: item.enabled ? null : theme.disabledColor,
                                      ),
                                      child: item.child,
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
