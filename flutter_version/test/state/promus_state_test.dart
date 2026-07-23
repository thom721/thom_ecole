import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/state/promus_state.dart';

/// Vérifie le suivi des changements d'aide financière (bourse) pendant la
/// promotion — voir PromusState.pendingAideFinanciere. Le point fragile :
/// seul le DIFF (étudiants réellement modifiés) doit partir au serveur, pas
/// une copie complète du tableau à chaque promotion, sinon un aller-retour
/// annulé par l'utilisateur (reposer la même valeur) enverrait quand même
/// une "modification" qui n'en est pas une.
class _RecordedRequest {
  _RecordedRequest(this.path, this.data);
  final String path;
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
    requests.add(_RecordedRequest(options.path, options.data));
    return _handler(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _json(Map<String, dynamic> body) => ResponseBody.fromString(
  jsonEncode(body),
  200,
  headers: {
    Headers.contentTypeHeader: [Headers.jsonContentType],
  },
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  late _FakeHttpClientAdapter adapter;
  late PromusState state;

  void setUpWith(ResponseBody Function(RequestOptions options) handler) {
    adapter = _FakeHttpClientAdapter(handler);
    final apiClient = ApiClient(TokenStorage());
    apiClient.dio.httpClientAdapter = adapter;
    state = PromusState(apiClient);
  }

  Future<void> search() =>
      state.rechercher(annee: 'an-1', niveau: 'niv-1', classe: 'cls-1');

  test(
    'rechercher() peuple aideFinanciere depuis la réponse serveur',
    () async {
      setUpWith(
        (_) => _json({
          'result': [
            {
              'id': 'e1',
              'nom': 'DUPONT',
              'prenom': 'Jean',
              'note': 80,
              'max': 100,
              'moyenne': '8.0',
              'status': 'Succès',
              'aide_financiere': 'Démie Bourse',
            },
          ],
        }),
      );
      await search();
      expect(state.resultats.single.aideFinanciere, 'Démie Bourse');
      expect(state.aideFinanciereFor(state.resultats.single), 'Démie Bourse');
    },
  );

  test(
    'setAideFinanciere retire le diff quand on revient à la valeur d\'origine',
    () async {
      setUpWith(
        (_) => _json({
          'result': [
            {
              'id': 'e1',
              'nom': 'DUPONT',
              'prenom': 'Jean',
              'note': 80,
              'max': 100,
              'moyenne': '8.0',
              'status': 'Succès',
              'aide_financiere': 'Aucune',
            },
          ],
        }),
      );
      await search();
      final e = state.resultats.single;

      state.setAideFinanciere(e, 'Bourse');
      expect(state.pendingAideFinanciere, {'e1': 'Bourse'});
      expect(state.aideFinanciereFor(e), 'Bourse');

      // Revenir à la valeur d'origine : le diff doit redevenir vide, pas
      // contenir {'e1': 'Aucune'} (ce ne serait pas un vrai changement).
      state.setAideFinanciere(e, 'Aucune');
      expect(state.pendingAideFinanciere, isEmpty);
      expect(state.aideFinanciereFor(e), 'Aucune');
    },
  );

  test(
    'promouvoir() sans changement n\'envoie PAS aide_financiere_updates',
    () async {
      setUpWith((options) {
        if (options.path.contains('get-promus')) {
          return _json({
            'result': [
              {
                'id': 'e1',
                'nom': 'DUPONT',
                'prenom': 'Jean',
                'note': 80,
                'max': 100,
                'moyenne': '8.0',
                'status': 'Succès',
                'aide_financiere': 'Aucune',
              },
            ],
          });
        }
        return _json({
          'statistics': {
            'promus': 1,
            'redoublants': 0,
            'aide_financiere_modifiee': 0,
          },
        });
      });
      await search();

      final ok = await state.promouvoir(
        anneeActuelle: 'an-1',
        niveauActuel: 'niv-1',
        classeActuelle: 'cls-1',
        anneeFuture: 'an-2',
        niveauFuture: 'niv-1',
        classeFuture: 'cls-2',
      );

      expect(ok, isTrue);
      final promoteRequest = adapter.requests.firstWhere(
        (r) => r.path.contains('etudiant-promus-to'),
      );
      final data = promoteRequest.data as Map;
      expect(data.containsKey('aide_financiere_updates'), isFalse);
    },
  );

  test(
    'promouvoir() avec changement envoie UNIQUEMENT le diff, puis le vide',
    () async {
      setUpWith((options) {
        if (options.path.contains('get-promus')) {
          return _json({
            'result': [
              {
                'id': 'e1',
                'nom': 'DUPONT',
                'prenom': 'Jean',
                'note': 80,
                'max': 100,
                'moyenne': '8.0',
                'status': 'Succès',
                'aide_financiere': 'Aucune',
              },
              {
                'id': 'e2',
                'nom': 'MARTIN',
                'prenom': 'Alice',
                'note': 90,
                'max': 100,
                'moyenne': '9.0',
                'status': 'Succès',
                'aide_financiere': 'Bourse',
              },
            ],
          });
        }
        return _json({
          'statistics': {
            'promus': 2,
            'redoublants': 0,
            'aide_financiere_modifiee': 1,
          },
        });
      });
      await search();

      // e1 gagne une bourse, e2 garde la sienne (pas de diff pour e2).
      state.setAideFinanciere(state.resultats[0], 'Bourse');

      final ok = await state.promouvoir(
        anneeActuelle: 'an-1',
        niveauActuel: 'niv-1',
        classeActuelle: 'cls-1',
        anneeFuture: 'an-2',
        niveauFuture: 'niv-1',
        classeFuture: 'cls-2',
      );

      expect(ok, isTrue);
      final promoteRequest = adapter.requests.firstWhere(
        (r) => r.path.contains('etudiant-promus-to'),
      );
      final data = promoteRequest.data as Map;
      expect(data['aide_financiere_updates'], {'e1': 'Bourse'});

      // Le diff est vidé après une promotion réussie — une nouvelle
      // recherche/promotion ne doit pas renvoyer un changement déjà appliqué.
      expect(state.pendingAideFinanciere, isEmpty);
    },
  );

  test(
    'rechercher() vide le diff en attente d\'une recherche précédente',
    () async {
      setUpWith(
        (_) => _json({
          'result': [
            {
              'id': 'e1',
              'nom': 'DUPONT',
              'prenom': 'Jean',
              'note': 80,
              'max': 100,
              'moyenne': '8.0',
              'status': 'Succès',
              'aide_financiere': 'Aucune',
            },
          ],
        }),
      );
      await search();
      state.setAideFinanciere(state.resultats.single, 'Bourse');
      expect(state.pendingAideFinanciere, isNotEmpty);

      await search();
      expect(
        state.pendingAideFinanciere,
        isEmpty,
        reason:
            'un diff calculé pour une classe ne doit pas fuiter vers une autre recherche',
      );
    },
  );

  group('préscolaire (sansEvaluation)', () {
    test(
      'rechercher() peuple sansEvaluation depuis la réponse serveur',
      () async {
        setUpWith(
          (_) => _json({
            'result': [
              {
                'id': 'e1',
                'nom': 'DUPONT',
                'prenom': 'Jean',
                'note': 0,
                'max': 0,
                'moyenne': '-',
                'status': 'Succès',
                'sans_evaluation': true,
                'aide_financiere': 'Aucune',
              },
            ],
          }),
        );
        await search();
        expect(state.resultats.single.sansEvaluation, isTrue);
      },
    );

    test(
      'setForcerRedoublant retire l\'entrée quand on désactive à nouveau',
      () async {
        setUpWith(
          (_) => _json({
            'result': [
              {
                'id': 'e1',
                'nom': 'DUPONT',
                'prenom': 'Jean',
                'note': 0,
                'max': 0,
                'moyenne': '-',
                'status': 'Succès',
                'sans_evaluation': true,
                'aide_financiere': 'Aucune',
              },
            ],
          }),
        );
        await search();
        final e = state.resultats.single;

        expect(state.isForcedRedoublant(e), isFalse);
        state.setForcerRedoublant(e, true);
        expect(state.isForcedRedoublant(e), isTrue);
        expect(state.forcedRedoublants, {'e1'});

        state.setForcerRedoublant(e, false);
        expect(state.isForcedRedoublant(e), isFalse);
        expect(state.forcedRedoublants, isEmpty);
      },
    );

    test(
      'promouvoir() sans redoublant forcé n\'envoie PAS forcer_redoublant',
      () async {
        setUpWith((options) {
          if (options.path.contains('get-promus')) {
            return _json({
              'result': [
                {
                  'id': 'e1',
                  'nom': 'DUPONT',
                  'prenom': 'Jean',
                  'note': 0,
                  'max': 0,
                  'moyenne': '-',
                  'status': 'Succès',
                  'sans_evaluation': true,
                  'aide_financiere': 'Aucune',
                },
              ],
            });
          }
          return _json({
            'statistics': {
              'promus': 1,
              'redoublants': 0,
              'aide_financiere_modifiee': 0,
            },
          });
        });
        await search();

        await state.promouvoir(
          anneeActuelle: 'an-1',
          niveauActuel: 'niv-1',
          classeActuelle: 'cls-1',
          anneeFuture: 'an-2',
          niveauFuture: 'niv-1',
          classeFuture: 'cls-2',
        );

        final promoteRequest = adapter.requests.firstWhere(
          (r) => r.path.contains('etudiant-promus-to'),
        );
        final data = promoteRequest.data as Map;
        expect(data.containsKey('forcer_redoublant'), isFalse);
      },
    );

    test(
      'promouvoir() avec redoublant forcé envoie la liste, puis la vide',
      () async {
        setUpWith((options) {
          if (options.path.contains('get-promus')) {
            return _json({
              'result': [
                {
                  'id': 'e1',
                  'nom': 'DUPONT',
                  'prenom': 'Jean',
                  'note': 0,
                  'max': 0,
                  'moyenne': '-',
                  'status': 'Succès',
                  'sans_evaluation': true,
                  'aide_financiere': 'Aucune',
                },
                {
                  'id': 'e2',
                  'nom': 'MARTIN',
                  'prenom': 'Alice',
                  'note': 0,
                  'max': 0,
                  'moyenne': '-',
                  'status': 'Succès',
                  'sans_evaluation': true,
                  'aide_financiere': 'Aucune',
                },
              ],
            });
          }
          return _json({
            'statistics': {
              'promus': 1,
              'redoublants': 1,
              'aide_financiere_modifiee': 0,
            },
          });
        });
        await search();

        // e1 redouble manuellement, e2 est promu automatiquement (par défaut).
        state.setForcerRedoublant(state.resultats[0], true);

        final ok = await state.promouvoir(
          anneeActuelle: 'an-1',
          niveauActuel: 'niv-1',
          classeActuelle: 'cls-1',
          anneeFuture: 'an-2',
          niveauFuture: 'niv-1',
          classeFuture: 'cls-2',
        );

        expect(ok, isTrue);
        final promoteRequest = adapter.requests.firstWhere(
          (r) => r.path.contains('etudiant-promus-to'),
        );
        final data = promoteRequest.data as Map;
        expect(data['forcer_redoublant'], ['e1']);
        expect(state.forcedRedoublants, isEmpty);
      },
    );
  });
}
