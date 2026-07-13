import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/widgets/badge_photo_effects.dart';

void main() {
  group('badgePhotoColorMatrix', () {
    test('des réglages neutres produisent la matrice identité', () {
      final m = badgePhotoColorMatrix(brightness: 0, contrast: 1, saturation: 1);
      const identity = [
        1.0, 0, 0, 0, 0, //
        0, 1, 0, 0, 0, //
        0, 0, 1, 0, 0, //
        0, 0, 0, 1, 0,
      ];
      for (var i = 0; i < identity.length; i++) {
        expect(m[i], closeTo(identity[i], 1e-9), reason: 'index $i');
      }
    });

    test('saturation à 0 réduit chaque canal à la même pondération de luminance', () {
      final m = badgePhotoColorMatrix(brightness: 0, contrast: 1, saturation: 0);
      // Ligne rouge : coefficients R,G,B doivent être identiques (poids de
      // luminance), et pareil pour les lignes verte/bleue (image en niveaux
      // de gris : chaque canal de sortie est la même combinaison des trois).
      expect(m[0], closeTo(m[5], 1e-9));
      expect(m[1], closeTo(m[6], 1e-9));
      expect(m[2], closeTo(m[7], 1e-9));
      expect(m[5], closeTo(m[10], 1e-9));
      expect(m[6], closeTo(m[11], 1e-9));
      expect(m[7], closeTo(m[12], 1e-9));
      // Les poids R+G+B de la ligne rouge doivent sommer à 1 (luminance
      // normalisée).
      expect(m[0] + m[1] + m[2], closeTo(1, 1e-9));
    });

    test('la luminosité ajoute un décalage constant sur chaque canal', () {
      final m = badgePhotoColorMatrix(brightness: 0.5, contrast: 1, saturation: 1);
      expect(m[4], closeTo(0.5 * 255, 1e-9));
      expect(m[9], closeTo(0.5 * 255, 1e-9));
      expect(m[14], closeTo(0.5 * 255, 1e-9));
    });

    test('le contraste multiplie la diagonale', () {
      final m = badgePhotoColorMatrix(brightness: 0, contrast: 1.5, saturation: 1);
      expect(m[0], closeTo(1.5, 1e-9));
      expect(m[6], closeTo(1.5, 1e-9));
      expect(m[12], closeTo(1.5, 1e-9));
    });
  });

  group('badgePhotoCropRect', () {
    test('valeurs par défaut : recadrage centré classique (image plus large que la cible)', () {
      final rect = badgePhotoCropRect(srcWidth: 400, srcHeight: 200, targetWidth: 100, targetHeight: 100);
      // Image 2:1, cible 1:1 -> recadre une bande carrée 200×200 centrée.
      expect(rect.width, closeTo(200, 1e-6));
      expect(rect.height, closeTo(200, 1e-6));
      expect(rect.left, closeTo(100, 1e-6));
      expect(rect.top, closeTo(0, 1e-6));
    });

    test('offsetX/offsetY déplacent le point focal, borné aux limites de l\'image', () {
      final rect = badgePhotoCropRect(
        srcWidth: 400,
        srcHeight: 200,
        targetWidth: 100,
        targetHeight: 100,
        offsetX: 0,
        offsetY: 0.5,
      );
      // Point focal tout à gauche -> le recadrage colle au bord gauche
      // (borné à 0, pas de valeur négative).
      expect(rect.left, closeTo(0, 1e-6));
    });

    test('zoom > 1 resserre le recadrage sans changer son centre', () {
      final base = badgePhotoCropRect(srcWidth: 400, srcHeight: 200, targetWidth: 100, targetHeight: 100);
      final zoomed = badgePhotoCropRect(
        srcWidth: 400,
        srcHeight: 200,
        targetWidth: 100,
        targetHeight: 100,
        zoom: 2,
      );
      expect(zoomed.width, closeTo(base.width / 2, 1e-6));
      expect(zoomed.height, closeTo(base.height / 2, 1e-6));
      expect(zoomed.center.dx, closeTo(base.center.dx, 1e-6));
      expect(zoomed.center.dy, closeTo(base.center.dy, 1e-6));
    });
  });
}
