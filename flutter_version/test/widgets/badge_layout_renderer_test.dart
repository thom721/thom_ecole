import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/widgets/badge_layout_renderer.dart';

Future<Uint8List> _fakePhoto() async {
  final recorder = ui.PictureRecorder();
  final canvas = ui.Canvas(recorder, const ui.Rect.fromLTWH(0, 0, 40, 40));
  canvas.drawRect(const ui.Rect.fromLTWH(0, 0, 40, 40), ui.Paint()..color = const ui.Color(0xFFB08D57));
  final image = await recorder.endRecording().toImage(40, 40);
  final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
  return bytes!.buffer.asUint8List();
}

Future<({int width, int height})> _pngSize(Uint8List bytes) async {
  final codec = await ui.instantiateImageCodec(bytes);
  final frame = await codec.getNextFrame();
  return (width: frame.image.width, height: frame.image.height);
}

void main() {
  testWidgets('rend un gabarit paysage complet (texte, forme, photo, QR) sans exception', (tester) async {
    final layout = BadgeLayoutTemplate(
      id: 't1',
      name: 'Gabarit test',
      recto: BadgeSide(
        elements: [
          BadgeElement(
            id: 'border',
            type: BadgeElementType.shape,
            x: 2,
            y: 2,
            width: 1009,
            height: 634,
            shapeKind: BadgeShapeKind.roundedRectangle,
            cornerRadius: 12,
            strokeColor: 0xFF003366,
            strokeWidth: 4,
            strokeStyle: BadgeStrokeStyle.dashed,
          ),
          BadgeElement(
            id: 'name',
            type: BadgeElementType.text,
            x: 100,
            y: 180,
            width: 800,
            height: 60,
            text: '{{nom}} {{prenom}}',
            fontSize: 24,
            bold: true,
            textAlign: BadgeTextAlign.center,
          ),
          BadgeElement(
            id: 'photo',
            type: BadgeElementType.photoPlaceholder,
            x: 97,
            y: 127,
            width: 234,
            height: 261,
          ),
          BadgeElement(
            id: 'qr',
            type: BadgeElementType.qrPlaceholder,
            x: 880,
            y: 530,
            width: 90,
            height: 90,
          ),
        ],
      ),
    );

    final photoBytes = await _fakePhoto();
    final png = await renderBadgeFromLayout(
      layout: layout,
      side: layout.recto,
      placeholderValues: const {'{{nom}}': 'DUPONT', '{{prenom}}': 'Jean'},
      photoBytes: photoBytes,
      qrData: 'ETU-0001',
    );

    final size = await _pngSize(png);
    expect(size.width, 1013);
    expect(size.height, 638);
  });

  testWidgets('un gabarit portrait produit un canevas 638x1013 (dimensions inversées)', (tester) async {
    final layout = BadgeLayoutTemplate(id: 't2', name: 'Portrait', isLandscape: false);
    final png = await renderBadgeFromLayout(layout: layout, side: layout.recto);
    final size = await _pngSize(png);
    expect(size.width, 638);
    expect(size.height, 1013);
  });

  testWidgets('des éléments sans photo/QR fourni retombent sur un placeholder gris sans exception', (tester) async {
    final layout = BadgeLayoutTemplate(
      id: 't3',
      name: 'Placeholders',
      recto: BadgeSide(
        elements: [
          BadgeElement(id: 'photo', type: BadgeElementType.photoPlaceholder, x: 0, y: 0, width: 100, height: 100),
          BadgeElement(id: 'qr', type: BadgeElementType.qrPlaceholder, x: 0, y: 0, width: 50, height: 50),
        ],
      ),
    );

    final png = await renderBadgeFromLayout(layout: layout, side: layout.recto);
    final size = await _pngSize(png);
    expect(size.width, 1013);
    expect(size.height, 638);
  });
}
