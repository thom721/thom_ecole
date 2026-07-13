import 'dart:math' as math;

import '../models/badge_layout.dart';

/// Les 10 gabarits de démarrage (5 paysage, 5 portrait) — fonds en
/// dégradé colorés avec un halo décoratif en tracé bézier (voir
/// [_blobPoints]) et un bandeau blanc inférieur, prêts à être modifiés
/// dans l'éditeur (screens/etudiant/badge_builder/). Enregistrés une
/// seule fois via `BadgeLayoutStore.list()` (voir
/// badge_layout_store.dart::_ensureSeedTemplates) — identifiants FIXES
/// (pas `BadgeLayoutStore.newId()`, horodaté) pour rester stables d'un
/// lancement à l'autre.
///
/// Contrairement à `badge_builder_screen.dart::_standardBadgeElements`
/// (auto-placement optionnel dans l'éditeur, voir "Charger un template"),
/// ces gabarits de démarrage ne placent QUE le titre, la photo et le QR —
/// les informations propres à l'étudiant (nom, prénom, classe,
/// identifiant, expiration, salle) restent à placer manuellement, un
/// gabarit de démarrage n'ayant aucun moyen de deviner où l'utilisateur
/// voudra les mettre sur SON design.
class _SeedSpec {
  const _SeedSpec(
    this.id,
    this.name,
    this.isLandscape,
    this.colorA,
    this.colorB, {
    this.blobVariant = 0,
    this.blobRotationDeg = 0,
    this.photoX,
  });
  final String id;
  final String name;
  final bool isLandscape;
  final int colorA;
  final int colorB;

  /// Index dans [_blobRadiiVariants] — fait varier la FORME du halo
  /// décoratif d'un gabarit à l'autre, plutôt que le même ovale répété
  /// identiquement sur les 10 (ce qui les faisait tous se ressembler).
  final int blobVariant;

  /// Pivote le point de départ du tracé — deux gabarits avec le même
  /// [blobVariant] gardent quand même une allure différente.
  final double blobRotationDeg;

  /// Position horizontale de la photo — `null` garde la position par
  /// défaut (gauche en paysage, centrée en portrait) ; un petit nombre de
  /// gabarits la déplacent (droite/centre) pour varier, sans le faire
  /// systématiquement.
  final double? photoX;
}

// Couleurs reprises de la palette des cartes du dashboard
// (theme/app_theme.dart::_darkCardPalette) pour rester cohérent avec le
// reste de l'app plutôt que d'inventer une palette séparée.
const _seedSpecs = [
  _SeedSpec('seed_badge_ocean', 'Océan (paysage)', true, 0xFF0EA5E9, 0xFF06B6D4, blobVariant: 0, blobRotationDeg: 0),
  _SeedSpec(
    'seed_badge_emeraude',
    'Émeraude (paysage)',
    true,
    0xFF10B981,
    0xFF06B6D4,
    blobVariant: 1,
    blobRotationDeg: 25,
  ),
  _SeedSpec(
    'seed_badge_violet',
    'Violet Prestige (paysage)',
    true,
    0xFF8B5CF6,
    0xFFA855F7,
    blobVariant: 2,
    blobRotationDeg: -15,
    photoX: 682, // droite (défaut : gauche)
  ),
  _SeedSpec(
    'seed_badge_sunset',
    'Coucher de Soleil (paysage)',
    true,
    0xFFF59E0B,
    0xFFF43F5E,
    blobVariant: 0,
    blobRotationDeg: 50,
    photoX: 390, // centre (défaut : gauche)
  ),
  _SeedSpec(
    'seed_badge_rose',
    'Rose Élégance (paysage)',
    true,
    0xFFF43F5E,
    0xFFA855F7,
    blobVariant: 1,
    blobRotationDeg: -35,
  ),
  _SeedSpec('seed_badge_ciel', 'Ciel (portrait)', false, 0xFF4F8EF7, 0xFF0EA5E9, blobVariant: 2, blobRotationDeg: 10),
  _SeedSpec(
    'seed_badge_foret',
    'Forêt (portrait)',
    false,
    0xFF10B981,
    0xFF4F8EF7,
    blobVariant: 0,
    blobRotationDeg: -40,
    photoX: 40, // gauche (défaut : centre)
  ),
  _SeedSpec(
    'seed_badge_corail',
    'Corail (portrait)',
    false,
    0xFFF43F5E,
    0xFFF59E0B,
    blobVariant: 1,
    blobRotationDeg: 20,
  ),
  _SeedSpec(
    'seed_badge_rubis',
    'Rubis (portrait)',
    false,
    0xFFF43F5E,
    0xFF8B5CF6,
    blobVariant: 2,
    blobRotationDeg: -10,
    photoX: 398, // droite (défaut : centre)
  ),
  _SeedSpec(
    'seed_badge_indigo',
    'Indigo Nuit (portrait)',
    false,
    0xFF8B5CF6,
    0xFF4F8EF7,
    blobVariant: 0,
    blobRotationDeg: 35,
  ),
];

