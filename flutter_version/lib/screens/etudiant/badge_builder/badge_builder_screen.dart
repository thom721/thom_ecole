import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:provider/provider.dart';

import '../../../core/badge_output_path.dart';
import '../../../core/print_gate.dart';
import '../../../models/badge_layout.dart';
import '../../../models/student.dart';
import '../../../models/student_detail.dart';
import '../../../services/badge_layout_store.dart';
import '../../../state/students_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_layout_renderer.dart';
import '../../../widgets/pill_button.dart';
import '../../../widgets/section_header.dart';
import 'badge_builder_canvas.dart';
import 'badge_builder_layers_panel.dart';
import 'badge_builder_property_panel.dart';
import 'badge_builder_toolbar.dart';
import 'badge_test_photo_capture_dialog.dart';

// Mêmes listes que badge_screen.dart (`_salles`/`_moisNoms`) — `{{salle}}`/
// `{{expiration}}` sont des réglages globaux au moment de générer un badge
// (pas des données de la fiche étudiant), donc sans équivalent dans
// `StudentDetail` ; dupliquées ici plutôt que partagées pour rester
// cohérent avec le reste de ce module (ex. `_fontFamilies` dans
// badge_builder_property_panel.dart, une liste fermée similaire).
const _salles = {
  'A': 'Salle A',
  'B': 'Salle B',
  'C': 'Salle C',
  'D': 'Salle D',
};

const _moisNoms = [
  'Janvier',
  'Février',
  'Mars',
  'Avril',
  'Mai',
  'Juin',
  'Juillet',
  'Août',
  'Septembre',
  'Octobre',
  'Novembre',
  'Décembre',
];

/// Éditeur visuel de gabarit de badge recto-verso (style Canva) — écran
/// séparé, sans lien avec le flux de génération existant
/// (`etudiant/badge_screen.dart`/`widgets/badge_renderer.dart`, tous deux
/// laissés inchangés). Les gabarits construits ici sont persistés via
/// [BadgeLayoutStore] et deviennent sélectionnables dans badge_screen.dart
/// au même titre que les 2 templates fixes existants (seul point de
/// contact avec l'existant, ajouté séparément).
class BadgeBuilderScreen extends StatefulWidget {
  const BadgeBuilderScreen({super.key, this.onBack});

  /// Affiche une flèche de retour (icône seule) en ligne avec le titre,
  /// à la place du bandeau "Retour à la liste" séparé qu'utilisent les
  /// autres écrans (etudiant_screen.dart) — sur demande explicite.
  final VoidCallback? onBack;

  @override
  State<BadgeBuilderScreen> createState() => _BadgeBuilderScreenState();
}

class _BadgeBuilderScreenState extends State<BadgeBuilderScreen> {
  BadgeLayoutTemplate? _layout;
  bool _isVerso = false;
  String? _selectedId;
  bool _saving = false;
  bool _exporting = false;

  // Sélecteur d'onglet du panneau latéral (badge_builder_screen.dart::
  // _buildInspectorColumn) — false = Propriétés, true = Calques. Une seule
  // colonne à la fois plutôt que les deux côte à côte comme avant : ça
  // réduisait considérablement la place laissée au canevas.
  bool _showLayersTab = false;

  // Repère (guide) en cours de glissement — voir badge_builder_canvas.dart
  // (onGuideCreateStart/onGuideMoveStart/onGuideDragUpdate/onGuideDragEnd).
  // `null` = aucun glissement en cours. `_draggingGuideVertical` distingue
  // `_currentSide.guidesX` (repère vertical) de `guidesY` (horizontal).
  int? _draggingGuideIndex;
  bool _draggingGuideVertical = false;

  // Élément (un tracé, `shapeKind == path`) actuellement en mode "Modifier
  // les points" — voir badge_builder_canvas.dart::insertPathPoint et
  // badge_builder_property_panel.dart (bouton "Modifier les points").
  // `null` = aucun tracé en édition.
  String? _editingPathElementId;

  // Outil plume — voir badge_builder_canvas.dart::penDraft pour le détail
  // des coordonnées (absolues tant que le tracé n'est pas terminé).
  bool _penActive = false;
  final List<BadgePathPoint> _penDraft = [];

  // Aperçu en direct avec de vraies données (recherche d'étudiant) et/ou
  // une photo test capturée à la caméra OU chargée depuis un fichier —
  // jamais persistés dans le gabarit, seulement les réglages de
  // badge_builder_property_panel.dart (photoBrightness/Contrast/
  // Saturation/OffsetX/OffsetY/Zoom) le sont.
  Uint8List? _testPhotoBytes;
  bool _savingPhoto = false;

  // Réglages globaux au moment de générer un badge (pas des données de la
  // fiche étudiant) — mêmes champs que badge_screen.dart, absents ici
  // jusqu'ici, ce qui faisait que `{{expiration}}`/`{{salle}}` restaient
  // toujours affichés littéralement dans l'aperçu ET l'export.
  int _expMonth = DateTime.now().month;
  int _expYear = DateTime.now().year;
  String _salle = 'A';

  @override
  void initState() {
    super.initState();
    _newLayout();
  }

  void _newLayout() {
    setState(() {
      _layout = BadgeLayoutTemplate(
        id: BadgeLayoutStore.instance.newId(),
        name: 'Nouveau gabarit',
      );
      _isVerso = false;
      _selectedId = null;
    });
  }

  BadgeSide get _currentSide {
    final layout = _layout!;
    if (_isVerso) return layout.verso ??= BadgeSide();
    return layout.recto;
  }

  BadgeElement? get _selectedElement {
    final id = _selectedId;
    if (id == null) return null;
    for (final el in _currentSide.elements) {
      if (el.id == id) return el;
    }
    return null;
  }

  void _addElement(BadgeElement Function(String id) build) {
    final id = BadgeLayoutStore.instance.newId();
    setState(() {
      _currentSide.elements.add(build(id));
      _selectedId = id;
    });
  }

