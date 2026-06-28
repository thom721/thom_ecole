import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../core/dual_auth.dart';
import '../models/depense.dart';

/// Équivalent de depense_page()/enregistrer_depense()/delete_depense()
/// (school_client, Controllers/Main.py:5122-5295) → GET/POST v1/depense,
/// GET v1/delete-depense (RVente.py:330-454).
class DepenseState extends ChangeNotifier {
  DepenseState(this._apiClient);

  final ApiClient _apiClient;

  List<DepenseRecord> items = [];
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
      final response = await _apiClient.get(
        'depense',
        query: {'page': page, if (searchTerm.isNotEmpty) 'search': searchTerm},
      );
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => DepenseRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des dépenses.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> save({
    String? id,
    required String description,
    required double prix,
    String? approvalToken,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'depense',
        data: {'id': id, 'description': description, 'prix': prix},
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      // Dio ne lève jamais d'exception pour un 202 (2xx est "succès" par
      // défaut, voir _defaultValidateStatus) : DualAuthChecker doit donc
      // être détecté ici, sur la réponse, pas dans le catch ci-dessous.
      if (response.statusCode == 202) return kApprovalRequiredError;
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> delete(
    String id, {
    required String raison,
    String? approvalToken,
  }) async {
    deletingId = id;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get(
        'delete-depense',
        queryParameters: {'id_depense': id, 'raison': raison},
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      if (response.statusCode == 202) return kApprovalRequiredError;
      items.removeWhere((d) => d.id == id);
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
      if (data is Map && data['detail'] != null)
        return data['detail'].toString();
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
