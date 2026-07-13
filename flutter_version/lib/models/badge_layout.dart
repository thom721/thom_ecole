import 'dart:convert';

/// Modèle d'un gabarit de badge construit dans l'éditeur visuel
/// (`screens/etudiant/badge_builder/`) — totalement distinct des 2
/// templates fixes (`template_badge_1`/`template_badge_2`, voir
/// `services/template_store.dart`) et du rendu à coordonnées figées de
/// `widgets/badge_renderer.dart`, qu'aucun des deux ne modifie.
///
/// Canvas toujours 1013×638 (paysage) ou 638×1013 (portrait) — mêmes
/// dimensions que `badge_renderer.dart` (8,5×5,1cm @300dpi), pas une
/// taille inventée pour l'éditeur.
const double kBadgeLandscapeWidth = 1013;
const double kBadgeLandscapeHeight = 638;

/// Pixels par centimètre à 300dpi — même référence que le commentaire
/// ci-dessus (8,5×5,1cm), utilisée par les règles graduées de l'éditeur
/// (badge_builder_canvas.dart) pour convertir l'échelle d'affichage en cm.
const double kBadgePxPerCm = 300 / 2.54;

/// Jetons de substitution reconnus dans le texte d'un `BadgeElement` —
/// source unique partagée par le panneau de propriétés (aperçu) et le
/// renderer (substitution réelle), pour éviter deux listes divergentes.
const List<String> kBadgePlaceholderTokens = [
  '{{nom}}',
  '{{prenom}}',
  '{{classe}}',
  '{{identifiant}}',
  '{{expiration}}',
  '{{salle}}',
];

/// Valeur factice utilisée par le menu "Champ dynamique" (barre d'outils)
/// pour son option "Personnalisé" — sélectionner cette valeur ajoute un
/// texte libre ordinaire (comme le bouton "Ajouter du texte libre")
/// plutôt qu'un jeton de `kBadgePlaceholderTokens` ; un identifiant
/// partagé évite de dupliquer la chaîne magique entre la barre d'outils
/// et l'écran qui la traite.
const kBadgeCustomFieldToken = '__custom_text__';

// `staticImage` : un fichier (logo, signature scannée...) choisi UNE FOIS
// dans l'éditeur et identique sur chaque badge généré — contrairement à
// `photoPlaceholder`, qui affiche une photo DIFFÉRENTE par étudiant.
enum BadgeElementType {
  text,
  photoPlaceholder,
  qrPlaceholder,
  shape,
  staticImage,
}

enum BadgeShapeKind { rectangle, roundedRectangle, oval, line, curve, path }

enum BadgeStrokeStyle { solid, dashed, dotted }

enum BadgeTextAlign { left, center, right }

enum BadgePhotoFit { centerCrop, contain }

enum BadgeGradientType { linear, radial }

/// Un point ancre d'un tracé libre (`BadgeShapeKind.path`, outil plume) —
/// coordonnées NORMALISÉES (0..1, fraction de `el.width`/`el.height`) pour
/// que le tracé suive automatiquement un redimensionnement de l'élément
/// sans recalcul. [inX]/[inY]/[outX]/[outY] sont des décalages RELATIFS à
/// l'ancre (mêmes unités normalisées) pour les poignées de courbure
/// entrante/sortante façon Illustrator ; `null` = pas de poignée (segment
/// droit de ce côté).
class BadgePathPoint {
  BadgePathPoint({
    required this.x,
    required this.y,
    this.inX,
    this.inY,
    this.outX,
    this.outY,
  });

  factory BadgePathPoint.fromJson(Map<String, dynamic> json) => BadgePathPoint(
    x: (json['x'] as num).toDouble(),
    y: (json['y'] as num).toDouble(),
    inX: (json['inX'] as num?)?.toDouble(),
    inY: (json['inY'] as num?)?.toDouble(),
    outX: (json['outX'] as num?)?.toDouble(),
    outY: (json['outY'] as num?)?.toDouble(),
  );

  double x;
  double y;
  double? inX;
  double? inY;
  double? outX;
  double? outY;

