import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/note.dart';
import '../models/programme.dart' show CoursCombo;

/// Équivalent de notes_page()/show_dialog_for_notes()/
/// show_data_after_search_for_insert_notes()/enregistrer_notes()/
/// action_on_notes()/print_bulletin()/action_print_bulletin() (school_client,
/// Controllers/Main.py:10296-11346), aligné sur le vrai contrat backend
/// (RCoursEtudiant.py / RNotes.py / pdf/BulletinPrint.py / pdf/
/// MasBulletinPrint.py).
///
/// Important (confirmé en lisant Main.py) : sur le bureau, la condition
/// `if response['examEcheance']['evaluation_par']=='Mois' or 'mois':`
/// (ligne ~10730) est TOUJOURS vraie quel que soit `evaluation_par` (un
/// `X or 'mois'` est toujours truthy puisque 'mois' est une chaîne non
/// vide) — donc la saisie par "Contrôle"/"Trimestre" (configurable dans
/// Paramètres > Examens, et présente côté web) n'est en réalité JAMAIS
/// utilisée par le bureau : tout niveau non-Universitaire est saisi par
/// MOIS, et Universitaire par session (Intra/Finale). Le sélecteur de
/// période de action_on_notes() (ligne ~11394) confirme la même
/// simplification (`if niveau != 'Universitaire': mois ... else: session`).
/// Reproduit ici à l'identique — Contrôle/Trimestre est donc volontairement
/// omis (fonctionnalité morte côté bureau).
///
/// Également confirmé : `notes_show()` (Voir une fiche de notes) appelle à
/// tort `GET v1/coursEtudiant/{id}` alors que la route réelle est
/// `POST /coursEtudiant/{student}` (RCoursEtudiant.py:155) ET ne renvoie
/// même pas `data_etudiant`/`mois` — "Voir" est donc cassé côté bureau, et
/// les boutons "Modifier"/"Supprimer" de action_on_notes() ne sont jamais
/// connectés (`edit_button`/`delete_button` n'ont pas de `.clicked.connect`)
/// — fonctionnalités mortes, non reproduites ici (même logique que pour les
/// boutons morts déjà rencontrés côté web pour Cours/Programme).
class NoteState extends ChangeNotifier {
  NoteState(this._apiClient);

  final ApiClient _apiClient;

  /// Ordre exact de self.mois_ (Main.py:629) — année scolaire, pas calendaire.
  static const moisAnneeScolaire = [
    'Septembre', 'Octobre', 'Novembre', 'Décembre', 'Janvier', 'Février',
    'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août',
  ];

  List<CoursEtudiantRecord> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;

  List<CoursCombo> coursCombo = [];
  bool isLoadingCombo = false;

  bool isSearching = false;
  bool isSubmitting = false;
  String? printingId;
  bool isPrintingMass = false;

  Future<void> loadCoursCombo() async {
    if (coursCombo.isNotEmpty) return;
    isLoadingCombo = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('for-combo-cours');
      coursCombo = ((response.data['cours'] as List?) ?? const [])
          .map((e) => CoursCombo.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      // Liste vide en cas d'échec : la matière restera simplement non listée.
    } finally {
      isLoadingCombo = false;
      notifyListeners();
    }
  }

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();

