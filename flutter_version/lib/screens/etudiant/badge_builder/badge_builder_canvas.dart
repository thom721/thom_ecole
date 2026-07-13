import 'dart:io';
import 'dart:math' show cos, pi, sin;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../../models/badge_layout.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_canvas_element.dart';
import '../../../widgets/badge_photo_effects.dart';

/// Zone d'édition visuelle d'une face du gabarit — fond (image choisie ou
/// gris neutre) + un [BadgeCanvasElement] par élément de [side]. L'aperçu
/// des formes (traits pointillés/pointillés) reste simplifié ici (trait
/// plein) pour la fluidité de l'édition ; le rendu exporté
/// (`widgets/badge_layout_renderer.dart`) applique le style réel.
class BadgeBuilderCanvas extends StatelessWidget {
  const BadgeBuilderCanvas({
    super.key,
    required this.layout,
    required this.side,
    required this.selectedId,
    required this.onSelect,
    required this.onElementChanged,
    this.penActive = false,
    this.penDraft = const [],
    this.onPenPointerDown,
    this.onPenDrag,
    this.previewValues = const {},
    this.previewPhotoBytes,
    this.previewQrData,
    this.onGuideCreateStart,
    this.onGuideMoveStart,
    this.onGuideDragUpdate,
    this.onGuideDragEnd,
    this.editingPathElementId,
  });

  final BadgeLayoutTemplate layout;
  final BadgeSide side;
  final String? selectedId;
  final ValueChanged<String?> onSelect;
  final ValueChanged<BadgeElement> onElementChanged;

  /// Aperçu en direct avec de vraies données — voir
  /// badge_builder_screen.dart (recherche d'étudiant / photo test). Un
  /// jeton (`{{nom}}`, etc.) sans entrée correspondante dans
  /// [previewValues] reste affiché littéralement, comme avant.
  final Map<String, String> previewValues;
  final Uint8List? previewPhotoBytes;

  /// Donnée automatique du QR (contact du responsable de l'étudiant
  /// prévisualisé) — `el.qrCustomData`, saisi dans le panneau de
  /// propriétés, reste prioritaire quand renseigné (voir `_QrPreview`).
  final String? previewQrData;

  /// Outil plume (voir badge_builder_screen.dart) — [penDraft] est en
  /// coordonnées modèle ABSOLUES pendant le tracé (pas encore normalisées
  /// dans la boîte d'un élément, contrairement à `BadgeElement.pathPoints`
  /// une fois le tracé terminé) ; [onPenPointerDown]/[onPenDrag] reçoivent
  /// déjà des coordonnées modèle (conversion depuis les pixels d'affichage
  /// faite ici, via `scale`).
  final bool penActive;
  final List<BadgePathPoint> penDraft;
  final ValueChanged<Offset>? onPenPointerDown;
  final ValueChanged<Offset>? onPenDrag;

  /// Repères (guides) style Adobe/Figma — voir `BadgeSide.guidesX`/`guidesY`
  /// (models/badge_layout.dart). [onGuideCreateStart] : un glissement
  /// commencé depuis une règle crée un NOUVEAU repère (`vertical` = repère
  /// vertical né de la règle de GAUCHE, sinon horizontal né de la règle du
  /// HAUT), `initialModelValue` déjà converti depuis les pixels d'affichage.
  /// [onGuideMoveStart] : un glissement commencé directement SUR un repère
  /// EXISTANT (dans le canevas) le repositionne au lieu d'en créer un
  /// nouveau. [onGuideDragUpdate] reçoit un DELTA (déjà en unités modèle,
  /// pas une position absolue) — le repère concerné est identifié une seule
  /// fois par le callback de démarrage, pas reçu à chaque appel, comme
  /// `BadgeCanvasElement._move` accumule `event.delta` directement sur
  /// `el.x`/`el.y` plutôt que de recalculer une position absolue à chaque
  /// frame (plus simple qu'un repère de coordonnées qui resterait valide
  /// après le `setState` déclenché par le déplacement précédent).
  /// [onGuideDragEnd] : à l'appelant de retirer le repère si sa position
  /// finale tombe hors du canevas (glissé en arrière sur la règle ou hors
  /// bord — supprime le repère, convention Adobe).
  final void Function(bool vertical, double initialModelValue)?
  onGuideCreateStart;
  final void Function(bool vertical, int index)? onGuideMoveStart;
  final ValueChanged<double>? onGuideDragUpdate;
  final VoidCallback? onGuideDragEnd;

  /// Mode "Modifier les points" (voir badge_builder_property_panel.dart) —
  /// `null` = aucun tracé en édition. Quand non-null, l'élément
  /// correspondant (un tracé, `shapeKind == path`) affiche une poignée par
  /// ancre (glissable, [insertPathPoint] n'y touche jamais) ET une couche
  /// plein cadre qui insère un nouveau point là où l'utilisateur clique SUR
  /// le tracé (jamais sur une ancre existante — la fonction elle-même
  /// l'ignore, voir sa doc). Les deux mutent `element.pathPoints` EN PLACE
  /// puis rappellent [onElementChanged] — pas de nouveau callback dédié,
  /// ce mécanisme de notification existe déjà pour tout le reste.
  final String? editingPathElementId;

