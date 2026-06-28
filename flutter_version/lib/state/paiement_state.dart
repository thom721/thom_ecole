import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../core/dual_auth.dart';
import '../models/paiement.dart';
import '../models/student.dart';

/// Équivalent de paiement_page()/go_to_paiement_page()/valider_paiement()
/// (Controllers/Main.py, school_client) : liste des paiements, recherche
/// d'étudiant en direct, contexte de paiement (GET v1/next-payment-step) et
/// enregistrement d'un versement (POST v1/post-payment-save).
class PaiementState extends ChangeNotifier {
  PaiementState(this._apiClient);

  final ApiClient _apiClient;

  List<PaymentListItem> payments = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;

  List<Student> liveSearchResults = [];
  bool isSearching = false;

  /// Toutes les années académiques de l'étudiant (une entrée par
  /// classes_etudiants/etudiant_facultes), pas seulement l'année active —
  /// affichées dans la colonne de gauche du formulaire (PaymentByComponents.vue).
  List<StudentPaymentContext> studentYears = [];
  int? selectedYearIndex;

  PaymentInfo? currentInfo;
  bool isLoadingInfo = false;
  String? infoError;

  PaymentDetail? currentDetail;
  bool isLoadingDetail = false;
  String? detailError;
  String? returningKey;
  String? printingKey;

