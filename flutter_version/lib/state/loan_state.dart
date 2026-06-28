import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/loan.dart';

/// Équivalent de tab_loans()/loans_form()/sauvegarder_loans()/
/// to_loans_repayments() (school_client, Controllers/Main.py:4871-4972) →
/// GET v1/get-loans, GET v1/get-data-user-for-loans, POST v1/post-loans,
/// POST v1/loans/repay (RVente.py:259-330).
class LoanState extends ChangeNotifier {
  LoanState(this._apiClient);

  final ApiClient _apiClient;

  List<LoanRecord> items = [];
  int currentPage = 1;
  int lastPage = 1;
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;

  List<LoanUserOption> userOptions = [];
  bool isLoadingUserOptions = false;

  /// Options réelles de loans_status (QComboBox, Main.py:1110-1111) — le
  /// bureau n'expose pas "default", seulement ces 5 valeurs.
  static const statusOptions = [
    'pending',
    'approved',
    'declined',
    'disbursed',
    'paid',
  ];

  /// Côté backend, un admin reçoit une liste paginée (avec `meta`) ; un
  /// utilisateur non-admin ne reçoit que ses propres prêts, sans pagination
  /// (RVente.py:259-296) — on gère donc les deux formes de réponse.
  Future<void> load({int page = 1}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('get-loans', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => LoanRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des prêts.';
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

  /// Équivalent de sauvegarder_loans() (Main.py:4946-4964) : sur le bureau,
  /// `monthly_payment` est un QLineEdit saisi à la main (jamais calculé
  /// automatiquement — la formule en commentaire de SVente.py:164 n'est
  /// exécutée nulle part, ni bureau ni serveur), et `loans_status` est un
  /// vrai QComboBox envoyé à la création.
  Future<String?> createLoan({
    required String userId,
    required double amount,
    required int termMonths,
    required double interestRate,
    required double monthlyPayment,
    required String status,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post(
        'post-loans',
        data: {
          'user_id': userId,
          'amount': amount,
          'term_months': termMonths,
          'interest_rate': interestRate,
          'monthly_payment': monthlyPayment,
          'status': status,
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

  Future<String?> repay({
    required String loansId,
    required double paidAmount,
    String? paymentMethod,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post(
        'loans/repay',
        data: {
          'loans_id': loansId,
          'paid_amount': paidAmount,
          'payment_method': paymentMethod,
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