  static const _rulerThickness = 20.0;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, outer) {
        // Tient compte de la largeur ET de la hauteur disponibles (comme
        // BoxFit.contain) — se baser uniquement sur la largeur (comme
        // avant) ignorait complètement `outer.maxHeight` et provoquait un
        // débordement vertical (RenderFlex overflow) dès que la fenêtre
        // était trop basse pour la hauteur déduite de la largeur seule.
        var canvasWidth = (outer.maxWidth - _rulerThickness).clamp(
          0.0,
          double.infinity,
        );
        var canvasHeight =
            canvasWidth * layout.canvasHeight / layout.canvasWidth;
        if (outer.hasBoundedHeight) {
          final maxCanvasHeight = (outer.maxHeight - _rulerThickness).clamp(
            0.0,
            double.infinity,
          );
          if (canvasHeight > maxCanvasHeight) {
            canvasHeight = maxCanvasHeight;
            canvasWidth =
                canvasHeight * layout.canvasWidth / layout.canvasHeight;
          }
        }
        final scale = canvasWidth / layout.canvasWidth;

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(width: _rulerThickness, height: _rulerThickness),
                SizedBox(
                  width: canvasWidth,
                  height: _rulerThickness,
                  child: Listener(
                    onPointerDown: (event) => onGuideCreateStart?.call(
                      false,
                      (event.localPosition.dy - _rulerThickness) / scale,
                    ),
                    onPointerMove: (event) =>
                        onGuideDragUpdate?.call(event.delta.dy / scale),
                    onPointerUp: (_) => onGuideDragEnd?.call(),
                    child: CustomPaint(
                      painter: _RulerPainter(scale: scale, vertical: false),
                    ),
                  ),
                ),
              ],
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: _rulerThickness,
                  height: canvasHeight,
                  child: Listener(
                    onPointerDown: (event) => onGuideCreateStart?.call(
                      true,
                      (event.localPosition.dx - _rulerThickness) / scale,
                    ),
                    onPointerMove: (event) =>
                        onGuideDragUpdate?.call(event.delta.dx / scale),
                    onPointerUp: (_) => onGuideDragEnd?.call(),
                    child: CustomPaint(
                      painter: _RulerPainter(scale: scale, vertical: true),
                    ),
                  ),
                ),
                _buildCanvasArea(canvasWidth, canvasHeight, scale),
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildCanvasArea(double width, double height, double scale) {
    return SizedBox(
      width: width,
      height: height,
      // `foregroundDecoration` (peint PAR-DESSUS, sans influencer la mise
      // en page) plutôt que `decoration` : un `Border.all()` sur
      // `decoration` avec `clipBehavior != Clip.none` décale de sa propre
      // épaisseur (1px) le repère local des pointeurs pour TOUS les
      // descendants (poignées, sélection, plume...) — piégé une première
      // fois par le test `flutter_test` de l'outil plume, qui vérifie des
      // coordonnées au pixel près (contrairement au test de sélection,
      // trop tolérant — une cible ~100×40px — pour l'avoir révélé).
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Container(
          foregroundDecoration: BoxDecoration(
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              _buildLayeredContent(scale),
              // Calque de la plume — au-dessus de tout le reste (opaque),
              // capte tous les pointeurs pendant le tracé pour ne jamais
              // interagir par erreur avec un élément existant en dessous.
              if (penActive)
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: (event) =>
                        onPenPointerDown?.call(event.localPosition / scale),
                    onPointerMove: (event) =>
                        onPenDrag?.call(event.delta / scale),
                    child: CustomPaint(
                      painter: _PenDraftPainter(points: penDraft, scale: scale),
                    ),
                  ),
                ),
              ..._buildGuideHandles(scale),
              ..._buildPathPointHandles(scale),
            ],
          ),
        ),
      ),
    );
  }

  /// Mode "Modifier les points" (voir [editingPathElementId] et
  /// badge_builder_property_panel.dart) — une couche plein cadre qui
  /// INSÈRE un nouveau point là où l'utilisateur clique sur le tracé
  /// ([insertPathPoint], qui ignore lui-même les clics trop proches d'une
  /// ancre existante), PLUS une poignée par ancre EXISTANTE, glissable
  /// pour la repositionner. Les deux tiennent compte de la rotation de
  /// l'élément ([_elementTransform]/[_unrotateDelta]) — sans ça, le point
  /// inséré tomberait au mauvais endroit, ou glisser une ancre sur un
  /// élément pivoté la déplacerait dans le mauvais axe.
  ///
  /// Limite assumée, comme pour les repères ([_buildGuideHandles]) : la
  /// couche d'insertion couvre tout le canevas et un `Listener` ne bloque
  /// jamais ses frères qui se chevauchent — cliquer-glisser sur l'élément
  /// édité pendant que ce mode est actif peut donc AUSSI le déplacer en
  /// même temps. Un compromis accepté plutôt qu'un vrai mode exclusif.
  List<Widget> _buildPathPointHandles(double scale) {
    final id = editingPathElementId;
    if (id == null) return [];
    BadgeElement? el;
    for (final e in side.elements) {
      if (e.id == id) {
        el = e;
        break;
      }
    }
    final target = el;
    if (target == null || target.shapeKind != BadgeShapeKind.path) return [];

    final transform = _elementTransform(target, scale);
    final rect = Rect.fromLTWH(0, 0, target.width, target.height);

    Offset anchorDisplayPos(BadgePathPoint p) {
      final local = _denormalizePreview(rect, p.x, p.y) * scale;
      return MatrixUtils.transformPoint(transform, local);
    }

    const handleSize = 10.0;
    final widgets = <Widget>[
      Positioned.fill(
        child: Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (event) {
            final inverse = Matrix4.copy(transform)..invert();
            final localDisplay = MatrixUtils.transformPoint(
              inverse,
              event.localPosition,
            );
            if (insertPathPoint(target, localDisplay / scale)) {
              onElementChanged(target);
            }
          },
        ),
      ),
    ];

    for (var j = 0; j < target.pathPoints.length; j++) {
      final pos = anchorDisplayPos(target.pathPoints[j]);
      widgets.add(
        Positioned(
          left: pos.dx - handleSize / 2,
          top: pos.dy - handleSize / 2,
          width: handleSize,
          height: handleSize,
          child: Listener(
            onPointerMove: (event) {
              final delta =
                  _unrotateDelta(event.delta, target.rotationDegrees) / scale;
              final p = target.pathPoints[j];
              p.x += delta.dx / target.width;
              p.y += delta.dy / target.height;
              onElementChanged(target);
            },
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: const Color(0xFFFF9800),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 1.5),
              ),
            ),
          ),
        ),
      );
    }
    return widgets;
  }

  /// Repères EXISTANTS (voir `BadgeSide.guidesX`/`guidesY`,
  /// models/badge_layout.dart) — une fine ligne visuelle plein cadre PLUS
  /// une bande de saisie un peu plus large ([_guideHitSize]) centrée
  /// dessus, glissable pour repositionner ([onGuideMoveStart]). Peints
  /// PAR-DESSUS les éléments (dernier du Stack), comme dans Adobe/Figma.
  ///
  /// Limite assumée : cette bande de saisie couvre toute la largeur/hauteur
  /// du canevas — un `Listener` Flutter, contrairement au hit-test
  /// "premier gagnant" d'Adobe, ne bloque jamais les frères qui se
  /// chevauchent (voir la doc de `_buildLayeredContent`) : si un repère
  /// croise exactement une poignée ou une zone de glissement d'un élément,
  /// les deux gestes démarrent simultanément. Un cas rare (il faut cliquer
  /// PRÉCISÉMENT sur la ligne), accepté plutôt que de construire un vrai
  /// système d'arbitrage de gestes pour ce seul cas.
  List<Widget> _buildGuideHandles(double scale) {
    const hitHalf = _guideHitSize / 2;
    return [
      for (var i = 0; i < side.guidesY.length; i++)
        Positioned(
          left: 0,
          right: 0,
          top: side.guidesY[i] * scale - hitHalf,
          height: _guideHitSize,
          child: Listener(
            onPointerDown: (_) => onGuideMoveStart?.call(false, i),
            onPointerMove: (event) =>
                onGuideDragUpdate?.call(event.delta.dy / scale),
            onPointerUp: (_) => onGuideDragEnd?.call(),
            child: MouseRegion(
              cursor: SystemMouseCursors.resizeUpDown,
              child: CustomPaint(
                painter: _GuideLinePainter(vertical: false, hitHalf: hitHalf),
              ),
            ),
          ),
        ),
      for (var i = 0; i < side.guidesX.length; i++)
        Positioned(
          top: 0,
          bottom: 0,
          left: side.guidesX[i] * scale - hitHalf,
          width: _guideHitSize,
          child: Listener(
            onPointerDown: (_) => onGuideMoveStart?.call(true, i),
            onPointerMove: (event) =>
                onGuideDragUpdate?.call(event.delta.dx / scale),
            onPointerUp: (_) => onGuideDragEnd?.call(),
            child: MouseRegion(
              cursor: SystemMouseCursors.resizeLeftRight,
              child: CustomPaint(
                painter: _GuideLinePainter(vertical: true, hitHalf: hitHalf),
              ),
            ),
          ),
        ),
    ];
  }

  static const _guideHitSize = 8.0;

  /// Construit fond + grille + tous les éléments, triés par `zIndex`
  /// (comme widgets/badge_layout_renderer.dart::renderBadgeFromLayout —
  /// sans ce tri, l'ordre de superposition à l'écran suivait l'ordre BRUT
  /// de la liste (insertion), ignorant totalement `zIndex` : "Premier
  /// plan"/"Arrière-plan", qui ne modifient QUE `zIndex`, pas la position
  /// dans la liste — voir badge_builder_screen.dart::_reorderSelected —
  /// n'avaient donc AUCUN effet visible ici).
  ///
  /// Chaque élément découpe son PROPRE `cutoutPaths` (trous PERMANENTS,
  /// gravés une fois pour toutes par [bakeSubtraction] — voir sa doc et
  /// celle de `BadgeElement.subtractBackground` dans models/badge_layout.dart
  /// pour l'historique de ce choix). Contrairement à un essai précédent
  /// (un `ClipPath` recalculé à CHAQUE frame selon la position COURANTE
  /// d'une forme "Soustraire du fond" voisine), ce calque n'a plus besoin
  /// de connaître les AUTRES éléments pour se dessiner : le trou est déjà
  /// dans le repère local de CET élément, une simple boîte moins des
  /// polygones, sans transformation croisée.
  Widget _buildLayeredContent(double scale) {
    final sorted = [...side.elements]
      ..sort((a, b) => a.zIndex.compareTo(b.zIndex));

    return Stack(
      clipBehavior: Clip.none,
      children: [
        // Désélection au clic sur le fond. Un `Listener` sur ce calque ET
        // le `Listener` de l'élément cliqué reçoivent TOUS LES DEUX
        // l'événement (les enfants d'un `Stack` ne s'arrêtent PAS au
        // premier "hit" — vérifié par le test `flutter_test` de ce
        // fichier, qui a d'abord échoué avec un `Listener` de fond
        // inconditionnel : il se déclenchait après celui de l'élément et
        // annulait aussitôt la sélection qui venait d'être faite).
        // Solution déterministe : vérifier nous-mêmes en Dart si le point
        // cliqué tombe dans un élément avant de désélectionner, plutôt
        // que de compter sur un ordre de dispatch implicite.
        Positioned.fill(
          child: Listener(
            behavior: HitTestBehavior.opaque,
            onPointerDown: (event) =>
                _onBackgroundPointerDown(event.localPosition, scale),
            child: side.backgroundImagePath != null
                ? Image.file(File(side.backgroundImagePath!), fit: BoxFit.cover)
                : Container(color: const Color(0xFFF3F4F6)),
          ),
        ),
        // Grille d'alignement (style Canva/Figma) — repère visuel
        // uniquement, jamais exportée (widgets/badge_layout_renderer.dart
        // n'en a aucune connaissance).
        Positioned.fill(
          child: IgnorePointer(
            child: CustomPaint(painter: _GridPainter(spacing: 50 * scale)),
          ),
        ),
        // Un calque `hidden` (voir badge_builder_layers_panel.dart) est
        // exclu de l'aperçu — ni visible ni sélectionnable, comme un
        // calque masqué dans Illustrator/Photoshop — et de l'export
        // (widgets/badge_layout_renderer.dart::paintElement), pas
        // seulement estompé pendant l'édition.
        for (var i = 0; i < sorted.length; i++)
          if (!sorted[i].hidden)
            BadgeCanvasElement(
              key: ValueKey(sorted[i].id),
              element: sorted[i],
              scale: scale,
              selected: sorted[i].id == selectedId,
              onSelect: () => onSelect(sorted[i].id),
              onChanged: onElementChanged,
              child: _cutoutClip(
                _ElementPreview(
                  element: sorted[i],
                  previewValues: previewValues,
                  previewPhotoBytes: previewPhotoBytes,
                  previewQrData: previewQrData,
                ),
                sorted[i],
              ),
            ),
      ],
    );
  }

  /// Découpe [child] par les trous PERMANENTS déjà gravés dans
  /// `el.cutoutPaths` (repère local à [el], voir [bakeSubtraction]) —
  /// jamais appliqué au `BadgeCanvasElement` en entier : ce widget porte
  /// aussi les `Listener` de sélection/déplacement/redimensionnement, et
  /// `ClipPath` restreint le hit-test tout autant que la peinture. Un essai
  /// qui enveloppait le widget entier rendait donc les poignées de
  /// redimensionnement injoignables dès qu'elles tombaient dans la zone
  /// découpée (symptôme rapporté : impossible de réduire la hauteur d'un
  /// rectangle). Ici, seul [_ElementPreview] (déjà non-interactif, enveloppé
  /// dans un `IgnorePointer` par `BadgeCanvasElement` lui-même) est découpé.
  Widget _cutoutClip(Widget child, BadgeElement el) {
    if (el.cutoutPaths.isEmpty) return child;
    return ClipPath(
      clipper: _CutoutClipper(cutoutPaths: el.cutoutPaths),
      child: child,
    );
  }

  /// Vérifie si [localPosition] (repère du calque de fond, même origine
  /// que `el.x*scale`/`el.y*scale`) tombe dans la boîte d'un élément —
  /// englobante non pivotée, une approximation suffisante pour décider
  /// s'il faut désélectionner (un élément pivoté cliqué tout près d'un
  /// coin extérieur à sa boîte non pivotée pourrait, dans de rares cas,
  /// désélectionner à tort ; l'inverse — un vrai clic dans le vide qui ne
  /// désélectionne pas — n'arrive jamais).
  void _onBackgroundPointerDown(Offset localPosition, double scale) {
    final hitsElement = side.elements.where((el) => !el.hidden).any((el) {
      final rect = Rect.fromLTWH(
        el.x * scale,
        el.y * scale,
        el.width * scale,
        el.height * scale,
      );
      return rect.contains(localPosition);
    });
    if (!hitsElement) onSelect(null);
  }
}

