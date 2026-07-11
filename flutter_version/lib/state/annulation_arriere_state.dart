import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/annulation_arriere.dart';

/// Dérogation manuelle et réversible au blocage d'arriéré d'année
/// précédente (RSavePaiement.py:_check_arrears_previous_year) — voir
/// RAnnulationArriere.py côté backend. Ne modifie jamais
/// Paiement.paiement_details ; annuler l'action désactive juste la
/// dérogation, l'historique de paiement original reste intact.
class AnnulationArriereState extends ChangeNotifier {
  AnnulationArriereState(this._apiClient);

  final ApiClient _apiClient;

  bool isLoading = false;
  bool isSubmitting = false;

  /// Équivalent de GET v1/annulation-arriere?paiement_id= — la dérogation
  /// active pour ce paiement (année précise), ou null s'il n'y en a pas.
  Future<AnnulationArriere?> fetchActive(String paiementId) async {
    isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'annulation-arriere',
        query: {'paiement_id': paiementId},
      );
      final list = (response.data as List?) ?? const [];
      for (final item in list) {
        final a = AnnulationArriere.fromJson(item as Map<String, dynamic>);
        if (a.estActive) return a;
      }
      return null;
    } catch (_) {
      return null;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de POST v1/annulation-arriere.
  Future<String?> creer({
    required String paiementId,
    required String typeAnnulation,
    double? montantAnnule,
    required String ordonnePar,
    required String ordonneParFonction,
    required String raison,
    required bool contratAccepte,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('annulation-arriere', data: {
        'paiement_id': paiementId,
        'type_annulation': typeAnnulation,
        'montant_annule': montantAnnule,
        'ordonne_par': ordonnePar,
        'ordonne_par_fonction': ordonneParFonction,
        'raison': raison,
        'contrat_accepte': contratAccepte,
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  /// Équivalent de POST v1/annulation-arriere/{id}/annuler.
  Future<String?> revoquer({
    required String annulationId,
    required String raison,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('annulation-arriere/$annulationId/annuler', data: {
        'raison': raison,
      });
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
      if (data is Map) {
        final detail = data['detail'];
        if (detail is Map && detail['errors'] != null) {
          final errors = detail['errors'];
          if (errors is Map) return errors.values.expand((v) => v is List ? v : [v]).join('\n');
          return errors.toString();
        }
        if (detail != null) return detail.toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
