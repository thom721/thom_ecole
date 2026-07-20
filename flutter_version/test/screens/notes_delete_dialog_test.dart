import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:school_client_flutter/core/api_client.dart';
import 'package:school_client_flutter/core/token_storage.dart';
import 'package:school_client_flutter/models/student.dart';
import 'package:school_client_flutter/screens/notes/notes_screen.dart';
import 'package:school_client_flutter/state/auth_state.dart';
import 'package:school_client_flutter/state/note_state.dart';
import 'package:school_client_flutter/state/reference_data_state.dart';

/// Vérifie le champ "Étudiant (optionnel)" ajouté au dialogue "Supprimer
/// notes" (notes_screen.dart) — la classe `_DeleteNotesDialog` est privée,
/// donc testée ici indirectement via `NotesScreen` + interaction utilisateur
/// plutôt que par un test unitaire isolé sur le widget. Se concentre sur le
/// point le plus fragile : que modifier ce champ invalide bien l'aperçu déjà
/// obtenu (comme les autres filtres), pour ne jamais supprimer sur la base
/// d'une sélection différente de celle vérifiée par l'utilisateur.
class _FakeHttpClientAdapter implements HttpClientAdapter {
  _FakeHttpClientAdapter(this._handler);
  final ResponseBody Function(RequestOptions options) _handler;
  final List<RequestOptions> requests = [];

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(options);
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

  Future<void> pumpNotesScreen(
    WidgetTester tester,
    _FakeHttpClientAdapter adapter,
  ) async {
    // NotesScreen est conçu pour une fenêtre desktop large (la Row de
    // boutons + barre de recherche déborde sur la taille par défaut, très
    // étroite, du banc de test) — pas un bug de l'écran, juste une taille de
    // viewport de test à assortir à un vrai écran desktop.
    tester.view.physicalSize = const Size(1400, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final apiClient = ApiClient(TokenStorage());
    apiClient.dio.httpClientAdapter = adapter;

    final refData = ReferenceDataState(apiClient)
      ..niveaux = [Niveau(id: 'niv-1', name: 'Primaire')]
      ..classes = [Classe(id: 'cls-1', niveauId: 'niv-1', nomClasse: 'CMI B')]
      ..annees = [AnneeAcademique(id: 'an-1', nom: '2025/2026')]
      ..isLoaded = true; // court-circuite loadOnce(), aucun appel réseau

    final authState = AuthState(apiClient, TokenStorage())
      ..permissions = ['Supprimer note'];

    final noteState = NoteState(apiClient);

    // Les providers doivent envelopper `MaterialApp`, pas se contenter
    // d'envelopper `home` : `showDialog` insère la route dans l'Overlay du
    // Navigator, qui n'est PAS un descendant de `home` dans l'arbre de
    // widgets — un Provider posé seulement autour de `home` serait invisible
    // depuis le dialogue (ProviderNotFoundException).
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider<ReferenceDataState>.value(value: refData),
          ChangeNotifierProvider<AuthState>.value(value: authState),
          ChangeNotifierProvider<NoteState>.value(value: noteState),
        ],
        child: const MaterialApp(home: Scaffold(body: NotesScreen())),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> openDeleteDialogWithCompleteFilters(WidgetTester tester) async {
    await tester.tap(find.text('Supprimer notes'));
    await tester.pumpAndSettle();

    await tester.tap(
      find.widgetWithText(DropdownButtonFormField<String>, 'Niveau'),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Primaire').last);
    await tester.pumpAndSettle();

    await tester.tap(
      find.widgetWithText(DropdownButtonFormField<String>, 'Classe'),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('CMI B').last);
    await tester.pumpAndSettle();

    await tester.tap(
      find.widgetWithText(DropdownButtonFormField<String>, 'Année académique'),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('2025/2026').last);
    await tester.pumpAndSettle();

    await tester.tap(
      find.widgetWithText(DropdownButtonFormField<String>, 'Mois'),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Septembre').last);
    await tester.pumpAndSettle();
  }

  testWidgets(
    'le champ "Étudiant (optionnel)" est présent et vide par défaut',
    (tester) async {
      final adapter = _FakeHttpClientAdapter(
        (_) => _json({'data': [], 'meta': {}}),
      );
      await pumpNotesScreen(tester, adapter);

      await tester.tap(find.text('Supprimer notes'));
      await tester.pumpAndSettle();

      expect(find.text('Étudiant (optionnel)'), findsOneWidget);
      final field = tester.widget<TextField>(
        find.ancestor(
          of: find.text('Étudiant (optionnel)'),
          matching: find.byType(TextField),
        ),
      );
      expect(field.controller!.text, isEmpty);
    },
  );

  testWidgets("modifier le champ Étudiant invalide un aperçu déjà obtenu — "
      'exactement comme changer Niveau/Classe/Année/Mois (pour ne jamais '
      'supprimer sur la base d\'une sélection différente de celle vérifiée)', (
    tester,
  ) async {
    final adapter = _FakeHttpClientAdapter((options) {
      if (options.path.contains('apercu-suppression')) {
        return _json({'etudiants_concernes': 24, 'notes_a_supprimer': 24});
      }
      return _json({'data': [], 'meta': {}});
    });
    await pumpNotesScreen(tester, adapter);
    await openDeleteDialogWithCompleteFilters(tester);

    await tester.tap(find.text('Vérifier'));
    await tester.pumpAndSettle();
    expect(find.textContaining('24 note(s)'), findsOneWidget);

    await tester.enterText(
      find.ancestor(
        of: find.text('Étudiant (optionnel)'),
        matching: find.byType(TextField),
      ),
      '1-68979',
    );
    await tester.pumpAndSettle();

    // L'aperçu précédent (pour TOUTE la classe) ne doit plus être affiché
    // une fois le filtre étudiant changé — sinon le bouton "Supprimer
    // définitivement" resterait activable sur la base du mauvais compte.
    expect(find.textContaining('24 note(s)'), findsNothing);
  });

  testWidgets(
    "l'identifiant saisi est bien transmis à l'aperçu ET à la suppression",
    (tester) async {
      final adapter = _FakeHttpClientAdapter((options) {
        if (options.path.contains('apercu-suppression')) {
          expect(options.queryParameters['identifiant'], '1-68979');
          return _json({'etudiants_concernes': 1, 'notes_a_supprimer': 3});
        }
        return _json({'data': [], 'meta': {}});
      });
      await pumpNotesScreen(tester, adapter);
      await openDeleteDialogWithCompleteFilters(tester);

      await tester.enterText(
        find.ancestor(
          of: find.text('Étudiant (optionnel)'),
          matching: find.byType(TextField),
        ),
        '1-68979',
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Vérifier'));
      await tester.pumpAndSettle();

      expect(find.textContaining('1 étudiant(s)'), findsOneWidget);
    },
  );
}
