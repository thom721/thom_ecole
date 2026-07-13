import 'dart:math' show atan2, pi;

import 'package:flutter/material.dart';

import '../models/badge_layout.dart';

/// Élément interactif du canevas de l'éditeur de badge — déplacement,
/// redimensionnement (poignées aux 4 coins, diagonal, PLUS 4 poignées de
/// bord au milieu de chaque côté, un seul axe à la fois — largeur seule à
/// gauche/droite, hauteur seule en haut/bas) et rotation (poignée
/// au-dessus du centre).
///
/// Utilise `Listener` (événements pointeur bruts) plutôt que
/// `GestureDetector.onPan*` : un `PanGestureRecognizer` exige une distance
/// minimale ("slop", ~36px) avant de délivrer le premier `onPanUpdate`, ce
/// qui rend un redimensionnement au pixel près sur une petite poignée
/// imprécis/collant au début du geste. `Listener` rapporte chaque
/// mouvement immédiatement, sans arène de gestes ni seuil.
///
/// Le `Positioned` englobant est volontairement plus grand que
/// [element] lui-même (marge [_padSide]/[_padTop]) : le hit-test par
/// défaut d'un `RenderBox` rejette tout point hors de sa PROPRE taille
/// avant même de tester ses enfants — `clipBehavior: Clip.none` permet le
/// débordement visuel mais PAS le débordement cliquable. Sans cette
/// marge, la poignée de rotation (au-dessus de la boîte) et les poignées
/// du bord bas/droit (exactement sur la limite, exclusive) resteraient
/// invisibles au hit-test malgré un rendu visuel correct — piégé une
/// première fois par les tests `flutter_test` de ce fichier.
///
/// Pas de portage des maths PySide (`TransformablePixmapItem`/
/// `HandleItem`, school_client/input.py) : rotation via un simple
/// `atan2` + `Transform.rotate` natif.
///
/// Simplification assumée : les poignées de redimensionnement/rotation
/// restent dans le repère NON pivoté de la boîte englobante (pas de
/// rotation visuelle des poignées elles-mêmes) — seul [child] pivote via
/// `Transform.rotate`. Prévisible à manipuler quel que soit l'angle
/// courant, au prix d'un détail visuel (les poignées ne "suivent" pas la
/// rotation), jugé secondaire pour un éditeur de badge.
///
/// [element] est modifié EN PLACE à chaque étape du geste (cohérent avec
/// le choix de mutabilité documenté dans `models/badge_layout.dart`), puis
/// [onChanged] est appelé pour que l'appelant déclenche un `setState`.
/// Les coordonnées de [element] sont en unités modèle (mêmes unités que le
/// canevas du badge, 1013×638 ou 638×1013) ; [scale] convertit vers les
/// pixels d'affichage réels du widget parent.
class BadgeCanvasElement extends StatefulWidget {
  const BadgeCanvasElement({
    super.key,
    required this.element,
    required this.scale,
    required this.selected,
    required this.onSelect,
    required this.onChanged,
    required this.child,
    this.minSize = 16,
  });

  final BadgeElement element;
  final double scale;
  final bool selected;
  final VoidCallback onSelect;
  final ValueChanged<BadgeElement> onChanged;
  final Widget child;
  final double minSize;

  @override
  State<BadgeCanvasElement> createState() => _BadgeCanvasElementState();
}

class _BadgeCanvasElementState extends State<BadgeCanvasElement> {
  static const _handleSize = 12.0;
  static const _rotationOffset = 28.0;
  static const _padSide = _handleSize;
  static const _padTop = _rotationOffset + _handleSize;

