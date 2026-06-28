import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/cours.dart';

/// Équivalent de cours_page()/go_to_cours_page()/enregistrer_cours()/
/// delete_cours() (school_client, Controllers/Main.py:9625-10227), aligné
/// sur le vrai contrat backend (RCours.py) :
/// - GET v1/cours?page=X&search=Y → liste paginée.
/// - POST v1/cours avec {"CoursesObject": [...]} (toujours une LISTE, même
///   pour un seul cours — c'est le seul chemin du serveur réellement
///   atteignable : la branche "id au premier niveau" du serveur exige elle
///   aussi `CoursesObject`, donc invalide sans lui — ignorée).
/// - GET v1/delete-cours/{id} pour la suppression (pas DELETE — le web
///   appelle à tort `DELETE /cours/{id}`, route inexistante côté serveur ;
///   non reproduit, on suit le vrai contrat, identique à AsyncDataHandler.py
///   côté bureau).
class CoursState extends ChangeNotifier {
  CoursState(this._apiClient);

  final ApiClient _apiClient;

  List<Cours> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? deletingId;

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();

    try {
      final response = await _apiClient.get('cours', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => Cours.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des cours.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de enregistrer_cours() (Main.py:10227-10246) → POST v1/cours,
  /// {"CoursesObject": [...]} — TOUJOURS un lot, même pour une seule ligne
  /// (self.cours_dictionary y compris pour 1 élément) ; chaque item peut
  /// créer (id absent) ou modifier (id présent) — un même envoi peut
  /// mélanger les deux.
  Future<String?> save(List<Map<String, dynamic>> items) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('cours', data: {'CoursesObject': items});
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> delete(String coursId) async {
    deletingId = coursId;
    notifyListeners();
    try {
      await _apiClient.dio.get('delete-cours/$coursId');
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      deletingId = null;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map) {
        if (data['detail'] != null) return data['detail'].toString();
        if (data['errors'] is Map) {
          final errors = (data['errors'] as Map).values.expand((v) {
            return v is List ? v : [v];
          }).join('\n');
          if (errors.isNotEmpty) return errors;
        }
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
