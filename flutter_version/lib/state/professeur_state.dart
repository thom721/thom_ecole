import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/professeur.dart';

/// Équivalent de professeur_page()/set_table_refresh_data_teacher()/
/// add_professeur()/active_teacher() (school_client, Controllers/Main.py:
/// 9388-9627), aligné sur le vrai contrat backend (GET/POST v1/professeur,
/// PATCH v1/active-teacher — voir RAcademic.py:312-648). La suppression
/// n'existe nulle part côté serveur (aucune route DELETE /professeur) ; le
/// bouton "Supprimer" du web (Professeur.vue) n'est qu'un `console.log`
/// jamais relié à une requête — volontairement absente ici aussi.
class ProfesseurState extends ChangeNotifier {
  ProfesseurState(this._apiClient);

  final ApiClient _apiClient;

  List<Professeur> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? activatingId;

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();

    try {
      final response = await _apiClient.get('professeur', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => Professeur.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des professeurs.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de submitProfesseur() — un seul endpoint POST v1/professeur
  /// pour créer ET modifier (le champ `id` dans le payload décide), comme
  /// add_professeur() côté bureau. Le web appelle à tort `PUT /professeur/
  /// {id}` pour la modification (endpoint inexistant côté serveur) — non
  /// reproduit, on suit le vrai contrat backend.
  Future<String?> save(Map<String, dynamic> payload) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('professeur', data: payload);
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<({int? status, String? error})> toggleActive(String professeurId) async {
    activatingId = professeurId;
    notifyListeners();
    try {
      final response = await _apiClient.dio.patch('active-teacher', data: {'id': professeurId});
      final status = (response.data as Map<String, dynamic>)['status'];
      return (status: status is bool ? (status ? 1 : 0) : (status as num?)?.toInt(), error: null);
    } catch (e) {
      return (status: null, error: _extractError(e));
    } finally {
      activatingId = null;
      notifyListeners();
    }
  }

  bool isResettingPassword = false;

  /// Équivalent de reset_password_professeur()/reset_password_prof()
  /// (school_client, Controllers/Main.py:4632, Models/AsyncDataHandler.py:
  /// 348) → PATCH v1/change-password-teacher. Absent du web (aucune route
  /// ni bouton équivalent côté frontend) — repris ici fidèle au bureau.
  Future<String?> resetPassword({
    required String professeurId,
    required String password,
    required String passwordConfirm,
  }) async {
    isResettingPassword = true;
    notifyListeners();
    try {
      await _apiClient.dio.patch('change-password-teacher', data: {
        'professeur_id': professeurId,
        'password': password,
        'password_confirm': passwordConfirm,
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isResettingPassword = false;
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
