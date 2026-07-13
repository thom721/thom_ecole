import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';

void main() {
  test('BadgeLayoutTemplate round-trip JSON (recto-verso, tous les types d\'éléments)', () {
    final layout = BadgeLayoutTemplate(
      id: 'test-1',
      name: 'Mon gabarit',
      isLandscape: true,
      recto: BadgeSide(
        backgroundImagePath: '/tmp/bg.jpg',
        elements: [
          BadgeElement(
            id: 'el-1',
            type: BadgeElementType.text,
            x: 100,
            y: 180,
            width: 400,
            height: 40,
            rotationDegrees: 5.5,
            text: '{{nom}} {{prenom}}',
            fontFamily: 'Roboto',
            fontSize: 24,
            bold: true,
            color: 0xFF003366,
            textAlign: BadgeTextAlign.center,
          ),
          BadgeElement(
            id: 'el-2',
            type: BadgeElementType.shape,
            x: 0,
            y: 0,
            width: 1013,
            height: 638,
            shapeKind: BadgeShapeKind.roundedRectangle,
            strokeColor: 0xFF003366,
            strokeWidth: 4,
            strokeStyle: BadgeStrokeStyle.dashed,
            cornerRadius: 12,
          ),
        ],
      ),
      verso: BadgeSide(
        elements: [
          BadgeElement(
            id: 'el-3',
            type: BadgeElementType.qrPlaceholder,
            x: 880,
            y: 530,
            width: 90,
            height: 90,
          ),
        ],
      ),
    );

    final decoded = BadgeLayoutTemplate.fromJsonString(layout.toJsonString());

    expect(decoded.id, layout.id);
    expect(decoded.name, layout.name);
    expect(decoded.isLandscape, isTrue);
    expect(decoded.recto.backgroundImagePath, '/tmp/bg.jpg');
    expect(decoded.recto.elements, hasLength(2));
    expect(decoded.recto.elements[0].text, '{{nom}} {{prenom}}');
    expect(decoded.recto.elements[0].rotationDegrees, 5.5);
    expect(decoded.recto.elements[0].textAlign, BadgeTextAlign.center);
    expect(decoded.recto.elements[1].shapeKind, BadgeShapeKind.roundedRectangle);
    expect(decoded.recto.elements[1].strokeStyle, BadgeStrokeStyle.dashed);
    expect(decoded.hasVerso, isTrue);
    expect(decoded.verso!.elements.single.type, BadgeElementType.qrPlaceholder);
    expect(decoded.canvasWidth, kBadgeLandscapeWidth);
    expect(decoded.canvasHeight, kBadgeLandscapeHeight);
  });

  test('Portrait bascule largeur/hauteur du canevas', () {
    final layout = BadgeLayoutTemplate(id: 'p', name: 'Portrait', isLandscape: false);
    expect(layout.canvasWidth, kBadgeLandscapeHeight);
    expect(layout.canvasHeight, kBadgeLandscapeWidth);
  });

  test('BadgeElement chemin libre (outil plume) + dégradé : aller-retour JSON', () {
    final el = BadgeElement(
      id: 'path-1',
      type: BadgeElementType.shape,
      x: 50,
      y: 60,
      width: 200,
      height: 150,
      shapeKind: BadgeShapeKind.path,
      pathPoints: [
        BadgePathPoint(x: 0, y: 1, outX: 0.1, outY: -0.2),
        BadgePathPoint(x: 0.5, y: 0, inX: -0.1, inY: 0.15, outX: 0.1, outY: -0.15),
        BadgePathPoint(x: 1, y: 1),
      ],
      pathClosed: true,
      fillGradient: BadgeGradient(
        type: BadgeGradientType.radial,
        angleDegrees: 45,
        stops: [
          BadgeGradientStop(color: 0xFFFF0000, offset: 0),
          BadgeGradientStop(color: 0xFF0000FF, offset: 0.5),
          BadgeGradientStop(color: 0xFF00FF00, offset: 1),
        ],
      ),
      subtractBackground: true,
    );

    final decoded = BadgeElement.fromJson(el.toJson());

    expect(decoded.shapeKind, BadgeShapeKind.path);
    expect(decoded.pathClosed, isTrue);
    expect(decoded.pathPoints, hasLength(3));
    expect(decoded.pathPoints[1].inX, closeTo(-0.1, 1e-9));
    expect(decoded.pathPoints[1].outY, closeTo(-0.15, 1e-9));
    expect(decoded.pathPoints[0].inX, isNull);
    expect(decoded.fillGradient, isNotNull);
    expect(decoded.fillGradient!.type, BadgeGradientType.radial);
    expect(decoded.fillGradient!.angleDegrees, 45);
    expect(decoded.fillGradient!.stops, hasLength(3));
    expect(decoded.fillGradient!.stops[1].color, 0xFF0000FF);
    expect(decoded.fillGradient!.stops[1].offset, 0.5);
    expect(decoded.subtractBackground, isTrue);
  });

  test('BadgeElement.subtractBackground : false par défaut, y compris décodé depuis un JSON existant sans ce champ', () {
    final el = BadgeElement(id: 'e', type: BadgeElementType.shape, x: 0, y: 0, width: 10, height: 10);
    expect(el.subtractBackground, isFalse);

    final legacyJson = el.toJson()..remove('subtractBackground');
    final decoded = BadgeElement.fromJson(legacyJson);
    expect(decoded.subtractBackground, isFalse);
  });

  test(
    'BadgeElement.hidden/locked (panneau des calques, badge_builder_layers_panel.dart) : '
    'false par défaut, aller-retour JSON, y compris décodé depuis un JSON existant sans ces champs',
    () {
      final el = BadgeElement(id: 'e', type: BadgeElementType.shape, x: 0, y: 0, width: 10, height: 10);
      expect(el.hidden, isFalse);
      expect(el.locked, isFalse);

      final legacyJson = el.toJson()
        ..remove('hidden')
        ..remove('locked');
      final decodedLegacy = BadgeElement.fromJson(legacyJson);
      expect(decodedLegacy.hidden, isFalse);
      expect(decodedLegacy.locked, isFalse);

      el.hidden = true;
      el.locked = true;
      final decoded = BadgeElement.fromJson(el.toJson());
      expect(decoded.hidden, isTrue);
      expect(decoded.locked, isTrue);
    },
  );

  test(
    'BadgeElement.cutoutPaths (trous PERMANENTS gravés par bakeSubtraction, '
    'voir badge_builder_canvas.dart) : aller-retour JSON, vide par défaut '
    'y compris décodé depuis un JSON existant sans ce champ',
    () {
      final el = BadgeElement(id: 'e', type: BadgeElementType.shape, x: 0, y: 0, width: 10, height: 10);
      expect(el.cutoutPaths, isEmpty);

      final legacyJson = el.toJson()..remove('cutoutPaths');
      expect(BadgeElement.fromJson(legacyJson).cutoutPaths, isEmpty);

      el.cutoutPaths.addAll([
        [BadgePathPoint(x: 0, y: 0), BadgePathPoint(x: 1, y: 0), BadgePathPoint(x: 0.5, y: 1)],
        [BadgePathPoint(x: 0.2, y: 0.2), BadgePathPoint(x: 0.8, y: 0.8)],
      ]);
      final decoded = BadgeElement.fromJson(el.toJson());
      expect(decoded.cutoutPaths, hasLength(2));
      expect(decoded.cutoutPaths[0], hasLength(3));
      expect(decoded.cutoutPaths[0][2].x, closeTo(0.5, 1e-9));
      expect(decoded.cutoutPaths[1][1].y, closeTo(0.8, 1e-9));
    },
  );

  test('BadgeElementType.staticImage : imagePath et fit survivent à l\'aller-retour JSON', () {
    final el = BadgeElement(
      id: 'img-1',
      type: BadgeElementType.staticImage,
      x: 10,
      y: 20,
      width: 200,
      height: 120,
      imagePath: '/tmp/signature.jpg',
      fit: BadgePhotoFit.contain,
    );

    final decoded = BadgeElement.fromJson(el.toJson());

    expect(decoded.type, BadgeElementType.staticImage);
    expect(decoded.imagePath, '/tmp/signature.jpg');
    expect(decoded.fit, BadgePhotoFit.contain);
  });

  test(
    'BadgeSide.guidesX/guidesY (repères Adobe/Figma, badge_builder_canvas.dart) : '
    'vides par défaut, aller-retour JSON, y compris décodé depuis un JSON existant sans ces champs',
    () {
      final side = BadgeSide();
      expect(side.guidesX, isEmpty);
      expect(side.guidesY, isEmpty);

      final legacyJson = side.toJson()
        ..remove('guidesX')
        ..remove('guidesY');
      final decodedLegacy = BadgeSide.fromJson(legacyJson);
      expect(decodedLegacy.guidesX, isEmpty);
      expect(decodedLegacy.guidesY, isEmpty);

      side.guidesX.addAll([100.5, 400.25]);
      side.guidesY.add(200.0);
      final decoded = BadgeSide.fromJson(side.toJson());
      expect(decoded.guidesX, [100.5, 400.25]);
      expect(decoded.guidesY, [200.0]);
    },
  );

  test('Gabarit sans verso : hasVerso est false et verso reste null', () {
    final layout = BadgeLayoutTemplate(id: 's', name: 'Recto seul');
    expect(layout.hasVerso, isFalse);

    final decoded = BadgeLayoutTemplate.fromJsonString(layout.toJsonString());
    expect(decoded.hasVerso, isFalse);
    expect(decoded.verso, isNull);
  });
}
