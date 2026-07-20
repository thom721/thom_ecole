import 'package:flutter/gestures.dart' show kSecondaryButton;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show LogicalKeyboardKey;
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
    'cliquer au MILIEU d\'un segment DROIT insère un simple coin (aucune poignée parasite) juste après le premier point du segment',
    () {
      final el = square();
      // Segment (0,0)-(100,0) [coin haut-gauche → coin haut-droit, modèle
      // 0..100] — son milieu est (50,0).
      final insertedAt = insertPathPoint(el, const Offset(50, 0));

      expect(insertedAt, 1);
      expect(el.pathPoints, hasLength(5));
      final newPoint = el.pathPoints[1];
      expect(newPoint.x, closeTo(0.5, 0.02));
      expect(newPoint.y, closeTo(0, 0.02));
      expect(newPoint.outX, isNull, reason: 'un segment droit ne doit jamais recevoir de poignée parasite');
      expect(newPoint.inX, isNull);
      expect(el.pathPoints[0].outX, isNull, reason: 'les points d\'origine, sans poignée, ne doivent pas en gagner une');
      expect(el.pathPoints[2].inX, isNull);
    },
  );

  test(
    'cliquer sur un segment COURBE (avec de vraies poignées) subdivise la courbe par De Casteljau — le nouveau point hérite de poignées, la forme d\'origine reste exactement préservée',
    () {
      // Un segment unique de (0,0) à (100,0), courbé vers le bas via des
      // poignées symétriques — un simple carré n'a que des coins, donc ce
      // fixture dédié a un VRAI arc de cercle à préserver.
      final el = BadgeElement(
        id: 'c1',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 100,
        height: 100,
        shapeKind: BadgeShapeKind.path,
        pathClosed: false,
        pathPoints: [
          BadgePathPoint(x: 0, y: 0, outX: 0.2, outY: 0.3),
          BadgePathPoint(x: 1, y: 0, inX: -0.2, inY: 0.3),
        ],
      );

      // Point exactement sur la courbe à t=0.5 (calculé par la même
      // formule cubique que insertPathPoint/_cubicPointAt) — pas une
      // approximation du milieu géométrique de la corde, qui ne tomberait
      // pas exactement sur une courbe bombée.
      final p0 = Offset(0, 0);
      final p1 = Offset(100, 0);
      final cp1 = Offset(20, 30);
      final cp2 = Offset(80, 30);
      Offset cubicAt(double t) {
        final mt = 1 - t;
        final a = mt * mt * mt, b = 3 * mt * mt * t, c = 3 * mt * t * t, d = t * t * t;
        return Offset(
          a * p0.dx + b * cp1.dx + c * cp2.dx + d * p1.dx,
          a * p0.dy + b * cp1.dy + c * cp2.dy + d * p1.dy,
        );
      }

      final target = cubicAt(0.5);
      final insertedAt = insertPathPoint(el, target);

      expect(insertedAt, 1);
      expect(el.pathPoints, hasLength(3));
      final newPoint = el.pathPoints[1];
      expect(newPoint.x, closeTo(target.dx / 100, 0.02));
      expect(newPoint.y, closeTo(target.dy / 100, 0.02));
      expect(newPoint.outX, isNotNull, reason: 'un segment courbe doit donner de vraies poignées au nouveau point');
      expect(newPoint.inX, isNotNull);

      // La courbe d'origine doit rester EXACTEMENT la même après
      // subdivision — même position qu'avant à n'importe quel t, en
      // reconstruisant les deux moitiés avec leurs nouvelles poignées.
      final first = el.pathPoints[0];
      final firstCp1 = Offset(100 * (first.x + first.outX!), 100 * (first.y + first.outY!));
      final firstCp2 = Offset(100 * (newPoint.x + newPoint.inX!), 100 * (newPoint.y + newPoint.inY!));
      Offset cubicAtOnFirstHalf(double t) {
        final a0 = Offset(100 * first.x, 100 * first.y);
        final a1 = Offset(100 * newPoint.x, 100 * newPoint.y);
        final mt = 1 - t;
        final a = mt * mt * mt, b = 3 * mt * mt * t, c = 3 * mt * t * t, d = t * t * t;
        return Offset(
          a * a0.dx + b * firstCp1.dx + c * firstCp2.dx + d * a1.dx,
          a * a0.dy + b * firstCp1.dy + c * firstCp2.dy + d * a1.dy,
        );
      }

      // t=0.25 de la courbe d'origine == t=0.5 de la première moitié (la
      // subdivision a coupé exactement à t=0.5).
      final expected = cubicAt(0.25);
      final actual = cubicAtOnFirstHalf(0.5);
      expect(actual.dx, closeTo(expected.dx, 0.5));
      expect(actual.dy, closeTo(expected.dy, 0.5));
    },
  );

  test(
    'insère aussi sur le segment de FERMETURE (dernier point → premier point) d\'un tracé fermé',
    () {
      final el = square();
      // Segment de fermeture (0,100)→(0,0) [coin bas-gauche → coin haut-gauche] — milieu (0,50).
      final insertedAt = insertPathPoint(el, const Offset(0, 50));

      expect(insertedAt, 4);
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
    final insertedAt = insertPathPoint(el, const Offset(0, 50));

    expect(insertedAt, isNull, reason: 'un tracé ouvert n\'a pas de segment entre le dernier et le premier point');
    expect(el.pathPoints, hasLength(4));
  });

  test('ignore un clic trop proche d\'une ancre EXISTANTE (pour laisser la poignée gérer un glissement à la place)', () {
    final el = square();
    // Très proche du premier point (0,0) — à l'intérieur de la tolérance par défaut (10).
    final insertedAt = insertPathPoint(el, const Offset(2, 1));

    expect(insertedAt, isNull);
    expect(el.pathPoints, hasLength(4));
  });

  test('ignore un clic trop loin de tout segment', () {
    final el = square();
    // Centre du carré (50,50) — loin des 4 bords.
    final insertedAt = insertPathPoint(el, const Offset(50, 50));

    expect(insertedAt, isNull);
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
    expect(insertPathPoint(el, const Offset(50, 0)), isNull);
  });

  test('respecte une [tolerance] personnalisée', () {
    final el = square();
    // (50,5) est à 5 unités du segment (0,0)-(100,0) — hors tolérance par
    // défaut (10)? Non, 5 < 10, serait accepté ; on teste plutôt une
    // tolérance réduite à 2 pour le rejeter explicitement.
    expect(insertPathPoint(el, const Offset(50, 5), tolerance: 2), isNull);
    expect(insertPathPoint(el, const Offset(50, 5), tolerance: 8), isNotNull);
  });

  test('deletePathPoint supprime le point à l\'index donné', () {
    final el = square();
    expect(deletePathPoint(el, 1), isTrue);
    expect(el.pathPoints, hasLength(3));
    expect(el.pathPoints[0].x, closeTo(0, 1e-9));
    expect(el.pathPoints[1].x, closeTo(1, 1e-9), reason: 'le point à l\'ancien index 2 devient le nouvel index 1');
  });

  test('deletePathPoint refuse de descendre sous 2 points', () {
    final el = square();
    deletePathPoint(el, 0);
    deletePathPoint(el, 0);
    expect(el.pathPoints, hasLength(2));
    expect(deletePathPoint(el, 0), isFalse, reason: 'un tracé à 2 points est le minimum valide');
    expect(el.pathPoints, hasLength(2));
  });

  test('deletePathPoint ignore un index hors bornes', () {
    final el = square();
    expect(deletePathPoint(el, -1), isFalse);
    expect(deletePathPoint(el, 99), isFalse);
    expect(el.pathPoints, hasLength(4));
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

  testWidgets('dans le canevas : Ctrl + clic droit sur une ancre EXISTANTE la supprime, comme dans Illustrator', (tester) async {
    final el = square();
    final side = BadgeSide(elements: [el]);
    final layout = BadgeLayoutTemplate(id: 'lp4', name: 'Test', recto: side);

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

    await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
    final gesture = await tester.startGesture(anchorPoint, buttons: kSecondaryButton);
    await gesture.up();
    await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);
    await tester.pump();

    expect(el.pathPoints, hasLength(3), reason: 'Ctrl + clic droit sur une ancre doit la supprimer');
  });

  testWidgets('dans le canevas : un clic droit SANS Ctrl sur une ancre ne supprime rien', (tester) async {
    final el = square();
    final side = BadgeSide(elements: [el]);
    final layout = BadgeLayoutTemplate(id: 'lp5', name: 'Test', recto: side);

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
    final anchorPoint = Offset(rulerThickness + 0 * scale, rulerThickness + 0 * scale);

    final gesture = await tester.startGesture(anchorPoint, buttons: kSecondaryButton);
    await gesture.up();
    await tester.pump();

    expect(el.pathPoints, hasLength(4), reason: 'un clic droit seul (sans Ctrl) ne doit rien supprimer');
  });
}