  @override
  Widget build(BuildContext context) {
    final el = widget.element;
    final width = el.width * widget.scale;
    final height = el.height * widget.scale;
    // La zone de déplacement est rétractée d'une demi-poignée sur chaque
    // bord du contenu : ses limites touchent celles des poignées de coin
    // sans jamais les chevaucher, pour qu'un seul Listener reçoive chaque
    // pointeur (deux Listener superposés recevraient chacun l'événement
    // indépendamment, sans mécanisme de résolution).
    final moveInset = (_handleSize / 2).clamp(0, width / 2).toDouble();
    final moveInsetV = (_handleSize / 2).clamp(0, height / 2).toDouble();

    return Positioned(
      left: el.x * widget.scale - _padSide,
      top: el.y * widget.scale - _padTop,
      width: width + 2 * _padSide,
      height: height + _padTop + _padSide,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned(
            left: _padSide,
            top: _padTop,
            width: width,
            height: height,
            child: IgnorePointer(
              child: Transform.rotate(
                angle: el.rotationDegrees * pi / 180,
                child: DecoratedBox(
                  decoration: widget.selected
                      ? BoxDecoration(
                          border: Border.all(
                            color: const Color(0xFF1A73E8),
                            width: 1.5,
                          ),
                        )
                      : const BoxDecoration(),
                  child: SizedBox(
                    width: width,
                    height: height,
                    child: widget.child,
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: _padSide + moveInset,
            top: _padTop + moveInsetV,
            width: width - 2 * moveInset,
            height: height - 2 * moveInsetV,
            child: Listener(
              behavior: HitTestBehavior.opaque,
              onPointerDown: (_) => widget.onSelect(),
              onPointerMove: (event) => _move(event.delta),
            ),
          ),
          if (widget.selected) ..._buildHandles(width, height),
        ],
      ),
    );
  }

  void _move(Offset delta) {
    final el = widget.element;
    el.x += delta.dx / widget.scale;
    el.y += delta.dy / widget.scale;
    widget.onChanged(el);
  }

  /// [fromLeft]/[fromTop] : `true`/`false` déplace le bord correspondant
  /// (gauche/droite, haut/bas) ; `null` laisse cet axe INCHANGÉ — utilisé
  /// par les poignées de bord (milieu), qui n'étirent qu'une seule
  /// dimension à la fois, contrairement aux poignées de coin (les 4
  /// premières, qui redimensionnent toujours les deux).
  void _resize(Offset delta, {bool? fromLeft, bool? fromTop}) {
    final el = widget.element;
    final dx = delta.dx / widget.scale;
    final dy = delta.dy / widget.scale;

    var newX = el.x;
    var newY = el.y;
    var newW = el.width;
    var newH = el.height;
    if (fromLeft == true) {
      newX += dx;
      newW -= dx;
    } else if (fromLeft == false) {
      newW += dx;
    }
    if (fromTop == true) {
      newY += dy;
      newH -= dy;
    } else if (fromTop == false) {
      newH += dy;
    }
    if (newW < widget.minSize || newH < widget.minSize) return;

    el.x = newX;
    el.y = newY;
    el.width = newW;
    el.height = newH;
    widget.onChanged(el);
  }

  /// [localPositionInHandle] est fournie par `PointerEvent.localPosition`
  /// dans le repère propre de la poignée (taille `_handleSize`) ;
  /// [handleTopLeftInContent] est la position (connue statiquement) du
  /// coin haut-gauche de cette poignée dans le repère du CONTENU
  /// (0,0)=coin haut-gauche de [element], indépendant du padding d'affichage.
  void _rotate(
    Offset localPositionInHandle,
    double width,
    double height,
    Offset handleTopLeftInContent,
  ) {
    final localInContent = handleTopLeftInContent + localPositionInHandle;
    final center = Offset(width / 2, height / 2);
    final vector = localInContent - center;
    // Une poignée au-dessus du centre correspond à 0° -> décalage de +90°
    // par rapport à atan2 (qui prend l'axe des x comme référence).
    final angleDeg = atan2(vector.dy, vector.dx) * 180 / pi + 90;
    widget.element.rotationDegrees = angleDeg;
    widget.onChanged(widget.element);
  }

  List<Widget> _buildHandles(double width, double height) {
    const handleSize = _handleSize;
    // Poignées de BORD (milieu d'un côté) : plus étroites/allongées dans
    // leur axe d'étirement qu'un cercle de coin, pour se distinguer
    // visuellement (convention courante : coin = redimensionnement
    // diagonal, bord = redimensionnement d'un seul axe).
    const edgeHandleLength = handleSize * 1.6;

    Widget resizeHandle({
      required double contentLeft,
      required double contentTop,
      bool? fromLeft,
      bool? fromTop,
      double? handleWidth,
      double? handleHeight,
    }) {
      final w = handleWidth ?? handleSize;
      final h = handleHeight ?? handleSize;
      return Positioned(
        left: _padSide + contentLeft - w / 2,
        top: _padTop + contentTop - h / 2,
        width: w,
        height: h,
        child: Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (_) => widget.onSelect(),
          onPointerMove: (event) =>
              _resize(event.delta, fromLeft: fromLeft, fromTop: fromTop),
          child: Container(
            decoration: w == h
                ? BoxDecoration(
                    color: Colors.white,
                    border: Border.all(
                      color: const Color(0xFF1A73E8),
                      width: 1.5,
                    ),
                    shape: BoxShape.circle,
                  )
                : BoxDecoration(
                    color: Colors.white,
                    border: Border.all(
                      color: const Color(0xFF1A73E8),
                      width: 1.5,
                    ),
                    borderRadius: BorderRadius.circular(3),
                  ),
          ),
        ),
      );
    }

    final rotationHandleTopLeftInContent = Offset(
      width / 2 - handleSize / 2,
      -_rotationOffset,
    );
    return [
      // Coins — redimensionnement diagonal (largeur ET hauteur).
      resizeHandle(
        contentLeft: 0,
        contentTop: 0,
        fromLeft: true,
        fromTop: true,
      ),
      resizeHandle(
        contentLeft: width,
        contentTop: 0,
        fromLeft: false,
        fromTop: true,
      ),
      resizeHandle(
        contentLeft: 0,
        contentTop: height,
        fromLeft: true,
        fromTop: false,
      ),
      resizeHandle(
        contentLeft: width,
        contentTop: height,
        fromLeft: false,
        fromTop: false,
      ),
      // Bords — redimensionnement d'un seul axe (`fromLeft`/`fromTop` à
      // `null` sur l'axe non concerné, voir la doc de [_resize]).
      resizeHandle(
        contentLeft: width / 2,
        contentTop: 0,
        fromTop: true,
        handleWidth: edgeHandleLength,
        handleHeight: handleSize,
      ),
      resizeHandle(
        contentLeft: width / 2,
        contentTop: height,
        fromTop: false,
        handleWidth: edgeHandleLength,
        handleHeight: handleSize,
      ),
      resizeHandle(
        contentLeft: 0,
        contentTop: height / 2,
        fromLeft: true,
        handleWidth: handleSize,
        handleHeight: edgeHandleLength,
      ),
      resizeHandle(
        contentLeft: width,
        contentTop: height / 2,
        fromLeft: false,
        handleWidth: handleSize,
        handleHeight: edgeHandleLength,
      ),
      Positioned(
        left: _padSide + rotationHandleTopLeftInContent.dx,
        top: _padTop + rotationHandleTopLeftInContent.dy,
        width: handleSize,
        height: handleSize,
        child: Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (_) => widget.onSelect(),
          onPointerMove: (event) => _rotate(
            event.localPosition,
            width,
            height,
            rotationHandleTopLeftInContent,
          ),
          child: const DecoratedBox(
            decoration: BoxDecoration(
              color: Color(0xFF1A73E8),
              shape: BoxShape.circle,
            ),
          ),
        ),
      ),
    ];
  }
}