List<BadgeLayoutTemplate> buildSeedBadgeTemplates() => _seedSpecs.map(_buildTemplate).toList();

BadgeLayoutTemplate _buildTemplate(_SeedSpec spec) {
  final elements = [
    ..._backgroundElements(spec.colorA, spec.colorB, spec.isLandscape, spec.blobVariant, spec.blobRotationDeg),
    ..._contentElements(spec.isLandscape, photoX: spec.photoX),
  ];
  return BadgeLayoutTemplate(
    id: spec.id,
    name: spec.name,
    isLandscape: spec.isLandscape,
    recto: BadgeSide(elements: elements),
  );
}

/// Rayons (0..1, distance au centre de la boîte de l'élément) de quelques
/// points répartis à angle égal autour d'un cercle — la base d'un halo
/// "blob" irrégulier mais lisse (voir [_blobPoints]). Trois jeux distincts
/// (arrondi doux / pétale allongé / asymétrique) pour que les 10 gabarits
/// n'affichent plus tous exactement le même ovale.
const _blobRadiiVariants = [
  [0.46, 0.40, 0.44, 0.38, 0.42],
  [0.48, 0.28, 0.46, 0.26, 0.44],
  [0.40, 0.46, 0.28, 0.44, 0.34],
];

/// Construit un tracé bézier fermé pour le halo décoratif — les points
/// eux-mêmes sont irréguliers ([_blobRadiiVariants]) mais les poignées
/// entrante/sortante restent tangentes au cercle sous-jacent (magnitude
/// ≈ 0.43×rayon, l'approximation classique d'un arc de cercle par une
/// courbe de Bézier cubique pour un pas angulaire de 360°/n), ce qui
/// donne un contour organique lisse plutôt qu'un polygone à coins vifs.
/// [rotationDeg] tourne le point de départ pour varier l'allure d'un
/// gabarit à l'autre même à rayons identiques.
List<BadgePathPoint> _blobPoints(int variant, double rotationDeg) {
  final radii = _blobRadiiVariants[variant % _blobRadiiVariants.length];
  final n = radii.length;
  final points = <BadgePathPoint>[];
  for (var i = 0; i < n; i++) {
    final angle = (rotationDeg + 360 * i / n) * math.pi / 180;
    final r = radii[i];
    final cx = 0.5 + r * math.cos(angle);
    final cy = 0.5 + r * math.sin(angle);
    final tangentMag = r * 0.43;
    final outX = -math.sin(angle) * tangentMag;
    final outY = math.cos(angle) * tangentMag;
    points.add(BadgePathPoint(x: cx, y: cy, outX: outX, outY: outY, inX: -outX, inY: -outY));
  }
  return points;
}

