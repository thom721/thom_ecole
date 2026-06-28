import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/presence.dart';

/// Équivalent de Presences.vue (ecole_nginx/frontend/src/views/admin/
/// Presences.vue) — fonctionnalité absente du bureau (school_client),
/// reprise du web sur demande explicite. Endpoints : RPresences.py
/// (classes/{id}/etudiants, presences, presences/jour,
/// presences/historique, stats-presence-aujourdhui).
class PresenceState extends ChangeNotifier {
  PresenceState(this._apiClient);

  final ApiClient _apiClient;

  // --- Onglet "Appel du jour" ---
  List<PresenceStudent> appelStudents = [];
  bool isLoadingAppel = false;
  bool isSavingAppel = false;
  bool dejaEnregistre = false;
  String? appelError;
  String? appelSuccess;

  int get presentsCount => appelStudents.where((s) => s.valeur == true).length;
  int get absentsCount => appelStudents.where((s) => s.valeur == false).length;
  int get nonMarquesCount =>
      appelStudents.where((s) => s.valeur == null).length;
  double get tauxAppel =>
      appelStudents.isEmpty ? 0 : (presentsCount / appelStudents.length) * 100;

  Future<void> loadAppel({
    required String classeId,
    required String anneeId,
    required String date,
  }) async {
    isLoadingAppel = true;
    appelError = null;
    appelSuccess = null;
    notifyListeners();
    try {
      final etudiantsResp = await _apiClient.get(
        'classes/$classeId/etudiants',
        query: {'annee_academique_id': anneeId},
      );
      final students = ((etudiantsResp.data as List?) ?? const [])
          .map((e) => PresenceStudent.fromJson(e as Map<String, dynamic>))
          .toList();

      final jourResp = await _apiClient.get(
        'presences/jour',
        query: {
          'classes_id': classeId,
          'annee_academique_id': anneeId,
          'date': date,
        },
      );
      final jourData = (jourResp.data as Map?) ?? const {};
      for (final s in students) {
        if (jourData.containsKey(s.id)) {
          s.valeur = jourData[s.id] as bool?;
        }
      }
      appelStudents = students;
      dejaEnregistre = jourData.isNotEmpty;
    } catch (e) {
      appelError = 'Impossible de charger les élèves de cette classe.';
      appelStudents = [];
    } finally {
      isLoadingAppel = false;
      notifyListeners();
    }
  }

  void toggleValeur(PresenceStudent student, bool valeur) {
    student.valeur = valeur;
    notifyListeners();
  }

  void markAll(bool valeur) {
    for (final s in appelStudents) {
      s.valeur = valeur;
    }
    notifyListeners();
  }

  Future<String?> saveAppel({
    required String classeId,
    required String anneeId,
    required String date,
  }) async {
    isSavingAppel = true;
    appelError = null;
    appelSuccess = null;
    notifyListeners();
    try {
      await _apiClient.post(
        'presences',
        data: {
          'classes_id': classeId,
          'annee_academique_id': anneeId,
          'date_daujourdhui': date,
          'presences': appelStudents
              .map((s) => {'etudiant_id': s.id, 'valeur': s.valeur ?? false})
              .toList(),
        },
      );
      dejaEnregistre = true;
      appelSuccess = "L'appel a été enregistré avec succès.";
      return null;
    } catch (e) {
      appelError = _extractError(e);
      return appelError;
    } finally {
      isSavingAppel = false;
      notifyListeners();
    }
  }

  // --- Onglet "Historique" ---
  List<PresenceHistoriqueRecord> historique = [];
  bool isLoadingHistorique = false;
  String? historiqueError;

  Future<void> loadHistorique({
    String? classeId,
    String? anneeId,
    String? mois,
  }) async {
    isLoadingHistorique = true;
    historiqueError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'presences/historique',
        query: {
          'classe_id': ?classeId,
          'annee_academique_id': ?anneeId,
          'mois': ?mois,
        },
      );
      historique = ((response.data as List?) ?? const [])
          .map(
            (e) => PresenceHistoriqueRecord.fromJson(e as Map<String, dynamic>),
          )
          .toList();
    } catch (e) {
      historiqueError = "Impossible de charger l'historique.";
      historique = [];
    } finally {
      isLoadingHistorique = false;
      notifyListeners();
    }
  }

  // --- Onglet "Statistiques" ---
  PresenceStatsGlobal? statsGlobal;
  List<PresenceClasseStat> statsClasses = [];
  bool isLoadingStats = false;
  String? statsError;

  Future<void> loadStats() async {
    isLoadingStats = true;
    statsError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('stats-presence-aujourdhui');
      final data = response.data as Map<String, dynamic>;
      statsGlobal = PresenceStatsGlobal.fromJson(
        data['global'] as Map<String, dynamic>,
      );
      statsClasses = ((data['classes'] as List?) ?? const [])
          .map((e) => PresenceClasseStat.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      statsError = 'Impossible de charger les statistiques.';
    } finally {
      isLoadingStats = false;
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
