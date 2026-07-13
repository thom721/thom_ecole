import 'dart:io';
import 'dart:math' show cos, pi, sin;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:qr_flutter/qr_flutter.dart';

import '../models/badge_layout.dart';
import 'badge_photo_effects.dart';
import 'png_dpi.dart';

/// Rendu générique d'une face de [BadgeLayoutTemplate] — même approche
/// `dart:ui` Canvas hors-écran → PNG que `widgets/badge_renderer.dart`,
/// mais pilotée par une liste d'éléments positionnés au lieu de
/// coordonnées figées. Ne remplace pas `renderBadgePng` (toujours utilisé
/// pour les 2 templates fixes existants) : sert uniquement les gabarits
/// construits dans `screens/etudiant/badge_builder/`.
///
/// [placeholderValues] mappe un jeton de `kBadgePlaceholderTokens` (ex.
/// `'{{nom}}'`) à sa valeur réelle pour l'étudiant courant — appliqué par
/// simple remplacement dans le texte de chaque élément `text`.
Future<Uint8List> renderBadgeFromLayout({
  required BadgeLayoutTemplate layout,
  required BadgeSide side,
  Map<String, String> placeholderValues = const {},
  Uint8List? backgroundImageBytes,
  Uint8List? photoBytes,
  String? qrData,
}) async {
  final width = layout.canvasWidth;
  final height = layout.canvasHeight;
  final fullCanvasRect = ui.Rect.fromLTWH(0, 0, width, height);

  final recorder = ui.PictureRecorder();
  final canvas = ui.Canvas(recorder, fullCanvasRect);

  Future<void> paintBackground() async {
    canvas.drawRect(
      fullCanvasRect,
      ui.Paint()..color = const ui.Color(0xFFFFFFFF),
    );
    if (backgroundImageBytes != null) {
      final bgImage = await _decodeImage(backgroundImageBytes);
      canvas.drawImageRect(
        bgImage,
        ui.Rect.fromLTWH(
          0,
          0,
          bgImage.width.toDouble(),
          bgImage.height.toDouble(),
        ),
        fullCanvasRect,
        ui.Paint(),
      );
    }
  }

  Future<void> paintElement(BadgeElement el) async {
    canvas.save();
    // Pivote autour du centre de l'élément, comme un `Transform.rotate`
    // Flutter avec `alignment: Alignment.center` — cohérent avec la
    // manipulation interactive de `BadgeCanvasElement`.
    final centerX = el.x + el.width / 2;
    final centerY = el.y + el.height / 2;
    canvas.translate(centerX, centerY);
    if (el.rotationDegrees != 0) {
      canvas.rotate(el.rotationDegrees * pi / 180);
    }
    canvas.translate(-el.width / 2, -el.height / 2);

    // Trous PERMANENTS déjà gravés dans `el.cutoutPaths` (voir
    // badge_builder_canvas.dart::bakeSubtraction et la doc de
    // `BadgeElement.subtractBackground`/`cutoutPaths` dans
    // models/badge_layout.dart) — un simple `clipPath` dans le repère déjà
    // LOCAL de cet élément, gravé une fois pour toutes au moment de la
    // découpe, plutôt qu'un regroupement `saveLayer`/`BlendMode.clear`
    // recalculé à chaque export selon la position d'une autre forme.
    if (el.cutoutPaths.isNotEmpty) {
      canvas.clipPath(_cutoutClipPath(el));
    }

    switch (el.type) {
      case BadgeElementType.text:
        _drawText(canvas, el, placeholderValues);
      case BadgeElementType.shape:
        _drawShape(canvas, el);
      case BadgeElementType.photoPlaceholder:
        await _drawPhoto(canvas, el, photoBytes);
      case BadgeElementType.qrPlaceholder:
        _drawQr(canvas, el, qrData);
      case BadgeElementType.staticImage:
        await _drawStaticImage(canvas, el);
    }
    canvas.restore();
  }

  await paintBackground();
  final elements = [...side.elements]
    ..sort((a, b) => a.zIndex.compareTo(b.zIndex));
  // `el.hidden` (voir badge_builder_layers_panel.dart) exclut cet élément
  // du badge généré, pas seulement de l'aperçu d'édition — comme un
  // calque masqué dans Illustrator/Photoshop, jamais inclus dans l'export
  // final.
  for (final el in elements.where((el) => !el.hidden)) {
    await paintElement(el);
  }

  final picture = recorder.endRecording();
  final image = await picture.toImage(width.toInt(), height.toInt());
  final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
  // 300 DPI — voir kBadgePxPerCm (models/badge_layout.dart), la référence
  // sur laquelle les dimensions en pixels du badge sont déjà basées ;
  // `dart:ui` n'embarque aucune métadonnée de résolution de lui-même.
  return injectPngDpi(bytes!.buffer.asUint8List(), dpi: 300);
}

