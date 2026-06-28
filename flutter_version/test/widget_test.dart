import 'package:flutter_test/flutter_test.dart';

import 'package:school_client_flutter/main.dart';

void main() {
  testWidgets('Affiche l\'écran de connexion au démarrage', (tester) async {
    await tester.pumpWidget(const SchoolClientApp());

    expect(find.text('Connexion'), findsOneWidget);
    expect(find.text('Valider'), findsOneWidget);
  });
}
