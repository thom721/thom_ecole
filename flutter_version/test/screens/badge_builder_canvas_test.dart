import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';
import 'package:school_client_flutter/widgets/badge_canvas_element.dart';

void main() {
  testWidgets(
    'les éléments sont peints triés par zIndex, pas dans l\'ordre brut de '
    'la liste ("Premier plan"/"Arrière-plan" ne modifient QUE zIndex, pas '
    'la position dans la liste — voir badge_builder_screen.dart::_reorderSelected)',
    (tester) async {
      final front = BadgeElement(
        id: 'front',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 100,
        height: 100,
        zIndex: 10,
      );
      final back = BadgeElement(
        id: 'back',
        type: BadgeElementType.shape,
        x: 0,
        y: 0,
        width: 100,
        height: 100,
        zIndex: -10,
      );
      // Ordre de LISTE délibérément inverse de l'ordre de zIndex attendu.
      final side = BadgeSide(elements: [front, back]);
      final layout = BadgeLayoutTemplate(id: 'l', name: 'Test', recto: side);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: BadgeBuilderCanvas(
            layout: layout,
            side: side,
            selectedId: null,
            onSelect: (_) {},
            onElementChanged: (_) {},
          ),
        ),
      );

      final ids = tester
          .widgetList<BadgeCanvasElement>(find.byType(BadgeCanvasElement))
          .map((w) => w.element.id)
          .toList();
      expect(
        ids,
        ['back', 'front'],
        reason: 'zIndex -10 doit être peint avant zIndex 10, même si la liste les range dans l\'ordre inverse',
      );
    },
  );

  testWidgets(
    'cliquer sur un élément le (re)sélectionne sans que le fond ne le désélectionne aussitôt après',
    (tester) async {
      final element = BadgeElement(
        id: 'e1',
        type: BadgeElementType.text,
        x: 100,
        y: 100,
        width: 300,
        height: 40,
        text: 'Bonjour',
      );
      final side = BadgeSide(elements: [element]);
      final layout = BadgeLayoutTemplate(id: 'l1', name: 'Test', recto: side);

      String? selected;

      // `SizedBox(width/height:)` seul ne suffit PAS à fixer la taille
      // réelle du canevas de test : la racine du test binding impose des
      // contraintes déjà tendues à la taille de la fenêtre (800×600 par
      // défaut), qu'un SizedBox descendant ne peut pas réduire (une
      // contrainte tendue ne peut jamais être outrepassée par un enfant).
      // Piégé une première fois par ce test lui-même : les coordonnées de
      // clic calculées ci-dessous supposaient une zone de 400×400 alors
      // que le canevas occupait réellement 800×600 en entier.
      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: StatefulBuilder(
            builder: (context, setState) {
              return BadgeBuilderCanvas(
                layout: layout,
                side: side,
                selectedId: selected,
                onSelect: (id) => setState(() => selected = id),
                onElementChanged: (_) => setState(() {}),
              );
            },
          ),
        ),
      );

      // Reproduit les constantes internes de badge_builder_canvas.dart
      // (`_rulerThickness`) et du modèle (`kBadgeLandscapeWidth`) — la
      // zone canevas commence après les règles, à l'échelle du reste
      // disponible.
      const rulerThickness = 20.0;
      const canvasOrigin = Offset(rulerThickness, rulerThickness);
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;
      final elementCenter = canvasOrigin + Offset((element.x + element.width / 2) * scale, (element.y + element.height / 2) * scale);
      const backgroundPoint = Offset(5, 5);

      await tester.tapAt(elementCenter);
      await tester.pump();
      expect(selected, 'e1', reason: 'un clic direct sur l\'élément doit le sélectionner');

      // Reclique sur le MÊME élément déjà sélectionné : ne doit PAS se
      // désélectionner. Avant correction, un GestureDetector.onTap
      // ancêtre englobant tout le canevas se déclenchait EN PLUS du
      // Listener de l'élément cliqué (un ancêtre n'est jamais "arrêté"
      // par le hit-test de ses descendants) et annulait aussitôt la
      // sélection qui venait d'être faite.
      await tester.tapAt(elementCenter);
      await tester.pump();
      expect(selected, 'e1', reason: 'recliquer sur l\'élément déjà sélectionné doit le garder sélectionné');

      await tester.tapAt(canvasOrigin + backgroundPoint);
      await tester.pump();
      expect(selected, isNull, reason: 'un clic sur le fond (loin de tout élément) doit désélectionner');

      // Le bug initialement rapporté : après une désélection, un clic sur
      // l'élément ne le resélectionnait plus.
      await tester.tapAt(elementCenter);
      await tester.pump();
      expect(selected, 'e1', reason: 'après une désélection, recliquer sur l\'élément doit le resélectionner');
    },
  );

  /// Un polygone couvrant tout le rectangle unité (0,0)-(1,1) — simule un
  /// trou PERMANENT déjà gravé (voir `bakeSubtraction`,
  /// badge_builder_bake_subtraction_test.dart pour les tests de la
  /// découpe elle-même) recouvrant entièrement l'élément.
  List<BadgePathPoint> fullCoverageCutout() => [
    BadgePathPoint(x: 0, y: 0),
    BadgePathPoint(x: 1, y: 0),
    BadgePathPoint(x: 1, y: 1),
    BadgePathPoint(x: 0, y: 1),
  ];

  testWidgets(
    'la poignée de redimensionnement d\'un élément reste utilisable même '
    'quand il porte un trou PERMANENT (cutoutPaths) qui le recouvre '
    'entièrement — le ClipPath du trou ne doit découper que le rendu '
    'visuel, jamais la zone interactive (voir '
    'badge_builder_canvas.dart::_cutoutClip)',
    (tester) async {
      final back = BadgeElement(
        id: 'back',
        type: BadgeElementType.shape,
        x: 100,
        y: 100,
        width: 200,
        height: 200,
        zIndex: 0,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 0xFF0000FF,
        cutoutPaths: [fullCoverageCutout()],
      );
      final side = BadgeSide(elements: [back]);
      final layout = BadgeLayoutTemplate(id: 'l2', name: 'Test', recto: side);

      String? selected = 'back';

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: StatefulBuilder(
            builder: (context, setState) {
              return BadgeBuilderCanvas(
                layout: layout,
                side: side,
                selectedId: selected,
                onSelect: (id) => setState(() => selected = id),
                onElementChanged: (_) => setState(() {}),
              );
            },
          ),
        ),
      );
      await tester.pump();

      const rulerThickness = 20.0;
      const canvasOrigin = Offset(rulerThickness, rulerThickness);
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;
      final handleCenter = canvasOrigin + Offset((back.x + back.width) * scale, (back.y + back.height) * scale);

      final originalWidth = back.width;
      final originalHeight = back.height;

      final gesture = await tester.startGesture(handleCenter);
      await gesture.moveBy(const Offset(-20, -20));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      expect(
        back.width,
        lessThan(originalWidth),
        reason: 'la poignée bas-droite doit rester saisissable même sous une forme soustractive qui la recouvre entièrement',
      );
      expect(back.height, lessThan(originalHeight));
    },
  );

  testWidgets(
    'un élément "hidden" (panneau des calques) n\'est ni peint ni sélectionnable — comme un calque masqué dans Illustrator/Photoshop',
    (tester) async {
      final visible = BadgeElement(id: 'visible', type: BadgeElementType.text, x: 0, y: 0, width: 100, height: 40, text: 'A');
      final hidden = BadgeElement(id: 'hidden', type: BadgeElementType.text, x: 200, y: 0, width: 100, height: 40, text: 'B', hidden: true);
      final side = BadgeSide(elements: [visible, hidden]);
      final layout = BadgeLayoutTemplate(id: 'l8', name: 'Test', recto: side);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: BadgeBuilderCanvas(
            layout: layout,
            side: side,
            selectedId: null,
            onSelect: (_) {},
            onElementChanged: (_) {},
          ),
        ),
      );

      final painted = tester.widgetList<BadgeCanvasElement>(find.byType(BadgeCanvasElement)).map((w) => w.element.id).toList();
      expect(painted, ['visible'], reason: '"hidden" ne doit même pas être construit dans l\'arbre de widgets');
    },
  );

  // Les anciens tests de ce fichier (conversion de repère, tracé plume,
  // coordonnées négatives reproduisant un cas réel, élément sans rapport
  // intercalé...) pompaient un widget et lisaient `subtractBackground:
  // true` directement, pour vérifier le masque DYNAMIQUE alors recalculé
  // à chaque frame par `_buildLayeredContent`. Ce mécanisme n'existe plus
  // — la conversion de repère et le regroupement par ordre de peinture ne
  // s'exécutent maintenant qu'UNE FOIS, dans `bakeSubtraction` (voir
  // models/badge_layout.dart::BadgeElement.subtractBackground pour
  // l'historique de ce changement de modèle). Cette même couverture
  // géométrique (repère non nul, tracé plume, coordonnées négatives
  // reproduisant le cas rapporté, élément sans rapport intercalé) est
  // reprise dans test/screens/badge_builder_bake_subtraction_test.dart,
  // en appelant `bakeSubtraction` directement plutôt qu'en inspectant un
  // `ClipPath` recalculé en direct.
  testWidgets(
    'un élément portant un trou PERMANENT (cutoutPaths, déjà gravé par '
    'bakeSubtraction) est rendu avec un ClipPath dont le trou tombe au bon '
    'endroit dans SON PROPRE repère local — aucune conversion croisée avec '
    'un autre élément n\'est plus nécessaire ici (contrairement à l\'ancien '
    'masque dynamique), le trou est déjà exprimé dans le repère de cet '
    'élément au moment où il a été gravé',
    (tester) async {
      // Un trou occupant le quart supérieur-gauche de l'élément (0,0) à
      // (0.5,0.5) en coordonnées normalisées.
      final el = BadgeElement(
        id: 'el',
        type: BadgeElementType.shape,
        x: 50,
        y: 50,
        width: 200,
        height: 200,
        shapeKind: BadgeShapeKind.rectangle,
        fillColor: 0xFF0000FF,
        cutoutPaths: [
          [
            BadgePathPoint(x: 0, y: 0),
            BadgePathPoint(x: 0.5, y: 0),
            BadgePathPoint(x: 0.5, y: 0.5),
            BadgePathPoint(x: 0, y: 0.5),
          ],
        ],
      );
      final side = BadgeSide(elements: [el]);
      final layout = BadgeLayoutTemplate(id: 'l4', name: 'Test', recto: side);

      tester.view.physicalSize = const Size(400, 400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      await tester.pumpWidget(
        Directionality(
          textDirection: TextDirection.ltr,
          child: BadgeBuilderCanvas(
            layout: layout,
            side: side,
            selectedId: null,
            onSelect: (_) {},
            onElementChanged: (_) {},
          ),
        ),
      );
      await tester.pump();

      const rulerThickness = 20.0;
      final canvasWidth = 400 - rulerThickness;
      final scale = canvasWidth / kBadgeLandscapeWidth;

      final widget = tester.widget<BadgeCanvasElement>(
        find.byWidgetPredicate((w) => w is BadgeCanvasElement && w.element.id == 'el'),
      );
      final clipPath = widget.child as ClipPath;
      final size = Size(el.width * scale, el.height * scale);
      final clip = clipPath.clipper!.getClip(size);

      final insideHole = const Offset(20, 20) * scale;
      final outsideHole = const Offset(150, 150) * scale;

      expect(clip.contains(insideHole), isFalse, reason: 'le quart supérieur-gauche doit être découpé (exclu du chemin de clip)');
      expect(clip.contains(outsideHole), isTrue, reason: 'le quart opposé, hors du trou, doit rester visible');
    },
  );
}
