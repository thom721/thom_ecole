import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_property_panel.dart';

void main() {
  testWidgets(
    'un champ numérique du panneau valide la saisie en perdant le focus, pas seulement sur Entrée',
    (tester) async {
      final element = BadgeElement(
        id: 'e1',
        type: BadgeElementType.shape,
        x: 10,
        y: 10,
        width: 100,
        height: 50,
        shapeKind: BadgeShapeKind.rectangle,
      );
      var changeCount = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BadgeBuilderPropertyPanel(element: element, onChanged: (_) => changeCount++),
          ),
        ),
      );

      final xField = find.widgetWithText(TextFormField, 'X');
      expect(xField, findsOneWidget);

      await tester.enterText(xField, '250');
      expect(element.x, 10, reason: 'ne doit pas encore être appliqué avant la perte de focus');

      // Simule "cliquer ailleurs" sans appuyer sur Entrée dans le champ
      // modifié — retirer le focus directement plutôt que de dépendre
      // d'un autre widget cliquable dont la position dans un panneau
      // défilant/étroit n'est pas garantie à l'écran dans ce harnais.
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pumpAndSettle();

      expect(element.x, 250, reason: 'cliquer ailleurs doit valider la saisie comme Entrée le ferait');
      expect(changeCount, greaterThan(0));
    },
  );

  testWidgets(
    'le bouton "Soustraire du fond" déclenche BadgeElement.subtractBackground '
    'à true — une action PONCTUELLE consommée par badge_builder_screen.dart::'
    '_onElementChanged (bakeSubtraction), pas un état persistant : ce '
    'panneau, isolé de l\'écran, ne fait que déclencher et laisse le '
    'remplissage normal toujours visible',
    (tester) async {
      final element = BadgeElement(
        id: 'e2',
        type: BadgeElementType.shape,
        x: 10,
        y: 10,
        width: 100,
        height: 50,
        shapeKind: BadgeShapeKind.rectangle,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: StatefulBuilder(
            builder: (context, setState) => Scaffold(
              body: BadgeBuilderPropertyPanel(element: element, onChanged: (_) => setState(() {})),
            ),
          ),
        ),
      );

      expect(element.subtractBackground, isFalse);
      expect(find.text('Remplissage'), findsOneWidget, reason: 'le remplissage normal est toujours visible (n\'est plus masqué par ce déclencheur ponctuel)');

      // Le panneau défile (`SingleChildScrollView`) — ce bouton est plus
      // bas que la hauteur de test par défaut, `tester.tap` échouerait un
      // "hit test" sur un widget hors écran sans la faire défiler d'abord.
      final button = find.text('Soustraire du fond (découper maintenant)');
      await tester.ensureVisible(button);
      await tester.pumpAndSettle();
      await tester.tap(button);
      await tester.pump();

      expect(
        element.subtractBackground,
        isTrue,
        reason: 'ce panneau, seul, ne fait que positionner le déclencheur — la découpe elle-même (bakeSubtraction) est effectuée par l\'écran, qui a accès aux autres éléments',
      );
      expect(find.text('Remplissage'), findsOneWidget);
    },
  );
}
