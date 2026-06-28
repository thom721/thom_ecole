import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/services.dart' show rootBundle;
import 'package:qr_flutter/qr_flutter.dart';

/// Équivalent de generate_badge() (school_client, Controllers/Main.py:6144-
/// 6267) : compose un badge 1013×638 (8.5×5.1cm @300DPI, comme l'original)
/// avec QPainter — ici un Canvas hors-écran (PictureRecorder) produisant un
/// PNG. Les coordonnées reprennent approximativement celles du bureau (les
/// QRect Qt d'origine débordent volontairement du canevas par endroits,
/// signe d'un alignement jamais peaufiné côté source ; reproduit ici de
/// façon fidèle au contenu, pas pixel pour pixel).
///
/// Différences disclosées par rapport au bureau :
/// - "Template 2" (combo_template, Main.py:637-640) n'est pas pré-installé
///   ici (le bureau le cherche dans son AppData, où il a pu être uploadé via
///   template_badge_2()) : sa sélection déclenche un choix de fichier dont
///   les octets sont passés ici via [templateBytes], sans persistance entre
///   sessions (le bureau persiste sur disque dans son AppData).
/// - La date d'expiration "Juin 2026" reste codée en dur, identique au
///   bureau (jamais calculée dynamiquement dans la source d'origine).
Future<Uint8List> renderBadgePng({
  required String schoolName,
  required String fullName,
  required String classeName,
  required String identifiant,
  required String salleLabel,
  required String expirationLabel,
  required Uint8List photoBytes,
  required String qrData,
  Uint8List? templateBytes,
}) async {
  const width = 1013.0;
  const height = 638.0;

  final recorder = ui.PictureRecorder();
  final canvas = ui.Canvas(recorder, const ui.Rect.fromLTWH(0, 0, width, height));

  // Fond blanc + template ("Template 1" bundle par défaut, ou le template
  // personnalisé choisi via le sélecteur "Template").
  canvas.drawRect(const ui.Rect.fromLTWH(0, 0, width, height), ui.Paint()..color = const ui.Color(0xFFFFFFFF));
  final bgBytes = templateBytes ?? Uint8List.view((await rootBundle.load('assets/badges/template_badge_1.jpg')).buffer);
  final bgImage = await _decodeImage(bgBytes);
  canvas.drawImageRect(
    bgImage,
    ui.Rect.fromLTWH(0, 0, bgImage.width.toDouble(), bgImage.height.toDouble()),
    const ui.Rect.fromLTWH(0, 0, width, height),
    ui.Paint(),
  );

  // Bordure.
  canvas.drawRect(
    const ui.Rect.fromLTWH(2, 2, width - 4, height - 4),
    ui.Paint()
      ..color = const ui.Color(0xFF003366)
      ..style = ui.PaintingStyle.stroke
      ..strokeWidth = 4,
  );

  // En-tête : nom de l'école — painter.drawText(0, 40, 1013, 50, AlignCenter, ...).
  _drawCenteredText(canvas, schoolName, const ui.Rect.fromLTWH(0, 40, width, 50), fontSize: 28, bold: true, color: const ui.Color(0xFF003366));

  // Cadre photo (97,127,234,261) — crop centré, comme KeepAspectRatioByExpanding + crop.
  const frame = ui.Rect.fromLTWH(97, 127, 234, 261);
  final photoImage = await _decodeImage(photoBytes);
  final src = _centerCropRect(photoImage.width.toDouble(), photoImage.height.toDouble(), frame.width, frame.height);
  canvas.save();
  canvas.clipRect(frame);
  canvas.drawImageRect(photoImage, src, frame, ui.Paint());
  canvas.restore();
  canvas.drawRect(frame, ui.Paint()..color = const ui.Color(0xFF003366)..style = ui.PaintingStyle.stroke..strokeWidth = 2);

  // painter.drawText(100, 180, 1013, 200, AlignCenter, full_name) / (100, 220, 1013, 200, ..., classe).
  _drawCenteredText(canvas, fullName, const ui.Rect.fromLTWH(100, 180, width, 200), fontSize: 24, bold: true);
  _drawCenteredText(canvas, classeName, const ui.Rect.fromLTWH(100, 220, width, 200), fontSize: 20);

  // painter.drawText(x, y, text) — (x,y) est la ligne de base, pas le coin.
  _drawBaselineText(canvas, identifiant, const ui.Offset(62, 475), fontSize: 18, bold: true);
  _drawBaselineText(canvas, expirationLabel, const ui.Offset(300, 480), fontSize: 17);
  _drawBaselineText(canvas, salleLabel, const ui.Offset(560, 480), fontSize: 17);

  // QR code (880,530), ~90x90 — reprend generate_qrcode() (responsable).
  canvas.save();
  canvas.translate(880, 530);
  QrPainter(data: qrData, version: QrVersions.auto, errorCorrectionLevel: QrErrorCorrectLevel.L)
      .paint(canvas, const ui.Size(90, 90));
  canvas.restore();

  final picture = recorder.endRecording();
  final image = await picture.toImage(width.toInt(), height.toInt());
  final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
  return bytes!.buffer.asUint8List();
}