/// Chemin de découpe pour `el.cutoutPaths` (trous PERMANENTS, voir
/// badge_builder_canvas.dart::bakeSubtraction) — chaque polygone est déjà
/// dans le repère LOCAL de [el] (0,0)–(width,height), donc une simple
/// boîte moins des polygones, sans transformation croisée avec un autre
/// élément (contrairement à l'ancien mécanisme dynamique, qui devait
/// recalculer la position relative d'une forme "Soustraire du fond"
/// voisine à chaque export).
ui.Path _cutoutClipPath(BadgeElement el) {
  final rect = ui.Rect.fromLTWH(0, 0, el.width, el.height);
  var clip = ui.Path()..addRect(rect);
  for (final polygon in el.cutoutPaths) {
    clip = ui.Path.combine(
      ui.PathOperation.difference,
      clip,
      _pathFromPoints(rect, polygon, true),
    );
  }
  return clip;
}

Future<ui.Image> _decodeImage(Uint8List bytes) async {
  final codec = await ui.instantiateImageCodec(bytes);
  final frame = await codec.getNextFrame();
  return frame.image;
}

String _substitutePlaceholders(String text, Map<String, String> values) {
  var result = text;
  values.forEach((token, value) => result = result.replaceAll(token, value));
  return result;
}

/// Dessine dans un repère déjà translaté à (0,0)=coin de l'élément — le
/// texte est centré verticalement dans `el.height`, alignement horizontal
/// piloté par `el.textAlign` (comme `_drawCenteredText` de
/// `badge_renderer.dart`, généralisé aux 3 alignements).
void _drawText(ui.Canvas canvas, BadgeElement el, Map<String, String> values) {
  final resolved = _substitutePlaceholders(el.text ?? '', values);
  final align = switch (el.textAlign) {
    BadgeTextAlign.left => ui.TextAlign.left,
    BadgeTextAlign.center => ui.TextAlign.center,
    BadgeTextAlign.right => ui.TextAlign.right,
  };
  final fontWeight = el.bold ? ui.FontWeight.bold : ui.FontWeight.normal;
  final fontStyle = el.italic ? ui.FontStyle.italic : ui.FontStyle.normal;
  final fontSize = el.fontSize ?? 16;

  final builder =
      ui.ParagraphBuilder(
          ui.ParagraphStyle(
            textAlign: align,
            fontWeight: fontWeight,
            fontStyle: fontStyle,
            fontFamily: el.fontFamily,
          ),
        )
        ..pushStyle(
          ui.TextStyle(
            color: ui.Color(el.color ?? 0xFF000000),
            fontSize: fontSize,
            fontWeight: fontWeight,
            fontStyle: fontStyle,
            fontFamily: el.fontFamily,
          ),
        )
        ..addText(resolved);
  final paragraph = builder.build()
    ..layout(ui.ParagraphConstraints(width: el.width));
  canvas.drawParagraph(
    paragraph,
    ui.Offset(0, (el.height - paragraph.height) / 2),
  );
}