class _ElementPreview extends StatelessWidget {
  const _ElementPreview({
    required this.element,
    this.previewValues = const {},
    this.previewPhotoBytes,
    this.previewQrData,
  });

  final BadgeElement element;
  final Map<String, String> previewValues;
  final Uint8List? previewPhotoBytes;
  final String? previewQrData;

  @override
  Widget build(BuildContext context) {
    switch (element.type) {
      case BadgeElementType.text:
        return _TextPreview(element: element, previewValues: previewValues);
      case BadgeElementType.shape:
        return CustomPaint(
          painter: _ShapePreviewPainter(element),
          child: const SizedBox.expand(),
        );
      case BadgeElementType.photoPlaceholder:
        return _PhotoPreview(element: element, photoBytes: previewPhotoBytes);
      case BadgeElementType.qrPlaceholder:
        return _QrPreview(element: element, previewQrData: previewQrData);
      case BadgeElementType.staticImage:
        return _StaticImagePreview(element: element);
    }
  }
}

/// Contrairement à `_PhotoPreview` (photo différente par étudiant, jamais
/// persistée), l'image ici EST le fichier persisté de l'élément
/// (`el.imagePath`) — un logo ou une signature scannée, identique sur
/// chaque badge généré.
class _StaticImagePreview extends StatelessWidget {
  const _StaticImagePreview({required this.element});

