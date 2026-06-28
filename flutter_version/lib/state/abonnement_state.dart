import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

class AbonnementHistoriqueEntry {
  AbonnementHistoriqueEntry({
    required this.id,
    required this.dateActivation,
    required this.dateExpiration,
  });

  factory AbonnementHistoriqueEntry.fromJson(Map<String, dynamic> json) {
    return AbonnementHistoriqueEntry(
      id: json['id']?.toString() ?? '',
      dateActivation: json['date_activation']?.toString(),
      dateExpiration: json['date_expiration']?.toString(),
    );
  }

  final String id;
  final String? dateActivation;
  final String? dateExpiration;

  /// Équivalent de isEntryActif() (Abonnement.vue:77-85) : recalculé côté
  /// client à partir de la date d'expiration de CETTE entrée, pas d'un champ
  /// "actif" renvoyé par le serveur (qui n'existe que pour la dernière
  /// activation, cf. AbonnementState.actif).
  bool get actif {
    if (dateExpiration == null) return false;
    final expiration = DateTime.tryParse(dateExpiration!);
    if (expiration == null) return false;
    final today = DateTime.now();
    final t = DateTime(today.year, today.month, today.day);
    final e = DateTime(expiration.year, expiration.month, expiration.day);
    return !e.isBefore(t);
  }
}

/// Équivalent de GET v1/abonnement (ecole_nginx/app/Routes/dashboard.py:504-548)
/// — statut de la licence (table log_actives) + historique des activations.
/// Réservé aux admins côté serveur (403 sinon). Reproduit fidèlement
/// Abonnement.vue (ecole_nginx/frontend), seule page réellement routée pour
/// "Abonnement" — pas d'équivalent desktop direct (l'onglet du bureau est un
/// widget construit dynamiquement et non relié à une .ui, avec un bouton
/// "Renouveler" cantonné au flux de licence locale, hors périmètre ici).
class AbonnementState extends ChangeNotifier {
  AbonnementState(this._apiClient);

  final ApiClient _apiClient;

  bool isLoading = false;
  String? errorMessage;

  bool actif = false;
  String? cleActuelle;
  String? dateExpiration;
  int? joursRestants;
  List<AbonnementHistoriqueEntry> historique = [];

  Future<void> load() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('abonnement');
      final data = response.data as Map<String, dynamic>;
      actif = data['actif'] == true;
      cleActuelle = data['cle_actuelle']?.toString();
      dateExpiration = data['date_expiration']?.toString();
      joursRestants = (data['jours_restants'] as num?)?.toInt();
      historique = ((data['historique'] as List?) ?? const [])
          .map((e) => AbonnementHistoriqueEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      errorMessage = e is DioException
          ? (e.response?.data is Map ? (e.response?.data['detail']?.toString()) : null) ??
              "Impossible de récupérer les informations d'abonnement."
          : "Impossible de récupérer les informations d'abonnement.";
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