/// Chemin partagé entre `_drawShape` (formes libres) et `_drawPhoto` (masque
/// + bordure du cadre photo) — une seule définition de "à quoi ressemble
/// chaque BadgeShapeKind" pour les deux usages. [pathPoints]/[pathClosed]
/// ne sont utiles que pour `BadgeShapeKind.path` (outil plume).
ui.Path _shapePath(
  ui.Rect rect,
  BadgeShapeKind kind,
  double? cornerRadius, {
  List<BadgePathPoint> pathPoints = const [],
  bool pathClosed = true,
}) {
  switch (kind) {
    case BadgeShapeKind.rectangle:
      return ui.Path()..addRect(rect);
    case BadgeShapeKind.roundedRectangle:
      return ui.Path()..addRRect(
        ui.RRect.fromRectAndRadius(rect, ui.Radius.circular(cornerRadius ?? 8)),
      );
    case BadgeShapeKind.oval:
      return ui.Path()..addOval(rect);
    case BadgeShapeKind.line:
      return ui.Path()
        ..moveTo(rect.left, rect.top + rect.height / 2)
        ..lineTo(rect.right, rect.top + rect.height / 2);
    case BadgeShapeKind.curve:
      // Bézier quadratique du coin bas-gauche au coin bas-droite de la
      // boîte, bombée vers le haut de `cornerRadius` (réutilisé comme
      // hauteur de courbe) — un simple trait courbe, pas une forme fermée.
      final bulge = cornerRadius ?? rect.height / 2;
      return ui.Path()
        ..moveTo(rect.left, rect.bottom)
        ..quadraticBezierTo(
          rect.left + rect.width / 2,
          rect.bottom - bulge,
          rect.right,
          rect.bottom,
        );
    case BadgeShapeKind.path:
      return _pathFromPoints(rect, pathPoints, pathClosed);
  }
}

ui.Offset _denormalize(ui.Rect rect, double nx, double ny) =>
    ui.Offset(rect.left + nx * rect.width, rect.top + ny * rect.height);

/// Construit un tracé Bézier cubique (façon Illustrator) à partir de
/// [points] normalisés (0..1, fraction de [rect]) — chaque segment entre
/// deux ancres utilise la poignée SORTANTE de la précédente et la poignée
/// ENTRANTE de la suivante (`null` = poignée confondue avec l'ancre, donc
/// segment droit de ce côté).
ui.Path _pathFromPoints(
  ui.Rect rect,
  List<BadgePathPoint> points,
  bool closed,
) {
  final path = ui.Path();
  if (points.isEmpty) return path;

  final first = _denormalize(rect, points.first.x, points.first.y);
  path.moveTo(first.dx, first.dy);
  for (var i = 1; i < points.length; i++) {
    _cubicBetween(path, rect, points[i - 1], points[i]);
  }
  if (closed && points.length > 1) {
    _cubicBetween(path, rect, points.last, points.first);
    path.close();
  }
  return path;
}

void _cubicBetween(
  ui.Path path,
  ui.Rect rect,
  BadgePathPoint from,
  BadgePathPoint to,
) {
  final cp1 = from.outX != null
      ? _denormalize(rect, from.x + from.outX!, from.y + from.outY!)
      : _denormalize(rect, from.x, from.y);
  final cp2 = to.inX != null
      ? _denormalize(rect, to.x + to.inX!, to.y + to.inY!)
      : _denormalize(rect, to.x, to.y);
  final end = _denormalize(rect, to.x, to.y);
  path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, end.dx, end.dy);
}

/// Dégradé linéaire (direction pilotée par `angleDegrees`, centré sur la
/// boîte) ou radial (toujours centré) — au moins 2 arrêts de couleur.
ui.Shader _buildGradientShader(BadgeGradient gradient, ui.Rect rect) {
  final colors = gradient.stops.map((s) => ui.Color(s.color)).toList();
  final stops = gradient.stops.map((s) => s.offset).toList();
  if (gradient.type == BadgeGradientType.radial) {
    return ui.Gradient.radial(rect.center, rect.longestSide / 2, colors, stops);
  }
  final angleRad = gradient.angleDegrees * pi / 180;
  final direction =
      ui.Offset(cos(angleRad), sin(angleRad)) * (rect.longestSide / 2);
  return ui.Gradient.linear(
    rect.center - direction,
    rect.center + direction,
    colors,
    stops,
  );
}

