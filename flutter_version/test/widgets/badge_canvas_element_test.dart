import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/widgets/badge_canvas_element.dart';

/// Racine de test minimale : pas de MaterialApp/Scaffold (qui ajoutent des
/// paddings/safe-areas imprévisibles), juste un Stack plein écran — le
/// coin (0,0) du Positioned de l'élément coïncide alors exactement avec
/// l'origine globale de l'écran de test, ce qui rend les coordonnées des
/// poignées calculables à la main pour piloter `tester.dragFrom`.
Widget _harness(BadgeElement element, {required bool selected, double scale = 1}) {
  return Directionality(
    textDirection: TextDirection.ltr,
    child: Stack(
      children: [
        BadgeCanvasElement(
          element: element,
          scale: scale,
          selected: selected,
          onSelect: () {},
          onChanged: (_) {},
          child: const ColoredBox(color: Color(0xFFEEEEEE)),
        ),
      ],
    ),
  );
}

BadgeElement _textElement({double x = 50, double y = 50, double width = 100, double height = 60}) {
  return BadgeElement(
    id: 'e1',
    type: BadgeElementType.text,
    x: x,
    y: y,
    width: width,
    height: height,
  );
}

void main() {
  testWidgets('glisser la zone centrale déplace x/y sans changer width/height', (tester) async {
    final el = _textElement();
    await tester.pumpWidget(_harness(el, selected: false));

    // Centre de l'élément : (50+50, 50+30) = (100,80) — loin de tout bord.
    await tester.dragFrom(const Offset(100, 80), const Offset(30, 20));
    await tester.pump();

    expect(el.x, closeTo(80, 0.01));
    expect(el.y, closeTo(70, 0.01));
    expect(el.width, closeTo(100, 0.01));
    expect(el.height, closeTo(60, 0.01));
  });

  testWidgets('glisser la poignée coin bas-droite agrandit width/height sans déplacer x/y', (tester) async {
    final el = _textElement();
    await tester.pumpWidget(_harness(el, selected: true));
    await tester.pump();

    // Coin bas-droite global = (x+width, y+height) = (150,110).
    await tester.dragFrom(const Offset(150, 110), const Offset(20, 10));
    await tester.pump();

    expect(el.x, closeTo(50, 0.01));
    expect(el.y, closeTo(50, 0.01));
    expect(el.width, closeTo(120, 0.01));
    expect(el.height, closeTo(70, 0.01));
  });

  testWidgets('glisser la poignée coin haut-gauche déplace x/y et réduit width/height en sens opposé', (
    tester,
  ) async {
    final el = _textElement();
    await tester.pumpWidget(_harness(el, selected: true));
    await tester.pump();

    // Coin haut-gauche global = (x,y) = (50,50).
    await tester.dragFrom(const Offset(50, 50), const Offset(10, 5));
    await tester.pump();

    expect(el.x, closeTo(60, 0.01));
    expect(el.y, closeTo(55, 0.01));
    expect(el.width, closeTo(90, 0.01));
    expect(el.height, closeTo(55, 0.01));
  });

  testWidgets('le redimensionnement refuse de passer sous minSize', (tester) async {
    final el = _textElement(width: 20, height: 20);
    await tester.pumpWidget(_harness(el, selected: true));
    await tester.pump();

    // Coin bas-droite global = (70,70) ; on tente de réduire de 30px (minSize=16).
    await tester.dragFrom(const Offset(70, 70), const Offset(-30, -30));
    await tester.pump();

    expect(el.width, greaterThanOrEqualTo(16));
    expect(el.height, greaterThanOrEqualTo(16));
  });

  testWidgets(
    'glisser la poignée de BORD droite (milieu) n\'étire que la largeur, x/y/height inchangés',
    (tester) async {
      final el = _textElement();
      await tester.pumpWidget(_harness(el, selected: true));
      await tester.pump();

      // Bord droit milieu global = (x+width, y+height/2) = (150,80).
      await tester.dragFrom(const Offset(150, 80), const Offset(20, 15));
      await tester.pump();

      expect(el.x, closeTo(50, 0.01));
      expect(el.y, closeTo(50, 0.01));
      expect(el.width, closeTo(120, 0.01), reason: 'la largeur suit le glissement horizontal');
      expect(el.height, closeTo(60, 0.01), reason: 'un déplacement vertical du pointeur ne doit PAS affecter la hauteur sur cette poignée');
    },
  );

  testWidgets(
    'glisser la poignée de BORD gauche (milieu) déplace x et réduit la largeur en sens opposé, y/height inchangés',
    (tester) async {
      final el = _textElement();
      await tester.pumpWidget(_harness(el, selected: true));
      await tester.pump();

      // Bord gauche milieu global = (x, y+height/2) = (50,80).
      await tester.dragFrom(const Offset(50, 80), const Offset(10, 15));
      await tester.pump();

      expect(el.x, closeTo(60, 0.01));
      expect(el.width, closeTo(90, 0.01));
      expect(el.y, closeTo(50, 0.01));
      expect(el.height, closeTo(60, 0.01), reason: 'un déplacement vertical du pointeur ne doit PAS affecter la hauteur sur cette poignée');
    },
  );

  testWidgets(
    'glisser la poignée de BORD bas (milieu) n\'étire que la hauteur, x/y/width inchangés',
    (tester) async {
      final el = _textElement();
      await tester.pumpWidget(_harness(el, selected: true));
      await tester.pump();

      // Bord bas milieu global = (x+width/2, y+height) = (100,110).
      await tester.dragFrom(const Offset(100, 110), const Offset(15, 20));
      await tester.pump();

      expect(el.y, closeTo(50, 0.01));
      expect(el.height, closeTo(80, 0.01));
      expect(el.x, closeTo(50, 0.01), reason: 'un déplacement horizontal du pointeur ne doit PAS affecter la largeur sur cette poignée');
      expect(el.width, closeTo(100, 0.01));
    },
  );

  testWidgets(
    'glisser la poignée de BORD haut (milieu) déplace y et réduit la hauteur en sens opposé, x/width inchangés',
    (tester) async {
      final el = _textElement();
      await tester.pumpWidget(_harness(el, selected: true));
      await tester.pump();

      // Bord haut milieu global = (x+width/2, y) = (100,50).
      await tester.dragFrom(const Offset(100, 50), const Offset(15, 10));
      await tester.pump();

      expect(el.y, closeTo(60, 0.01));
      expect(el.height, closeTo(50, 0.01));
      expect(el.x, closeTo(50, 0.01), reason: 'un déplacement horizontal du pointeur ne doit PAS affecter la largeur sur cette poignée');
      expect(el.width, closeTo(100, 0.01));
    },
  );

  testWidgets('glisser la poignée de rotation depuis le nord vers l\'est fixe rotationDegrees à 90°', (
    tester,
  ) async {
    final el = _textElement();
    await tester.pumpWidget(_harness(el, selected: true));
    await tester.pump();

    // Centre global de l'élément = (100,80). Poignée de rotation au repos
    // (0°) = 28px au-dessus du centre = (100,22).
    const center = Offset(100, 80);
    const north = Offset(100, 22);
    final east = center + const Offset(58, 0);

    await tester.dragFrom(north, east - north);
    await tester.pump();

    expect(el.rotationDegrees, closeTo(90, 0.5));
  });

  testWidgets('une échelle d\'affichage différente de 1 est convertie correctement en unités modèle', (
    tester,
  ) async {
    final el = _textElement();
    await tester.pumpWidget(_harness(el, selected: false, scale: 0.5));

    // À l'échelle 0.5, le centre affiché est à (25+25,25+15)=(50,40).
    await tester.dragFrom(const Offset(50, 40), const Offset(15, 10));
    await tester.pump();

    // 15px affichés / 0.5 = 30 unités modèle.
    expect(el.x, closeTo(80, 0.01));
    expect(el.y, closeTo(70, 0.01));
  });
}