  Map<String, dynamic> toJson() => {
    'x': x,
    'y': y,
    'inX': inX,
    'inY': inY,
    'outX': outX,
    'outY': outY,
  };
}

/// Un arrêt de couleur dans un dégradé — [offset] entre 0 (début) et 1 (fin).
class BadgeGradientStop {
  BadgeGradientStop({required this.color, required this.offset});

  factory BadgeGradientStop.fromJson(Map<String, dynamic> json) =>
      BadgeGradientStop(
        color: json['color'] as int,
        offset: (json['offset'] as num).toDouble(),
      );

  int color;
  double offset;

  Map<String, dynamic> toJson() => {'color': color, 'offset': offset};
}

/// Dégradé de remplissage — linéaire (direction réglable via
/// [angleDegrees]) ou radial (toujours centré sur la boîte de l'élément),
/// au moins 2 [stops].
class BadgeGradient {
  BadgeGradient({
    required this.type,
    required this.stops,
    this.angleDegrees = 0,
  });

  factory BadgeGradient.fromJson(Map<String, dynamic> json) => BadgeGradient(
    type: BadgeGradientType.values.byName(json['type'] as String),
    stops: (json['stops'] as List)
        .map((s) => BadgeGradientStop.fromJson(s as Map<String, dynamic>))
        .toList(),
    angleDegrees: (json['angleDegrees'] as num?)?.toDouble() ?? 0,
  );

  BadgeGradientType type;
  List<BadgeGradientStop> stops;
  double angleDegrees;

  Map<String, dynamic> toJson() => {
    'type': type.name,
    'stops': stops.map((s) => s.toJson()).toList(),
    'angleDegrees': angleDegrees,
  };
}

/// Un élément positionné sur une face (recto ou verso) du badge. Mutable
/// à dessein : pendant un glisser/redimensionner/pivoter, l'instance est
/// modifiée en place puis `setState` déclenché — reconstruire via
/// `copyWith` à chaque pixel de déplacement serait inutilement coûteux.
class BadgeElement {
  BadgeElement({
    required this.id,
    required this.type,
    required this.x,
    required this.y,
    required this.width,
    required this.height,
    this.rotationDegrees = 0,
    this.zIndex = 0,
    this.text,
    this.fontFamily,
    this.fontSize,
    this.bold = false,
    this.italic = false,
    this.color,
    this.textAlign = BadgeTextAlign.left,
    this.shapeKind,
    this.strokeColor,
    this.strokeWidth,
    this.strokeStyle = BadgeStrokeStyle.solid,
    this.fillColor,
    this.cornerRadius,
    this.fit = BadgePhotoFit.centerCrop,
    List<BadgePathPoint>? pathPoints,
    this.pathClosed = true,
    this.fillGradient,
    this.photoBrightness = 0,
    this.photoContrast = 1,
    this.photoSaturation = 1,
    this.photoOffsetX = 0.5,
    this.photoOffsetY = 0.5,
    this.photoZoom = 1,
    this.qrCustomData,
    this.subtractBackground = false,
    List<List<BadgePathPoint>>? cutoutPaths,
    this.imagePath,
    this.hidden = false,
    this.locked = false,
  }) : pathPoints = pathPoints ?? [],
       cutoutPaths = cutoutPaths ?? [];

