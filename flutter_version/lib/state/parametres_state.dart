import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/parametres.dart';

/// Équivalent des fonctions CRUD de la page Paramètres (school_client:
/// settings_page(), Controllers/Main.py:13384 + Helper/Components/*.py) —
/// endpoints confirmés réels via Models/AsyncDataHandler.py ET
/// ecole_nginx/frontend/src/views/admin/Parametres.vue (seul fichier
/// vraiment routé, cf. router/index.js — pas les "*copy*.vue").
///
/// Suppression : les boutons "Supprimer" existent visuellement dans
/// Parametres.vue mais AUCUN n'est câblé (le switch `actionsOnClasse` ne
/// gère que les cas 'edit_*' ; les id 'delete_*' ne font rien) — donc aucune
/// méthode delete n'est exposée ici, fidèle au comportement réel.
class ParametresState extends ChangeNotifier {
  ParametresState(this._apiClient);

  final ApiClient _apiClient;

  // ── Années Académiques (v1/anneeAcademique) ──────────────────────────
  List<AnneeAcademiqueRecord> annees = [];
  int anneeCurrentPage = 1;
  int anneeLastPage = 1;
  bool anneeLoading = false;
  String? anneeError;
  bool anneeSubmitting = false;

  Future<void> loadAnnees({int page = 1}) async {
    anneeLoading = true;
    anneeError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('anneeAcademique', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      annees = ((data['data'] as List?) ?? const [])
          .map((e) => AnneeAcademiqueRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      anneeCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      anneeLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      anneeError = _extractError(e);
    } finally {
      anneeLoading = false;
      notifyListeners();
    }
  }

  Future<AnneeAcademiqueRecord?> fetchAnnee(String id) async {
    final response = await _apiClient.get('anneeAcademique/$id');
    final data = (response.data as Map<String, dynamic>)['data'];
    return data == null ? null : AnneeAcademiqueRecord.fromJson(data as Map<String, dynamic>);
  }

  Future<String?> submitAnnee({
    String? id,
    required String dateDebut,
    required String dateFin,
    required bool status,
  }) async {
    anneeSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('anneeAcademique', data: {
        'id': id,
        'date_debut': dateDebut,
        'date_fin': dateFin,
        'status': status,
      });
      await loadAnnees(page: anneeCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      anneeSubmitting = false;
      notifyListeners();
    }
  }

  // ── Classes (v1/classes) ──────────────────────────────────────────────
  List<ClasseRecord> classesList = [];
  int classeCurrentPage = 1;
  int classeLastPage = 1;
  bool classeLoading = false;
  String? classeError;
  bool classeSubmitting = false;

  Future<void> loadClasses({int page = 1}) async {
    classeLoading = true;
    classeError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('classes', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      classesList = ((data['data'] as List?) ?? const [])
          .map((e) => ClasseRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      classeCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      classeLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      classeError = _extractError(e);
    } finally {
      classeLoading = false;
      notifyListeners();
    }
  }

  Future<ClasseRecord?> fetchClasse(String id) async {
    final response = await _apiClient.get('classes/$id');
    final data = (response.data as Map<String, dynamic>)['data'];
    return data == null ? null : ClasseRecord.fromJson(data as Map<String, dynamic>);
  }

  Future<String?> submitClasse({String? id, required String niveauId, required String nomClasse}) async {
    classeSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('classes', data: {'id': id, 'niveau_id': niveauId, 'nom_classe': nomClasse});
      await loadClasses(page: classeCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      classeSubmitting = false;
      notifyListeners();
    }
  }

  // ── Facultés (v1/faculte, v1/post-faculte) — création seulement, pas ──
  // ── d'édition ni de suppression câblées côté Parametres.vue ──────────
  List<FaculteRecord> facultesList = [];
  int faculteCurrentPage = 1;
  int faculteLastPage = 1;
  bool faculteLoading = false;
  String? faculteError;
  bool faculteSubmitting = false;

  Future<void> loadFacultes({int page = 1}) async {
    faculteLoading = true;
    faculteError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('faculte', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      facultesList = ((data['data'] as List?) ?? const [])
          .map((e) => FaculteRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      faculteCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      faculteLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      faculteError = _extractError(e);
    } finally {
      faculteLoading = false;
      notifyListeners();
    }
  }

  Future<String?> submitFaculte({required String nom, required String nbAnnee}) async {
    faculteSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('post-faculte', data: {'nom': nom, 'nb_annee': nbAnnee});
      await loadFacultes(page: faculteCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      faculteSubmitting = false;
      notifyListeners();
    }
  }

  // ── Paramètres d'examen (v1/paramsExam) ───────────────────────────────
  List<ParamExamRecord> examensList = [];
  int examenCurrentPage = 1;
  int examenLastPage = 1;
  bool examenLoading = false;
  String? examenError;
  bool examenSubmitting = false;

  Future<void> loadExamens({int page = 1}) async {
    examenLoading = true;
    examenError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('paramsExam', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      examensList = ((data['data'] as List?) ?? const [])
          .map((e) => ParamExamRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      examenCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      examenLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      examenError = _extractError(e);
    } finally {
      examenLoading = false;
      notifyListeners();
    }
  }

  Future<ParamExamRecord?> fetchExamen(String id) async {
    final response = await _apiClient.get('paramsExam/$id');
    final data = (response.data as Map<String, dynamic>)['data'];
    return data == null ? null : ParamExamRecord.fromJson(data as Map<String, dynamic>);
  }

  Future<String?> submitExamen({
    String? id,
    required String niveauId,
    required String anneeAcademiqueId,
    required String evaluationPar,
  }) async {
    examenSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('paramsExam', data: {
        'id': id,
        'niveau_id': niveauId,
        'annee_academique_id': anneeAcademiqueId,
        'evaluation_par': evaluationPar,
      });
      await loadExamens(page: examenCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      examenSubmitting = false;
      notifyListeners();
    }
  }

  // ── Frais d'inscription (v1/fraisDinscription) — pas de pagination ───
  // ── affichée côté Parametres.vue (frais_paginate.value = res.data.data) ─
  List<FraisInscriptionRecord> fraisList = [];
  bool fraisLoading = false;
  String? fraisError;
  bool fraisSubmitting = false;

  Future<void> loadFrais() async {
    fraisLoading = true;
    fraisError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('fraisDinscription');
      final data = (response.data as Map<String, dynamic>)['data'];
      fraisList = ((data as List?) ?? const [])
          .map((e) => FraisInscriptionRecord.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      fraisError = _extractError(e);
    } finally {
      fraisLoading = false;
      notifyListeners();
    }
  }

  Future<String?> submitFrais({
    String? id,
    required String niveauId,
    required String anneeAc,
    required num prix,
  }) async {
    fraisSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('fraisDinscription', data: {
        'id': id,
        'prix': prix,
        'niveau_id': niveauId,
        'anneeAc': anneeAc,
      });
      await loadFrais();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      fraisSubmitting = false;
      notifyListeners();
    }
  }

  // ── Frais Divers (v1/frais-divers-index|store) — feature 100% bureau,
  // absente de Parametres.vue (Helper/Components/Frais_divers.py). Paginée,
  // contrairement à "Frais d'inscription" ci-dessus.
  List<FraisDiversRecord> fraisDiversList = [];
  int fraisDiversCurrentPage = 1;
  int fraisDiversLastPage = 1;
  bool fraisDiversLoading = false;
  String? fraisDiversError;
  bool fraisDiversSubmitting = false;

  Future<void> loadFraisDivers({int page = 1}) async {
    fraisDiversLoading = true;
    fraisDiversError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('frais-divers-index', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      fraisDiversList = ((data['data'] as List?) ?? const [])
          .map((e) => FraisDiversRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      fraisDiversCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      fraisDiversLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      fraisDiversError = _extractError(e);
    } finally {
      fraisDiversLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de Frais_divers.enregistrer() : `description` est envoyée
  /// mais ne sera jamais relue (voir FraisDiversRecord) — comportement réel
  /// reproduit tel quel, pas "corrigé".
  Future<String?> submitFraisDivers({
    String? id,
    required String niveauId,
    required String anneeAc,
    required num prix,
    required String description,
  }) async {
    fraisDiversSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('frais-divers-store', data: {
        'id': id,
        'description': description,
        'prix': prix,
        'niveau_id': niveauId,
        'anneeAc': anneeAc,
      });
      await loadFraisDivers(page: fraisDiversCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      fraisDiversSubmitting = false;
      notifyListeners();
    }
  }

  // ── Paramètres de paiement (v1/parametrePaiement) ─────────────────────
  List<ParametrePaiementRecord> paiementParamsList = [];
  int paiementParamCurrentPage = 1;
  int paiementParamLastPage = 1;
  bool paiementParamLoading = false;
  String? paiementParamError;
  bool paiementParamSubmitting = false;

  Future<void> loadPaiementParams({int page = 1}) async {
    paiementParamLoading = true;
    paiementParamError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('parametrePaiement', query: {'page': page});
      final data = response.data as Map<String, dynamic>;
      paiementParamsList = ((data['data'] as List?) ?? const [])
          .map((e) => ParametrePaiementRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      paiementParamCurrentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      paiementParamLastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      paiementParamError = _extractError(e);
    } finally {
      paiementParamLoading = false;
      notifyListeners();
    }
  }

  Future<ParametrePaiementRecord?> fetchPaiementParam(String id) async {
    final response = await _apiClient.get('parametrePaiement/$id');
    final data = (response.data as Map<String, dynamic>)['data'];
    return data == null ? null : ParametrePaiementRecord.fromJson(data as Map<String, dynamic>);
  }

  /// Équivalent de submitPaymentParams() (Parametres.vue:250-259), payload
  /// identique à ParamPaiementSchema (RPaiementParam.py:346-356) — le
  /// serveur lui-même imbrique `montant_par` sous la clé `echeance`
  /// (RPaiementParam.py:582), le client envoie une map PLATE.
  Future<String?> submitPaiementParam({
    String? id,
    required String niveauId,
    String? faculteId,
    required String classeId,
    required String echeance,
    required String devise,
    required String anneeAcademiqueId,
    int? nbEcheance,
    num? montant,
    required Map<String, num> montantPar,
    required List<AccessoireConfig> accessoires,
  }) async {
    paiementParamSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('parametrePaiement', data: {
        'id': id,
        'niveau_id': niveauId,
        'faculte_id': faculteId,
        'classe': classeId,
        'echeance': echeance,
        'devise': devise,
        'anneeAcademique': anneeAcademiqueId,
        'nb_echeance': nbEcheance,
        'montant': montant,
        'montant_par': montantPar,
        'accessoires': accessoires.map((a) => a.toJson()).toList(),
      });
      await loadPaiementParams(page: paiementParamCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      paiementParamSubmitting = false;
      notifyListeners();
    }
  }

  // ── Méthodes de suppression ────────────────────────────────────────────
  // Les boutons "Supprimer" étaient visuellement présents dans Parametres.vue
  // mais non câblés ; on tente les endpoints REST standard DELETE /{resource}/{id}.

  Future<String?> deleteExamen(String id) async {
    try {
      await _apiClient.delete('paramsExam/$id');
      await loadExamens(page: examenCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deleteFaculte(String id) async {
    try {
      await _apiClient.delete('faculte/$id');
      await loadFacultes(page: faculteCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deleteAnnee(String id) async {
    try {
      await _apiClient.delete('anneeAcademique/$id');
      await loadAnnees(page: anneeCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deleteClasse(String id) async {
    try {
      await _apiClient.delete('classes/$id');
      await loadClasses(page: classeCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deleteFrais(String id) async {
    try {
      await _apiClient.delete('fraisDinscription/$id');
      await loadFrais();
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deleteFraisDivers(String id) async {
    try {
      await _apiClient.delete('frais-divers/$id');
      await loadFraisDivers(page: fraisDiversCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> deletePaiementParam(String id) async {
    try {
      await _apiClient.delete('parametrePaiement/$id');
      await loadPaiementParams(page: paiementParamCurrentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map) {
        if (data['detail'] != null) return data['detail'].toString();
        if (data['errors'] is Map) {
          final errors = (data['errors'] as Map).values.expand((v) {
            return v is List ? v : [v];
          }).join('\n');
          if (errors.isNotEmpty) return errors;
        }
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
