import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/state/note_state.dart';

/// Vérifie le paramètre [identifiant] (optionnel) ajouté à
/// `NoteState.previewDeleteNotes`/`deleteNotes` — restreint la suppression
/// groupée (niveau/classe/année/mois) à UN seul étudiant de la classe.
/// Fragile par nature (suppression irréversible côté backend) : ce test
/// vérifie que le paramètre part bien dans la requête HTTP quand fourni, et
/// est bien ABSENT quand omis (garantit que le comportement par défaut —
/// toute la classe — reste identique à avant cet ajout).
///
/// Aucun mock HTTP n'existait déjà dans ce dépôt pour les classes d'état
/// basées sur `ApiClient`/Dio — un faux [HttpClientAdapter] minimal est
/// construit ici plutôt que d'ajouter une dépendance de mock (mockito/
/// mocktail) juste pour ce test.
class _RecordedRequest {
  _RecordedRequest(this.method, this.path, this.queryParameters, this.data);
  final String method;
  final String path;
  final Map<String, dynamic> queryParameters;
  final dynamic data;
}

class _FakeHttpClientAdapter implements HttpClientAdapter {
  _FakeHttpClientAdapter(this._handler);
  final ResponseBody Function(RequestOptions options) _handler;
  final List<_RecordedRequest> requests = [];

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(
      _RecordedRequest(
        options.method,
        options.path,
        options.queryParameters,
        options.data,
      ),
    );
    return _handler(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _jsonResponse(Map<String, dynamic> body, int statusCode) {
  return ResponseBody.fromString(
    jsonEncode(body),
    statusCode,
    headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    },
  );
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  late _FakeHttpClientAdapter adapter;
  late NoteState noteState;

  /// [nextResponse] : réponse renvoyée par le prochain appel HTTP fait via
  /// [noteState] — construit un [NoteState] neuf à chaque test pour éviter
  /// toute fuite d'état entre cas.
  void setUpWith(ResponseBody Function(RequestOptions options) handler) {
    adapter = _FakeHttpClientAdapter(handler);
    final apiClient = ApiClient(TokenStorage());
    apiClient.dio.httpClientAdapter = adapter;
    noteState = NoteState(apiClient);
  }

  group('previewDeleteNotes', () {
    test("sans [identifiant] : la requête ne contient PAS la clé 'identifiant' "
        '(comportement par défaut — toute la classe — inchangé)', () async {
      setUpWith(
        (_) => _jsonResponse({
          'etudiants_concernes': 24,
          'notes_a_supprimer': 24,
        }, 200),
      );

      final result = await noteState.previewDeleteNotes(
        niveauId: 'niv-1',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
      );

      expect(result.error, isNull);
      expect(result.etudiants, 24);
      expect(result.notes, 24);
      expect(adapter.requests, hasLength(1));
      expect(
        adapter.requests.single.queryParameters.containsKey('identifiant'),
        isFalse,
      );
    });

    test("avec [identifiant] : la requête contient 'identifiant' avec la "
        'valeur exacte fournie', () async {
      setUpWith(
        (_) => _jsonResponse({
          'etudiants_concernes': 1,
          'notes_a_supprimer': 3,
        }, 200),
      );

      final result = await noteState.previewDeleteNotes(
        niveauId: 'niv-1',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
        identifiant: '1-68979',
      );

      expect(result.error, isNull);
      expect(result.etudiants, 1);
      expect(result.notes, 3);
      expect(adapter.requests.single.queryParameters['identifiant'], '1-68979');
    });

    test('un [identifiant] vide/blanc est traité comme absent (pas envoyé '
        'du tout, pour ne jamais matcher "" côté backend)', () async {
      setUpWith(
        (_) => _jsonResponse({
          'etudiants_concernes': 24,
          'notes_a_supprimer': 24,
        }, 200),
      );

      await noteState.previewDeleteNotes(
        niveauId: 'niv-1',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
        identifiant: '   ',
      );

      expect(
        adapter.requests.single.queryParameters.containsKey('identifiant'),
        isFalse,
      );
    });

    test('une erreur serveur (422) remonte un message exploitable, pas une '
        'exception non gérée', () async {
      setUpWith(
        (_) => _jsonResponse({
          'detail': {'errors': 'Niveau introuvable'},
        }, 422),
      );

      final result = await noteState.previewDeleteNotes(
        niveauId: 'niv-inconnu',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
      );

      expect(result.error, 'Niveau introuvable');
      expect(result.etudiants, isNull);
      expect(result.notes, isNull);
    });
  });

  group('deleteNotes', () {
    test("sans [identifiant] : le corps de la requête ne contient PAS la clé "
        "'identifiant' (comportement par défaut — toute la classe — "
        'inchangé)', () async {
      setUpWith(
        (_) => _jsonResponse({
          'success': 'ok',
          'etudiants_affectes': 24,
          'notes_supprimees': 24,
        }, 200),
      );

      final error = await noteState.deleteNotes(
        niveauId: 'niv-1',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
        raison: 'Erreur de saisie',
      );

      expect(error, isNull);
      expect(adapter.requests, hasLength(1));
      final data = adapter.requests.single.data as Map;
      expect(data.containsKey('identifiant'), isFalse);
      expect(data['raison'], 'Erreur de saisie');
    });

    test("avec [identifiant] : le corps de la requête contient 'identifiant' "
        'avec la valeur exacte fournie — restreint la suppression à cet '
        'étudiant', () async {
      setUpWith(
        (_) => _jsonResponse({
          'success': 'ok',
          'etudiants_affectes': 1,
          'notes_supprimees': 3,
        }, 200),
      );

      final error = await noteState.deleteNotes(
        niveauId: 'niv-1',
        classeId: 'cls-1',
        anneeAcademique: '2025/2026',
        mois: 'Septembre',
        raison: 'Doublon',
        identifiant: '1-68979',
      );

      expect(error, isNull);
      final data = adapter.requests.single.data as Map;
      expect(data['identifiant'], '1-68979');
    });

    test(
      'une erreur serveur (500) remonte un message, pas une exception',
      () async {
        setUpWith(
          (_) => _jsonResponse({'errors': 'Erreur interne : boom'}, 500),
        );

        final error = await noteState.deleteNotes(
          niveauId: 'niv-1',
          classeId: 'cls-1',
          anneeAcademique: '2025/2026',
          mois: 'Septembre',
        );

        expect(error, 'Erreur interne : boom');
      },
    );
  });
}