  factory BadgeElement.fromJson(Map<String, dynamic> json) {
    return BadgeElement(
      id: json['id'] as String,
      type: BadgeElementType.values.byName(json['type'] as String),
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
      width: (json['width'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
      rotationDegrees: (json['rotationDegrees'] as num?)?.toDouble() ?? 0,
      zIndex: (json['zIndex'] as num?)?.toInt() ?? 0,
      text: json['text'] as String?,
      fontFamily: json['fontFamily'] as String?,
      fontSize: (json['fontSize'] as num?)?.toDouble(),
      bold: json['bold'] as bool? ?? false,
      italic: json['italic'] as bool? ?? false,
      color: json['color'] as int?,
      textAlign: json['textAlign'] == null
          ? BadgeTextAlign.left
          : BadgeTextAlign.values.byName(json['textAlign'] as String),
      shapeKind: json['shapeKind'] == null
          ? null
          : BadgeShapeKind.values.byName(json['shapeKind'] as String),
      strokeColor: json['strokeColor'] as int?,
      strokeWidth: (json['strokeWidth'] as num?)?.toDouble(),
      strokeStyle: json['strokeStyle'] == null
          ? BadgeStrokeStyle.solid
          : BadgeStrokeStyle.values.byName(json['strokeStyle'] as String),
      fillColor: json['fillColor'] as int?,
      cornerRadius: (json['cornerRadius'] as num?)?.toDouble(),
      fit: json['fit'] == null
          ? BadgePhotoFit.centerCrop
          : BadgePhotoFit.values.byName(json['fit'] as String),
      pathPoints: (json['pathPoints'] as List?)
          ?.map((p) => BadgePathPoint.fromJson(p as Map<String, dynamic>))
          .toList(),
      pathClosed: json['pathClosed'] as bool? ?? true,
      fillGradient: json['fillGradient'] == null
          ? null
          : BadgeGradient.fromJson(
              json['fillGradient'] as Map<String, dynamic>,
            ),
      photoBrightness: (json['photoBrightness'] as num?)?.toDouble() ?? 0,
      photoContrast: (json['photoContrast'] as num?)?.toDouble() ?? 1,
      photoSaturation: (json['photoSaturation'] as num?)?.toDouble() ?? 1,
      photoOffsetX: (json['photoOffsetX'] as num?)?.toDouble() ?? 0.5,
      photoOffsetY: (json['photoOffsetY'] as num?)?.toDouble() ?? 0.5,
      photoZoom: (json['photoZoom'] as num?)?.toDouble() ?? 1,
      qrCustomData: json['qrCustomData'] as String?,
      subtractBackground: json['subtractBackground'] as bool? ?? false,
      cutoutPaths: (json['cutoutPaths'] as List?)
          ?.map(
            (polygon) => (polygon as List)
                .map((p) => BadgePathPoint.fromJson(p as Map<String, dynamic>))
                .toList(),
          )
          .toList(),
      imagePath: json['imagePath'] as String?,
      hidden: json['hidden'] as bool? ?? false,
      locked: json['locked'] as bool? ?? false,
    );
  }

  String id;
  BadgeElementType type;
  double x;
  double y;
  double width;
  double height;
  double rotationDegrees;
  int zIndex;

  // Texte
  String? text;
  String? fontFamily;
  double? fontSize;
  bool bold;
  bool italic;
  int? color;
  BadgeTextAlign textAlign;

  // Forme / traces (bordures, cadres — border du badge, cadre photo...)
  BadgeShapeKind? shapeKind;
  int? strokeColor;
  double? strokeWidth;
  BadgeStrokeStyle strokeStyle;
  int? fillColor;
  // Rayon des coins pour `roundedRectangle` ; réutilisé comme hauteur de
  // bulle pour `curve` (courbe de Bézier quadratique dans la boîte de
  // l'élément) — un seul champ, deux significations selon `shapeKind`.
  double? cornerRadius;

  // Photo — le cadre (shapeKind/cornerRadius : rectangle, arrondi, cercle)
  // et la bordure (strokeColor/strokeWidth/strokeStyle) réutilisent les
  // mêmes champs que les éléments "forme" ci-dessus.
  BadgePhotoFit fit;

  // Tracé libre (`BadgeShapeKind.path`, outil plume) — voir BadgePathPoint.
  List<BadgePathPoint> pathPoints;
  bool pathClosed;

  // Remplissage en dégradé — prioritaire sur `fillColor` quand non-null,
  // pour les formes fermables (rectangle/arrondi/ovale/tracé).
  BadgeGradient? fillGradient;

  // Réglages persistés de la photo — appliqués à la photo de CHAQUE
  // étudiant au moment de générer un badge réel (pas seulement à une
  // photo test pendant la conception), voir widgets/badge_photo_effects.dart.
  // brightness: -1..1 (0 = neutre) ; contrast/saturation: 0..2 (1 = neutre,
  // saturation 0 = noir et blanc) ; offsetX/offsetY: 0..1, point focal du
  // recadrage (0.5,0.5 = centré) ; zoom: >=1 (1 = pas de zoom).
  double photoBrightness;
  double photoContrast;
  double photoSaturation;
  double photoOffsetX;
  double photoOffsetY;
  double photoZoom;

  // Donnée QR personnalisée — prioritaire sur la donnée automatique (le
  // contact du responsable de l'étudiant, calculée par badge_screen.dart)
  // quand non-null/non-vide ; sert de repli pour les cas où cette
  // information n'est pas disponible ou pas pertinente.
  String? qrCustomData;

  // Déclencheur PONCTUEL (jamais persisté à `true` — voir
  // badge_builder_screen.dart::_onElementChanged) : le passer à `true`
  // grave IMMÉDIATEMENT un trou PERMANENT dans chaque élément situé en
  // dessous (selon l'ordre de peinture) et RÉELLEMENT chevauché par cette
  // forme, dans LEUR PROPRE `cutoutPaths`, puis se réinitialise à `false`.
  // Ce n'est PAS un masque dynamique lié à la position courante de cette
  // forme : déplacer ou supprimer la forme après coup n'efface plus le
  // trou déjà gravé (comportement demandé explicitement après qu'un
  // premier essai, un masque `ClipPath` recalculé à chaque frame selon la
  // position courante de la forme, ait donné l'impression que "rien
  // n'était fait" — l'utilisateur déplaçait systématiquement la forme
  // après coup pour vérifier qu'un trou restait en place).
  bool subtractBackground;

  // Trous PERMANENTS gravés dans CET élément (voir `subtractBackground`
  // ci-dessus) — chaque polygone est en coordonnées NORMALISÉES (0..1,
  // fraction de `width`/`height` de CET élément, même repère que
  // `pathPoints`), point par point (segments droits, échantillonnés
  // depuis la forme découpeuse au moment de la découpe — pas de poignées
  // de courbure, un trou n'a plus besoin d'être réédité après coup).
  List<List<BadgePathPoint>> cutoutPaths;

  // Fichier choisi pour `BadgeElementType.staticImage` (logo, signature
  // scannée...) — copié dans `badge_layouts/images/` par
  // `BadgeLayoutStore.pickElementImage`, même mécanisme que
  // `BadgeSide.backgroundImagePath`.
  String? imagePath;

  // Panneau des calques (badge_builder_layers_panel.dart), style Adobe —
  // `hidden` : invisible et non sélectionnable dans l'aperçu ET absent de
  // l'export (comme un calque masqué dans Illustrator/Photoshop, pas
  // seulement un repère d'édition). `locked` : PROTÈGE cet élément contre
  // toute découpe reçue d'une AUTRE forme "Soustraire du fond"
  // ([bakeSubtraction] l'ignore comme cible) — utile pour un fond coloré
  // qu'on veut garder intact quand on découpe un élément voisin qui le
  // recouvre. Ne verrouille PAS la sélection/le déplacement (portée
  // volontairement limitée à ce qui a été demandé) et n'empêche pas cet
  // élément d'agir lui-même comme découpeur.
  bool hidden;
  bool locked;

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.name,
    'x': x,
    'y': y,
    'width': width,
    'height': height,
    'rotationDegrees': rotationDegrees,
    'zIndex': zIndex,
    'text': text,
    'fontFamily': fontFamily,
    'fontSize': fontSize,
    'bold': bold,
    'italic': italic,
    'color': color,
    'textAlign': textAlign.name,
    'shapeKind': shapeKind?.name,
    'strokeColor': strokeColor,
    'strokeWidth': strokeWidth,
    'strokeStyle': strokeStyle.name,
    'fillColor': fillColor,
    'cornerRadius': cornerRadius,
    'fit': fit.name,
    'pathPoints': pathPoints.map((p) => p.toJson()).toList(),
    'pathClosed': pathClosed,
    'fillGradient': fillGradient?.toJson(),
    'photoBrightness': photoBrightness,
    'photoContrast': photoContrast,
    'photoSaturation': photoSaturation,
    'photoOffsetX': photoOffsetX,
    'photoOffsetY': photoOffsetY,
    'photoZoom': photoZoom,
    'qrCustomData': qrCustomData,
    'subtractBackground': subtractBackground,
    'cutoutPaths': cutoutPaths
        .map((polygon) => polygon.map((p) => p.toJson()).toList())
        .toList(),
    'imagePath': imagePath,
    'hidden': hidden,
    'locked': locked,
  };

  BadgeElement clone() => BadgeElement.fromJson(toJson());
}

/// Une face (recto ou verso) d'un gabarit — son image de fond + ses
/// éléments positionnés.
class BadgeSide {
  BadgeSide({
    this.backgroundImagePath,
    List<BadgeElement>? elements,
    List<double>? guidesX,
    List<double>? guidesY,
  }) : elements = elements ?? [],
       guidesX = guidesX ?? [],
       guidesY = guidesY ?? [];