    try {
      final response = await _apiClient.get('coursEtudiant', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => CoursEtudiantRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des notes.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de search_for_enter_notes() → POST v1/cours-etudiant-add-note.
  Future<({NoteSearchResult? result, String? error})> search({
    required String niveauId,
    required String coursId,
    required String classeId,
    required String anneeAcademiqueId,
    String? faculteId,
    String? session,
  }) async {
    isSearching = true;
    notifyListeners();
    try {
      final response = await _apiClient.post('cours-etudiant-add-note', data: {
        'niveau': niveauId,
        'cours': coursId,
        'class': classeId,
        'annee_academique': anneeAcademiqueId,
        'faculte': faculteId,
        'session': session,
      });
      final datas = (response.data as Map<String, dynamic>)['datas'] as Map<String, dynamic>;
      return (result: NoteSearchResult.fromJson(datas), error: null);
    } catch (e) {
      return (result: null, error: _extractError(e));
    } finally {
      isSearching = false;
      notifyListeners();
    }
  }

  /// Équivalent de edit_data_note_all() → POST v1/cours-etudiant-edit-note :
  /// récupère les notes déjà enregistrées pour préremplir la grille quand on
  /// change de matière/évaluation. Retourne {etudiant_id: note}.
  Future<Map<String, double>> fetchExisting({
    required String coursNom,
    required String examen,
    required String anneeAcademique,
    required String typeMatiere,
    required List<NoteSearchStudent> students,
  }) async {
    try {
      final response = await _apiClient.post('cours-etudiant-edit-note', data: {
        'cours': coursNom,
        'examen': examen,
        'annee_academique': anneeAcademique,
        'type_matiere': typeMatiere,
        'notes': students.map((s) => {'id': s.id, 'identifiant': s.identifiant}).toList(),
      });
      final success = (response.data as Map<String, dynamic>)['success'] as List?;
      return {
        for (final item in success ?? const [])
          (item as Map<String, dynamic>)['etudiant_id'].toString(): (item['note'] as num).toDouble(),
      };
    } catch (_) {
      return {};
    }
  }

  /// Équivalent de enregistrer_notes() → POST v1/coursEtudiant.
  Future<String?> save({
    required String controle,
    required String examen,
    required String coursNom,
    required String typeMatiere,
    double? coefficients,
    String? session,
    double? noteDePassage,
    required String professeurId,
    required String anneeAcademique,
    required List<NoteSearchStudent> students,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('coursEtudiant', data: {
        'controle': controle,
        'examen': examen,
        'cours': coursNom,
        'type_matiere': typeMatiere,
        'coefficients': coefficients,
        'session': session,
        'note_de_passage': noteDePassage ?? 0.0,
        'professeur_id': professeurId,
        'annee_academique': anneeAcademique,
        'notes': students.map((s) => {'id': s.id, 'identifiant': s.identifiant, 'note': s.note ?? 0}).toList(),
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  /// Équivalent de print_bulletin() → POST v1/imprime-bulletin (PDF), ouvert
  /// avec le lecteur par défaut du système (motif de
  /// PaiementState.printRecu()).
  Future<String?> printBulletin(String coursEtudiantId, {String? mois, String? session}) async {
    printingId = coursEtudiantId;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'imprime-bulletin',
        data: {'bulletin': coursEtudiantId, 'mois': mois, 'session': session},
        options: Options(responseType: ResponseType.bytes),
      );
      final file = File('${Directory.systemTemp.path}/bulletin_$coursEtudiantId.pdf');
      await file.writeAsBytes(response.data as List<int>);
      await _openFile(file.path);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      printingId = null;
      notifyListeners();
    }
  }

  /// Équivalent de action_print_bulletin() → POST v1/imprime-mas-bulletin.
  /// Attention : `annee_academique` attend ici le NOM ("2024/2025"), pas
  /// l'id — c'est ce que le bureau envoie (`.currentText()`, pas
  /// `.currentData()`) et ce que le serveur filtre dessus.
  Future<String?> printMassBulletin({
    required String anneeAcademiqueNom,
    required String classeId,
    required String mois,
  }) async {
    isPrintingMass = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'imprime-mas-bulletin',
        data: {'annee_academique': anneeAcademiqueNom, 'classe': classeId, 'mois': mois},
        options: Options(responseType: ResponseType.bytes),
      );
      final file = File('${Directory.systemTemp.path}/bulletin_classe_${classeId}_$mois.pdf');
      await file.writeAsBytes(response.data as List<int>);
      await _openFile(file.path);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isPrintingMass = false;
      notifyListeners();
    }
  }

  Future<void> _openFile(String path) async {
    if (Platform.isMacOS) {
      await Process.run('open', [path]);
    } else if (Platform.isWindows) {
      await Process.run('cmd', ['/c', 'start', '', path]);
    } else if (Platform.isLinux) {
      await Process.run('xdg-open', [path]);
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map) {
        final detail = data['detail'];
        if (detail is Map && detail['errors'] != null) {
          final errors = detail['errors'];
          if (errors is Map) return errors.values.expand((v) => v is List ? v : [v]).join('\n');
          return errors.toString();
        }
        if (detail != null) return detail.toString();
        if (data['errors'] is Map) {
          final errors = (data['errors'] as Map).values.expand((v) => v is List ? v : [v]).join('\n');
          if (errors.isNotEmpty) return errors;
        }
        if (data['errors'] != null) return data['errors'].toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
