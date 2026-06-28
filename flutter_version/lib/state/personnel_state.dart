import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/personnel.dart';

/// Équivalent de admin_page()/set_table_refresh_data_admin()/
/// add_personnel()/active_personnel() (school_client, Controllers/Main.py:
/// 7691-7970), aligné sur le vrai contrat backend (GET/POST v1/personnel,
/// PATCH v1/active-personnel — voir RAcademic.py:686-1180). La suppression
/// n'existe nulle part côté serveur (aucune route DELETE /personnel) ; le
/// bouton "Supprimer" du web (Administration.vue) a un onClick vide —
/// volontairement absente ici aussi.
class PersonnelState extends ChangeNotifier {
  PersonnelState(this._apiClient);

  final ApiClient _apiClient;

  List<Personnel> items = [];
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
      final response = await _apiClient.get('personnel', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => Personnel.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste du personnel.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de submitPersonnel() → POST v1/personnel (créer ET modifier,
  /// le champ `id` décide), comme add_personnel() côté bureau.
  Future<String?> save(Map<String, dynamic> payload) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('personnel', data: payload);
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<({int? status, String? error})> toggleActive(String personnelId) async {
    activatingId = personnelId;
    notifyListeners();
    try {
      final response = await _apiClient.dio.patch('active-personnel', data: {'id': personnelId});
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

  /// Équivalent de reset_password_personnel()/reset_password_perso()
  /// (school_client, Controllers/Main.py:4619, Models/AsyncDataHandler.py:
  /// 357) → PATCH v1/change-password-personnel. Absent du web (aucune
  /// route ni bouton équivalent côté frontend) — repris ici fidèle au
  /// bureau.
  Future<String?> resetPassword({
    required String personnelId,
    required String password,
    required String passwordConfirm,
  }) async {
    isResettingPassword = true;
    notifyListeners();
    try {
      await _apiClient.dio.patch('change-password-personnel', data: {
        'personnel_id': personnelId,
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
