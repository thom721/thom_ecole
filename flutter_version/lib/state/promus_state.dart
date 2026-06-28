import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

class PromusEtudiant {
  PromusEtudiant({
    required this.id,
    required this.nom,
    required this.prenom,
    required this.note,
    required this.max,
    required this.moyenne,
    required this.status,
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
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final double note;
  final double max;
  final String moyenne;
  final String status;

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

  /// Équivalent de rechercher_for_promus() → POST v1/get-promus.
  Future<void> rechercher({required String annee, required String niveau, required String classe}) async {
    isSearching = true;
    searchError = null;
    _hasSearched = true;
    resultats = [];
    notifyListeners();
    try {
      final response = await _apiClient.post('get-promus', data: {
        'data': {
          'annee_academique_id': annee,
          'niveau_id': niveau,
          'classes_id': classe,
        },
      });
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
      final response = await _apiClient.post('etudiant-promus-to', data: {
        'annee_academique_id': anneeActuelle,
        'niveau_id': niveauActuel,
        'classes_id': classeActuelle,
        'annee_academique_future': anneeFuture,
        'niveau_future': niveauFuture,
        'classe_future': classeFuture,
      });
      final stats = (response.data as Map<String, dynamic>)['statistics'] as Map<String, dynamic>?;
      lastStats = stats?.map((k, v) => MapEntry(k, (v as num).toInt()));
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
    _hasSearched = false;
    searchError = null;
    lastStats = null;
    notifyListeners();
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] != null) return data['detail'].toString();
    }
    return 'Une erreur est survenue.';
  }
}
