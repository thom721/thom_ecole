import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/services/badge_layout_store.dart';

void main() {
  test(
    'newId() reste unique même appelé en boucle serrée synchrone '
    '(ex. placer plusieurs éléments d\'un coup)',
    () {
      // La résolution réelle de l'horloge système peut être plus
      // grossière qu'une microseconde (observé sur macOS) : plusieurs
      // appels synchrones rapprochés basés uniquement sur l'horodatage
      // pouvaient renvoyer la même valeur, provoquant des id dupliqués
      // (et donc des clés Flutter dupliquées dans le canevas).
      final ids = List.generate(200, (_) => BadgeLayoutStore.instance.newId());
      expect(ids.toSet(), hasLength(ids.length));
    },
  );
}
