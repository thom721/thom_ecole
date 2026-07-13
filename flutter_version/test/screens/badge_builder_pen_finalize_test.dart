import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_canvas.dart';
import 'package:school_client_flutter/screens/etudiant/badge_builder/badge_builder_screen.dart';
import 'package:school_client_flutter/state/students_state.dart';

const _noSelectionText = 'Sélectionnez un élément pour modifier ses propriétés.';

void main() {
  testWidgets(
    'un tracé à la plume avec une grosse poignée reste sélectionnable après coup '
    '(la boîte de l\'élément doit couvrir la poignée, pas seulement les ancres)',
    (tester) async {
      tester.view.physicalSize = const Size(1400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.reset);

      // BadgeBuilderScreen consulte StudentsState (recherche d'étudiant
      // pour l'aperçu en direct) — un vrai ApiClient suffit ici puisque ce
      // test ne déclenche aucune requête réseau (pas d'interaction avec
      // le dialogue de recherche).
      await tester.pumpWidget(
        ChangeNotifierProvider<StudentsState>(
          create: (_) => StudentsState(ApiClient(TokenStorage())),
          child: const MaterialApp(home: Scaffold(body: BadgeBuilderScreen())),
        ),
      );
      await tester.pumpAndSettle();

      // Aucune sélection au départ.
      expect(find.text(_noSelectionText), findsOneWidget);

      await tester.tap(find.byIcon(Icons.draw_outlined));
      await tester.pump();

      final canvasRect = tester.getRect(find.byType(BadgeBuilderCanvas));
      const rulerThickness = 20.0;
      final canvasOrigin = canvasRect.topLeft + const Offset(rulerThickness, rulerThickness);
      final scale = (canvasRect.width - rulerThickness) / kBadgeLandscapeWidth;
      Offset atModel(double mx, double my) => canvasOrigin + Offset(mx * scale, my * scale);

      // Point 1 (coin, en bas) — clic simple, sans poignée.
      await tester.tapAt(atModel(100, 600));
      await tester.pump();

      // Point 2 (en bas aussi) — clic-glisser vers le haut : une grosse
      // poignée qui fait largement déborder la courbe au-dessus de la
      // ligne reliant les deux ancres (comme dans le rapport utilisateur :
      // une courbe bien visible, mais des ancres presque à la même
      // hauteur).
      await tester.dragFrom(atModel(900, 600), Offset(0, -400 * scale));
      await tester.pump();

      await tester.tap(find.text('Terminer (ouvert)'));
      await tester.pump();

      // L'élément vient d'être créé : sélectionné automatiquement.
      expect(find.text(_noSelectionText), findsNothing);

      // Désélectionne en cliquant loin du tracé (coin haut-gauche du
      // canevas, hors de toute boîte englobante plausible).
      await tester.tapAt(atModel(10, 10));
      await tester.pump();
      expect(find.text(_noSelectionText), findsOneWidget);

      // Reclique à l'intérieur de la zone que seule une boîte englobante
      // incluant la poignée peut couvrir (loin des ancres, dans la bosse
      // de la courbe) — avant correction, la boîte ne couvrait que les
      // ancres (hauteur ≈1px) et ce clic ne sélectionnait plus rien.
      await tester.tapAt(atModel(500, 400));
      await tester.pump();
      expect(find.text(_noSelectionText), findsNothing, reason: 'le tracé doit redevenir sélectionnable');
    },
  );
}
