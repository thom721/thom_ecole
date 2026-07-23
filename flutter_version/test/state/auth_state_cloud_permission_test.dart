import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/state/auth_state.dart';

/// Vérifie le filtre "Autorisation cloud" (AuthState.login()) : en mode
/// cloud (ApiClient.useCloudServer), un identifiant/mot de passe valides ne
/// suffisent plus — il faut aussi cette permission précise dans la réponse
/// serveur. Fragile par nature (c'est un contrôle d'accès) : le test
/// vérifie autant le cas accepté que le cas refusé, et surtout qu'un refus
/// ne laisse aucune trace (aucun token sauvegardé, aucun user/permissions
/// retenu en mémoire).
class _FakeHttpClientAdapter implements HttpClientAdapter {
  _FakeHttpClientAdapter(this._handler);
  final ResponseBody Function(RequestOptions options) _handler;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async => _handler(options);

  @override
  void close({bool force = false}) {}
}

ResponseBody _json(Map<String, dynamic> body, [int status = 200]) =>
    ResponseBody.fromString(
      jsonEncode(body),
      status,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );

Map<String, dynamic> _loginResponse(List<String> permissions) => {
  'token': 'fake-token',
  'user': {
    'id': 'u1',
    'email': 'prof@ecole.test',
    'status': '1',
    'userable_type': 'App\\Models\\Personnel',
    'userable_id': 'p1',
    'password_changed_at': '2026-01-01',
  },
  'roles': ['teacher'],
  'permissions': permissions,
  'tab_ids': null,
};

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  // Le stockage simulé de SharedPreferences est global au fichier, pas
  // réinitialisé automatiquement entre les `test()` — sans ce reset, un
  // token sauvegardé par un test antérieur (ex. la connexion locale
  // réussie) fuiterait dans les tests suivants via une nouvelle instance
  // TokenStorage() qui lirait pourtant le même stockage sous-jacent.
  setUp(() => SharedPreferences.setMockInitialValues({}));

  test(
    'mode local : la connexion réussit même SANS "Autorisation cloud"',
    () async {
      final adapter = _FakeHttpClientAdapter((_) => _json(_loginResponse([])));
      final apiClient = ApiClient(TokenStorage());
      // useLocalServer() est déjà le mode par défaut du constructeur, mais
      // explicite ici pour ne pas dépendre de ce détail d'implémentation —
      // DOIT être appelé avant d'installer le faux adaptateur, sinon il
      // écrase notre faux avec un vrai IOHttpClientAdapter().
      apiClient.useLocalServer();
      apiClient.dio.httpClientAdapter = adapter;
      final auth = AuthState(apiClient, TokenStorage());

      final ok = await auth.login('prof@ecole.test', 'motdepasse');

      expect(ok, isTrue);
      expect(auth.user, isNotNull);
      expect(auth.permissions, isEmpty);
    },
  );

  test(
    'mode cloud SANS "Autorisation cloud" : connexion refusée, aucun état retenu',
    () async {
      final adapter = _FakeHttpClientAdapter(
        (_) => _json(_loginResponse(['Voir paiement'])),
      );
      final tokenStorage = TokenStorage();
      final apiClient = ApiClient(tokenStorage);
      apiClient.useCloudServer('https://ecole.exemple.com/api');
      apiClient.dio.httpClientAdapter = adapter;
      final auth = AuthState(apiClient, tokenStorage);

      final ok = await auth.login('prof@ecole.test', 'motdepasse');

      expect(ok, isFalse);
      expect(auth.errorMessage, contains('cloud'));
      expect(
        auth.user,
        isNull,
        reason: "un refus ne doit laisser AUCUNE identité en mémoire",
      );
      expect(auth.permissions, isEmpty);
      expect(
        await tokenStorage.getToken(),
        isNull,
        reason: 'un refus ne doit jamais persister de token',
      );
    },
  );

  test(
    'mode cloud AVEC "Autorisation cloud" : connexion acceptée normalement',
    () async {
      final adapter = _FakeHttpClientAdapter(
        (_) => _json(_loginResponse(['Autorisation cloud', 'Voir paiement'])),
      );
      final tokenStorage = TokenStorage();
      final apiClient = ApiClient(tokenStorage);
      apiClient.useCloudServer('https://ecole.exemple.com/api');
      apiClient.dio.httpClientAdapter = adapter;
      final auth = AuthState(apiClient, tokenStorage);

      final ok = await auth.login('prof@ecole.test', 'motdepasse');

      expect(ok, isTrue);
      expect(auth.user, isNotNull);
      expect(auth.permissions, contains('Autorisation cloud'));
      expect(await tokenStorage.getToken(), 'fake-token');
    },
  );

  test(
    'le filtre cloud ne masque pas les refus existants (compte inactif)',
    () async {
      final adapter = _FakeHttpClientAdapter(
        (_) => _json({
          'token': 'x',
          'user': {
            'id': 'u1',
            'email': 'prof@ecole.test',
            'status': '0',
            'userable_type': 'App\\Models\\Personnel',
            'userable_id': 'p1',
            'password_changed_at': '2026-01-01',
          },
          'roles': [],
          'permissions': ['Autorisation cloud'],
          'tab_ids': null,
        }),
      );
      final apiClient = ApiClient(TokenStorage());
      apiClient.useCloudServer('https://ecole.exemple.com/api');
      apiClient.dio.httpClientAdapter = adapter;
      final auth = AuthState(apiClient, TokenStorage());

      final ok = await auth.login('prof@ecole.test', 'motdepasse');

      expect(ok, isFalse);
      expect(auth.errorMessage, contains('actif'));
    },
  );
}
