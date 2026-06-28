import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/dashboard_charts.dart';
import '../models/dashboard_stats.dart';

/// Équivalent de dash_page()/show_data_in_dash() (Controllers/Main.py) pour
/// les 6 stats de base — étendu avec les panneaux de statistiques détaillées
/// (étudiants/paiements) et la liste d'élèves par classe, qui n'existent que
/// dans le frontend web (Dashboard.vue + DashboardStudentStats.vue +
/// PaiementsStats.vue, ecole_nginx/frontend), repris ici sur demande
/// explicite ("toutes les fonctionnalités du web").
class DashboardState extends ChangeNotifier {
  DashboardState(this._apiClient);

  final ApiClient _apiClient;

  DashboardStats? stats;
  bool isLoading = false;
  String? errorMessage;

  Future<void> load({String? anneeAcademiqueId}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.get(
        'dashboard',
        query: anneeAcademiqueId != null ? {'search': anneeAcademiqueId} : null,
      );
      stats = DashboardStats.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      errorMessage = 'Impossible de charger le tableau de bord.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  // ── Drill-down Étudiants (DashboardStudentStats.vue) ──────────────────
  List<EtudiantStatsAnnee> etudiantStats = [];
  bool isLoadingEtudiantStats = false;
  String? etudiantStatsError;

  /// Équivalent de chargerStats() → GET v1/stats/etudiants. `resolveAnneeLabel`
  /// doit venir de données de référence déjà chargées (le champ `libelle`
  /// renvoyé par le serveur est toujours "—", cf. dashboard_charts.dart).
  Future<void> loadEtudiantStats({
    String? anneeId,
    required String Function(String) resolveAnneeLabel,
  }) async {
    isLoadingEtudiantStats = true;
    etudiantStatsError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'stats/etudiants',
        query: anneeId != null ? {'annee_id': anneeId} : null,
      );
      etudiantStats = ((response.data as List?) ?? const [])
          .map((e) => EtudiantStatsAnnee.fromJson(e as Map<String, dynamic>, resolveAnneeLabel))
          .toList();
    } catch (e) {
      etudiantStatsError = 'Impossible de charger les statistiques des élèves.';
    } finally {
      isLoadingEtudiantStats = false;
      notifyListeners();
    }
  }

  // ── Drill-down Paiements (PaiementsStats.vue) ──────────────────────────
  List<String> paiementAnnees = [];
  bool isLoadingPaiementAnnees = false;

  PaiementAnnuelStats? paiementAnnuel;
  bool isLoadingPaiementAnnuel = false;
  String? paiementAnnuelError;

  PaiementJournalierStats? paiementJournalier;
  bool isLoadingPaiementJournalier = false;

  /// Équivalent du peuplement de `anneesDisponibles` → GET
  /// v1/paiements/stats/annees.
  Future<void> loadPaiementAnnees() async {
    isLoadingPaiementAnnees = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('paiements/stats/annees');
      paiementAnnees = ((response.data as List?) ?? const []).map((e) => e.toString()).toList();
    } catch (_) {
      paiementAnnees = [];
    } finally {
      isLoadingPaiementAnnees = false;
      notifyListeners();
    }
  }

  /// Équivalent de chargerStats() → GET v1/paiements/stats/annuel.
  Future<void> loadPaiementAnnuel(String anneeAcademique) async {
    isLoadingPaiementAnnuel = true;
    paiementAnnuelError = null;
    paiementJournalier = null;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'paiements/stats/annuel',
        query: {'annee_academique': anneeAcademique},
      );
      paiementAnnuel = PaiementAnnuelStats.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      paiementAnnuelError = 'Impossible de charger les paiements de cette année.';
    } finally {
      isLoadingPaiementAnnuel = false;
      notifyListeners();
    }
  }

  /// Équivalent de chargerJournalier() → GET v1/paiements/stats/journalier.
  Future<void> loadPaiementJournalier(String anneeAcademique, String mois) async {
    isLoadingPaiementJournalier = true;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'paiements/stats/journalier',
        query: {'annee_academique': anneeAcademique, 'mois': mois},
      );
      paiementJournalier = PaiementJournalierStats.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      paiementJournalier = null;
    } finally {
      isLoadingPaiementJournalier = false;
      notifyListeners();
    }
  }

  void clearPaiementJournalier() {
    paiementJournalier = null;
    notifyListeners();
  }

  // ── Liste des élèves d'une classe ("Gérer", show_student_number_in_classes()
  // + dialogue "Liste des élèves de la classe", Controllers/Main.py:2883+) ──
  List<ClasseStudentRow> classeStudents = [];
  bool isLoadingClasseStudents = false;
  String? classeStudentsError;
  String? _classeIdForStudents;
  String? _anneeIdForStudents;

  /// Équivalent de on_row_clicked_class_show() → GET v1/student-with-classe.
  Future<void> loadClasseStudents({required String classeId, required String anneeId}) async {
    _classeIdForStudents = classeId;
    _anneeIdForStudents = anneeId;
    isLoadingClasseStudents = true;
    classeStudentsError = null;
    classeStudents = [];
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'student-with-classe',
        query: {'classe_id': classeId, 'annee_id': anneeId},
      );
      final data = (response.data as Map<String, dynamic>)['data'] as List? ?? const [];
      classeStudents = data.map((e) => ClasseStudentRow.fromJson(e as Map<String, dynamic>)).toList();
    } catch (e) {
      classeStudentsError = 'Impossible de charger les élèves de cette classe.';
    } finally {
      isLoadingClasseStudents = false;
      notifyListeners();
    }
  }

  /// Équivalent de update_student_status() (Controllers/Main.py:7485) →
  /// PATCH v1/update-etudiant-classe. Le serveur (Routes/dashboard.py)
  /// bascule lui-même le statut courant ou supprime l'enregistrement — il
  /// ne lit pas un état envoyé par le client — donc on recharge la liste
  /// après coup pour que la case "Actif" reflète la vraie valeur en base.
  Future<String?> updateClasseStudentStatus({
    required String classeEtudiantId,
    required bool delete,
  }) async {
    try {
      await _apiClient.dio.patch(
        'update-etudiant-classe',
        data: {'classe_student_id': classeEtudiantId, 'delete': delete},
      );
      if (_classeIdForStudents != null && _anneeIdForStudents != null) {
        await loadClasseStudents(classeId: _classeIdForStudents!, anneeId: _anneeIdForStudents!);
      }
      return null;
    } catch (e) {
      return delete
          ? "Impossible de supprimer l'élève de la classe."
          : "Impossible de changer le statut de l'élève.";
    }
  }
}