/// Fond dégradé + halo décoratif (tracé bézier, [_blobPoints]) + bandeau
/// blanc inférieur (pour les champs id/expiration/salle, plus lisibles
/// sur blanc que sur le dégradé) — communs aux 10 gabarits, les couleurs
/// ET la forme du halo changent d'un gabarit à l'autre.
List<BadgeElement> _backgroundElements(
  int colorA,
  int colorB,
  bool isLandscape,
  int blobVariant,
  double blobRotationDeg,
) {
  final w = isLandscape ? kBadgeLandscapeWidth : kBadgeLandscapeHeight;
  final h = isLandscape ? kBadgeLandscapeHeight : kBadgeLandscapeWidth;
  final panelHeight = h * 0.34;
  return [
    BadgeElement(
      id: 'bg',
      type: BadgeElementType.shape,
      x: 0,
      y: 0,
      width: w,
      height: h,
      shapeKind: BadgeShapeKind.rectangle,
      fillGradient: BadgeGradient(
        type: BadgeGradientType.linear,
        angleDegrees: 135,
        stops: [BadgeGradientStop(color: colorA, offset: 0), BadgeGradientStop(color: colorB, offset: 1)],
      ),
      zIndex: -30,
    ),
    BadgeElement(
      id: 'blob',
      type: BadgeElementType.shape,
      x: w * 0.68,
      y: -h * 0.12,
      width: w * 0.42,
      height: w * 0.42,
      shapeKind: BadgeShapeKind.path,
      pathPoints: _blobPoints(blobVariant, blobRotationDeg),
      pathClosed: true,
      fillColor: 0x26FFFFFF,
      zIndex: -25,
    ),
    BadgeElement(
      id: 'panel',
      type: BadgeElementType.shape,
      x: 0,
      y: h - panelHeight,
      width: w,
      height: panelHeight,
      shapeKind: BadgeShapeKind.rectangle,
      fillColor: 0xFFFFFFFF,
      zIndex: -20,
    ),
  ];
}

/// Titre, photo et QR déjà positionnés — mêmes rôles que
/// `badge_builder_screen.dart::_standardBadgeElements`, coordonnées
/// adaptées à l'orientation puisque le paysage (1013×638) et le portrait
/// (638×1013) ne peuvent pas partager la même disposition. Les
/// informations propres à l'étudiant (nom, prénom, classe, identifiant,
/// expiration, salle) sont volontairement ABSENTES : un gabarit de
/// démarrage générique n'a aucun moyen de deviner où l'utilisateur voudra
/// les placer sur son design — il les ajoute lui-même dans l'éditeur
/// (toolbar "Ajouter un champ"), comme pour un template importé (voir
/// badge_builder_screen.dart::_loadTemplateImage, qui laisse le même
/// choix pour un visuel importé).
List<BadgeElement> _contentElements(bool isLandscape, {double? photoX}) {
  const white = 0xFFFFFFFF;

  BadgeElement text({
    required String id,
    required double x,
    required double y,
    required double width,
    required double height,
    required String text,
    required double fontSize,
    bool bold = false,
    int color = white,
    BadgeTextAlign align = BadgeTextAlign.center,
  }) => BadgeElement(
    id: id,
    type: BadgeElementType.text,
    x: x,
    y: y,
    width: width,
    height: height,
    text: text,
    fontSize: fontSize,
    bold: bold,
    color: color,
    textAlign: align,
    zIndex: 1,
  );

  if (isLandscape) {
    return [
      text(id: 'title', x: 0, y: 34, width: 1013, height: 44, text: 'Nom de l\'école', fontSize: 24, bold: true),
      BadgeElement(
        id: 'photo',
        type: BadgeElementType.photoPlaceholder,
        x: photoX ?? 97,
        y: 110,
        width: 234,
        height: 261,
        shapeKind: BadgeShapeKind.roundedRectangle,
        cornerRadius: 14,
        strokeColor: white,
        strokeWidth: 4,
        zIndex: 1,
      ),
      BadgeElement(id: 'qr', type: BadgeElementType.qrPlaceholder, x: 860, y: 460, width: 120, height: 120, zIndex: 1),
    ];
  }

  return [
    text(id: 'title', x: 0, y: 34, width: 638, height: 40, text: 'Nom de l\'école', fontSize: 20, bold: true),
    BadgeElement(
      id: 'photo',
      type: BadgeElementType.photoPlaceholder,
      x: photoX ?? 219,
      y: 100,
      width: 200,
      height: 223,
      shapeKind: BadgeShapeKind.roundedRectangle,
      cornerRadius: 14,
      strokeColor: white,
      strokeWidth: 4,
      zIndex: 1,
    ),
    BadgeElement(id: 'qr', type: BadgeElementType.qrPlaceholder, x: 249, y: 770, width: 140, height: 140, zIndex: 1),
  ];
}
