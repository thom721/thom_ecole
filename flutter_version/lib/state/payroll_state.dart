import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/loan.dart' show LoanUserOption;
import '../models/parametre_payroll.dart';
import '../models/payroll.dart';

/// Versements de salaire — GET/POST v1/payroll, POST v1/payroll/{id}/verser,
/// DELETE v1/payroll/{id} (ecole_nginx/app/Routes/RPayroll.py). Fonctionnalité
/// ajoutée sur demande explicite (absente du bureau et du web). Deux modes :
/// 'fixe' (montant saisi/pré-rempli depuis Professeur.salaireFixe) ou
/// 'horaire' (montant dû = Σ heures × taux, un cours à la fois via
/// ParametrePayroll) ; les versements partiels sont possibles (mirror de
/// LoanState/repay), voir `verser()`.
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

  List<BilanMensuelRow> bilanMensuel = [];
  bool isLoadingBilan = false;
  String? bilanError;

  /// "Bilan mensuel" (demande explicite) : pour chaque professeur, son
  /// Payroll du mois sélectionné (montant dû/versé/solde/statut) s'il
  /// existe déjà, ou 'Aucun' sinon.
  Future<void> loadBilanMensuel({required String mois, required String annee}) async {
    isLoadingBilan = true;
    bilanError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('payroll/bilan-mensuel', query: {
        'mois': mois,
        'annee': annee,
      });
      final data = response.data as Map<String, dynamic>;
      bilanMensuel = ((data['data'] as List?) ?? const [])
          .map((e) => BilanMensuelRow.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      bilanError = 'Impossible de charger le bilan mensuel.';
    } finally {
      isLoadingBilan = false;
      notifyListeners();
    }
  }

  List<LoanUserOption> userOptions = [];
  bool isLoadingUserOptions = false;

  // --- Mode horaire : professeur sélectionné (résolu depuis user_id) ---
  bool isLoadingProfesseurInfo = false;
  bool selectedIsProfesseur = false;
  String? selectedProfesseurId;
  String selectedTypePaiement = 'fixe';
  double? selectedSalaireFixe;
  // Personnel avec une casquette enseignante (rôle teacher/Enseignant) :
  // peut avoir DEUX salaires distincts (fixe Personnel + rémunération de
  // sa fiche Professeur liée) — le formulaire propose alors un choix.
  bool selectedHasLinkedProfesseur = false;
  double? selectedPersonnelSalaireFixe;

  List<CoursPayrollOption> coursOptions = [];
  bool isLoadingCoursOptions = false;

  double? heuresPointeesRef;
  bool isLoadingHeuresPointees = false;

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

  /// Résout le user_id sélectionné (dropdown employé, partagé avec Prêts)
  /// vers un Professeur OU un Personnel — determine si le formulaire doit
  /// passer en mode horaire (professeur uniquement) et pré-remplit le
  /// salaire fixe (les deux types de personnel peuvent en avoir un).
  Future<void> loadProfesseurInfo(String userId) async {
    isLoadingProfesseurInfo = true;
    selectedIsProfesseur = false;
    selectedProfesseurId = null;
    selectedTypePaiement = 'fixe';
    selectedSalaireFixe = null;
    selectedHasLinkedProfesseur = false;
    selectedPersonnelSalaireFixe = null;
    coursOptions = [];
    heuresPointeesRef = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('payroll/professeur-info', query: {'user_id': userId});
      final data = response.data as Map<String, dynamic>;
      selectedIsProfesseur = data['is_professeur'] == true;
      selectedSalaireFixe = (data['salaire_fixe'] as num?)?.toDouble();
      selectedHasLinkedProfesseur = data['has_linked_professeur'] == true;
      selectedPersonnelSalaireFixe = (data['personnel_salaire_fixe'] as num?)?.toDouble();
      if (selectedIsProfesseur) {
        selectedProfesseurId = data['professeur_id']?.toString();
        selectedTypePaiement = data['type_paiement']?.toString() ?? 'fixe';
      }
    } catch (_) {
      // Reste en mode fixe par défaut si la résolution échoue.
    } finally {
      isLoadingProfesseurInfo = false;
      notifyListeners();
    }
  }

  Future<void> loadCoursOptions({required String anneeAcademique}) async {
    if (selectedProfesseurId == null) return;
    isLoadingCoursOptions = true;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'professeur/$selectedProfesseurId/cours-payroll',
        query: {'annee_academique': anneeAcademique},
      );
      final data = response.data as Map<String, dynamic>;
      coursOptions = ((data['data'] as List?) ?? const [])
          .map((e) => CoursPayrollOption.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      coursOptions = [];
    } finally {
      isLoadingCoursOptions = false;
      notifyListeners();
    }
  }

  Future<void> loadHeuresPointees({required int mois, required int annee}) async {
    if (selectedProfesseurId == null) return;
    isLoadingHeuresPointees = true;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'professeur/$selectedProfesseurId/heures-pointees',
        query: {'mois': mois, 'annee': annee},
      );
      final data = response.data as Map<String, dynamic>;
      heuresPointeesRef = (data['total_heures'] as num?)?.toDouble();
    } catch (_) {
      heuresPointeesRef = null;
    } finally {
      isLoadingHeuresPointees = false;
      notifyListeners();
    }
  }

  Future<String?> create({
    required String userId,
    required String mois,
    required String annee,
    required String methodePaiement,
    required String typeCalcul,
    double? montant,
    List<Map<String, dynamic>>? detailsHoraires,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post(
        'payroll',
        data: {
          'user_id': userId,
          'mois': mois,
          'annee': annee,
          'methode_paiement': methodePaiement,
          'type_calcul': typeCalcul,
          if (montant != null) 'montant': montant,
          if (detailsHoraires != null) 'details_horaires': detailsHoraires,
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

  /// Versement (partiel ou intégral) contre un Payroll — mirror de
  /// LoanState.repay(). Remplace l'ancien markPaid()/POST .../pay.
  Future<String?> verser({
    required String payrollId,
    required double montant,
    required String methodePaiement,
    String? note,
  }) async {
    payingId = payrollId;
    notifyListeners();
    try {
      await _apiClient.post('payroll/$payrollId/verser', data: {
        'payroll_id': payrollId,
        'montant': montant,
        'methode_paiement': methodePaiement,
        if (note != null) 'note': note,
      });
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