  factory BadgeSide.fromJson(Map<String, dynamic> json) => BadgeSide(
    backgroundImagePath: json['backgroundImagePath'] as String?,
    elements: (json['elements'] as List? ?? [])
        .map((e) => BadgeElement.fromJson(e as Map<String, dynamic>))
        .toList(),
    guidesX: (json['guidesX'] as List?)
        ?.map((v) => (v as num).toDouble())
        .toList(),
    guidesY: (json['guidesY'] as List?)
        ?.map((v) => (v as num).toDouble())
        .toList(),
  );

  String? backgroundImagePath;
  List<BadgeElement> elements;

  // Repères (guides) style Adobe/Figma — glissés depuis les règles de
  // l'éditeur (badge_builder_canvas.dart) pour aider à positionner/
  // dimensionner des éléments à l'œil. Purement visuels pendant l'édition
  // (jamais dessinés par widgets/badge_layout_renderer.dart, comme la
  // grille d'alignement) mais PERSISTÉS avec le gabarit — comme dans
  // Adobe, un repère placé une fois reste disponible aux prochaines
  // ouvertures. Unités modèle, position absolue sur le canevas.
  List<double> guidesX;
  List<double> guidesY;

  Map<String, dynamic> toJson() => {
    'backgroundImagePath': backgroundImagePath,
    'elements': elements.map((e) => e.toJson()).toList(),
    'guidesX': guidesX,
    'guidesY': guidesY,
  };
}

/// Un gabarit de badge complet, éventuellement recto-verso — sauvegardé
/// localement via `services/badge_layout_store.dart`.
class BadgeLayoutTemplate {
  BadgeLayoutTemplate({
    required this.id,
    required this.name,
    this.isLandscape = true,
    BadgeSide? recto,
    this.verso,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) : recto = recto ?? BadgeSide(),
       createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  factory BadgeLayoutTemplate.fromJson(Map<String, dynamic> json) {
    return BadgeLayoutTemplate(
      id: json['id'] as String,
      name: json['name'] as String,
      isLandscape: json['isLandscape'] as bool? ?? true,
      recto: BadgeSide.fromJson(json['recto'] as Map<String, dynamic>),
      verso: json['verso'] == null
          ? null
          : BadgeSide.fromJson(json['verso'] as Map<String, dynamic>),
      createdAt: DateTime.tryParse(json['createdAt'] as String? ?? ''),
      updatedAt: DateTime.tryParse(json['updatedAt'] as String? ?? ''),
    );
  }

  factory BadgeLayoutTemplate.fromJsonString(String source) =>
      BadgeLayoutTemplate.fromJson(jsonDecode(source) as Map<String, dynamic>);

  String id;
  String name;
  bool isLandscape;
  BadgeSide recto;
  BadgeSide? verso;
  DateTime createdAt;
  DateTime updatedAt;

  double get canvasWidth =>
      isLandscape ? kBadgeLandscapeWidth : kBadgeLandscapeHeight;
  double get canvasHeight =>
      isLandscape ? kBadgeLandscapeHeight : kBadgeLandscapeWidth;

  bool get hasVerso => verso != null;

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'isLandscape': isLandscape,
    'recto': recto.toJson(),
    'verso': verso?.toJson(),
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  String toJsonString() => jsonEncode(toJson());
}