  /// `el.subtractBackground == true` est un DÉCLENCHEUR ponctuel (voir sa
  /// doc dans models/badge_layout.dart) : consommé ICI — jamais peint à
  /// `true` — en gravant un trou permanent dans chaque élément en dessous
  /// de [el] qui le chevauche réellement ([bakeSubtraction]), puis
  /// réinitialisé. Ce handler est le seul point de passage commun entre le
  /// canevas (glisser/redimensionner/pivoter) et le panneau de propriétés
  /// (bouton "Soustraire du fond"), donc le seul endroit qui voit à la
  /// fois l'élément modifié ET la liste complète de ses voisins
  /// (`_currentSide.elements`, nécessaire à [bakeSubtraction]).
  void _onElementChanged(BadgeElement el) => setState(() {
    if (el.subtractBackground) {
      // [bakeSubtraction] suppose une liste déjà triée par `zIndex` (ordre
      // de peinture réel, voir badge_builder_canvas.dart::_buildLayeredContent)
      // — `_currentSide.elements` suit l'ordre BRUT d'insertion, pas
      // forcément l'ordre de peinture (exactement la confusion liste/zIndex
      // à l'origine de tout le fil de bugs précédent sur cette fonctionnalité).
      final sorted = [..._currentSide.elements]
        ..sort((a, b) => a.zIndex.compareTo(b.zIndex));
      bakeSubtraction(el, sorted);
      el.subtractBackground = false;
    }
  });

  /// Un glissement commencé sur une règle (voir badge_builder_canvas.dart::
  /// onGuideCreateStart) ajoute un NOUVEAU repère à la liste concernée
  /// (`guidesX` pour un repère vertical né de la règle de gauche, sinon
  /// `guidesY`) à sa position initiale, puis le marque comme "en cours de
  /// glissement" pour que les mouvements suivants ([_onGuideDragUpdate])
  /// l'ajustent.
  void _onGuideCreateStart(bool vertical, double initialModelValue) {
    setState(() {
      final list = vertical ? _currentSide.guidesX : _currentSide.guidesY;
      list.add(initialModelValue);
      _draggingGuideVertical = vertical;
      _draggingGuideIndex = list.length - 1;
    });
  }

  /// Un glissement commencé directement SUR un repère existant (dans le
  /// canevas, voir badge_builder_canvas.dart::onGuideMoveStart) le
  /// repositionne au lieu d'en créer un nouveau.
  void _onGuideMoveStart(bool vertical, int index) {
    setState(() {
      _draggingGuideVertical = vertical;
      _draggingGuideIndex = index;
    });
  }

  /// [modelDelta] est déjà en unités modèle (voir la doc de
  /// `BadgeBuilderCanvas.onGuideDragUpdate`) — accumulé DIRECTEMENT sur la
  /// valeur déjà persistée du repère, comme `BadgeCanvasElement._move`
  /// accumule `event.delta` sur `el.x`/`el.y`, plutôt que de recalculer une
  /// position absolue à chaque frame.
  void _onGuideDragUpdate(double modelDelta) {
    final index = _draggingGuideIndex;
    if (index == null) return;
    setState(() {
      final list = _draggingGuideVertical
          ? _currentSide.guidesX
          : _currentSide.guidesY;
      if (index < list.length) list[index] += modelDelta;
    });
  }

  /// Un repère relâché HORS du canevas (glissé en arrière sur la règle, ou
  /// au-delà du bord opposé) est supprimé — convention Adobe/Figma.
  void _onGuideDragEnd() {
    final index = _draggingGuideIndex;
    final vertical = _draggingGuideVertical;
    _draggingGuideIndex = null;
    if (index == null) return;
    final layout = _layout;
    if (layout == null) return;
    final extent = vertical ? layout.canvasWidth : layout.canvasHeight;
    setState(() {
      final list = vertical ? _currentSide.guidesX : _currentSide.guidesY;
      if (index < list.length && (list[index] < 0 || list[index] > extent)) {
        list.removeAt(index);
      }
    });
  }

  /// Grave tout déclencheur `subtractBackground` laissé à `true` dans un
  /// gabarit chargé depuis le disque — compatibilité avec des fichiers
  /// enregistrés par une version antérieure de cet éditeur, où ce champ
  /// était un état PERSISTANT (masque dynamique recalculé à chaque frame,
  /// voir l'historique dans badge_builder_canvas.dart) plutôt qu'un
  /// déclencheur ponctuel. Sans cette migration, une forme qui découpait
  /// visuellement quelque chose dans l'ancien modèle redeviendrait un
  /// simple élément normal, sans trou, à l'ouverture du fichier.
  void _migrateLegacySubtractFlags(BadgeLayoutTemplate layout) {
    for (final side in [
      layout.recto,
      if (layout.verso != null) layout.verso!,
    ]) {
      final sorted = [...side.elements]
        ..sort((a, b) => a.zIndex.compareTo(b.zIndex));
      for (final el in sorted) {
        if (!el.subtractBackground) continue;
        bakeSubtraction(el, sorted);
        el.subtractBackground = false;
      }
    }
  }

  void _addText() => _addElement(
    (id) => BadgeElement(
      id: id,
      type: BadgeElementType.text,
      x: 100,
      y: 100,
      width: 300,
      height: 40,
      text: 'Nouveau texte',
      fontSize: 18,
    ),
  );

  /// Champ dynamique lié aux données de l'étudiant (voir barre d'outils,
  /// menu "Champ dynamique") — un texte prérempli avec le jeton
  /// (`{{nom}}`, etc.), substitué par la vraie valeur au moment de générer
  /// un badge (badge_screen.dart::_generate()) plutôt qu'un texte libre
  /// que l'utilisateur devrait taper lui-même : c'est ce qui fait d'un
  /// gabarit un vrai "template" réutilisable capable de recevoir les
  /// informations de chaque étudiant, pas juste une image statique.
  void _addField(String token) {
    // "Personnalisé", dernière option du menu — un texte libre ordinaire,
    // pas un jeton de substitution (il n'y a rien à substituer pour une
    // valeur que l'utilisateur invente lui-même).
    if (token == kBadgeCustomFieldToken) {
      _addText();
      return;
    }
    _addElement(
      (id) => BadgeElement(
        id: id,
        type: BadgeElementType.text,
        x: 100,
        y: 100,
        width: 300,
        height: 40,
        text: token,
        fontSize: 18,
      ),
    );
  }

  void _addShape() => _addElement(
    (id) => BadgeElement(
      id: id,
      type: BadgeElementType.shape,
      x: 100,
      y: 100,
      width: 200,
      height: 100,
      shapeKind: BadgeShapeKind.rectangle,
      strokeColor: 0xFF003366,
      strokeWidth: 2,
    ),
  );

  void _addPhotoPlaceholder() => _addElement(
    (id) => BadgeElement(
      id: id,
      type: BadgeElementType.photoPlaceholder,
      x: 97,
      y: 127,
      width: 234,
      height: 261,
    ),
  );

