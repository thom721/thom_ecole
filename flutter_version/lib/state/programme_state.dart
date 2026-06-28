import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/programme.dart';

/// Équivalent de programme_index()/enregistrer_programme()/delete_programme()
/// (school_client, Controllers/Main.py:9714-10227), aligné sur le vrai
/// contrat backend (RProgramme.py) :
/// - GET v1/programme?page&search&niveau_id&class_id&annee_academique_id&
///   faculte_id → liste paginée.
/// - POST v1/programme avec {"programmeCoursObject": [...]} (toujours une
///   LISTE, comme pour /cours).
/// - GET v1/delete-programme/{id} pour la suppression (pas DELETE).
class ProgrammeState extends ChangeNotifier {
  ProgrammeState(this._apiClient);

  final ApiClient _apiClient;

  List<Programme> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  String? niveauFilter;
  String? classeFilter;
  String? anneeFilter;
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? deletingId;

  List<ProfesseurCombo> professeurs = [];
  List<CoursCombo> cours = [];
  bool isLoadingCombos = false;

  Future<void> loadCombos() async {
    if (professeurs.isNotEmpty && cours.isNotEmpty) return;
    isLoadingCombos = true;
    notifyListeners();
    try {
      final results = await Future.wait([
        _apiClient.get('prof-for-combo'),
        _apiClient.get('for-combo-cours'),
      ]);
      professeurs = ((results[0].data['prof'] as List?) ?? const [])
          .map((e) => ProfesseurCombo.fromJson(e as Map<String, dynamic>))
          .toList();
      cours = ((results[1].data['cours'] as List?) ?? const [])
          .map((e) => CoursCombo.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      // Listes vides en cas d'échec : le formulaire affichera simplement
      // des menus déroulants vides plutôt que de planter.
    } finally {
      isLoadingCombos = false;
      notifyListeners();
    }
  }

  Future<void> load({
    int page = 1,
    String? search,
    String? niveauId,
    String? classeId,
    String? anneeId,
  }) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    if (niveauId != null) niveauFilter = niveauId.isEmpty ? null : niveauId;
    if (classeId != null) classeFilter = classeId.isEmpty ? null : classeId;
    if (anneeId != null) anneeFilter = anneeId.isEmpty ? null : anneeId;
    notifyListeners();

    try {
      final response = await _apiClient.get('programme', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
        if (niveauFilter != null) 'niveau_id': niveauFilter,
        if (classeFilter != null) 'class_id': classeFilter,
        if (anneeFilter != null) 'annee_academique_id': anneeFilter,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => Programme.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des programmes.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de enregistrer_programme() (Main.py:10058-10082) → POST
  /// v1/programme, {"programmeCoursObject": [...]} — TOUJOURS un lot,
  /// même pour une seule ligne (self.programme_dictionary y compris pour 1
  /// élément) ; chaque item peut créer (id absent) ou modifier (id
  /// présent) — un même envoi peut mélanger les deux. `item` utilise les
  /// clés requête (`cours_id`, `class`), pas les alias de réponse
  /// (`Cours_id`, `class_`).
  Future<String?> save(List<Map<String, dynamic>> items) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('programme', data: {'programmeCoursObject': items});
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> delete(String programmeId) async {
    deletingId = programmeId;
    notifyListeners();
    try {
      await _apiClient.dio.get('delete-programme/$programmeId');
      await load(page: currentPage);
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
