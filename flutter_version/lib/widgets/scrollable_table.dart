import 'package:flutter/material.dart';

/// Enveloppe un tableau (DataTable, Table…) pour qu'il :
/// - occupe toute la largeur disponible (équivalent de `w-full` côté web) ;
/// - reste entièrement accessible quand la fenêtre est réduite, grâce à un
///   ascenseur horizontal TOUJOURS visible (sans lui, sur bureau, la partie
///   cachée n'était atteignable qu'au trackpad ou avec Maj + molette).
///
/// Constructeur par défaut : défilement horizontal seul, pour un tableau dont
/// la hauteur est gérée par la page (ex. dans une carte d'une page qui défile).
///
/// [ScrollableTable.both] : pour un tableau placé dans une zone de hauteur
/// bornée (Expanded d'un dialogue…). Le défilement vertical est alors interne,
/// et l'ascenseur horizontal reste collé au bas de la zone au lieu d'être
/// repoussé sous la dernière ligne.
class ScrollableTable extends StatefulWidget {
  const ScrollableTable({super.key, required this.child, this.padding})
    : vertical = false;

  const ScrollableTable.both({super.key, required this.child, this.padding})
    : vertical = true;

  final Widget child;
  final EdgeInsetsGeometry? padding;
  final bool vertical;

  @override
  State<ScrollableTable> createState() => _ScrollableTableState();
}

class _ScrollableTableState extends State<ScrollableTable> {
  static const double _barSpace = 12;

  final _horizontal = ScrollController();
  final _vertical = ScrollController();

  @override
  void dispose() {
    _horizontal.dispose();
    _vertical.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        Widget content = ConstrainedBox(
          constraints: BoxConstraints(minWidth: constraints.maxWidth),
          child: widget.padding == null
              ? widget.child
              : Padding(padding: widget.padding!, child: widget.child),
        );

        if (widget.vertical) {
          content = SizedBox(
            height: constraints.maxHeight - _barSpace,
            child: SingleChildScrollView(controller: _vertical, child: content),
          );
        }

        Widget table = Scrollbar(
          controller: _horizontal,
          thumbVisibility: true,
          trackVisibility: true,
          // Le défilement vertical imbriqué émet lui aussi des notifications :
          // on ne réagit qu'à celles du défilement horizontal (profondeur 0).
          notificationPredicate: (n) => n.depth == 0,
          child: SingleChildScrollView(
            controller: _horizontal,
            scrollDirection: Axis.horizontal,
            // Réserve la place de l'ascenseur pour qu'il ne recouvre pas la
            // dernière ligne du tableau.
            padding: const EdgeInsets.only(bottom: _barSpace),
            child: content,
          ),
        );

        if (widget.vertical) {
          // Placé à l'extérieur du défilement horizontal pour rester collé au
          // bord droit visible, quelle que soit la position horizontale.
          table = Scrollbar(
            controller: _vertical,
            thumbVisibility: true,
            notificationPredicate: (n) => n.depth == 1,
            child: table,
          );
        }

        return table;
      },
    );
  }
}
