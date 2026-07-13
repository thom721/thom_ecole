/// Maths partagées par `widgets/badge_layout_renderer.dart` (export PNG) et
/// `screens/etudiant/badge_builder/badge_builder_canvas.dart` (aperçu en
/// direct) — une seule implémentation garantit que ce qui s'affiche
/// pendant la conception correspond exactement au badge réellement généré.
///
/// Les réglages (`BadgeElement.photoBrightness`/`photoContrast`/
/// `photoSaturation`/`photoOffsetX`/`photoOffsetY`/`photoZoom`) sont
/// persistés dans le gabarit — appliqués à la photo de CHAQUE étudiant au
/// moment de générer son badge, pas seulement à une photo test pendant la
/// conception (décision explicite, voir la conversation).
library;

import 'dart:ui' as ui;

/// Matrice de couleur combinée (luminosité + contraste + saturation),
/// utilisable directement avec `ui.ColorFilter.matrix()`/`ColorFilter.matrix()`
/// (même type `dart:ui`, que le fichier appelant l'importe préfixé ou non).
///
/// [brightness] : -1..1 (0 = neutre, additif).
/// [contrast] : 0..2 (1 = neutre, multiplicatif autour du gris moyen).
/// [saturation] : 0..2 (1 = neutre, 0 = noir et blanc).
List<double> badgePhotoColorMatrix({
  required double brightness,
  required double contrast,
  required double saturation,
}) {
  return _multiplyColorMatrices(
    _brightnessContrastMatrix(brightness, contrast),
    _saturationMatrix(saturation),
  );
}

List<double> _saturationMatrix(double s) {
  const lumR = 0.2126, lumG = 0.7152, lumB = 0.0722;
  final sr = (1 - s) * lumR;
  final sg = (1 - s) * lumG;
  final sb = (1 - s) * lumB;
  return [
    sr + s,
    sg,
    sb,
    0,
    0,
    sr,
    sg + s,
    sb,
    0,
    0,
    sr,
    sg,
    sb + s,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
  ];
}

List<double> _brightnessContrastMatrix(double brightness, double contrast) {
  final b = brightness * 255;
  final t = (1 - contrast) * 127.5 + b;
  return [
    contrast,
    0,
    0,
    0,
    t,
    0,
    contrast,
    0,
    0,
    t,
    0,
    0,
    contrast,
    0,
    t,
    0,
    0,
    0,
    1,
    0,
  ];
}

/// Compose deux matrices 4×5 (`ColorFilter.matrix`) — applique [inner]
/// PUIS [outer], en les traitant comme des matrices 5×5 affines (dernière
/// ligne implicite [0,0,0,0,1]) multipliées entre elles.
List<double> _multiplyColorMatrices(List<double> outer, List<double> inner) {
  final a = [...outer, 0, 0, 0, 0, 1];
  final b = [...inner, 0, 0, 0, 0, 1];
  final result = List<double>.filled(25, 0);
  for (var r = 0; r < 5; r++) {
    for (var c = 0; c < 5; c++) {
      var sum = 0.0;
      for (var k = 0; k < 5; k++) {
        sum += a[r * 5 + k] * b[k * 5 + c];
      }
      result[r * 5 + c] = sum;
    }
  }
  return result.sublist(0, 20);
}

/// Rectangle source (dans l'image d'origine) à recadrer pour remplir une
/// boîte cible de ratio [targetWidth]/[targetHeight], centré sur le point
/// focal ([offsetX], [offsetY], fractions 0..1 de l'image source) et
/// resserré par [zoom] (>=1 : recadre plus serré). Avec les valeurs par
/// défaut (0.5, 0.5, 1.0), équivaut à un recadrage centré classique.
ui.Rect badgePhotoCropRect({
  required double srcWidth,
  required double srcHeight,
  required double targetWidth,
  required double targetHeight,
  double offsetX = 0.5,
  double offsetY = 0.5,
  double zoom = 1,
}) {
  final targetRatio = targetWidth / targetHeight;
  final srcRatio = srcWidth / srcHeight;
  double baseCropW, baseCropH;
  if (srcRatio > targetRatio) {
    baseCropH = srcHeight;
    baseCropW = srcHeight * targetRatio;
  } else {
    baseCropW = srcWidth;
    baseCropH = srcWidth / targetRatio;
  }

  final z = zoom < 1 ? 1.0 : zoom;
  final cropW = (baseCropW / z).clamp(1.0, srcWidth);
  final cropH = (baseCropH / z).clamp(1.0, srcHeight);

  final maxLeft = (srcWidth - cropW).clamp(0.0, double.infinity);
  final maxTop = (srcHeight - cropH).clamp(0.0, double.infinity);
  final left = (offsetX.clamp(0.0, 1.0) * srcWidth - cropW / 2).clamp(
    0.0,
    maxLeft,
  );
  final top = (offsetY.clamp(0.0, 1.0) * srcHeight - cropH / 2).clamp(
    0.0,
    maxTop,
  );

  return ui.Rect.fromLTWH(left, top, cropW, cropH);
}