void _drawShape(ui.Canvas canvas, BadgeElement el) {
  final rect = ui.Rect.fromLTWH(0, 0, el.width, el.height);
  final kind = el.shapeKind ?? BadgeShapeKind.rectangle;
  final path = _shapePath(
    rect,
    kind,
    el.cornerRadius,
    pathPoints: el.pathPoints,
    pathClosed: el.pathClosed,
  );

  // `el.subtractBackground` n'est plus qu'un DÉCLENCHEUR ponctuel (voir
  // models/badge_layout.dart) : réinitialisé à `false` de façon
  // synchrone dès qu'il est consommé (badge_builder_screen.dart::
  // _onElementChanged), donc jamais réellement peint à `true` — cette
  // forme se dessine toujours normalement, même juste après avoir servi
  // de découpeur (son propre trou éventuel, s'il a lui-même été découpé
  // par une AUTRE forme, reste appliqué via `el.cutoutPaths`/`clipPath`
  // dans `paintElement`, indépendamment de ce déclencheur).
  final isOpenPath =
      kind == BadgeShapeKind.line ||
      kind == BadgeShapeKind.curve ||
      (kind == BadgeShapeKind.path && !el.pathClosed);
  if (!isOpenPath) {
    if (el.fillGradient != null && el.fillGradient!.stops.length >= 2) {
      canvas.drawPath(
        path,
        ui.Paint()..shader = _buildGradientShader(el.fillGradient!, rect),
      );
    } else if (el.fillColor != null) {
      canvas.drawPath(path, ui.Paint()..color = ui.Color(el.fillColor!));
    }
  }
  _strokePath(canvas, path, el);
}

void _strokePath(ui.Canvas canvas, ui.Path path, BadgeElement el) {
  if (el.strokeColor == null || (el.strokeWidth ?? 0) <= 0) return;
  final strokePaint = ui.Paint()
    ..color = ui.Color(el.strokeColor!)
    ..style = ui.PaintingStyle.stroke
    ..strokeWidth = el.strokeWidth!;
  if (el.strokeStyle == BadgeStrokeStyle.solid) {
    canvas.drawPath(path, strokePaint);
  } else {
    _drawDashedPath(
      canvas,
      path,
      strokePaint,
      dashLength: el.strokeStyle == BadgeStrokeStyle.dashed ? 8 : 2,
      gapLength: el.strokeStyle == BadgeStrokeStyle.dashed ? 5 : 4,
    );
  }
}

/// `dart:ui` n'a pas de style de trait pointillé natif — on découpe le
/// chemin en segments via `computeMetrics()`/`extractPath()`, seule API
/// disponible sans dépendance externe (`path_drawing` n'est pas ajouté
/// pour ce seul besoin).
void _drawDashedPath(
  ui.Canvas canvas,
  ui.Path path,
  ui.Paint paint, {
  required double dashLength,
  required double gapLength,
}) {
  for (final metric in path.computeMetrics()) {
    var distance = 0.0;
    while (distance < metric.length) {
      final end = (distance + dashLength).clamp(0.0, metric.length);
      canvas.drawPath(metric.extractPath(distance, end), paint);
      distance += dashLength + gapLength;
    }
  }
}

/// Le cadre photo peut être rectangulaire, arrondi ou circulaire/ovale
/// (`el.shapeKind`/`el.cornerRadius`, réutilisés depuis les éléments
/// "forme") et porter une bordure (`el.strokeColor`/`strokeWidth`/
/// `strokeStyle`) — même logique que `_drawShape`, appliquée en masque
/// (`clipPath`) avant de dessiner la photo. Les réglages persistés
/// (`el.photoBrightness`/`Contrast`/`Saturation`/`OffsetX`/`OffsetY`/`Zoom`,
/// voir `badge_photo_effects.dart`) sont appliqués à la photo de CHAQUE
/// étudiant à la génération — pas seulement à une photo test en conception.
Future<void> _drawPhoto(
  ui.Canvas canvas,
  BadgeElement el,
  Uint8List? photoBytes,
) async {
  final frame = ui.Rect.fromLTWH(0, 0, el.width, el.height);
  final requested = el.shapeKind ?? BadgeShapeKind.rectangle;
  final isOpenOrPathKind =
      requested == BadgeShapeKind.line ||
      requested == BadgeShapeKind.curve ||
      requested == BadgeShapeKind.path;
  final kind = isOpenOrPathKind ? BadgeShapeKind.rectangle : requested;
  final path = _shapePath(frame, kind, el.cornerRadius);

  if (photoBytes == null) {
    canvas.drawPath(path, ui.Paint()..color = const ui.Color(0xFFE0E0E0));
    _strokePath(canvas, path, el);
    return;
  }

  final photoImage = await _decodeImage(photoBytes);
  final paint = ui.Paint()
    ..colorFilter = ui.ColorFilter.matrix(
      badgePhotoColorMatrix(
        brightness: el.photoBrightness,
        contrast: el.photoContrast,
        saturation: el.photoSaturation,
      ),
    );
  canvas.save();
  canvas.clipPath(path);
  if (el.fit == BadgePhotoFit.contain) {
    final srcW = photoImage.width.toDouble();
    final srcH = photoImage.height.toDouble();
    final scale = (frame.width / srcW < frame.height / srcH)
        ? frame.width / srcW
        : frame.height / srcH;
    final dstW = srcW * scale;
    final dstH = srcH * scale;
    final dst = ui.Rect.fromLTWH(
      (frame.width - dstW) / 2,
      (frame.height - dstH) / 2,
      dstW,
      dstH,
    );
    canvas.drawImageRect(
      photoImage,
      ui.Rect.fromLTWH(0, 0, srcW, srcH),
      dst,
      paint,
    );
  } else {
    final src = badgePhotoCropRect(
      srcWidth: photoImage.width.toDouble(),
      srcHeight: photoImage.height.toDouble(),
      targetWidth: frame.width,
      targetHeight: frame.height,
      offsetX: el.photoOffsetX,
      offsetY: el.photoOffsetY,
      zoom: el.photoZoom,
    );
    canvas.drawImageRect(photoImage, src, frame, paint);
  }
  canvas.restore();
  _strokePath(canvas, path, el);
}