  Future<void> loadList({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();

    try {
      final response = await _apiClient.get(
        'paiement',
        query: {'page': page, if (searchTerm.isNotEmpty) 'search': searchTerm},
      );
      final data = response.data as Map<String, dynamic>;
      payments = ((data['data'] as List?) ?? const [])
          .map((e) => PaymentListItem.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des paiements.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de fetchStudent() (Paiements.vue / Controllers/Main.py) :
  /// recherche en direct via POST v1/live-student.
  Future<void> searchStudents(String query) async {
    if (query.trim().length < 2) {
      liveSearchResults = [];
      notifyListeners();
      return;
    }
    isSearching = true;
    notifyListeners();
    try {
      final response = await _apiClient.post(
        'live-student',
        data: {'val': query},
      );
      final data = response.data as Map<String, dynamic>;
      liveSearchResults = ((data['data'] as List?) ?? const [])
          .map((e) => Student.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      liveSearchResults = [];
    } finally {
      isSearching = false;
      notifyListeners();
    }
  }

  void clearSearch() {
    liveSearchResults = [];
    notifyListeners();
  }

  /// Équivalent de loadData() (PaymentByComponents.vue) : récupère TOUTES
  /// les années académiques de l'étudiant (pas seulement l'active — un
  /// élève peut avoir des arriérés sur une année passée), affichées en
  /// colonne de gauche, puis sélectionne par défaut la plus récente (le
  /// backend les renvoie triées par date_debut croissante depuis
  /// RPaiement.py — donc le dernier élément), exactement comme le web
  /// (`data[data.length - 1]`).
  Future<String?> loadPaymentInfo(String etudiantId) async {
    isLoadingInfo = true;
    infoError = null;
    currentInfo = null;
    studentYears = [];
    selectedYearIndex = null;
    notifyListeners();

    try {
      final contextResponse = await _apiClient.get(
        'fetch-data-with-payment-params/$etudiantId',
      );
      final contextData =
          (contextResponse.data as Map<String, dynamic>)['data'] as List?;
      if (contextData == null || contextData.isEmpty) {
        infoError = "Aucune classe active trouvée pour cet étudiant.";
        return infoError;
      }
      studentYears = contextData
          .map((e) => StudentPaymentContext.fromJson(e as Map<String, dynamic>))
          .toList();
      return await selectYear(studentYears.length - 1);
    } catch (e) {
      infoError = _extractError(e);
      return infoError;
    } finally {
      isLoadingInfo = false;
      notifyListeners();
    }
  }

  /// Équivalent de showInfoToPay() (PaymentByComponents.vue) : recharge
  /// GET v1/next-payment-step pour l'année académique sélectionnée dans la
  /// colonne de gauche (chaque année est un vrai aller-retour serveur, pas
  /// un simple filtrage côté client de données déjà en mémoire).
  Future<String?> selectYear(int index) async {
    if (index < 0 || index >= studentYears.length) return null;
    final ctx = studentYears[index];
    selectedYearIndex = index;
    isLoadingInfo = true;
    infoError = null;
    currentInfo = null;
    notifyListeners();

    try {
      // GET v1/next-payment-step attend annee_academique au format
      // "YYYY-YYYY" (Routes/RPaiement.py:165 : annee_academique.split('-')),
      // alors que AnneeAcademique.annee_academique est stocké "YYYY/YYYY".
      final anneeDash = ctx.anneeAcademique.replaceAll('/', '-');

      final infoResponse = await _apiClient.get(
        'next-payment-step',
        query: {
          'etudiant': ctx.studentId,
          'annee_academique': anneeDash,
          'classe': ctx.classeId,
          'niveau': ctx.niveauId,
          'annee_a': ctx.anneeId,
          if (ctx.faculteId != null) 'faculte': ctx.faculteId,
        },
      );
      final infoData = (infoResponse.data as Map<String, dynamic>)['data'];
      if (infoData == null) {
        infoError = "Paramètres de paiement non configurés pour cette classe.";
        return infoError;
      }
      currentInfo = PaymentInfo.fromJson(infoData as Map<String, dynamic>);
      return null;
    } catch (e) {
      infoError = _extractError(e);
      return infoError;
    } finally {
      isLoadingInfo = false;
      notifyListeners();
    }
  }

  /// Équivalent de GET /paiement/{id} (Routes/RPaiement.py:307) : le dossier
  /// complet d'un paiement déjà enregistré (récapitulatif + historique),
  /// affiché par l'écran "Détail du paiement" (équivalent de
  /// DetaisPaiement.vue).
  Future<void> loadDetail(String paiementId) async {
    isLoadingDetail = true;
    detailError = null;
    currentDetail = null;
    notifyListeners();

    try {
      final response = await _apiClient.get('paiement/$paiementId');
      final data = (response.data as Map<String, dynamic>)['show_paiement'];
      currentDetail = PaymentDetail.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      detailError = _extractError(e);
    } finally {
      isLoadingDetail = false;
      notifyListeners();
    }
  }

  /// Équivalent de retournerPaiement() (DetaisPaiement.vue:223-280) : marque
  /// la dernière transaction non retournée comme "retourné" via POST
  /// /delete-paiement (Routes/Returns.py:177, soumis à double-autorisation
  /// — DualAuthChecker, pas de restriction de rôle côté serveur : un 202
  /// signifie que l'utilisateur courant n'a pas la permission "Supprimer
  /// paiement" et doit faire approuver l'action via un PIN admin/Comptable,
  /// voir lib/core/dual_auth.dart).
  Future<String?> returnPaiement(
    String paiementId,
    String dateKey, {
    required String raison,
    String? approvalToken,
  }) async {
    returningKey = dateKey;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'delete-paiement',
        data: {'id': paiementId, 'index': dateKey, 'raison': raison},
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      // Dio ne lève jamais d'exception pour un 202 (2xx = succès par défaut,
      // voir _defaultValidateStatus) : DualAuthChecker doit donc être
      // détecté ici, sur la réponse, pas dans le catch ci-dessous.
      if (response.statusCode == 202) return kApprovalRequiredError;
      await loadDetail(paiementId);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      returningKey = null;
      notifyListeners();
    }
  }

  /// Équivalent de printRecu() (DetaisPaiement.vue:182-198) : télécharge le
  /// PDF du reçu via POST /print-recu puis l'ouvre avec le lecteur par
  /// défaut du système (pas de visionneuse PDF intégrée à l'app).
  Future<String?> printRecu(String paiementId, String key) async {
    printingKey = key;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'print-recu',
        data: {'id': paiementId, 'key': key},
        options: Options(responseType: ResponseType.bytes),
      );
      final file = File(
        '${Directory.systemTemp.path}/recu_${paiementId}_$key.pdf',
      );
      await file.writeAsBytes(response.data as List<int>);
      // Process.run() ne lève pas d'exception sur un exit code non nul —
      // sans cette vérification, un échec de l'ouverture du PDF (lecteur
      // par défaut absent, chemin refusé...) passait pour un succès muet.
      ProcessResult result;
      if (Platform.isMacOS) {
        result = await Process.run('open', [file.path]);
      } else if (Platform.isWindows) {
        result = await Process.run('cmd', ['/c', 'start', '', file.path]);
      } else {
        result = await Process.run('xdg-open', [file.path]);
      }
      if (result.exitCode != 0) {
        return 'Impossible d\'ouvrir le reçu : ${result.stderr}'.trim();
      }
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      printingKey = null;
      notifyListeners();
    }
  }

  /// Équivalent de valider_paiement() (Controllers/Main.py:13090-13094) :
  /// construit le même payload que enregistrer_paiement()
  /// (Models/AsyncDataHandler.py:276-301) et appelle POST
  /// v1/post-payment-save.
  Future<String?> submitPayment({
    required double montantVerse,
    required Map<String, bool> moisCoches,
    required Map<String, bool> accessoiresCoches,
  }) async {
    final info = currentInfo;
    if (info == null) return 'Aucun contexte de paiement chargé.';

    try {
      final response = await _apiClient.post(
        'post-payment-save',
        data: {
          'niveau_id': info.niveauId,
          'etudiant_id': info.studentId,
          'identifiant': info.identifiant,
          'classe': info.classeId,
          'echeance': info.echeance,
          'prenom': info.prenom,
          'nom': info.nom,
          'annee_academique': info.anneeAcademique,
          'devise': info.devise,
          'index_paiement': null,
          'must_refresh_paiement': false,
          'paiement_details': {
            'depot': montantVerse,
            'depot_et_avance': null,
            'montant': null,
            'status': 0,
            'total_verse': 0,
            'total_annuel': 0,
            'devise': 0,
            'employer': '',
            'balance': null,
            'avance': null,
          },
          'mois': moisCoches,
          'accessoires': accessoiresCoches,
        },
      );
      final data = response.data as Map<String, dynamic>?;
      // Recharge la même année (pas forcément la plus récente — un élève
      // peut être en train de régler un arriéré d'une année passée) pour
      // refléter le nouveau solde/historique, sans changer la sélection.
      await selectYear(selectedYearIndex ?? studentYears.length - 1);
      if (data != null) {
        _lastReceiptId = data['id']?.toString();
        _lastReceiptKey = (data['keys'] as num?)?.toInt();
      }
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  String? _lastReceiptId;
  int? _lastReceiptKey;
  String? get lastReceiptId => _lastReceiptId;
  int? get lastReceiptKey => _lastReceiptKey;

  String _extractError(Object e) {
    if (e is DioException) {
      var data = e.response?.data;
      // Les requêtes en `responseType: ResponseType.bytes` (printRecu)
      // reçoivent TOUJOURS des octets bruts, même sur une erreur — sans ce
      // décodage, le vrai message JSON du serveur (403, 404, 500...) était
      // masqué et remplacé par le message générique "Impossible de
      // contacter le serveur.", qui s'affichait donc même quand le serveur
      // avait répondu normalement avec un detail explicite.
      if (data is List<int>) {
        try {
          data = jsonDecode(utf8.decode(data));
        } catch (_) {
          // corps non-JSON (vrai PDF tronqué, page HTML d'erreur...) : on
          // garde les octets bruts, le fallback générique s'appliquera.
        }
      }
      if (data is Map) {
        if (data['detail'] != null) return data['detail'].toString();
        if (data['errors'] is Map) {
          final errors = (data['errors'] as Map).values
              .expand((v) {
                return v is List ? v : [v];
              })
              .join('\n');
          if (errors.isNotEmpty) return errors;
        }
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