  void _addQrPlaceholder() => _addElement(
    (id) => BadgeElement(
      id: id,
      type: BadgeElementType.qrPlaceholder,
      x: 880,
      y: 530,
      width: 90,
      height: 90,
    ),
  );

  /// Charge un fichier PNG/JPEG (logo, signature scannée...) comme élément
  /// statique — contrairement à `_addPhotoPlaceholder`, la même image
  /// s'affiche sur CHAQUE badge généré, pas une photo différente par
  /// étudiant. L'id de l'élément est connu AVANT l'appel au sélecteur de
  /// fichier (`BadgeLayoutStore.pickElementImage` en a besoin pour nommer
  /// le fichier copié), donc pas de `_addElement` ici.
  Future<void> _addStaticImage() async {
    final id = BadgeLayoutStore.instance.newId();
    final path = await BadgeLayoutStore.instance.pickElementImage(
      elementId: id,
    );
    if (path == null || !mounted) return;
    setState(() {
      _currentSide.elements.add(
        BadgeElement(
          id: id,
          type: BadgeElementType.staticImage,
          x: 100,
          y: 100,
          width: 200,
          height: 120,
          imagePath: path,
          fit: BadgePhotoFit.contain,
        ),
      );
      _selectedId = id;
    });
  }

  /// "Remplacer l'image" du panneau de propriétés — remplace le fichier
  /// SANS changer l'id de l'élément (même nom de fichier copié, voir
  /// `BadgeLayoutStore.pickElementImage`), donc pas de nouvel id à
  /// répercuter ailleurs (position/taille/rotation déjà en place restent
  /// inchangées).
  Future<void> _replaceStaticImage() async {
    final el = _selectedElement;
    if (el == null || el.type != BadgeElementType.staticImage) return;
    final path = await BadgeLayoutStore.instance.pickElementImage(
      elementId: el.id,
    );
    if (path == null || !mounted) return;
    setState(() => el.imagePath = path);
  }

  void _duplicateSelected() {
    final el = _selectedElement;
    if (el == null) return;
    final clone = el.clone()
      ..id = BadgeLayoutStore.instance.newId()
      ..x += 16
      ..y += 16;
    setState(() {
      _currentSide.elements.add(clone);
      _selectedId = clone.id;
    });
  }

  void _deleteSelected() {
    final id = _selectedId;
    if (id == null) return;
    setState(() {
      _currentSide.elements.removeWhere((e) => e.id == id);
      _selectedId = null;
    });
  }

  /// Tolérance de fermeture du tracé, en unités MODÈLE (indépendante du
  /// zoom d'affichage) — cliquer à moins de cette distance du premier
  /// point ferme la forme plutôt que d'ajouter un nouveau point.
  static const _penCloseTolerance = 14.0;

  void _togglePenTool() {
    setState(() {
      _penActive = !_penActive;
      _penDraft.clear();
      _selectedId = null;
    });
  }

  void _onPenPointerDown(Offset modelPosition) {
    if (_penDraft.length >= 3) {
      final first = _penDraft.first;
      final dx = modelPosition.dx - first.x;
      final dy = modelPosition.dy - first.y;
      if (dx * dx + dy * dy <= _penCloseTolerance * _penCloseTolerance) {
        _finalizePen(closed: true);
        return;
      }
    }
    setState(
      () => _penDraft.add(
        BadgePathPoint(x: modelPosition.dx, y: modelPosition.dy),
      ),
    );
  }

  /// Glisser-déposer depuis l'ancre qu'on vient de poser façon Adobe : la
  /// poignée SORTANTE suit le glissement, l'ENTRANTE est son symétrique
  /// (point "lisse") — un simple clic sans glisser laisse les deux
  /// poignées `null` (point "coin", segments droits).
  void _onPenDrag(Offset modelDelta) {
    if (_penDraft.isEmpty) return;
    setState(() {
      final last = _penDraft.last;
      final newOutX = (last.outX ?? 0) + modelDelta.dx;
      final newOutY = (last.outY ?? 0) + modelDelta.dy;
      last.outX = newOutX;
      last.outY = newOutY;
      last.inX = -newOutX;
      last.inY = -newOutY;
    });
  }

  void _penUndoLastPoint() {
    if (_penDraft.isEmpty) return;
    setState(() => _penDraft.removeLast());
  }

  void _penCancel() {
    setState(() {
      _penActive = false;
      _penDraft.clear();
    });
  }

  void _penFinishOpen() => _finalizePen(closed: false);

  /// Calcule la boîte englobante des ancres posées (les poignées peuvent
  /// légèrement déborder, accepté — voir le plan de cette fonctionnalité)
  /// puis normalise chaque point dans cette boîte (0..1) avant de créer
  /// l'élément final, réutilisable comme n'importe quel autre (glisser/
  /// redimensionner/pivoter via BadgeCanvasElement, sans code spécifique).
  void _finalizePen({required bool closed}) {
    if (_penDraft.length < 2) {
      _penCancel();
      return;
    }
    // La boîte englobante doit couvrir les POIGNÉES, pas seulement les
    // ancres : une courbe très bombée (grande poignée) peut visuellement
    // dépasser très largement un rectangle qui ne couvrirait que les
    // points cliqués — sans ça, la boîte de l'élément (et donc sa zone
    // cliquable de sélection/redimensionnement) ne correspond pas à ce
    // qui est réellement dessiné, symptôme observé : une hauteur de 1px
    // pour une courbe bien visible, rendant l'élément quasi impossible à
    // resélectionner ensuite.
    final xs = <double>[];
    final ys = <double>[];
    for (final p in _penDraft) {
      xs.add(p.x);
      ys.add(p.y);
      if (p.inX != null) {
        xs.add(p.x + p.inX!);
        ys.add(p.y + p.inY!);
      }
      if (p.outX != null) {
        xs.add(p.x + p.outX!);
        ys.add(p.y + p.outY!);
      }
    }
    final minX = xs.reduce((a, b) => a < b ? a : b);
    final maxX = xs.reduce((a, b) => a > b ? a : b);
    final minY = ys.reduce((a, b) => a < b ? a : b);
    final maxY = ys.reduce((a, b) => a > b ? a : b);
    final width = (maxX - minX).clamp(1.0, double.infinity);
    final height = (maxY - minY).clamp(1.0, double.infinity);

    final normalized = _penDraft
        .map(
          (p) => BadgePathPoint(
            x: (p.x - minX) / width,
            y: (p.y - minY) / height,
            inX: p.inX == null ? null : p.inX! / width,
            inY: p.inY == null ? null : p.inY! / height,
            outX: p.outX == null ? null : p.outX! / width,
            outY: p.outY == null ? null : p.outY! / height,
          ),
        )
        .toList();

    final id = BadgeLayoutStore.instance.newId();
    setState(() {
      _currentSide.elements.add(
        BadgeElement(
          id: id,
          type: BadgeElementType.shape,
          x: minX,
          y: minY,
          width: width,
          height: height,
          shapeKind: BadgeShapeKind.path,
          pathPoints: normalized,
          pathClosed: closed,
          strokeColor: 0xFF003366,
          strokeWidth: 2,
        ),
      );
      _selectedId = id;
      _penActive = false;
      _penDraft.clear();
    });
  }

