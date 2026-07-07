import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/pointage.dart';

/// Pointage (arrivée/départ) du personnel — GET v1/pointage/personnel,
/// POST v1/pointage/arrivee, POST v1/pointage/depart, GET v1/pointage/
/// historique (ecole_nginx/app/Routes/RPointage.py). Fonctionnalité
/// ajoutée sur demande explicite, sert de source d'heures pour le payroll
/// horaire des professeurs (voir payroll_state.dart).
class PointageState extends ChangeNotifier {
  PointageState(this._apiClient);

  final ApiClient _apiClient;

  List<PointagePersonne> personnel = [];
  bool isLoading = false;
  String? errorMessage;
  String? pointingId;

  List<PointageHistoriqueEntry> historique = [];
  double historiqueTotalHeures = 0;
  bool isLoadingHistorique = false;
  String? historiqueError;

  Future<void> loadPersonnel({String? date}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('pointage/personnel', query: {
        if (date != null) 'date': date,
      });
      final data = response.data as Map<String, dynamic>;
      personnel = ((data['data'] as List?) ?? const [])
          .map((e) => PointagePersonne.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      errorMessage = 'Impossible de charger le personnel.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> pointerArrivee(String userId) async {
    pointingId = userId;
    notifyListeners();
    try {
      await _apiClient.post('pointage/arrivee', data: {'user_id': userId});
      await loadPersonnel();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      pointingId = null;
      notifyListeners();
    }
  }

  Future<String?> pointerDepart(String userId) async {
    pointingId = userId;
    notifyListeners();
    try {
      await _apiClient.post('pointage/depart', data: {'user_id': userId});
      await loadPersonnel();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      pointingId = null;
      notifyListeners();
    }
  }

  Future<void> loadHistorique({
    required String userId,
    required int mois,
    required int annee,
  }) async {
    isLoadingHistorique = true;
    historiqueError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('pointage/historique', query: {
        'user_id': userId,
        'mois': mois,
        'annee': annee,
      });
      final data = response.data as Map<String, dynamic>;
      historique = ((data['data'] as List?) ?? const [])
          .map((e) => PointageHistoriqueEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      historiqueTotalHeures = (data['total_heures'] as num?)?.toDouble() ?? 0;
    } catch (e) {
      historiqueError = 'Impossible de charger l\'historique.';
    } finally {
      isLoadingHistorique = false;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] != null) return data['detail'].toString();
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
