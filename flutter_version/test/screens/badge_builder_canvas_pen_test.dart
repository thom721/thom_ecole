import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';

void main() {
  testWidgets('l\'outil plume convertit les positions/deltas d\'affichage en coordonnées modèle', (tester) async {
    final side = BadgeSide();
    final layout = BadgeLayoutTemplate(id: 'l1', name: 'Test', recto: side);

    final downs = <Offset>[];
    final drags = <Offset>[];

    tester.view.physicalSize = const Size(400, 400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(
      Directionality(
        textDirection: TextDirection.ltr,
        child: BadgeBuilderCanvas(
          layout: layout,
          side: side,
          selectedId: null,
          onSelect: (_) {},
          onElementChanged: (_) {},
          penActive: true,
          penDraft: const [],
          onPenPointerDown: downs.add,
          onPenDrag: drags.add,
        ),
      ),
    );

    // Même repère que test/screens/badge_builder_canvas_test.dart : la
    // zone canevas commence après les règles (20px), à l'échelle du reste
    // de la largeur de test disponible (400) sur les 1013 unités modèle.
    const rulerThickness = 20.0;
    const canvasOrigin = Offset(rulerThickness, rulerThickness);
    final canvasWidth = 400 - rulerThickness;
    final scale = canvasWidth / kBadgeLandscapeWidth;

    // Clic à 100 unités modèle du coin du canevas dans chaque axe.
    final target = canvasOrigin + Offset(100 * scale, 100 * scale);
    await tester.tapAt(target);
    await tester.pump();

    expect(downs, hasLength(1));
    expect(downs.single.dx, closeTo(100, 0.5));
    expect(downs.single.dy, closeTo(100, 0.5));

    // Glisser de 40 unités modèle vers la droite/bas depuis un second point.
    final second = canvasOrigin + Offset(200 * scale, 150 * scale);
    await tester.dragFrom(second, Offset(40 * scale, 40 * scale));
    await tester.pump();

    expect(downs, hasLength(2));
    expect(downs.last.dx, closeTo(200, 0.5));
    expect(downs.last.dy, closeTo(150, 0.5));
    expect(drags, isNotEmpty);
    final totalDragX = drags.fold<double>(0, (sum, d) => sum + d.dx);
    final totalDragY = drags.fold<double>(0, (sum, d) => sum + d.dy);
    expect(totalDragX, closeTo(40, 0.5));
    expect(totalDragY, closeTo(40, 0.5));
  });
}