  final BadgeElement element;

  @override
  Widget build(BuildContext context) {
    final path = element.imagePath;
    if (path == null) {
      return const ColoredBox(
        color: Color(0xFFE0E0E0),
        child: Center(
          child: Icon(Icons.image_outlined, color: Colors.black38, size: 28),
        ),
      );
    }
    return Image.file(
      File(path),
      fit: element.fit == BadgePhotoFit.contain ? BoxFit.contain : BoxFit.cover,
    );
  }
}

/// Sans donnée (ni `el.qrCustomData`, ni donnée automatique de l'étudiant
/// prévisualisé), reste le pictogramme neutre d'avant ; avec une donnée,
/// affiche un vrai QR — même priorité que le rendu exporté
/// (`widgets/badge_layout_renderer.dart::_drawQr`) : `el.qrCustomData`
/// d'abord, sinon [previewQrData].
class _QrPreview extends StatelessWidget {
  const _QrPreview({required this.element, this.previewQrData});

  final BadgeElement element;
  final String? previewQrData;

  @override
  Widget build(BuildContext context) {
    final resolved = (element.qrCustomData?.isNotEmpty ?? false)
        ? element.qrCustomData
        : previewQrData;
    if (resolved == null || resolved.isEmpty) {
      return const ColoredBox(
        color: Color(0xFFE0E0E0),
        child: Center(
          child: Icon(Icons.qr_code_2, color: Colors.black38, size: 28),
        ),
      );
    }
    return ColoredBox(
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: QrImageView(data: resolved, padding: EdgeInsets.zero),
      ),
    );
  }
}

Path _photoMaskPath(BadgeShapeKind kind, Rect rect, double? cornerRadius) {
  return switch (kind) {
    BadgeShapeKind.roundedRectangle =>
      Path()..addRRect(
        RRect.fromRectAndRadius(rect, Radius.circular(cornerRadius ?? 8)),
      ),
    BadgeShapeKind.oval => Path()..addOval(rect),
    _ => Path()..addRect(rect),
  };
}

BadgeShapeKind _photoFrameKind(BadgeElement el) {
  final requested = el.shapeKind ?? BadgeShapeKind.rectangle;
  final isOpenOrPathKind =
      requested == BadgeShapeKind.line ||
      requested == BadgeShapeKind.curve ||
      requested == BadgeShapeKind.path;
  return isOpenOrPathKind ? BadgeShapeKind.rectangle : requested;
}

/// Aperçu du cadre photo — reflète la forme (rectangle/arrondi/cercle) et
/// la bordure choisies dans le panneau de propriétés. Sans [photoBytes]
/// (aucun étudiant recherché, aucune photo test capturée), reste le
/// pictogramme neutre d'avant ; avec une photo, applique les réglages
/// persistés de l'élément (`photoBrightness`/`Contrast`/`Saturation`/
/// `OffsetX`/`OffsetY`/`Zoom`) — les mêmes que
/// `widgets/badge_layout_renderer.dart` applique à la génération réelle,
/// via `widgets/badge_photo_effects.dart` (une seule source de vérité).
///
/// Décode et dessine l'image via `canvas.drawImageRect` (comme
/// `_drawPhoto` du renderer), plutôt qu'un simple `Image.memory(fit:
/// BoxFit.cover, alignment: ...)` : `Alignment` positionne le recadrage
/// par rapport à la BOÎTE de destination, alors que
/// `badgePhotoCropRect` positionne la fenêtre de recadrage par rapport à
/// l'IMAGE source — les deux formules ne coïncident QUE pour
/// `offsetX`/`offsetY` ∈ {0, 0,5, 1} (démontré algébriquement : `Alignment`
/// donne `left = maxLeft·offset`, `badgePhotoCropRect` donne
/// `left = offset·srcWidth − cropW/2`, égales seulement si `offset = 0,5`)
/// — pour toute autre valeur, l'aperçu et l'export montraient un cadrage
/// visiblement différent, symptôme observé avec `Centrage horizontal`
/// réglé à 0,36.
class _PhotoPreview extends StatefulWidget {
  const _PhotoPreview({required this.element, this.photoBytes});

  final BadgeElement element;
  final Uint8List? photoBytes;

  @override
  State<_PhotoPreview> createState() => _PhotoPreviewState();
}

class _PhotoPreviewState extends State<_PhotoPreview> {
  ui.Image? _image;
  Uint8List? _decodedFrom;

  @override
  void initState() {
    super.initState();
    _decode();
  }

  @override
  void didUpdateWidget(covariant _PhotoPreview oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.photoBytes != oldWidget.photoBytes) _decode();
  }

  Future<void> _decode() async {
    final bytes = widget.photoBytes;
    if (bytes == null) {
      setState(() {
        _image = null;
        _decodedFrom = null;
      });
      return;
    }
    if (identical(bytes, _decodedFrom)) return;
    final codec = await ui.instantiateImageCodec(bytes);
    final frame = await codec.getNextFrame();
    if (!mounted || !identical(widget.photoBytes, bytes)) return;
    setState(() {
      _image = frame.image;
      _decodedFrom = bytes;
    });
  }

  @override
  Widget build(BuildContext context) {
    final el = widget.element;
    final kind = _photoFrameKind(el);
    final image = _image;

    return CustomPaint(
      painter: _PhotoPreviewPainter(
        kind: kind,
        cornerRadius: el.cornerRadius,
        strokeColor: el.strokeColor,
        strokeWidth: el.strokeWidth,
        showPlaceholderFill: image == null,
      ),
      child: image == null
          ? const Center(
              child: Icon(
                Icons.person_outline,
                color: Colors.black38,
                size: 28,
              ),
            )
          : ClipPath(
              clipper: _PhotoMaskClipper(
                kind: kind,
                cornerRadius: el.cornerRadius,
              ),
              child: CustomPaint(
                painter: _PhotoImagePainter(
                  image: image,
                  colorMatrix: badgePhotoColorMatrix(
                    brightness: el.photoBrightness,
                    contrast: el.photoContrast,
                    saturation: el.photoSaturation,
                  ),
                  fit: el.fit,
                  offsetX: el.photoOffsetX,
                  offsetY: el.photoOffsetY,
                  zoom: el.photoZoom,
                ),
                child: const SizedBox.expand(),
              ),
            ),
    );
  }
}

