import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/note.dart';

void main() {
  group('NoteSearchResult.evaluationPar', () {
    test(
      'lu depuis examEcheance.evaluation_par (niveau Contrôle/Trimestre/Mois)',
      () {
        final result = NoteSearchResult.fromJson({
          'result': [],
          'cours': {'cours_nom': 'Français'},
          'session': null,
          'examEcheance': {'name': 'Secondaire', 'evaluation_par': 'Trimestre'},
          'list_cours': [],
          'annee': '2025/2026',
        });

        expect(result.evaluationPar, 'Trimestre');
      },
    );

    test(
      'null quand examEcheance est absent (niveau Universitaire, session à la place)',
      () {
        final result = NoteSearchResult.fromJson({
          'result': [],
          'cours': {'cours_nom': 'Droit civil'},
          'session': '1ère',
          'examEcheance': null,
          'list_cours': [],
          'annee': '2025/2026',
        });

        expect(result.evaluationPar, isNull);
        expect(result.session, '1ère');
      },
    );
  });
}