/// [qrData] est la donnée automatique (contact du responsable, calculée
/// par badge_screen.dart) — `el.qrCustomData`, saisi manuellement dans le
/// panneau de propriétés, est prioritaire quand renseigné (utile quand
/// l'information automatique n'est pas disponible ou pas pertinente).
void _drawQr(ui.Canvas canvas, BadgeElement el, String? qrData) {
  final frame = ui.Rect.fromLTWH(0, 0, el.width, el.height);
  final resolved = (el.qrCustomData?.isNotEmpty ?? false)
      ? el.qrCustomData
      : qrData;
  if (resolved == null || resolved.isEmpty) {
    canvas.drawRect(frame, ui.Paint()..color = const ui.Color(0xFFE0E0E0));
    return;
  }
  QrPainter(
    data: resolved,
    version: QrVersions.auto,
    errorCorrectionLevel: QrErrorCorrectLevel.L,
  ).paint(canvas, ui.Size(el.width, el.height));
}

/// Contrairement à [_drawPhoto] (une photo DIFFÉRENTE par étudiant, jamais
/// persistée dans le gabarit), [el.imagePath] EST le fichier persisté —
/// lu directement ici plutôt que de dépendre d'un paramètre `bytes` séparé
/// que l'appelant devrait penser à transmettre (la leçon du bug où
/// l'export ignorait l'image de fond faute d'avoir transmis ses octets :
/// même risque évité en amont pour ce nouveau type d'élément).
Future<void> _drawStaticImage(ui.Canvas canvas, BadgeElement el) async {
  final path = el.imagePath;
  if (path == null) return;
  final file = File(path);
  if (!file.existsSync()) return;

  final frame = ui.Rect.fromLTWH(0, 0, el.width, el.height);
  final image = await _decodeImage(await file.readAsBytes());

  canvas.save();
  canvas.clipRect(frame);
  if (el.fit == BadgePhotoFit.contain) {
    final srcW = image.width.toDouble();
    final srcH = image.height.toDouble();
    final scale = (frame.width / srcW < frame.height / srcH)
        ? frame.width / srcW
        : frame.height / srcH;
    final dstW = srcW * scale;
    final dstH = srcH * scale;
    final dst = ui.Rect.fromLTWH(
      (frame.width - dstW) / 2,
      (frame.height - dstH) / 2,
      dstW,
      dstH,
    );
    canvas.drawImageRect(
      image,
      ui.Rect.fromLTWH(0, 0, srcW, srcH),
      dst,
      ui.Paint(),
    );
  } else {
    final src = badgePhotoCropRect(
      srcWidth: image.width.toDouble(),
      srcHeight: image.height.toDouble(),
      targetWidth: frame.width,
      targetHeight: frame.height,
    );
    canvas.drawImageRect(image, src, frame, ui.Paint());
  }
  canvas.restore();
}