  void _reorderSelected({required bool toFront}) {
    final el = _selectedElement;
    if (el == null) return;
    final elements = _currentSide.elements;
    final zs = elements.map((e) => e.zIndex);
    setState(() {
      el.zIndex = toFront
          ? zs.fold(0, (a, b) => a > b ? a : b) + 1
          : zs.fold(0, (a, b) => a < b ? a : b) - 1;
    });
  }

  Future<void> _pickBackground() async {
    final path = await BadgeLayoutStore.instance.pickBackgroundImage(
      layoutId: _layout!.id,
      isVerso: _isVerso,
    );
    if (path != null) setState(() => _currentSide.backgroundImagePath = path);
  }

  /// Charge une image PNG/JPEG comme fond (même sélecteur/stockage que
  /// "Image de fond") et propose ENSUITE de placer les champs standards
  /// d'un badge — mêmes rôles/positions que generate_badge() côté bureau
  /// (school_client, Controllers/Main.py:6144) et son port
  /// widgets/badge_renderer.dart : photo (97,127,234,261), nom complet et
  /// classe centrés, identifiant/expiration/salle, QR (880,530,90,90).
  /// Ce placement automatique n'a de sens QUE pour un visuel qui suit
  /// réellement ce modèle connu ; pour un template personnalisé différent,
  /// il produirait des champs mal positionnés — l'utilisateur choisit donc
  /// explicitement, plutôt que de le subir.
  Future<void> _loadTemplateImage() async {
    final hasExistingContent =
        _currentSide.elements.isNotEmpty || !_layout!.isLandscape;
    if (hasExistingContent) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (dialogContext) => AlertDialog(
          title: const Text('Charger un template'),
          content: const Text(
            'Cela bascule le gabarit en paysage et remplace l\'image de fond '
            'ainsi que TOUS les éléments de cette face. Continuer ?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: const Text('Annuler'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: const Text('Remplacer'),
            ),
          ],
        ),
      );
      if (confirmed != true) return;
    }

    final path = await BadgeLayoutStore.instance.pickBackgroundImage(
      layoutId: _layout!.id,
      isVerso: _isVerso,
    );
    if (path == null || !mounted) return;

    final autoPlace = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Placement des champs'),
        content: const Text(
          'Placer automatiquement les champs standards d\'un badge (photo, '
          'nom, classe, identifiant, expiration, salle, QR) aux positions du '
          'modèle connu ?\n\nSi ce visuel est un template personnalisé '
          'différent, ces positions ne correspondront probablement pas au '
          'design — choisissez plutôt "Je les placerai moi-même" pour '
          'partir d\'un canevas vide.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Je les placerai moi-même'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Placer automatiquement'),
          ),
        ],
      ),
    );
    if (!mounted) return;
    setState(() {
      _layout!.isLandscape = true;
      _currentSide.backgroundImagePath = path;
      _currentSide.elements.clear();
      if (autoPlace == true) {
        _currentSide.elements.addAll(_standardBadgeElements());
      }
      _selectedId = null;
    });
  }

  List<BadgeElement> _standardBadgeElements() {
    final store = BadgeLayoutStore.instance;
    BadgeElement text({
      required double x,
      required double y,
      required double width,
      required double height,
      required String text,
      required double fontSize,
      bool bold = false,
      BadgeTextAlign align = BadgeTextAlign.center,
    }) => BadgeElement(
      id: store.newId(),
      type: BadgeElementType.text,
      x: x,
      y: y,
      width: width,
      height: height,
      text: text,
      fontSize: fontSize,
      bold: bold,
      textAlign: align,
    );

    return [
      text(
        x: 0,
        y: 40,
        width: 1013,
        height: 50,
        text: 'Nom de l\'école',
        fontSize: 28,
        bold: true,
      ),
      BadgeElement(
        id: store.newId(),
        type: BadgeElementType.photoPlaceholder,
        x: 97,
        y: 127,
        width: 234,
        height: 261,
      ),
      text(
        x: 100,
        y: 180,
        width: 1013,
        height: 200,
        text: '{{nom}} {{prenom}}',
        fontSize: 24,
        bold: true,
      ),
      text(
        x: 100,
        y: 220,
        width: 1013,
        height: 200,
        text: '{{classe}}',
        fontSize: 20,
      ),
      text(
        x: 62,
        y: 461,
        width: 300,
        height: 22,
        text: '{{identifiant}}',
        fontSize: 18,
        bold: true,
        align: BadgeTextAlign.left,
      ),
      text(
        x: 300,
        y: 466,
        width: 250,
        height: 20,
        text: '{{expiration}}',
        fontSize: 17,
        align: BadgeTextAlign.left,
      ),
      text(
        x: 560,
        y: 466,
        width: 250,
        height: 20,
        text: '{{salle}}',
        fontSize: 17,
        align: BadgeTextAlign.left,
      ),
      BadgeElement(
        id: store.newId(),
        type: BadgeElementType.qrPlaceholder,
        x: 880,
        y: 530,
        width: 90,
        height: 90,
      ),
    ];
  }

  /// Ouvre la recherche d'étudiant (dialogue) — sélectionner un résultat
  /// charge son détail (`StudentsState.loadDetail`, déjà utilisé de la
  /// même façon dans badge_screen.dart) pour alimenter l'aperçu en direct
  /// (jetons de substitution + vraie photo si disponible).
  Future<void> _openPreviewStudentSearch() async {
    final selected = await showDialog<Student>(
      context: context,
      builder: (dialogContext) => const _PreviewStudentSearchDialog(),
    );
    if (selected == null || !mounted) return;
    await context.read<StudentsState>().loadDetail(selected.id);
  }

  void _clearPreviewStudent() {
    context.read<StudentsState>().clearDetail();
    setState(() => _testPhotoBytes = null);
  }

  Future<void> _captureTestPhoto() async {
    final bytes = await showBadgeTestPhotoCaptureDialog(context);
    if (bytes != null && mounted) setState(() => _testPhotoBytes = bytes);
  }

  /// "Charger une photo" — même sélecteur que badge_screen.dart::_pickPhoto,
  /// absent ici jusqu'ici (seule la capture caméra était possible).
  Future<void> _loadTestPhoto() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    final bytes = result?.files.single.bytes;
    if (bytes != null && mounted) setState(() => _testPhotoBytes = bytes);
  }

  /// Enregistre `_testPhotoBytes` (capturée ou chargée) sur la fiche de
  /// l'étudiant prévisualisé — même appel que badge_screen.dart::_onEnregistrer
  /// (`StudentsState.saveBadgePhoto`), absent ici jusqu'ici : une photo
  /// test ne pouvait jamais être réutilisée pour de vrai sans repasser par
  /// le sous-onglet "Badge".
  Future<void> _saveTestPhotoToStudent(StudentDetail detail) async {
    final bytes = _testPhotoBytes;
    if (bytes == null) return;
    setState(() => _savingPhoto = true);
    final dataUri = 'data:image/jpeg;base64,${base64Encode(bytes)}';
    final error = await context.read<StudentsState>().saveBadgePhoto(
      studentId: detail.id,
      photoBase64: dataUri,
    );
    if (!mounted) return;
    setState(() => _savingPhoto = false);
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Photo enregistrée sur la fiche de l\'étudiant.'),
      ),
    );
  }

  String _formatExpiration() => '${_moisNoms[_expMonth - 1]} $_expYear';

  /// `{{expiration}}`/`{{salle}}` sont des réglages globaux (champs
  /// ci-dessous, mois/année/salle), résolus qu'un étudiant soit prévisualisé
  /// ou non — `{{nom}}`/`{{prenom}}`/`{{classe}}`/`{{identifiant}}` restent
  /// eux propres à l'étudiant recherché (voir `_openPreviewStudentSearch`).
  Map<String, String> _previewValues(StudentDetail? detail) {
    final values = <String, String>{
      '{{expiration}}': _formatExpiration(),
      '{{salle}}': _salles[_salle] ?? '',
    };
    if (detail != null) {
      values['{{nom}}'] = detail.nom;
      values['{{prenom}}'] = detail.prenom;
      values['{{classe}}'] = detail.classeActuelle?.nomClasse ?? '';
      values['{{identifiant}}'] = detail.identifiant;
    }
    return values;
  }

  /// La photo test capturée à la caméra a priorité (calibrage immédiat des
  /// réglages) ; sinon, la vraie photo de l'étudiant recherché si présente.
  Uint8List? _previewPhotoBytes(StudentDetail? detail) {
    if (_testPhotoBytes != null) return _testPhotoBytes;
    final base64Photo = detail?.photoBase64;
    if (base64Photo == null || base64Photo.isEmpty) return null;
    final raw = base64Photo.contains(',')
        ? base64Photo.split(',').last
        : base64Photo;
    try {
      return base64Decode(raw);
    } catch (_) {
      return null;
    }
  }

  /// Donnée automatique du QR (contact du responsable) — même construction
  /// que badge_screen.dart::_onGenerer (`adresseResponsable` + `\n` +
  /// `telephoneResponsable`), pour que l'aperçu en direct ET les exports
  /// affichent le même QR par défaut. `null` en l'absence de coordonnées
  /// (pas de fausse valeur "responsable info" ici, contrairement à
  /// badge_screen.dart : cette dernière garantit un badge réel toujours
  /// scannable, alors qu'ici pas de donnée reste le pictogramme neutre,
  /// cohérent avec l'aperçu quand aucun étudiant n'est recherché).
  /// `el.qrCustomData` reste prioritaire (voir
  /// badge_layout_renderer.dart::_drawQr / badge_builder_canvas.dart::_QrPreview).
  String? _previewQrData(StudentDetail? detail) {
    if (detail == null || !(detail.adresseResponsable?.isNotEmpty ?? false))
      return null;
    return '${detail.adresseResponsable} \n ${detail.telephoneResponsable ?? ''}';
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    await BadgeLayoutStore.instance.save(_layout!);
    if (!mounted) return;
    setState(() => _saving = false);
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Gabarit enregistré.')));
  }

  Future<void> _openLoadDialog() async {
    final layouts = await BadgeLayoutStore.instance.list();
    if (!mounted) return;
    final chosen = await showDialog<BadgeLayoutTemplate>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setDialogState) => SimpleDialog(
          title: const Text('Charger un gabarit'),
          children: [
            if (layouts.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 24),
                child: Text('Aucun gabarit enregistré.'),
              ),
            for (final l in layouts)
              SimpleDialogOption(
                onPressed: () => Navigator.pop(dialogContext, l),
                child: Row(
                  children: [
                    Expanded(child: Text(l.name)),
                    IconButton(
                      tooltip: 'Supprimer',
                      icon: const Icon(Icons.delete_outline, size: 18),
                      onPressed: () async {
                        await BadgeLayoutStore.instance.delete(l.id);
                        layouts.remove(l);
                        setDialogState(() {});
                      },
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
    if (chosen != null) {
      _migrateLegacySubtractFlags(chosen);
      setState(() {
        _layout = chosen;
        _isVerso = false;
        _selectedId = null;
      });
    }
  }

  void _toggleOrientation() {
    final layout = _layout!;
    final oldW = layout.canvasWidth;
    final oldH = layout.canvasHeight;
    setState(() {
      layout.isLandscape = !layout.isLandscape;
      final sx = layout.canvasWidth / oldW;
      final sy = layout.canvasHeight / oldH;
      for (final side in [
        layout.recto,
        if (layout.verso != null) layout.verso!,
      ]) {
        for (final el in side.elements) {
          el.x *= sx;
          el.y *= sy;
          el.width *= sx;
          el.height *= sy;
        }
      }
    });
  }

  /// Taille du badge selon l'orientation courante — 300dpi, comme
  /// `widgets/badge_renderer.dart`/`badge_layout_renderer.dart`.
  String _sizeLabel(BadgeLayoutTemplate layout) {
    final wCm = (layout.canvasWidth / 300 * 2.54)
        .toStringAsFixed(1)
        .replaceAll('.', ',');
    final hCm = (layout.canvasHeight / 300 * 2.54)
        .toStringAsFixed(1)
        .replaceAll('.', ',');
    return '${layout.canvasWidth.toInt()} × ${layout.canvasHeight.toInt()} px  ($wCm × $hCm cm)';
  }

  void _addVerso() => setState(() => _layout!.verso = BadgeSide());

  /// Écrit [bytes] puis l'ouvre avec l'application par défaut du système
  /// (pas de dépendance sur un dialogue "Enregistrer sous" natif, jamais
  /// utilisé ailleurs dans cette app). Avec un étudiant prévisualisé (voir
  /// "Aperçu avec un étudiant"), le fichier est un vrai badge pour CET
  /// étudiant — même organisation par dossiers que
  /// badge_screen.dart::_generate() (`badgeOutputFile`, sur demande
  /// explicite). Sans étudiant prévisualisé (test d'un gabarit à l'état
  /// abstrait, jetons `{{...}}` non résolus), aucune fiche à laquelle
  /// rattacher un dossier : fichier temporaire, comme avant.
  Future<void> _openGenerated(
    List<int> bytes, {
    required String baseName,
    required String extension,
    StudentDetail? previewDetail,
  }) async {
    final file = previewDetail != null
        ? badgeOutputFile(
            anneeLabel: previewDetail.classeActuelle?.anneeLabel ?? '',
            classeName: previewDetail.classeActuelle?.nomClasse ?? '',
            fullName: '${previewDetail.nom} ${previewDetail.prenom}',
            extension: extension,
          )
        : File('${Directory.systemTemp.path}/$baseName.$extension');
    await file.writeAsBytes(bytes);
    if (Platform.isMacOS) {
      await Process.run('open', [file.path]);
    } else if (Platform.isWindows) {
      await Process.run('cmd', ['/c', 'start', '', file.path]);
    } else if (Platform.isLinux) {
      await Process.run('xdg-open', [file.path]);
    }
  }

  /// Octets de l'image de fond de [side] (voir `BadgeSide.backgroundImagePath`,
  /// choisie via "Image de fond"/"Charger un template") — `null` si aucune
  /// image n'a été choisie pour cette face. Sans ça, l'export produisait un
  /// canevas blanc : `renderBadgeFromLayout` n'affiche l'image de fond QUE
  /// si on lui passe explicitement ses octets, contrairement à l'aperçu en
  /// direct (`badge_builder_canvas.dart`) qui lit directement le fichier.
  Future<Uint8List?> _backgroundImageBytes(BadgeSide side) async {
    final path = side.backgroundImagePath;
    if (path == null) return null;
    final file = File(path);
    if (!file.existsSync()) return null;
    return file.readAsBytes();
  }

  Future<void> _exportPng() async {
    if (!canPrintNonReceipt(context)) return;
    setState(() => _exporting = true);
    try {
      // Même donnée que l'aperçu en direct (recherche d'étudiant + photo
      // test) — sans ça, l'export ignorait tout ce qui était visible à
      // l'écran et ne montrait que les jetons `{{...}}` littéraux.
      final previewDetail = context.read<StudentsState>().currentDetail;
      final bytes = await renderBadgeFromLayout(
        layout: _layout!,
        side: _currentSide,
        placeholderValues: _previewValues(previewDetail),
        backgroundImageBytes: await _backgroundImageBytes(_currentSide),
        photoBytes: _previewPhotoBytes(previewDetail),
        qrData: _previewQrData(previewDetail),
      );
      await _openGenerated(
        bytes,
        baseName: '${_layout!.name}_${_isVerso ? 'verso' : 'recto'}',
        extension: 'png',
        previewDetail: previewDetail,
      );
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  Future<void> _exportPdf() async {
    if (!canPrintNonReceipt(context)) return;
    setState(() => _exporting = true);
    try {
      final layout = _layout!;
      final previewDetail = context.read<StudentsState>().currentDetail;
      final placeholderValues = _previewValues(previewDetail);
      final photoBytes = _previewPhotoBytes(previewDetail);
      final qrData = _previewQrData(previewDetail);
      final rectoBytes = await renderBadgeFromLayout(
        layout: layout,
        side: layout.recto,
        placeholderValues: placeholderValues,
        backgroundImageBytes: await _backgroundImageBytes(layout.recto),
        photoBytes: photoBytes,
        qrData: qrData,
      );
      final doc = pw.Document();
      doc.addPage(
        pw.Page(
          pageFormat: const pw.PageTheme().pageFormat,
          build: (context) =>
              pw.Center(child: pw.Image(pw.MemoryImage(rectoBytes))),
        ),
      );
      if (layout.verso != null) {
        final versoBytes = await renderBadgeFromLayout(
          layout: layout,
          side: layout.verso!,
          placeholderValues: placeholderValues,
          backgroundImageBytes: await _backgroundImageBytes(layout.verso!),
          photoBytes: photoBytes,
          qrData: qrData,
        );
        doc.addPage(
          pw.Page(
            build: (context) =>
                pw.Center(child: pw.Image(pw.MemoryImage(versoBytes))),
          ),
        );
      }
      final bytes = await doc.save();
      await _openGenerated(
        bytes,
        baseName: layout.name,
        extension: 'pdf',
        previewDetail: previewDetail,
      );
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final layout = _layout;
    if (layout == null) return const Center(child: CircularProgressIndicator());

    final previewDetail = context.watch<StudentsState>().currentDetail;
    final previewValues = _previewValues(previewDetail);
    final previewPhotoBytes = _previewPhotoBytes(previewDetail);
    final previewQrData = _previewQrData(previewDetail);

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              if (widget.onBack != null)
                Padding(
                  padding: const EdgeInsets.only(right: 4),
                  child: IconButton(
                    onPressed: widget.onBack,
                    icon: const Icon(Icons.arrow_back, size: 18),
                    tooltip: 'Retour à la liste',
                    visualDensity: VisualDensity.compact,
                  ),
                ),
              const Expanded(
                child: SectionHeader(
                  title: 'Construire la badge',
                  subtitle:
                      'Éditeur visuel de gabarit — recto-verso, positionnement libre',
                  icon: Icons.dashboard_customize_outlined,
                  colorKey: 'violet',
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildTopBar(layout),
          const SizedBox(height: 10),
          _buildPreviewBar(previewDetail),
          if (_penActive) ...[const SizedBox(height: 10), _buildPenBar()],
          const SizedBox(height: 12),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                BadgeBuilderToolbar(
                  onAddText: _addText,
                  onAddField: _addField,
                  onAddShape: _addShape,
                  onAddPhotoPlaceholder: _addPhotoPlaceholder,
                  onAddQrPlaceholder: _addQrPlaceholder,
                  onAddImage: _addStaticImage,
                  onPickBackground: _pickBackground,
                  hasSelection: _selectedElement != null,
                  onDuplicate: _duplicateSelected,
                  onDelete: _deleteSelected,
                  onBringToFront: () => _reorderSelected(toFront: true),
                  onSendToBack: () => _reorderSelected(toFront: false),
                  penActive: _penActive,
                  onTogglePen: _togglePenTool,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 880),
                      child: BadgeBuilderCanvas(
                        layout: layout,
                        side: _currentSide,
                        selectedId: _selectedId,
                        onSelect: (id) => setState(() => _selectedId = id),
                        onElementChanged: _onElementChanged,
                        penActive: _penActive,
                        penDraft: _penDraft,
                        onPenPointerDown: _onPenPointerDown,
                        onPenDrag: _onPenDrag,
                        previewValues: previewValues,
                        previewPhotoBytes: previewPhotoBytes,
                        previewQrData: previewQrData,
                        onGuideCreateStart: _onGuideCreateStart,
                        onGuideMoveStart: _onGuideMoveStart,
                        onGuideDragUpdate: _onGuideDragUpdate,
                        onGuideDragEnd: _onGuideDragEnd,
                        // Ne s'applique que si l'élément en édition de
                        // points EST TOUJOURS celui sélectionné — sinon
                        // des poignées orphelines resteraient affichées
                        // pour un élément qu'on ne regarde plus (voir la
                        // doc de _editingPathElementId).
                        editingPathElementId:
                            _editingPathElementId == _selectedId
                            ? _editingPathElementId
                            : null,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                _buildInspectorColumn(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Panneau "Propriétés"/"Calques" — une SEULE colonne de largeur fixe,
  /// basculée par un petit sélecteur d'onglet, plutôt que les deux
  /// affichés côte à côte comme avant : ça réduisait considérablement la
  /// place laissée au canevas (symptôme rapporté après l'ajout du panneau
  /// des calques).
  Widget _buildInspectorColumn() {
    return SizedBox(
      width: 280,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: _inspectorTabButton(
                  'Propriétés',
                  !_showLayersTab,
                  () => setState(() => _showLayersTab = false),
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: _inspectorTabButton(
                  'Calques',
                  _showLayersTab,
                  () => setState(() => _showLayersTab = true),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _showLayersTab
                ? BadgeBuilderLayersPanel(
                    elements: _currentSide.elements,
                    selectedId: _selectedId,
                    onSelect: (id) => setState(() => _selectedId = id),
                    onToggleHidden: (el) =>
                        setState(() => el.hidden = !el.hidden),
                    onToggleLocked: (el) =>
                        setState(() => el.locked = !el.locked),
                  )
                : BadgeBuilderPropertyPanel(
                    element: _selectedElement,
                    onChanged: _onElementChanged,
                    onCaptureTestPhoto: _captureTestPhoto,
                    onLoadTestPhoto: _loadTestPhoto,
                    onPickElementImage: _replaceStaticImage,
                    editingPoints:
                        _editingPathElementId != null &&
                        _editingPathElementId == _selectedElement?.id,
                    onToggleEditPoints: _selectedElement == null
                        ? null
                        : () => setState(() {
                            final id = _selectedElement!.id;
                            _editingPathElementId = _editingPathElementId == id
                                ? null
                                : id;
                          }),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _inspectorTabButton(String label, bool selected, VoidCallback onTap) {
    return OutlinedButton(
      onPressed: onTap,
      style: OutlinedButton.styleFrom(
        backgroundColor: selected
            ? AppColors.accentLight.withValues(alpha: 0.18)
            : null,
        side: BorderSide(
          color: selected ? AppColors.accent : AppColors.borderSubtle,
        ),
        padding: const EdgeInsets.symmetric(vertical: 8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
    );
  }

  Widget _buildTopBar(BadgeLayoutTemplate layout) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        SizedBox(
          width: 220,
          child: TextFormField(
            key: ValueKey('name-${layout.id}'),
            initialValue: layout.name,
            decoration: const InputDecoration(
              labelText: 'Nom du gabarit',
              isDense: true,
            ),
            onChanged: (v) => layout.name = v,
          ),
        ),
        SegmentedButton<bool>(
          segments: const [
            ButtonSegment(
              value: true,
              label: Text('Paysage'),
              icon: Icon(Icons.crop_landscape, size: 16),
            ),
            ButtonSegment(
              value: false,
              label: Text('Portrait'),
              icon: Icon(Icons.crop_portrait, size: 16),
            ),
          ],
          selected: {layout.isLandscape},
          onSelectionChanged: (_) => _toggleOrientation(),
        ),
        Text(
          _sizeLabel(layout),
          style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
        ),
        SegmentedButton<bool>(
          segments: [
            const ButtonSegment(value: false, label: Text('Recto')),
            ButtonSegment(
              value: true,
              label: const Text('Verso'),
              enabled: layout.hasVerso,
            ),
          ],
          selected: {_isVerso},
          onSelectionChanged: (s) => setState(() => _isVerso = s.first),
        ),
        if (!layout.hasVerso)
          PillButton(
            label: 'Ajouter un verso',
            colorKey: 'violet',
            icon: Icons.flip,
            onPressed: _addVerso,
          ),
        PillButton(
          label: 'Nouveau',
          colorKey: 'sky',
          icon: Icons.add,
          onPressed: _newLayout,
        ),
        PillButton(
          label: 'Charger',
          colorKey: 'sky',
          icon: Icons.folder_open_outlined,
          onPressed: _openLoadDialog,
        ),
        PillButton(
          label: 'Charger un template',
          colorKey: 'violet',
          icon: Icons.wallpaper_outlined,
          onPressed: _loadTemplateImage,
        ),
        PillButton(
          label: _saving ? 'Enregistrement…' : 'Enregistrer',
          colorKey: 'emerald',
          icon: Icons.save_outlined,
          onPressed: _saving ? null : _save,
        ),
        PillButton(
          label: 'Exporter PNG',
          colorKey: 'amber',
          icon: Icons.image_outlined,
          onPressed: _exporting ? null : _exportPng,
        ),
        PillButton(
          label: 'Exporter PDF',
          colorKey: 'amber',
          icon: Icons.picture_as_pdf_outlined,
          onPressed: _exporting ? null : _exportPdf,
        ),
      ],
    );
  }

  /// Aperçu en direct — rechercher un étudiant substitue ses vraies
  /// valeurs aux jetons (`{{nom}}`, etc.) et affiche sa photo dans les
  /// emplacements photo, pour voir immédiatement à quoi ressemblera un
  /// vrai badge sans quitter l'éditeur.
  Widget _buildPreviewBar(StudentDetail? previewDetail) {
    return Wrap(
      spacing: 10,
      runSpacing: 8,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        PillButton(
          label: previewDetail == null
              ? 'Aperçu avec un étudiant'
              : 'Aperçu : ${previewDetail.nom} ${previewDetail.prenom}',
          colorKey: 'cyan',
          icon: Icons.person_search_outlined,
          onPressed: _openPreviewStudentSearch,
        ),
        if (previewDetail != null)
          TextButton.icon(
            onPressed: _clearPreviewStudent,
            icon: const Icon(Icons.close, size: 15),
            label: const Text(
              'Effacer l\'aperçu',
              style: TextStyle(fontSize: 12.5),
            ),
          ),
        // Réglages globaux `{{expiration}}`/`{{salle}}` — voir
        // _previewValues, absents jusqu'ici (ces jetons restaient toujours
        // affichés littéralement dans l'aperçu ET l'export).
        SizedBox(
          width: 160,
          child: DropdownButtonFormField<int>(
            initialValue: _expMonth,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Mois d\'expiration',
              isDense: true,
            ),
            items: [
              for (var m = 1; m <= 12; m++)
                DropdownMenuItem(value: m, child: Text(_moisNoms[m - 1])),
            ],
            onChanged: (v) => setState(() => _expMonth = v ?? _expMonth),
          ),
        ),
        SizedBox(
          width: 130,
          child: DropdownButtonFormField<int>(
            initialValue: _expYear,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Année',
              isDense: true,
            ),
            items: [
              for (
                var y = DateTime.now().year;
                y <= DateTime.now().year + 5;
                y++
              )
                DropdownMenuItem(value: y, child: Text('$y')),
            ],
            onChanged: (v) => setState(() => _expYear = v ?? _expYear),
          ),
        ),
        SizedBox(
          width: 130,
          child: DropdownButtonFormField<String>(
            initialValue: _salle,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Salle',
              isDense: true,
            ),
            items: _salles.entries
                .map(
                  (e) => DropdownMenuItem(value: e.key, child: Text(e.value)),
                )
                .toList(),
            onChanged: (v) => setState(() => _salle = v ?? _salle),
          ),
        ),
        if (previewDetail != null && _testPhotoBytes != null)
          PillButton(
            label: _savingPhoto ? 'Enregistrement…' : 'Enregistrer la photo',
            colorKey: 'emerald',
            icon: Icons.save_outlined,
            onPressed: _savingPhoto
                ? null
                : () => _saveTestPhotoToStudent(previewDetail),
          ),
      ],
    );
  }

  Widget _buildPenBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.accent.withValues(alpha: 0.08),
        border: Border.all(color: AppColors.accent.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Wrap(
        spacing: 10,
        runSpacing: 6,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Icon(Icons.draw_outlined, size: 16, color: AppColors.accent),
          Text(
            'Plume active — cliquez pour poser un point, glissez pour le courber. '
            'Cliquez sur le premier point (vert) pour fermer la forme.',
            style: TextStyle(fontSize: 12, color: AppColors.textMuted),
          ),
          PillButton(
            label: 'Terminer (fermé)',
            colorKey: 'violet',
            icon: Icons.done_all,
            onPressed: _penDraft.length >= 3
                ? () => _finalizePen(closed: true)
                : null,
          ),
          PillButton(
            label: 'Terminer (ouvert)',
            colorKey: 'sky',
            icon: Icons.done,
            onPressed: _penDraft.length >= 2 ? _penFinishOpen : null,
          ),
          PillButton(
            label: 'Annuler dernier point',
            colorKey: 'amber',
            icon: Icons.undo,
            onPressed: _penDraft.isEmpty ? null : _penUndoLastPoint,
          ),
          PillButton(
            label: 'Annuler le tracé',
            colorKey: 'rose',
            icon: Icons.close,
            onPressed: _penCancel,
          ),
        ],
      ),
    );
  }
}

/// Dialogue de recherche d'étudiant pour l'aperçu en direct — même
/// mécanisme que la recherche de badge_screen.dart
/// (`StudentsState.searchLive`/`liveSearchResults`), en version dialogue
/// plutôt que panneau permanent puisque l'écran n'a pas la place d'un
/// volet de recherche dédié comme badge_screen.dart.
class _PreviewStudentSearchDialog extends StatefulWidget {
  const _PreviewStudentSearchDialog();

  @override
  State<_PreviewStudentSearchDialog> createState() =>
      _PreviewStudentSearchDialogState();
}

class _PreviewStudentSearchDialogState
    extends State<_PreviewStudentSearchDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StudentsState>();
    return AlertDialog(
      title: const Text('Aperçu avec un étudiant'),
      content: SizedBox(
        width: 420,
        height: 420,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _controller,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Rechercher (nom, prénom, identifiant…)',
                isDense: true,
                prefixIcon: Icon(Icons.search, size: 18),
              ),
              onChanged: (v) => context.read<StudentsState>().searchLive(v),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: state.liveSearchResults.isEmpty
                  ? Center(
                      child: Text(
                        state.isSearchingLive
                            ? 'Recherche…'
                            : 'Tapez pour rechercher un étudiant.',
                        style: TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 12.5,
                        ),
                      ),
                    )
                  : ListView.separated(
                      itemCount: state.liveSearchResults.length,
                      separatorBuilder: (context, index) =>
                          const Divider(height: 1),
                      itemBuilder: (context, i) {
                        final s = state.liveSearchResults[i];
                        return ListTile(
                          dense: true,
                          title: Text('${s.nom} ${s.prenom}'),
                          subtitle: Text(s.identifiant),
                          onTap: () => Navigator.of(context).pop(s),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Annuler'),
        ),
      ],
    );
  }
}