/// Dessine [image] dans les bornes du `CustomPaint` en reproduisant EXACTEMENT
/// `widgets/badge_layout_renderer.dart::_drawPhoto` (même branchement
/// contain/cover, même appel à `badgePhotoCropRect`) — voir la doc de
/// [_PhotoPreview] pour la raison de cette duplication plutôt qu'un simple
/// `Image(fit: ...)`.
class _PhotoImagePainter extends CustomPainter {
  _PhotoImagePainter({
    required this.image,
    required this.colorMatrix,
    required this.fit,
    required this.offsetX,
    required this.offsetY,
    required this.zoom,
  });

  final ui.Image image;
  final List<double> colorMatrix;
  final BadgePhotoFit fit;
  final double offsetX;
  final double offsetY;
  final double zoom;

  @override
  void paint(Canvas canvas, Size size) {
    final frame = Offset.zero & size;
    final paint = Paint()..colorFilter = ColorFilter.matrix(colorMatrix);
    final srcW = image.width.toDouble();
    final srcH = image.height.toDouble();

    if (fit == BadgePhotoFit.contain) {
      final scale = (frame.width / srcW < frame.height / srcH)
          ? frame.width / srcW
          : frame.height / srcH;
      final dstW = srcW * scale;
      final dstH = srcH * scale;
      final dst = Rect.fromLTWH(
        (frame.width - dstW) / 2,
        (frame.height - dstH) / 2,
        dstW,
        dstH,
      );
      canvas.drawImageRect(image, Rect.fromLTWH(0, 0, srcW, srcH), dst, paint);
    } else {
      final src = badgePhotoCropRect(
        srcWidth: srcW,
        srcHeight: srcH,
        targetWidth: frame.width,
        targetHeight: frame.height,
        offsetX: offsetX,
        offsetY: offsetY,
        zoom: zoom,
      );
      canvas.drawImageRect(image, src, frame, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _PhotoImagePainter oldDelegate) =>
      oldDelegate.image != image ||
      oldDelegate.colorMatrix != colorMatrix ||
      oldDelegate.fit != fit ||
      oldDelegate.offsetX != offsetX ||
      oldDelegate.offsetY != offsetY ||
      oldDelegate.zoom != zoom;
}

class _PhotoMaskClipper extends CustomClipper<Path> {
  _PhotoMaskClipper({required this.kind, this.cornerRadius});

  final BadgeShapeKind kind;
  final double? cornerRadius;

  @override
  Path getClip(Size size) =>
      _photoMaskPath(kind, Offset.zero & size, cornerRadius);

  @override
  bool shouldReclip(covariant _PhotoMaskClipper oldClipper) =>
      oldClipper.kind != kind || oldClipper.cornerRadius != cornerRadius;
}

class _PhotoPreviewPainter extends CustomPainter {
  _PhotoPreviewPainter({
    required this.kind,
    this.cornerRadius,
    this.strokeColor,
    this.strokeWidth,
    this.showPlaceholderFill = true,
  });

  final BadgeShapeKind kind;
  final double? cornerRadius;
  final int? strokeColor;
  final double? strokeWidth;
  final bool showPlaceholderFill;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    final path = _photoMaskPath(kind, rect, cornerRadius);
    if (showPlaceholderFill) {
      canvas.drawPath(path, Paint()..color = const Color(0xFFE0E0E0));
    }
    if (strokeColor != null && (strokeWidth ?? 0) > 0) {
      canvas.drawPath(
        path,
        Paint()
          ..color = Color(strokeColor!)
          ..style = PaintingStyle.stroke
          ..strokeWidth = strokeWidth!,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PhotoPreviewPainter oldDelegate) => true;
}

class _TextPreview extends StatelessWidget {
  const _TextPreview({required this.element, this.previewValues = const {}});

  final BadgeElement element;
  final Map<String, String> previewValues;

  @override
  Widget build(BuildContext context) {
    final el = element;
    var resolved = el.text ?? '';
    previewValues.forEach(
      (token, value) => resolved = resolved.replaceAll(token, value),
    );
    return Align(
      alignment: switch (el.textAlign) {
        BadgeTextAlign.left => Alignment.centerLeft,
        BadgeTextAlign.center => Alignment.center,
        BadgeTextAlign.right => Alignment.centerRight,
      },
      child: Text(
        resolved.isEmpty ? '(texte)' : resolved,
        overflow: TextOverflow.clip,
        softWrap: true,
        textAlign: switch (el.textAlign) {
          BadgeTextAlign.left => TextAlign.left,
          BadgeTextAlign.center => TextAlign.center,
          BadgeTextAlign.right => TextAlign.right,
        },
        style: TextStyle(
          fontSize: el.fontSize ?? 16,
          fontWeight: el.bold ? FontWeight.bold : FontWeight.normal,
          fontStyle: el.italic ? FontStyle.italic : FontStyle.normal,
          color: el.color != null ? Color(el.color!) : Colors.black,
          fontFamily: el.fontFamily,
        ),
      ),
    );
  }
}

/// Grille légère tous les 50 pixels modèle (mise à l'échelle par [spacing])
/// pour aider à l'alignement pendant l'édition — un simple repère visuel,
/// pas un système d'accroche ("snap").
/// Règle graduée en centimètres (300dpi, `kBadgePxPerCm`), à côté de la
/// grille — un repère d'échelle, comme les règles Canva/Figma en bordure
/// du canevas.
class _RulerPainter extends CustomPainter {
  _RulerPainter({required this.scale, required this.vertical});

  final double scale;
  final bool vertical;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Offset.zero & size,
      Paint()..color = const Color(0xFFF3F4F6),
    );
    final pxPerCm = kBadgePxPerCm * scale;
    if (pxPerCm <= 0) return;

    final length = vertical ? size.height : size.width;
    final thickness = vertical ? size.width : size.height;
    final tickPaint = Paint()..color = const Color(0xFF9AA1B5);
    const textStyle = TextStyle(fontSize: 8, color: Color(0xFF6B7280));

    var cm = 0;
    for (var pos = 0.0; pos <= length; pos += pxPerCm, cm++) {
      final tickLen = thickness * 0.55;
      if (vertical) {
        canvas.drawLine(
          Offset(thickness - tickLen, pos),
          Offset(thickness, pos),
          tickPaint,
        );
      } else {
        canvas.drawLine(
          Offset(pos, thickness - tickLen),
          Offset(pos, thickness),
          tickPaint,
        );
      }
      if (cm > 0) {
        final tp = TextPainter(
          text: TextSpan(text: '$cm', style: textStyle),
          textDirection: TextDirection.ltr,
        )..layout();
        final labelOffset = vertical
            ? Offset(2, pos - tp.height / 2)
            : Offset(pos + 2, 1);
        tp.paint(canvas, labelOffset);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _RulerPainter oldDelegate) =>
      oldDelegate.scale != scale || oldDelegate.vertical != vertical;
}

/// Aperçu en direct du tracé en cours (outil plume) — [points] en
/// coordonnées modèle ABSOLUES (voir `BadgeBuilderCanvas.penDraft`), pas
/// encore normalisées puisque l'élément final n'existe pas encore.
class _PenDraftPainter extends CustomPainter {
  _PenDraftPainter({required this.points, required this.scale});

  final List<BadgePathPoint> points;
  final double scale;

  @override
  void paint(Canvas canvas, Size size) {
    if (points.isEmpty) return;
    Offset toDisplay(double mx, double my) => Offset(mx * scale, my * scale);

    final linePaint = Paint()
      ..color = const Color(0xFF1A73E8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    final start = toDisplay(points.first.x, points.first.y);
    final path = Path()..moveTo(start.dx, start.dy);
    for (var i = 1; i < points.length; i++) {
      final prev = points[i - 1];
      final curr = points[i];
      final cp1 = prev.outX != null
          ? toDisplay(prev.x + prev.outX!, prev.y + prev.outY!)
          : toDisplay(prev.x, prev.y);
      final cp2 = curr.inX != null
          ? toDisplay(curr.x + curr.inX!, curr.y + curr.inY!)
          : toDisplay(curr.x, curr.y);
      final end = toDisplay(curr.x, curr.y);
      path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, end.dx, end.dy);
    }
    canvas.drawPath(path, linePaint);

    // Poignée du dernier point posé — retour visuel pendant le glisser.
    final last = points.last;
    if (last.outX != null) {
      final anchor = toDisplay(last.x, last.y);
      final handle = toDisplay(last.x + last.outX!, last.y + last.outY!);
      canvas.drawLine(anchor, handle, Paint()..color = Colors.orange);
      canvas.drawCircle(handle, 3, Paint()..color = Colors.orange);
    }

    for (var i = 0; i < points.length; i++) {
      final p = toDisplay(points[i].x, points[i].y);
      final radius = i == 0 ? 5.0 : 4.0;
      // Le premier point est vert : cliquer dessus referme le tracé.
      canvas.drawCircle(
        p,
        radius,
        Paint()..color = i == 0 ? const Color(0xFF34A853) : Colors.white,
      );
      canvas.drawCircle(
        p,
        radius,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.5
          ..color = const Color(0xFF1A73E8),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PenDraftPainter oldDelegate) => true;
}

class _GridPainter extends CustomPainter {
  _GridPainter({required this.spacing});

  final double spacing;

  @override
  void paint(Canvas canvas, Size size) {
    if (spacing <= 0) return;
    final paint = Paint()
      ..color = const Color(0x1A000000)
      ..strokeWidth = 1;
    for (var x = 0.0; x <= size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (var y = 0.0; y <= size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant _GridPainter oldDelegate) =>
      oldDelegate.spacing != spacing;
}

/// Trait d'un repère (guide) — dessiné au centre de la bande de saisie
/// [hitHalf]*2 (voir `_buildGuideHandles`), couleur cyan conventionnelle
/// (Adobe/Figma) pour se distinguer nettement de la grille et des bordures
/// d'éléments.
class _GuideLinePainter extends CustomPainter {
  _GuideLinePainter({required this.vertical, required this.hitHalf});

  final bool vertical;
  final double hitHalf;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00BCD4)
      ..strokeWidth = 1;
    if (vertical) {
      canvas.drawLine(Offset(hitHalf, 0), Offset(hitHalf, size.height), paint);
    } else {
      canvas.drawLine(Offset(0, hitHalf), Offset(size.width, hitHalf), paint);
    }
  }

  @override
  bool shouldRepaint(covariant _GuideLinePainter oldDelegate) => false;
}

/// Même géométrie que `widgets/badge_layout_renderer.dart::_shapePath` — le
/// tracé (façon Illustrator, `BadgeShapeKind.path`) et le dégradé de
/// remplissage doivent avoir exactement la même forme à l'écran que dans
/// le PNG exporté.
Path _shapePathPreview(Rect rect, BadgeElement element) {
  final kind = element.shapeKind ?? BadgeShapeKind.rectangle;
  switch (kind) {
    case BadgeShapeKind.rectangle:
      return Path()..addRect(rect);
    case BadgeShapeKind.roundedRectangle:
      return Path()..addRRect(
        RRect.fromRectAndRadius(
          rect,
          Radius.circular(element.cornerRadius ?? 8),
        ),
      );
    case BadgeShapeKind.oval:
      return Path()..addOval(rect);
    case BadgeShapeKind.line:
      return Path()
        ..moveTo(rect.left, rect.top + rect.height / 2)
        ..lineTo(rect.right, rect.top + rect.height / 2);
    case BadgeShapeKind.curve:
      final bulge = element.cornerRadius ?? rect.height / 2;
      return Path()
        ..moveTo(rect.left, rect.bottom)
        ..quadraticBezierTo(
          rect.left + rect.width / 2,
          rect.bottom - bulge,
          rect.right,
          rect.bottom,
        );
    case BadgeShapeKind.path:
      return _pathFromPointsPreview(
        rect,
        element.pathPoints,
        element.pathClosed,
      );
  }
}

Offset _denormalizePreview(Rect rect, double nx, double ny) =>
    Offset(rect.left + nx * rect.width, rect.top + ny * rect.height);

Path _pathFromPointsPreview(
  Rect rect,
  List<BadgePathPoint> points,
  bool closed,
) {
  final path = Path();
  if (points.isEmpty) return path;
  final first = _denormalizePreview(rect, points.first.x, points.first.y);
  path.moveTo(first.dx, first.dy);
  for (var i = 1; i < points.length; i++) {
    _cubicBetweenPreview(path, rect, points[i - 1], points[i]);
  }
  if (closed && points.length > 1) {
    _cubicBetweenPreview(path, rect, points.last, points.first);
    path.close();
  }
  return path;
}

void _cubicBetweenPreview(
  Path path,
  Rect rect,
  BadgePathPoint from,
  BadgePathPoint to,
) {
  final cp1 = from.outX != null
      ? _denormalizePreview(rect, from.x + from.outX!, from.y + from.outY!)
      : _denormalizePreview(rect, from.x, from.y);
  final cp2 = to.inX != null
      ? _denormalizePreview(rect, to.x + to.inX!, to.y + to.inY!)
      : _denormalizePreview(rect, to.x, to.y);
  final end = _denormalizePreview(rect, to.x, to.y);
  path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, end.dx, end.dy);
}

Shader _buildGradientShaderPreview(BadgeGradient gradient, Rect rect) {
  final colors = gradient.stops.map((s) => Color(s.color)).toList();
  final stops = gradient.stops.map((s) => s.offset).toList();
  if (gradient.type == BadgeGradientType.radial) {
    return ui.Gradient.radial(rect.center, rect.longestSide / 2, colors, stops);
  }
  final angleRad = gradient.angleDegrees * pi / 180;
  final direction =
      Offset(cos(angleRad), sin(angleRad)) * (rect.longestSide / 2);
  return ui.Gradient.linear(
    rect.center - direction,
    rect.center + direction,
    colors,
    stops,
  );
}

/// Matrice modèle→affichage de [el] (translation à sa position, pivot
/// autour de SON PROPRE centre) — même transformation que
/// `BadgeCanvasElement`/`Transform.rotate(alignment: Alignment.center)`
/// lui applique pour l'afficher.
Matrix4 _elementTransform(BadgeElement el, double scale) {
  final cx = el.width * scale / 2;
  final cy = el.height * scale / 2;
  return Matrix4.identity()
    ..translateByDouble(el.x * scale, el.y * scale, 0, 1)
    ..translateByDouble(cx, cy, 0, 1)
    ..rotateZ(el.rotationDegrees * pi / 180)
    ..translateByDouble(-cx, -cy, 0, 1);
}

/// Exprime [delta] (un déplacement brut à l'écran, `event.delta`) dans le
/// repère LOCAL NON PIVOTÉ d'un élément tourné de [rotationDegrees] — sans
/// cette rotation inverse, glisser une poignée "vers la droite" sur un
/// élément pivoté à 90° déplacerait le point sur le mauvais axe (voir
/// [_buildPathPointHandles]).
Offset _unrotateDelta(Offset delta, double rotationDegrees) {
  final rad = -rotationDegrees * pi / 180;
  final cosA = cos(rad);
  final sinA = sin(rad);
  return Offset(
    delta.dx * cosA - delta.dy * sinA,
    delta.dx * sinA + delta.dy * cosA,
  );
}

/// Chemin de [shape] (une forme "Soustraire du fond") exprimé dans le
/// repère LOCAL de [target] (`null` = repère absolu du canevas, utilisé
/// pour le fond/la grille, dont le repère local coïncide déjà avec le
/// canevas).
///
/// `ClipPath` clippe TOUJOURS dans le repère local de l'enfant qu'il
/// enveloppe, jamais dans un repère absolu — un premier essai calculait
/// le trou directement en coordonnées ABSOLUES du canevas et l'appliquait
/// tel quel à `ClipPath`, comme s'il s'agissait déjà de coordonnées
/// locales à l'élément découpé. Ça fonctionnait par coïncidence pour le
/// fond/la grille (dont le coin (0,0) local coïncide avec celui du
/// canevas), mais PAS pour un élément ordinaire positionné ailleurs :
/// le trou se retrouvait décalé de la position (x,y) de cet élément,
/// tombant potentiellement hors de son propre repère local — sans AUCUN
/// effet visible (symptôme rapporté : un tracé qui chevauche visuellement
/// un rectangle mais ne le découpe jamais). Ici, on compose l'inverse de
/// la transformation de [target] avec celle de [shape] pour obtenir le
/// trou dans le bon repère, quelle que soit la position de l'un ou
/// l'autre.
Path _shapePathInFrame(BadgeElement shape, BadgeElement? target, double scale) {
  final localRect = Rect.fromLTWH(
    0,
    0,
    shape.width * scale,
    shape.height * scale,
  );
  final localPath = _shapePathPreview(localRect, shape);
  final shapeTransform = _elementTransform(shape, scale);
  if (target == null) return localPath.transform(shapeTransform.storage);

  final inverseTargetTransform = Matrix4.copy(_elementTransform(target, scale))
    ..invert();
  final combined = inverseTargetTransform.multiplied(shapeTransform);
  return localPath.transform(combined.storage);
}

/// Grave DÉFINITIVEMENT [cutter] dans chaque élément de [sortedElements]
/// (déjà triés par `zIndex`) qui le précède en ordre de peinture (donc
/// visuellement "en dessous") ET qu'il chevauche RÉELLEMENT — appelé UNE
/// SEULE FOIS quand `BadgeElement.subtractBackground` passe à `true` (voir
/// sa doc dans models/badge_layout.dart et badge_builder_screen.dart::
/// _onElementChanged, qui appelle cette fonction puis réinitialise le
/// déclencheur), jamais à chaque frame — contrairement à un essai
/// précédent (masque `ClipPath` recalculé en direct selon la position
/// COURANTE du découpeur), le résultat est gravé dans le `cutoutPaths` de
/// CHAQUE cible : déplacer ou supprimer [cutter] ensuite n'efface plus le
/// trou.
///
/// Réutilise [_shapePathInFrame]/[_elementTransform] (`scale: 1`, unités
/// modèle pures — un trou gravé doit être indépendant du zoom d'édition
/// courant) : la même conversion de repère déjà vérifiée par les tests
/// géométriques de ce fichier pour le masque dynamique précédent reste
/// valable ici, exécutée une seule fois au lieu de à chaque peinture.
///
/// Un élément [BadgeElement.locked] (voir sa doc dans models/badge_layout.dart
/// et badge_builder_layers_panel.dart) est IGNORÉ comme cible — protégé
/// contre toute découpe reçue d'une autre forme, utile pour un fond coloré
/// qu'on veut garder intact quand on découpe un élément voisin qui le
/// recouvre.
void bakeSubtraction(BadgeElement cutter, List<BadgeElement> sortedElements) {
  final cutterIndex = sortedElements.indexOf(cutter);
  if (cutterIndex < 0) return;

  for (var i = 0; i < cutterIndex; i++) {
    final target = sortedElements[i];
    if (target.locked) continue;
    final cutterInTargetFrame = _shapePathInFrame(cutter, target, 1);
    final targetRect = Rect.fromLTWH(0, 0, target.width, target.height);
    final overlap = Path.combine(
      PathOperation.intersect,
      cutterInTargetFrame,
      Path()..addRect(targetRect),
    );
    if (overlap.getBounds().isEmpty) continue;
    final polygon = _flattenToNormalizedPolygon(
      cutterInTargetFrame,
      target.width,
      target.height,
    );
    if (polygon.isNotEmpty) target.cutoutPaths.add(polygon);
  }
}

/// Échantillonne le PLUS GRAND contour de [path] (un seul attendu pour une
/// forme simple — rectangle/ovale/tracé plume fermé) en un polygone à
/// segments droits, normalisé (0..1, fraction de [width]/[height]) — pas
/// de poignées de courbure : un trou gravé n'a plus besoin d'être réédité
/// après coup, contrairement à `BadgeElement.pathPoints` d'un tracé encore
/// modifiable.
List<BadgePathPoint> _flattenToNormalizedPolygon(
  Path path,
  double width,
  double height,
) {
  final metrics = path.computeMetrics().toList()
    ..sort((a, b) => b.length.compareTo(a.length));
  if (metrics.isEmpty || width <= 0 || height <= 0) return [];
  final metric = metrics.first;
  const samples = 72;
  final points = <BadgePathPoint>[];
  for (var i = 0; i < samples; i++) {
    final distance = metric.length * i / samples;
    final tangent = metric.getTangentForOffset(distance);
    if (tangent == null) continue;
    points.add(
      BadgePathPoint(
        x: tangent.position.dx / width,
        y: tangent.position.dy / height,
      ),
    );
  }
  return points;
}

/// Insère un nouveau point d'ancrage (un "coin", sans poignées de
/// courbure) sur le segment de `el.pathPoints` le plus proche de
/// [localModelClick] — repère LOCAL NON PIVOTÉ de [el] (0,0)-(width,height),
/// les mêmes unités que `pathPoints` une fois dénormalisés. Mute
/// `el.pathPoints` EN PLACE (cohérent avec la mutabilité documentée dans
/// models/badge_layout.dart) et retourne `true` si un point a bien été
/// inséré.
///
/// Ignore le clic (retourne `false`) :
/// - s'il tombe trop près d'une ancre EXISTANTE (à moins de [tolerance]) —
///   ce cas est celui d'un glissement voulu sur cette ancre, pas une
///   insertion (voir la poignée d'ancre dans `_buildPathPointHandles`, qui
///   reçoit ce même clic en parallèle : `Listener` ne bloque jamais les
///   frères qui se chevauchent, voir la doc de `_buildLayeredContent` —
///   sans cette garde, cliquer une ancre existante insérerait AUSSI un
///   point parasite juste à côté) ;
/// - s'il tombe trop loin de tout segment du tracé (au-delà de
///   [tolerance]) — un clic ailleurs dans la boîte de l'élément ne doit
///   rien faire.
///
/// Recherche par échantillonnage plutôt que par une formule fermée
/// (généralement impossible pour une distance point↔courbe cubique) — une
/// approche purement mathématique (`_cubicPointAt`), sans dépendre de
/// `dart:ui`/`Path`, pour rester testable sans `flutter_test`.
bool insertPathPoint(
  BadgeElement el,
  Offset localModelClick, {
  double tolerance = 10,
}) {
  if (el.shapeKind != BadgeShapeKind.path || el.pathPoints.length < 2) {
    return false;
  }
  final rect = Rect.fromLTWH(0, 0, el.width, el.height);
  Offset denorm(double x, double y) => _denormalizePreview(rect, x, y);

  for (final p in el.pathPoints) {
    if ((denorm(p.x, p.y) - localModelClick).distance < tolerance) return false;
  }

  final points = el.pathPoints;
  final segmentCount = el.pathClosed ? points.length : points.length - 1;
  var bestIndex = -1;
  var bestDist = double.infinity;
  const samples = 20;
  for (var i = 0; i < segmentCount; i++) {
    final from = points[i];
    final to = points[(i + 1) % points.length];
    final p0 = denorm(from.x, from.y);
    final p1 = denorm(to.x, to.y);
    final cp1 = from.outX != null
        ? denorm(from.x + from.outX!, from.y + from.outY!)
        : p0;
    final cp2 = to.inX != null ? denorm(to.x + to.inX!, to.y + to.inY!) : p1;
    for (var s = 1; s < samples; s++) {
      final t = s / samples;
      final dist =
          (_cubicPointAt(p0, cp1, cp2, p1, t) - localModelClick).distance;
      if (dist < bestDist) {
        bestDist = dist;
        bestIndex = i;
      }
    }
  }
  if (bestIndex < 0 || bestDist > tolerance) return false;

  points.insert(
    bestIndex + 1,
    BadgePathPoint(
      x: localModelClick.dx / rect.width,
      y: localModelClick.dy / rect.height,
    ),
  );
  return true;
}

Offset _cubicPointAt(Offset p0, Offset cp1, Offset cp2, Offset p1, double t) {
  final mt = 1 - t;
  final a = mt * mt * mt;
  final b = 3 * mt * mt * t;
  final c = 3 * mt * t * t;
  final d = t * t * t;
  return Offset(
    a * p0.dx + b * cp1.dx + c * cp2.dx + d * p1.dx,
    a * p0.dy + b * cp1.dy + c * cp2.dy + d * p1.dy,
  );
}

/// Découpe [child] par les trous PERMANENTS déjà gravés dans
/// `el.cutoutPaths` — repère déjà LOCAL à l'élément découpé (voir
/// [bakeSubtraction]), donc une simple boîte moins des polygones, sans
/// transformation croisée avec un autre élément.
class _CutoutClipper extends CustomClipper<Path> {
  _CutoutClipper({required this.cutoutPaths});

  final List<List<BadgePathPoint>> cutoutPaths;

  @override
  Path getClip(Size size) {
    final rect = Offset.zero & size;
    var clip = Path()..addRect(rect);
    for (final polygon in cutoutPaths) {
      clip = Path.combine(
        PathOperation.difference,
        clip,
        _pathFromPointsPreview(rect, polygon, true),
      );
    }
    return clip;
  }

  // `cutoutPaths` est muté EN PLACE (voir models/badge_layout.dart) : pas
  // de comparaison de valeur fiable entre l'ancien et le nouveau clipper,
  // même choix que `_ShapePreviewPainter.shouldRepaint`.
  @override
  bool shouldReclip(covariant _CutoutClipper oldClipper) => true;
}

class _ShapePreviewPainter extends CustomPainter {
  _ShapePreviewPainter(this.element);

  final BadgeElement element;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    final kind = element.shapeKind ?? BadgeShapeKind.rectangle;
    final path = _shapePathPreview(rect, element);

    // `element.subtractBackground` n'est plus qu'un DÉCLENCHEUR ponctuel
    // (voir models/badge_layout.dart) : consommé et réinitialisé à `false`
    // de façon synchrone par badge_builder_screen.dart::_onElementChanged
    // avant tout nouveau rendu, donc jamais réellement peint à `true` —
    // cette forme se dessine toujours normalement (fond + contour), même
    // juste après avoir servi de découpeur.
    final isOpenPath =
        kind == BadgeShapeKind.line ||
        kind == BadgeShapeKind.curve ||
        (kind == BadgeShapeKind.path && !element.pathClosed);
    if (!isOpenPath) {
      if (element.fillGradient != null &&
          element.fillGradient!.stops.length >= 2) {
        canvas.drawPath(
          path,
          Paint()
            ..shader = _buildGradientShaderPreview(element.fillGradient!, rect),
        );
      } else if (element.fillColor != null) {
        canvas.drawPath(path, Paint()..color = Color(element.fillColor!));
      }
    }
    if (element.strokeColor != null && (element.strokeWidth ?? 0) > 0) {
      canvas.drawPath(
        path,
        Paint()
          ..color = Color(element.strokeColor!)
          ..style = PaintingStyle.stroke
          ..strokeWidth = element.strokeWidth!,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _ShapePreviewPainter oldDelegate) => true;
}
