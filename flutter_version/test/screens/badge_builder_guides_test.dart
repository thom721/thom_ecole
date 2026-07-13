import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';

/// Teste l'intégration règles↔repères (guides) de `BadgeBuilderCanvas` —
/// [BadgeBuilderCanvas] ne possède aucun état propre pour ces repères
/// (comme l'outil plume, dont l'état vit dans badge_builder_screen.dart),
/// donc ce harnais reproduit ICI, à l'identique, la logique de
/// `_BadgeBuilderScreenState::_onGuideCreateStart`/`_onGuideMoveStart`/
/// `_onGuideDragUpdate`/`_onGuideDragEnd` — si cette logique change côté
/// écran, la garder synchronisée ici teste alors le VRAI contrat
/// d'intégration (quelles valeurs le canevas transmet), pas une
/// simulation déconnectée.
class _GuideDragState {
  int? index;
  bool vertical = false;
}

Widget _guideHarness(BadgeSide side, BadgeLayoutTemplate layout) {
  final drag = _GuideDragState();
  return Directionality(
    textDirection: TextDirection.ltr,
    child: StatefulBuilder(
      builder: (context, setState) => BadgeBuilderCanvas(
        layout: layout,
        side: side,
        selectedId: null,
        onSelect: (_) {},
        onElementChanged: (_) {},
        onGuideCreateStart: (vertical, initial) => setState(() {
          final list = vertical ? side.guidesX : side.guidesY;
          list.add(initial);
          drag.vertical = vertical;
          drag.index = list.length - 1;
        }),
        onGuideMoveStart: (vertical, index) => setState(() {
          drag.vertical = vertical;
          drag.index = index;
        }),
        onGuideDragUpdate: (delta) => setState(() {
          final idx = drag.index;
          if (idx == null) return;
          final list = drag.vertical ? side.guidesX : side.guidesY;
          if (idx < list.length) list[idx] += delta;
        }),
        onGuideDragEnd: () => setState(() {
          final idx = drag.index;
          drag.index = null;
          if (idx == null) return;
          final list = drag.vertical ? side.guidesX : side.guidesY;
          final extent = drag.vertical ? layout.canvasWidth : layout.canvasHeight;
          if (idx < list.length && (list[idx] < 0 || list[idx] > extent)) {
            list.removeAt(idx);
          }
        }),
      ),
    ),
  );
}

void main() {
  testWidgets(
    'glisser depuis la règle HORIZONTALE crée un nouveau repère (guidesY) à la position modèle attendue',
    (tester) async {
      final side = BadgeSide();
      final layout = BadgeLayoutTemplate(id: 'g1', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_guideHarness(side, layout));
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;

      const rulerPoint = Offset(100, 10);
      const dragDelta = Offset(0, 100);
      await tester.dragFrom(rulerPoint, dragDelta);
      await tester.pump();

      expect(side.guidesY, hasLength(1));
      final expected = (rulerPoint.dy - rulerThickness) / scale + dragDelta.dy / scale;
      expect(side.guidesY.single, closeTo(expected, 0.5));
      expect(side.guidesX, isEmpty, reason: 'un glissement depuis la règle horizontale ne doit créer qu\'un repère HORIZONTAL');
    },
  );

  testWidgets(
    'glisser depuis la règle VERTICALE crée un nouveau repère (guidesX) à la position modèle attendue',
    (tester) async {
      final side = BadgeSide();
      final layout = BadgeLayoutTemplate(id: 'g2', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_guideHarness(side, layout));
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;

      const rulerPoint = Offset(10, 100);
      const dragDelta = Offset(90, 0);
      await tester.dragFrom(rulerPoint, dragDelta);
      await tester.pump();

      expect(side.guidesX, hasLength(1));
      final expected = (rulerPoint.dx - rulerThickness) / scale + dragDelta.dx / scale;
      expect(side.guidesX.single, closeTo(expected, 0.5));
      expect(side.guidesY, isEmpty, reason: 'un glissement depuis la règle verticale ne doit créer qu\'un repère VERTICAL');
    },
  );

  testWidgets(
    'glisser un repère EXISTANT (directement dans le canevas) le repositionne, sans en créer un nouveau',
    (tester) async {
      final side = BadgeSide(guidesY: [200]);
      final layout = BadgeLayoutTemplate(id: 'g3', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_guideHarness(side, layout));
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;

      final guideGlobalY = rulerThickness + 200 * scale;
      final point = Offset(200, guideGlobalY);
      const dragDelta = Offset(0, 50);
      await tester.dragFrom(point, dragDelta);
      await tester.pump();

      expect(side.guidesY, hasLength(1), reason: 'un repère déplacé ne doit jamais créer de doublon');
      final expected = 200 + dragDelta.dy / scale;
      expect(side.guidesY.single, closeTo(expected, 0.5));
    },
  );

  testWidgets(
    'relâcher un repère HORS des limites du canevas le SUPPRIME (glissé en arrière sur la règle) — convention Adobe/Figma',
    (tester) async {
      final side = BadgeSide(guidesY: [50]);
      final layout = BadgeLayoutTemplate(id: 'g4', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_guideHarness(side, layout));
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;

      final guideGlobalY = rulerThickness + 50 * scale;
      final point = Offset(200, guideGlobalY);
      // Glissement bien au-delà du bord supérieur — position modèle finale négative.
      final dragDelta = Offset(0, -(guideGlobalY + 100));
      await tester.dragFrom(point, dragDelta);
      await tester.pump();

      expect(side.guidesY, isEmpty, reason: 'un repère relâché hors du canevas doit être supprimé, pas laissé à une position invalide');
    },
  );

  testWidgets(
    'un repère relâché À L\'INTÉRIEUR des limites du canevas est conservé',
    (tester) async {
      final side = BadgeSide();
      final layout = BadgeLayoutTemplate(id: 'g5', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(_guideHarness(side, layout));
      await tester.pump();

      const rulerPoint = Offset(100, 10);
      const dragDelta = Offset(0, 150);
      await tester.dragFrom(rulerPoint, dragDelta);
      await tester.pump();

      expect(side.guidesY, hasLength(1));
      expect(side.guidesY.single, greaterThan(0));
      expect(side.guidesY.single, lessThan(kBadgeLandscapeHeight));
    },
  );
}
