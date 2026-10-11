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

  /// Équivalent de GET v1/annulation-arriere?paiement_id= — le solde
  /// restant dû pour cette ligne (affiché avant même de choisir le
  /// montant), la dérogation active pour ce paiement s'il y en a une, et
  /// l'historique complet (actives et révoquées, le plus récent en
  /// premier — déjà renvoyé tel quel par le backend, RAnnulationArriere.py
  /// ::lister_annulations_arriere) pour que l'écran puisse aussi montrer
  /// qu'une dérogation a été révoquée, pas seulement qu'il n'y en a plus
  /// d'active.
  Future<({double? soldeRestant, String? devise, AnnulationArriere? existing, List<AnnulationArriere> history})>
  fetchContext(String paiementId) async {
    isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'annulation-arriere',
        query: {'paiement_id': paiementId},
      );
      final data = response.data as Map<String, dynamic>;
      final derogations = (data['derogations'] as List?) ?? const [];
      final history = derogations
          .map((item) => AnnulationArriere.fromJson(item as Map<String, dynamic>))
          .toList();
      AnnulationArriere? existing;
      for (final a in history) {
        if (a.estActive) {
          existing = a;
          break;
        }
      }
      return (
        soldeRestant: (data['solde_restant'] as num?)?.toDouble(),
        devise: data['devise']?.toString(),
        existing: existing,
        history: history,
      );
    } catch (_) {
      return (soldeRestant: null, devise: null, existing: null, history: <AnnulationArriere>[]);
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
