import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

/// Valeurs valides de `Etudiant.aide_financiere` (voir Ajout_etudiant.vue /
/// etudiant_detail_screen.dart pour les mêmes 4 options).
const kAideFinanciereOptions = [
  'Aucune',
  '1/4 Bourse',
  'Démie Bourse',
  'Bourse',
];

class PromusEtudiant {
  PromusEtudiant({
    required this.id,
    required this.nom,
    required this.prenom,
    required this.note,
    required this.max,
    required this.moyenne,
    required this.status,
    required this.aideFinanciere,
  });

  factory PromusEtudiant.fromJson(Map<String, dynamic> json) {
    return PromusEtudiant(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      note: (json['note'] as num?)?.toDouble() ?? 0,
      max: (json['max'] as num?)?.toDouble() ?? 0,
      moyenne: json['moyenne']?.toString() ?? '0',
      status: json['status']?.toString() ?? '',
      aideFinanciere: json['aide_financiere']?.toString() ?? 'Aucune',
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final double note;
  final double max;
  final String moyenne;
  final String status;
  final String aideFinanciere;

  bool get succes => status == 'Succès';
}

/// Équivalent de promus_page()/rechercher_for_promus()/promus_to()
/// (school_client, Controllers/Main.py:11644-11852) → POST v1/get-promus +
/// POST v1/etudiant-promus-to (ecole_nginx/app/Routes/RPromus.py) — feature
/// 100% bureau, absente du frontend web (aucune route /promus dans
/// router/index.js).
class PromusState extends ChangeNotifier {
  PromusState(this._apiClient);

  final ApiClient _apiClient;

  bool isSearching = false;
  String? searchError;
  List<PromusEtudiant> resultats = [];
  bool _hasSearched = false;
  bool get hasSearched => _hasSearched;

  bool isPromoting = false;
  String? promoteError;
  Map<String, int>? lastStats;

  /// {etudiant_id: nouvelle_valeur} — UNIQUEMENT les étudiants dont l'aide
  /// financière a été changée dans le tableau (diff par rapport à la valeur
  /// d'origine reçue de [rechercher]), pas une copie complète de
  /// [resultats]. Vidé après une promotion réussie ou une nouvelle recherche.
  final Map<String, String> pendingAideFinanciere = {};

  /// Valeur affichée pour un étudiant : celle en attente de sauvegarde si
  /// modifiée, sinon la valeur d'origine reçue du serveur.
  String aideFinanciereFor(PromusEtudiant e) =>
      pendingAideFinanciere[e.id] ?? e.aideFinanciere;

  /// Change la valeur affichée pour un étudiant — retire l'entrée du diff
  /// plutôt que d'y stocker une valeur identique à l'originale, pour que
  /// [promouvoir] n'envoie jamais un "changement" qui n'en est pas un.
  void setAideFinanciere(PromusEtudiant e, String value) {
    if (value == e.aideFinanciere) {
      pendingAideFinanciere.remove(e.id);
    } else {
      pendingAideFinanciere[e.id] = value;
    }
    notifyListeners();
  }

  /// Équivalent de rechercher_for_promus() → POST v1/get-promus.
  Future<void> rechercher({
    required String annee,
    required String niveau,
    required String classe,
  }) async {
    isSearching = true;
    searchError = null;
    _hasSearched = true;
    resultats = [];
    pendingAideFinanciere.clear();
    notifyListeners();
    try {
      final response = await _apiClient.post(
        'get-promus',
        data: {
          'data': {
            'annee_academique_id': annee,
            'niveau_id': niveau,
            'classes_id': classe,
          },
        },
      );
      final data = response.data as Map<String, dynamic>;
      resultats = ((data['result'] as List?) ?? const [])
          .map((e) => PromusEtudiant.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      searchError = _extractError(e);
    } finally {
      isSearching = false;
      notifyListeners();
    }
  }

  /// Équivalent de promus_to() → POST v1/etudiant-promus-to. Les étudiants
  /// "Succès" rejoignent la classe future, les "Échec" redoublent dans la
  /// même classe (logique entièrement côté serveur, RPromus.py:494-513).
  Future<bool> promouvoir({
    required String anneeActuelle,
    required String niveauActuel,
    required String classeActuelle,
    required String anneeFuture,
    required String niveauFuture,
    required String classeFuture,
  }) async {
    isPromoting = true;
    promoteError = null;
    notifyListeners();
    try {
      final response = await _apiClient.post(
        'etudiant-promus-to',
        data: {
          'annee_academique_id': anneeActuelle,
          'niveau_id': niveauActuel,
          'classes_id': classeActuelle,
          'annee_academique_future': anneeFuture,
          'niveau_future': niveauFuture,
          'classe_future': classeFuture,
          // Copie défensive : pendingAideFinanciere est vidé juste après cet
          // appel (mutation du même objet), et mieux vaut ne jamais dépendre
          // de l'ordre exact sérialisation-puis-mutation du transport HTTP
          // sous-jacent pour la justesse d'une donnée financière.
          if (pendingAideFinanciere.isNotEmpty)
            'aide_financiere_updates': Map<String, String>.from(
              pendingAideFinanciere,
            ),
        },
      );
      final stats =
          (response.data as Map<String, dynamic>)['statistics']
              as Map<String, dynamic>?;
      lastStats = stats?.map((k, v) => MapEntry(k, (v as num).toInt()));
      pendingAideFinanciere.clear();
      return true;
    } catch (e) {
      promoteError = _extractError(e);
      return false;
    } finally {
      isPromoting = false;
      notifyListeners();
    }
  }

  void reset() {
    resultats = [];
    pendingAideFinanciere.clear();
    _hasSearched = false;
    searchError = null;
    lastStats = null;
    notifyListeners();
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] != null)
        return data['detail'].toString();
    }
    return 'Une erreur est survenue.';
  }
}
