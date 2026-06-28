import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/student.dart';
import '../models/student_detail.dart';

/// Équivalent de etudiant_page()/go_to_student_page()/sauvegarde_etudiant()/
/// delete_student() (Controllers/Main.py) — étendu, sur demande explicite
/// ("comme le web"), avec des fonctionnalités réelles propres au frontend
/// web (Etudiants.vue + Ajout_etudiant.vue, ecole_nginx/frontend) : bascule
/// actif/inactif, profil détaillé avec parcours académique/financier, et les
/// 2 impressions PDF (reçu d'inscription, fiche détaillée) — ces deux
/// dernières existent aussi côté school_client (AsyncDataHandler.py:826-830)
/// mais n'avaient encore aucun équivalent ici.
class StudentsState extends ChangeNotifier {
  StudentsState(this._apiClient);

  final ApiClient _apiClient;

  List<Student> students = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();

    try {
      final response = await _apiClient.get('etudiant', query: {
        'page': page,
        if (searchTerm.isNotEmpty) 'search': searchTerm,
      });
      final data = response.data as Map<String, dynamic>;
      students = ((data['data'] as List?) ?? const [])
          .map((e) => Student.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des étudiants.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Crée (sans id) ou modifie (avec id) un étudiant — même endpoint
  /// POST v1/etudiant des deux côtés (voir EtudiantSchema, Routes/Etudiants.py).
  Future<String?> save(Map<String, dynamic> payload) async {
    try {
      await _apiClient.post('etudiant', data: payload);
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  Future<String?> delete(String studentId) async {
    try {
      await _apiClient.dio.delete('etudiant/$studentId');
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  // ── Recherche en direct pour le Badge (distincte de la liste paginée) ──
  List<Student> liveSearchResults = [];
  bool isSearchingLive = false;

  /// Réutilise GET v1/etudiant?search=... (même endpoint que la liste), sans
  /// toucher à `students`/`currentPage` puisque cette recherche alimente un
  /// écran séparé (Badge).
  Future<void> searchLive(String query) async {
    if (query.trim().isEmpty) {
      liveSearchResults = [];
      notifyListeners();
      return;
    }
    isSearchingLive = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('etudiant', query: {'search': query, 'page': 1});
      final data = (response.data as Map<String, dynamic>)['data'] as List? ?? const [];
      liveSearchResults = data.map((e) => Student.fromJson(e as Map<String, dynamic>)).toList();
    } catch (_) {
      liveSearchResults = [];
    } finally {
      isSearchingLive = false;
      notifyListeners();
    }
  }

  // ── Photo du badge (generate_badge/generate_badge_and_save,
  // Controllers/Main.py:6114-6267) ────────────────────────────────────────
  bool isSavingBadgePhoto = false;

  /// Équivalent du payload envoyé par generate_badge(auto_save_image=True)
  /// → PATCH v1/save-badge-image : c'est la PHOTO de l'étudiant qui est
  /// synchronisée ici, pas le badge composé (avec QR/texte) — le badge
  /// complet ne reste que localement (PNG), exactement comme sur le bureau.
  Future<String?> saveBadgePhoto({required String studentId, required String photoBase64}) async {
    isSavingBadgePhoto = true;
    notifyListeners();
    try {
      await _apiClient.dio.patch('save-badge-image', data: {
        'etudiant_id': studentId,
        'image_base64': photoBase64,
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSavingBadgePhoto = false;
      notifyListeners();
    }
  }

  // ── Bascule actif/inactif (toggleStatus, Etudiants.vue) ────────────────
  String? activatingId;

  /// Équivalent de toggleStatus() → PATCH v1/active-etudiant. Absent de
  /// school_client. Renvoie le nouveau statut (true=actif) en cas de succès,
  /// ou null + message d'erreur sinon.
  Future<({bool? status, String? error})> toggleActive(String studentId) async {
    activatingId = studentId;
    notifyListeners();
    try {
      final response = await _apiClient.dio.patch('active-etudiant', data: {'id': studentId});
      final status = (response.data as Map<String, dynamic>)['status'];
      return (status: status is bool ? status : null, error: null);
    } catch (e) {
      return (status: null, error: _extractError(e));
    } finally {
      activatingId = null;
      notifyListeners();
    }
  }

  // ── Profil détaillé (onglet "Détails", Ajout_etudiant.vue) ─────────────
  StudentDetail? currentDetail;
  bool isLoadingDetail = false;
  String? detailError;

  /// Équivalent de fetchStudentDetails() → GET v1/etudiant/{id}.
  Future<void> loadDetail(String studentId) async {
    isLoadingDetail = true;
    detailError = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('etudiant/$studentId');
      final data = (response.data as Map<String, dynamic>)['data'] as Map<String, dynamic>;
      currentDetail = StudentDetail.fromJson(data);
    } catch (e) {
      detailError = 'Impossible de charger le profil de l’étudiant.';
    } finally {
      isLoadingDetail = false;
      notifyListeners();
    }
  }

  void clearDetail() {
    currentDetail = null;
    _parcoursCache.clear();
    notifyListeners();
  }

  // ── Parcours académique/financier par (classe, année) ──────────────────
  final Map<String, ParcoursDetails> _parcoursCache = {};
  String? loadingParcoursKey;

  /// Équivalent de toggleParcours() → POST v1/student-specific-details.
  Future<ParcoursDetails?> loadParcoursDetails({
    required String studentId,
    required String classeId,
    required String niveauId,
    required String anneeId,
  }) async {
    final key = '$classeId|$anneeId';
    final cached = _parcoursCache[key];
    if (cached != null) return cached;

    loadingParcoursKey = key;
    notifyListeners();
    try {
      final response = await _apiClient.post('student-specific-details', data: {
        'student_id': studentId,
        'classe_id': classeId,
        'niveau_id': niveauId,
        'annee_id': anneeId,
      });
      final details = ParcoursDetails.fromJson(response.data as Map<String, dynamic>);
      _parcoursCache[key] = details;
      return details;
    } catch (e) {
      return null;
    } finally {
      loadingParcoursKey = null;
      notifyListeners();
    }
  }

  // ── Impressions PDF (réelles côté school_client ET frontend web) ───────
  bool isPrintingRecu = false;
  bool isPrintingFiche = false;

  /// Équivalent de impression_fiche() / submitPdf('/print-recu-inscrit/...').
  Future<String?> printRecuInscription(String studentId) async {
    isPrintingRecu = true;
    notifyListeners();
    try {
      await _downloadAndOpen('print-recu-inscrit/$studentId', {}, 'recu_inscription_$studentId.pdf');
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isPrintingRecu = false;
      notifyListeners();
    }
  }

  /// Équivalent de student_print_details() (school_client,
  /// AsyncDataHandler.py:826-830) / submitPdf('/student-print-details', ...).
  Future<String?> printStudentDetails(String studentId) async {
    isPrintingFiche = true;
    notifyListeners();
    try {
      await _downloadAndOpen('student-print-details', {'student_id': studentId}, 'fiche_etudiant_$studentId.pdf');
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isPrintingFiche = false;
      notifyListeners();
    }
  }

  Future<void> _downloadAndOpen(String endpoint, Map<String, dynamic> data, String fileName) async {
    final response = await _apiClient.dio.post(
      endpoint,
      data: data,
      options: Options(responseType: ResponseType.bytes),
    );
    final file = File('${Directory.systemTemp.path}/$fileName');
    await file.writeAsBytes(response.data as List<int>);
    if (Platform.isMacOS) {
      await Process.run('open', [file.path]);
    } else if (Platform.isWindows) {
      await Process.run('cmd', ['/c', 'start', '', file.path]);
    } else if (Platform.isLinux) {
      await Process.run('xdg-open', [file.path]);
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