Future<ui.Image> _decodeImage(Uint8List bytes) async {
  final codec = await ui.instantiateImageCodec(bytes);
  final frame = await codec.getNextFrame();
  return frame.image;
}

ui.Rect _centerCropRect(double srcW, double srcH, double targetW, double targetH) {
  final srcRatio = srcW / srcH;
  final targetRatio = targetW / targetH;
  if (srcRatio > targetRatio) {
    final cropW = srcH * targetRatio;
    return ui.Rect.fromLTWH((srcW - cropW) / 2, 0, cropW, srcH);
  } else {
    final cropH = srcW / targetRatio;
    return ui.Rect.fromLTWH(0, (srcH - cropH) / 2, srcW, cropH);
  }
}

/// Équivalent de painter.drawText(x, y, width, height, Qt.AlignCenter, text)
/// : (x,y,width,height) délimite un rectangle, le texte est centré dedans
/// (horizontalement ET verticalement) — pas un simple point central.
void _drawCenteredText(
  ui.Canvas canvas,
  String text,
  ui.Rect rect, {
  double fontSize = 16,
  bool bold = false,
  ui.Color color = const ui.Color(0xFF000000),
}) {
  final paragraphBuilder = ui.ParagraphBuilder(
    ui.ParagraphStyle(textAlign: ui.TextAlign.center, fontWeight: bold ? ui.FontWeight.bold : ui.FontWeight.normal),
  )
    ..pushStyle(ui.TextStyle(color: color, fontSize: fontSize, fontWeight: bold ? ui.FontWeight.bold : ui.FontWeight.normal))
    ..addText(text);
  final paragraph = paragraphBuilder.build()..layout(ui.ParagraphConstraints(width: rect.width));
  canvas.drawParagraph(paragraph, ui.Offset(rect.left, rect.top + (rect.height - paragraph.height) / 2));
}

/// Équivalent de painter.drawText(x, y, text) : (x,y) est la ligne de base
/// du texte (pas son coin supérieur gauche) — on remonte donc d'environ
/// 0.8×fontSize pour approximer le haut du texte.
void _drawBaselineText(
  ui.Canvas canvas,
  String text,
  ui.Offset baseline, {
  double fontSize = 16,
  bool bold = false,
  ui.Color color = const ui.Color(0xFF000000),
}) {
  final paragraphBuilder = ui.ParagraphBuilder(
    ui.ParagraphStyle(textAlign: ui.TextAlign.left, fontWeight: bold ? ui.FontWeight.bold : ui.FontWeight.normal),
  )
    ..pushStyle(ui.TextStyle(color: color, fontSize: fontSize, fontWeight: bold ? ui.FontWeight.bold : ui.FontWeight.normal))
    ..addText(text);
  final paragraph = paragraphBuilder.build()..layout(const ui.ParagraphConstraints(width: 600));
  canvas.drawParagraph(paragraph, ui.Offset(baseline.dx, baseline.dy - fontSize * 0.8));
}
