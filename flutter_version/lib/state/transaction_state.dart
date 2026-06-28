import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../core/dual_auth.dart';
import '../models/student.dart';
import '../models/transaction.dart';

/// "Autre transaction" — équivalent de autre_transaction()/
/// sauvegarder_other_transaction()/edit_other_transaction()
/// (school_client, Controllers/Main.py:5013-5119), via GET/POST
/// v1/other-transaction(s), PATCH v1/edit-other-transaction/{id}, DELETE
/// v1/transactions/{id} (ecole_nginx/app/Routes/RTransaction.py).
class TransactionState extends ChangeNotifier {
  TransactionState(this._apiClient);

  final ApiClient _apiClient;

  /// Options réelles de combo_transact_description (Main.py:5022).
  static const descriptionOptions = [
    'Initiale',
    'Badge perdu',
    'Relevé de notes',
    'Diplôme',
    'Autre',
  ];

  List<OtherTransactionRecord> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? deletingId;

  List<Student> liveSearchResults = [];
  bool isSearchingStudent = false;

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'other-transactions',
        query: {'page': page, if (searchTerm.isNotEmpty) 'q': searchTerm},
      );
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map(
            (e) => OtherTransactionRecord.fromJson(e as Map<String, dynamic>),
          )
          .toList();
      currentPage = (data['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (data['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des transactions.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchStudents(String query) async {
    if (query.trim().length < 2) {
      liveSearchResults = [];
      notifyListeners();
      return;
    }
    isSearchingStudent = true;
    notifyListeners();
    try {
      final response = await _apiClient.post(
        'live-student',
        data: {'val': query},
      );
      final data = response.data as Map<String, dynamic>;
      liveSearchResults = ((data['data'] as List?) ?? const [])
          .map((e) => Student.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      liveSearchResults = [];
    } finally {
      isSearchingStudent = false;
      notifyListeners();
    }
  }

  Future<String?> save({
    String? id,
    required String description,
    String? descriptionSupplementaire,
    String? identifiant,
    required double montant,
    String? approvalToken,
  }) async {
    isSubmitting = true;
    notifyListeners();
    final payload = {
      'description': description,
      'description_supplementaire': descriptionSupplementaire,
      'identifiant': identifiant,
      'montant': montant,
    };
    try {
      if (id == null) {
        await _apiClient.post('other-transaction', data: payload);
      } else {
        // Dio ne lève jamais d'exception pour un 202 (2xx = succès par
        // défaut, voir _defaultValidateStatus) : DualAuthChecker doit donc
        // être détecté ici, sur la réponse, pas dans le catch ci-dessous.
        final response = await _apiClient.dio.patch(
          'edit-other-transaction/$id',
          data: payload,
          options: approvalToken == null
              ? null
              : Options(headers: {'X-Approval-Token': approvalToken}),
        );
        if (response.statusCode == 202) return kApprovalRequiredError;
      }
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
      final response = await _apiClient.dio.delete(
        'transactions/$id',
        queryParameters: {'raison': raison},
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      if (response.statusCode == 202) return kApprovalRequiredError;
      items.removeWhere((t) => t.id == id);
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
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
