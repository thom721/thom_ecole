import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/state/auth_state.dart';
import 'package:school_client_flutter/state/theme_state.dart';
import 'package:school_client_flutter/screens/login/login_screen.dart';

const url = 'https://admin.institutionlemignon.com/le-mignon';
final radios = find.byWidgetPredicate((w) => w is Radio);
bool cloudChecked(WidgetTester t) {
  final r = t.widgetList(radios).elementAt(1) as dynamic;
  // ignore: deprecated_member_use
  return r.groupValue == r.value;
}

Future<ApiClient> pump(WidgetTester t, Map<String, Object> prefs) async {
  SharedPreferences.setMockInitialValues(prefs);
  t.view.physicalSize = const Size(1400, 1800);
  t.view.devicePixelRatio = 1;
  final ts = TokenStorage();
  final api = ApiClient(ts);
  await t.pumpWidget(MultiProvider(providers: [
    Provider<TokenStorage>.value(value: ts),
    Provider<ApiClient>.value(value: api),
    ChangeNotifierProvider(create: (_) => AuthState(api, ts)),
    ChangeNotifierProvider(create: (_) => ThemeState()),
  ], child: const MaterialApp(home: LoginScreen())));
  await t.pumpAndSettle();
  await t.tap(find.text('show ip'));
  await t.pumpAndSettle();
  return api;
}

void main() {
  testWidgets('clic sur le texte Cloud avec lien : coché, bascule, lien mémorisé', (t) async {
    final api = await pump(t, {});
    await t.enterText(find.byType(TextField).last, url);
    await t.tap(find.text('Cloud (serveur distant)'));
    await t.pumpAndSettle();
    expect(cloudChecked(t), isTrue);
    expect(api.isCloudMode, isTrue);
    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('cloud_server_url'), url);
    expect(prefs.getString('connection_mode'), 'cloud');
  });

  testWidgets('clic Cloud champ vide : coché + consigne ; connexion bloquée avec message clair', (t) async {
    final api = await pump(t, {});
    await t.tap(radios.at(1));
    await t.pumpAndSettle();
    expect(cloudChecked(t), isTrue);
    expect(api.isCloudMode, isFalse);
    expect(find.textContaining('Collez le lien complet'), findsOneWidget);
    await t.enterText(find.byType(TextField).at(0), 'a@b.c');
    await t.enterText(find.byType(TextField).at(1), 'x');
    await t.tap(find.text('Valider'));
    await t.pumpAndSettle();
    expect(find.textContaining('Mode Cloud : enregistrez'), findsOneWidget);
  });

  testWidgets('retour en local par le texte', (t) async {
    final api = await pump(t, {'connection_mode': 'cloud', 'cloud_server_url': url});
    expect(api.isCloudMode, isTrue);
    await t.tap(find.text("Modifier l'ip (réseau local)"));
    await t.pumpAndSettle();
    expect(api.isCloudMode, isFalse);
    expect(cloudChecked(t), isFalse);
  });
}
