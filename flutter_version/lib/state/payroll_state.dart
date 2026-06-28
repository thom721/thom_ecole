import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/loan.dart' show LoanUserOption;
import '../models/payroll.dart';

/// Versements de salaire — GET/POST v1/payroll, POST v1/payroll/{id}/pay,
/// DELETE v1/payroll/{id} (ecole_nginx/app/Routes/RPayroll.py). Fonctionnalité
/// ajoutée sur demande explicite (absente du bureau et du web).
class PayrollState extends ChangeNotifier {
  PayrollState(this._apiClient);

  final ApiClient _apiClient;

  static const moisOptions = [
    'Janvier',
    'Février',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Août',
    'Septembre',
    'Octobre',
    'Novembre',
    'Décembre',
  ];

  static const methodeOptions = ['Espèce', 'Chèque'];

  List<PayrollRecord> items = [];
  int currentPage = 1;
  int lastPage = 1;
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? payingId;
  String? deletingId;

  List<LoanUserOption> userOptions = [];
  bool isLoadingUserOptions = false;

  Future<void> load({int page = 1}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('payroll', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => PayrollRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des versements.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadUserOptions() async {
    if (userOptions.isNotEmpty) return;
    isLoadingUserOptions = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('get-data-user-for-loans');
      final data = response.data as Map<String, dynamic>;
      userOptions = ((data['data'] as List?) ?? const [])
          .map((e) => LoanUserOption.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      // Liste vide en cas d'échec.
    } finally {
      isLoadingUserOptions = false;
      notifyListeners();
    }
  }

  Future<String?> create({
    required String userId,
    required double montant,
    required String mois,
    required String annee,
    required String methodePaiement,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post(
        'payroll',
        data: {
          'user_id': userId,
          'montant': montant,
          'mois': mois,
          'annee': annee,
          'methode_paiement': methodePaiement,
        },
      );
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> markPaid(String id) async {
    payingId = id;
    notifyListeners();
    try {
      await _apiClient.dio.post('payroll/$id/pay');
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      payingId = null;
      notifyListeners();
    }
  }

  Future<String?> delete(String id) async {
    deletingId = id;
    notifyListeners();
    try {
      await _apiClient.dio.delete('payroll/$id');
      items.removeWhere((p) => p.id == id);
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
