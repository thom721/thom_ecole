import 'package:flutter/material.dart' show Offset, Path;
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';

/// Teste `bakeSubtraction` (badge_builder_canvas.dart) en isolation —
/// l'action déclenchée UNE SEULE FOIS par le bouton "Soustraire du fond"
/// (voir badge_builder_property_panel.dart / badge_builder_screen.dart::
/// _onElementChanged), qui grave un trou PERMANENT dans `cutoutPaths` de
/// chaque élément en dessous réellement chevauché, plutôt qu'un masque
/// dynamique recalculé à chaque frame (voir la doc de
/// `BadgeElement.subtractBackground` dans models/badge_layout.dart pour
/// l'historique de ce changement de modèle, motivé par le symptôme
/// rapporté : déplacer la forme découpeuse après coup faisait disparaître
/// le trou, comme si "rien n'avait été fait").
///
/// Reprend la même couverture géométrique que les anciens tests widget de
/// badge_builder_canvas_test.dart (conversion de repère, tracé plume,
/// coordonnées négatives reproduisant un cas réel, élément sans rapport
/// intercalé), adaptée pour appeler `bakeSubtraction` directement plutôt
/// que d'inspecter un `ClipPath` recalculé en direct.
void main() {
  /// Reconstruit le `Path` d'un polygone gravé (segments droits, voir
  /// `cutoutPaths`) dans le repère LOCAL de [target] (0,0)-(width,height) —
  /// exactement ce que fait `_CutoutClipper`/`_cutoutClipPath`, dupliqué
  /// ici en clair pour tester directement les données produites par
  /// `bakeSubtraction`, sans dépendre d'un widget pompé.
  Path polygonPath(List<BadgePathPoint> polygon, double width, double height) {
    final path = Path();
    if (polygon.isEmpty) return path;
    Offset denorm(BadgePathPoint p) => Offset(p.x * width, p.y * height);
    final first = denorm(polygon.first);
    path.moveTo(first.dx, first.dy);
    for (final p in polygon.skip(1)) {
      final o = denorm(p);
      path.lineTo(o.dx, o.dy);
    }
    path.close();
    return path;
  }

  test(
    'le trou d\'une forme soustractive tombe au bon endroit sur un élément '
    'qui n\'est PAS positionné à (0,0) — la découpe se calcule dans le '
    'repère ABSOLU du canevas mais doit être gravée dans le repère LOCAL '
    'de l\'élément découpé ; sans conversion, le trou se retrouve décalé '
    'de (x,y) de cet élément (symptôme historique : un tracé qui '
    'chevauche visuellement un rectangle mais ne le découpe jamais)',
    () {
      // "blue" n'est PAS à l'origine : exactement le cas qui révèle un
      // mélange repère absolu / repère local.
      final blue = BadgeElement(
        id: 'blue',
        type: BadgeElementType.shape,
        x: 50,
        y: 50,
        width: 200,
        height: 200,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 0xFF0000FF,
      );
      final cutter = BadgeElement(
        id: 'cutter',
        type: BadgeElementType.shape,
        x: 100,
        y: 100,
        width: 50,
        height: 50,
        zIndex: 10,
        shapeKind: BadgeShapeKind.rectangle,
      );
      final sorted = [blue, cutter];

      bakeSubtraction(cutter, sorted);

      expect(blue.cutoutPaths, hasLength(1));
      final clip = polygonPath(blue.cutoutPaths.single, blue.width, blue.height);

      // "cutter" (modèle 100,100 à 150,150) recouvre "blue" (modèle 50,50
      // à 250,250) sur son propre repère LOCAL de (50,50) à (100,100) —
      // donc son centre local (75,75) doit être DANS le trou, et un point
      // clairement en dehors (10,10) ne doit pas y être.
      expect(clip.contains(const Offset(75, 75)), isTrue, reason: 'le centre de la zone recouverte par "cutter" doit être gravé dans le trou');
      expect(clip.contains(const Offset(10, 10)), isFalse, reason: 'un point de "blue" clairement hors de "cutter" ne doit pas être dans le trou');
    },
  );

  test(
    'un tracé PLUME fermé (courbe de Bézier, pas un simple rectangle) '
    'découpe correctement un élément qu\'il recouvre — reproduit '
    'fidèlement le cas rapporté (outil plume, "Forme fermée" cochée) '
    'plutôt qu\'un simple rectangle comme découpeur',
    () {
      final green = BadgeElement(
        id: 'green',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 300,
        height: 300,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 0xFF00FF00,
      );
      // Un "blob" fermé à 4 points avec de vraies poignées de courbe
      // (comme un tracé à la plume), pas un simple polygone.
      BadgePathPoint anchor(double x, double y, double hx, double hy) =>
          BadgePathPoint(x: x, y: y, inX: -hx, inY: -hy, outX: hx, outY: hy);
      final cutter = BadgeElement(
        id: 'cutter',
        type: BadgeElementType.shape,
        x: 50,
        y: 50,
        width: 200,
        height: 200,
        zIndex: 10,
        shapeKind: BadgeShapeKind.path,
        pathClosed: true,
        pathPoints: [
          anchor(0.5, 0.05, 0.2, 0),
          anchor(0.95, 0.5, 0, 0.2),
          anchor(0.5, 0.95, -0.2, 0),
          anchor(0.05, 0.5, 0, -0.2),
        ],
      );
      final sorted = [green, cutter];

      bakeSubtraction(cutter, sorted);

      expect(green.cutoutPaths, hasLength(1));
      final clip = polygonPath(green.cutoutPaths.single, green.width, green.height);

      // Centre de "cutter" en repère local de "green" : cutter est à
      // (50,50)-(250,250) modèle, son centre (150,150) devient, en local
      // à green (qui commence à (0,0)), (150,150) — bien à l'intérieur du
      // blob fermé.
      expect(clip.contains(const Offset(150, 150)), isTrue, reason: 'le centre du tracé plume fermé doit être gravé dans le trou');
      expect(clip.contains(const Offset(5, 5)), isFalse, reason: 'un coin de "green" loin du tracé ne doit pas être dans le trou');
    },
  );

  test(
    'reproduit EXACTEMENT les données réelles rapportées (coordonnées x/y '
    'NÉGATIVES) : "cutter" chevauche géométriquement à la fois "green" ET '
    '"blue" — les deux doivent être découpés (pas de notion d\'occlusion '
    'entre deux éléments empilés sans système de calques/groupes '
    'explicite, un compromis assumé)',
    () {
      final blue = BadgeElement(
        id: 'blue',
        type: BadgeElementType.shape,
        x: -414.2293621416317,
        y: -86.88220148380782,
        width: 1189.5317211116505,
        height: 1125.190111440669,
        zIndex: 0,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 4279150057,
      );
      final green = BadgeElement(
        id: 'green',
        type: BadgeElementType.shape,
        x: -10.484926642610011,
        y: -4.551399577118357,
        width: 680.0468915049693,
        height: 370.8823198432713,
        zIndex: 2,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 4279286145,
      );
      final cutter = BadgeElement(
        id: 'cutter',
        type: BadgeElementType.shape,
        x: 145.53871394442865,
        y: 232.04287623856064,
        width: 264.2198281065127,
        height: 157.32269993975328,
        zIndex: 3,
        shapeKind: BadgeShapeKind.path,
        pathClosed: true,
        strokeColor: 4278203238,
        pathPoints: [
          BadgePathPoint(x: 0.7914285580271081, y: 1.0),
          BadgePathPoint(x: 0.0, y: 0.99751942924115),
          BadgePathPoint(x: 0.10746432474604785, y: 0.0),
          BadgePathPoint(x: 1.0, y: 0.1280307996908478),
        ],
      );
      final sorted = [blue, green, cutter];

      bakeSubtraction(cutter, sorted);

      final cutterCenterModel = Offset(cutter.x + cutter.width / 2, cutter.y + cutter.height / 2);
      for (final el in [green, blue]) {
        expect(el.cutoutPaths, hasLength(1), reason: '"${el.id}" doit avoir reçu un trou (les deux chevauchent "cutter")');
        final clip = polygonPath(el.cutoutPaths.single, el.width, el.height);
        final cutterCenterLocal = cutterCenterModel - Offset(el.x, el.y);
        expect(clip.contains(cutterCenterLocal), isTrue, reason: 'le centre du tracé doit être gravé dans le trou de "${el.id}"');
      }
    },
  );

  test(
    'un élément SANS RAPPORT (qui ne chevauche pas le tracé) intercalé '
    'dans la liste entre deux rectangles et le tracé ne doit PAS empêcher '
    'la découpe d\'atteindre le rectangle le plus loin — symptôme '
    'rapporté : un QR code/champ texte ajouté entre-temps faisait que la '
    'découpe s\'appliquait à CET élément sans rapport plutôt qu\'aux '
    'rectangles pourtant visuellement recouverts par le tracé',
    () {
      final rect1 = BadgeElement(
        id: 'rect1',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 600,
        height: 900,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 0xFFFFFF00,
      );
      // Ne chevauche PAS le tracé (voir plus bas) — inséré ENTRE rect1 et
      // le tracé dans la liste, comme le QR code/les champs texte du cas
      // rapporté.
      final unrelated = BadgeElement(
        id: 'unrelated',
        type: BadgeElementType.qrPlaceholder,
        x: 880,
        y: 530,
        width: 90,
        height: 90,
      );
      final cutter = BadgeElement(
        id: 'cutter',
        type: BadgeElementType.shape,
        x: 100,
        y: 100,
        width: 300,
        height: 300,
        shapeKind: BadgeShapeKind.rectangle,
      );
      final sorted = [rect1, unrelated, cutter];

      bakeSubtraction(cutter, sorted);

      expect(
        rect1.cutoutPaths,
        hasLength(1),
        reason: '"rect1" doit être découpé malgré "unrelated" (sans rapport, sans chevauchement) inséré entre les deux dans la liste',
      );
      expect(unrelated.cutoutPaths, isEmpty, reason: '"unrelated" ne chevauche pas "cutter", ne doit recevoir aucun trou');

      final clip = polygonPath(rect1.cutoutPaths.single, rect1.width, rect1.height);
      final cutterCenterModel = Offset(cutter.x + cutter.width / 2, cutter.y + cutter.height / 2);
      final cutterCenterLocal = cutterCenterModel - Offset(rect1.x, rect1.y);
      expect(clip.contains(cutterCenterLocal), isTrue, reason: 'le centre du tracé doit être gravé dans le trou de "rect1"');
    },
  );

  test('une forme soustractive ne se découpe jamais elle-même et ne touche rien au-dessus d\'elle', () {
    final below = BadgeElement(id: 'below', type: BadgeElementType.shape, x: 0, y: 0, width: 100, height: 100);
    final cutter = BadgeElement(id: 'cutter', type: BadgeElementType.shape, x: 0, y: 0, width: 100, height: 100, zIndex: 1);
    final above = BadgeElement(id: 'above', type: BadgeElementType.shape, x: 0, y: 0, width: 100, height: 100, zIndex: 2);
    final sorted = [below, cutter, above];

    bakeSubtraction(cutter, sorted);

    expect(below.cutoutPaths, hasLength(1));
    expect(cutter.cutoutPaths, isEmpty, reason: 'une forme ne peut pas se découper elle-même');
    expect(above.cutoutPaths, isEmpty, reason: 'un élément peint APRÈS le découpeur (au-dessus) ne doit jamais être affecté');
  });

  test(
    'un élément "locked" (panneau des calques, protection contre la '
    'découpe — voir models/badge_layout.dart) ne reçoit JAMAIS de trou, '
    'même s\'il chevauche réellement le découpeur',
    () {
      final protectedBg = BadgeElement(
        id: 'bg',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 300,
        height: 300,
        locked: true,
      );
      final cutter = BadgeElement(id: 'cutter', type: BadgeElementType.shape, x: 50, y: 50, width: 100, height: 100, zIndex: 1);
      final sorted = [protectedBg, cutter];

      bakeSubtraction(cutter, sorted);

      expect(protectedBg.cutoutPaths, isEmpty, reason: 'un élément verrouillé doit rester intact malgré le chevauchement réel');
    },
  );

  test('aucun chevauchement géométrique réel : aucun trou gravé', () {
    final farAway = BadgeElement(id: 'far', type: BadgeElementType.shape, x: 1000, y: 1000, width: 50, height: 50);
    final cutter = BadgeElement(id: 'cutter', type: BadgeElementType.shape, x: 0, y: 0, width: 50, height: 50, zIndex: 1);
    final sorted = [farAway, cutter];

    bakeSubtraction(cutter, sorted);

    expect(farAway.cutoutPaths, isEmpty, reason: 'sans chevauchement géométrique réel, aucun trou ne doit être gravé');
  });
}
