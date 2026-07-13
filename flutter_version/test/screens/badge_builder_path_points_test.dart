import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';
import 'package:school_client_flutter/widgets/badge_canvas_element.dart';

/// Teste `insertPathPoint` (badge_builder_canvas.dart) en isolation — la
/// fonction pure derrière le mode "Modifier les points"
/// (badge_builder_property_panel.dart) : cliquer sur le tracé d'un
/// élément déjà posé (shapeKind: path) insère un nouveau point d'ancrage
/// au bon endroit, pour affiner une forme plus complexe qu'à la création.
void main() {
  BadgeElement square({bool closed = true}) => BadgeElement(
    id: 'p1',
    type: BadgeElementType.shape,
    x: 0,
    y: 0,
    width: 100,
    height: 100,
    shapeKind: BadgeShapeKind.path,
    pathClosed: closed,
    pathPoints: [
      BadgePathPoint(x: 0, y: 0),
      BadgePathPoint(x: 1, y: 0),
      BadgePathPoint(x: 1, y: 1),
      BadgePathPoint(x: 0, y: 1),
    ],
  );

  test(
    'cliquer au MILIEU d\'un segment droit insère un nouveau point juste après le premier point du segment',
    () {
      final el = square();
      // Segment (0,0)-(100,0) [coin haut-gauche → coin haut-droit, modèle
      // 0..100] — son milieu est (50,0).
      final inserted = insertPathPoint(el, const Offset(50, 0));

      expect(inserted, isTrue);
      expect(el.pathPoints, hasLength(5));
      final newPoint = el.pathPoints[1];
      expect(newPoint.x, closeTo(0.5, 0.02));
      expect(newPoint.y, closeTo(0, 0.02));
    },
  );

  test(
    'insère aussi sur le segment de FERMETURE (dernier point → premier point) d\'un tracé fermé',
    () {
      final el = square();
      // Segment de fermeture (0,100)→(0,0) [coin bas-gauche → coin haut-gauche] — milieu (0,50).
      final inserted = insertPathPoint(el, const Offset(0, 50));

      expect(inserted, isTrue);
      expect(el.pathPoints, hasLength(5));
      // Inséré à la toute fin de la liste (après le dernier point d'origine).
      final newPoint = el.pathPoints[4];
      expect(newPoint.x, closeTo(0, 0.02));
      expect(newPoint.y, closeTo(0.5, 0.02));
    },
  );

  test('un tracé OUVERT ne propose pas le segment de fermeture', () {
    final el = square(closed: false);
    // Même point que le test précédent (milieu du segment de fermeture),
    // mais le tracé est ouvert : ce segment n'existe pas.
    final inserted = insertPathPoint(el, const Offset(0, 50));

    expect(inserted, isFalse, reason: 'un tracé ouvert n\'a pas de segment entre le dernier et le premier point');
    expect(el.pathPoints, hasLength(4));
  });

  test('ignore un clic trop proche d\'une ancre EXISTANTE (pour laisser la poignée gérer un glissement à la place)', () {
    final el = square();
    // Très proche du premier point (0,0) — à l'intérieur de la tolérance par défaut (10).
    final inserted = insertPathPoint(el, const Offset(2, 1));

    expect(inserted, isFalse);
    expect(el.pathPoints, hasLength(4));
  });

  test('ignore un clic trop loin de tout segment', () {
    final el = square();
    // Centre du carré (50,50) — loin des 4 bords.
    final inserted = insertPathPoint(el, const Offset(50, 50));

    expect(inserted, isFalse);
    expect(el.pathPoints, hasLength(4));
  });

  test('n\'agit jamais sur une forme qui n\'est pas un tracé plume (shapeKind != path)', () {
    final el = BadgeElement(
      id: 'r1',
      type: BadgeElementType.shape,
      x: 0,
      y: 0,
      width: 100,
      height: 100,
      shapeKind: BadgeShapeKind.rectangle,
    );
    expect(insertPathPoint(el, const Offset(50, 0)), isFalse);
  });

  test('respecte une [tolerance] personnalisée', () {
    final el = square();
    // (50,5) est à 5 unités du segment (0,0)-(100,0) — hors tolérance par
    // défaut (10)? Non, 5 < 10, serait accepté ; on teste plutôt une
    // tolérance réduite à 2 pour le rejeter explicitement.
    expect(insertPathPoint(el, const Offset(50, 5), tolerance: 2), isFalse);
    expect(insertPathPoint(el, const Offset(50, 5), tolerance: 8), isTrue);
  });

  testWidgets(
    'dans le canevas : cliquer sur le tracé (mode "Modifier les points" actif) insère un point ; glisser une ancre existante la déplace',
    (tester) async {
      final el = square();
      final side = BadgeSide(elements: [el]);
      final layout = BadgeLayoutTemplate(id: 'lp', name: 'Test', recto: side);
      final changed = <BadgeElement>[];

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: StatefulBuilder(
            builder: (context, setState) => BadgeBuilderCanvas(
              layout: layout,
              side: side,
              selectedId: el.id,
              onSelect: (_) {},
              onElementChanged: (e) => setState(() => changed.add(e)),
              editingPathElementId: el.id,
            ),
          ),
        ),
      );
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;
      // Milieu du segment (0,0)-(100,0), modèle → écran.
      final clickPoint = Offset(rulerThickness + 50 * scale, rulerThickness + 0 * scale);

      await tester.tapAt(clickPoint);
      await tester.pump();

      expect(el.pathPoints, hasLength(5), reason: 'le clic sur le tracé doit avoir inséré un point');
      expect(changed, isNotEmpty, reason: 'onElementChanged doit être rappelé après insertion');
    },
  );

  testWidgets(
    'dans le canevas : glisser une poignée d\'ancre EXISTANTE déplace ce point, sans en insérer un nouveau',
    (tester) async {
      final el = square();
      final side = BadgeSide(elements: [el]);
      final layout = BadgeLayoutTemplate(id: 'lp2', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: StatefulBuilder(
            builder: (context, setState) => BadgeBuilderCanvas(
              layout: layout,
              side: side,
              selectedId: el.id,
              onSelect: (_) {},
              onElementChanged: (_) => setState(() {}),
              editingPathElementId: el.id,
            ),
          ),
        ),
      );
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;
      // Première ancre (0,0) modèle → écran.
      final anchorPoint = Offset(rulerThickness + 0 * scale, rulerThickness + 0 * scale);

      final gesture = await tester.startGesture(anchorPoint);
      await gesture.moveBy(const Offset(20, 10));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      expect(el.pathPoints, hasLength(4), reason: 'glisser une ancre existante ne doit jamais insérer de nouveau point');
      expect(el.pathPoints[0].x, greaterThan(0), reason: 'la première ancre doit avoir bougé');
      expect(el.pathPoints[0].y, greaterThan(0));
    },
  );

  testWidgets(
    'sans mode "Modifier les points" actif (editingPathElementId null), le canevas se comporte normalement — aucune poignée d\'ancre, aucun clic-insertion',
    (tester) async {
      final el = square();
      final side = BadgeSide(elements: [el]);
      final layout = BadgeLayoutTemplate(id: 'lp3', name: 'Test', recto: side);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: BadgeBuilderCanvas(
            layout: layout,
            side: side,
            selectedId: el.id,
            onSelect: (_) {},
            onElementChanged: (_) {},
          ),
        ),
      );

      // BadgeCanvasElement (glisser/redimensionner) reste présent et
      // normal ; aucune poignée d'ancre orange n'a été ajoutée.
      expect(find.byType(BadgeCanvasElement), findsOneWidget);
      expect(el.pathPoints, hasLength(4));
    },
  );
}
