import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

const _infiniBaUrl = 'https://infini-software.cloud';

class AbonnementHistoriqueEntry {
  AbonnementHistoriqueEntry({
    required this.id,
    required this.dateActivation,
    required this.dateExpiration,
    required this.nouvelleCle,
  });

  factory AbonnementHistoriqueEntry.fromJson(Map<String, dynamic> json) {
    return AbonnementHistoriqueEntry(
      id: json['id']?.toString() ?? '',
      dateActivation: json['date_activation']?.toString(),
      dateExpiration: json['date_expiration']?.toString(),
      nouvelleCle: json['nouvelle_cle']?.toString(),
    );
  }

  final String id;
  final String? dateActivation;
  final String? dateExpiration;
  /// Clé de licence appliquée à cette activation (LogActive.new_key côté
  /// ecole_nginx) — c'est le seul identifiant commun avec infini-software,
  /// qui n'a jamais connaissance des id locaux : voir printRecu() ci-dessous.
  final String? nouvelleCle;

  /// Équivalent de isEntryActif() (Abonnement.vue:77-85).
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

/// Équivalent de la page Abonnement dans school_client (Controllers/Main.py:
/// 4245-4311, LicenceSyncWorker:154-192) : affiche le statut de la licence,
/// expose le lien de renouvellement infini-software, et synchronise
/// automatiquement une nouvelle clé via GET /api/licence/derniere-cle (modèle
/// "pull" — infini-software ne peut pas appeler directement le serveur).
class AbonnementState extends ChangeNotifier {
  AbonnementState(this._apiClient);

  final ApiClient _apiClient;

  bool isLoading = false;
  String? errorMessage;

  /// True une fois que load() a réussi au moins une fois — avant ça on ne
  /// bloque pas les impressions (on assume la licence active par défaut,
  /// comme school_client qui n'a pas encore vérifié la clé).
  bool isKnown = false;

  bool actif = false;
  String? cleActuelle;
  String? dateExpiration;
  int? joursRestants;
  String? mac;
  List<AbonnementHistoriqueEntry> historique = [];

  bool isSyncing = false;
  String? syncMessage;

  /// id (AbonnementHistoriqueEntry.id) de la ligne dont le reçu est en cours
  /// de téléchargement — permet de désactiver seulement le bouton de cette
  /// ligne pendant l'opération, comme printingKey dans PaiementState.
  String? printingRecuId;

  /// URL de renouvellement infini-software, pré-remplie avec le mac du serveur.
  /// Équivalent de _ouvrir_renouvellement() (Main.py:4286-4295).
  /// Null si le mac n'a pas encore été chargé.
  String? get renewalUrl => mac != null ? '$_infiniBaUrl/renouveler?mac=${Uri.encodeComponent(mac!)}' : null;

  /// Visible quand jours_restants <= 15 ou quand expiré — même logique que
  /// btn_abonnement_renouveler.setVisible() (Main.py:4311).
  bool get showRenewButton => joursRestants != null && joursRestants! <= 15;

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
      mac = data['mac']?.toString();
      historique = ((data['historique'] as List?) ?? const [])
          .map((e) => AbonnementHistoriqueEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      isKnown = true;
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

  /// Équivalent de LicenceSyncWorker (Main.py:154-192) : interroge
  /// infini-software pour savoir si une clé plus récente existe, et si oui
  /// l'applique via POST /api/v1/licence/appliquer.
  Future<String?> syncFromInfini() async {
    if (mac == null) return 'Adresse MAC du serveur introuvable.';
    isSyncing = true;
    syncMessage = null;
    notifyListeners();
    try {
      final infiniDio = Dio();
      final r = await infiniDio.get(
        '$_infiniBaUrl/api/licence/derniere-cle',
        queryParameters: {'mac': mac},
        options: Options(sendTimeout: const Duration(seconds: 5), receiveTimeout: const Duration(seconds: 5)),
      );
      final data = r.data as Map<String, dynamic>?;
      final newKey = data?['key']?.toString();
      final expirationDate = data?['expiration_date']?.toString();
      final daysValid = (data?['days_valid'] as num?)?.toInt();
      if (newKey == null || expirationDate == null) {
        syncMessage = 'Aucune clé disponible sur infini-software.';
        notifyListeners();
        return syncMessage;
      }
      if (newKey == cleActuelle) {
        syncMessage = 'Clé déjà à jour.';
        notifyListeners();
        return null;
      }
      await _apiClient.post('licence/appliquer', data: {
        'new_key': newKey,
        'expiration_date': expirationDate,
        'days_valid': daysValid,
      });
      await load();
      syncMessage = null;
      return null;
    } on DioException catch (e) {
      final isExternal = e.requestOptions.uri.host.contains('infini-software');
      final msg = isExternal
          ? 'Impossible de joindre infini-software.cloud.'
          : (e.response?.data is Map ? e.response?.data['detail']?.toString() : null) ??
              'Erreur lors de l\'application de la clé.';
      syncMessage = msg;
      notifyListeners();
      return msg;
    } catch (_) {
      syncMessage = 'Erreur inattendue lors de la synchronisation.';
      notifyListeners();
      return syncMessage;
    } finally {
      isSyncing = false;
      notifyListeners();
    }
  }

  /// Télécharge le reçu PDF d'une activation d'abonnement (GET
  /// infini-software.cloud/api/licence/recu, identifié par mac + clé — les
  /// seules infos communes aux deux systèmes, voir nouvelleCle ci-dessus) et
  /// l'ouvre avec le lecteur par défaut du système, comme printRecu()
  /// (PaiementState) pour les reçus de paiement scolaire.
  Future<String?> printRecu(AbonnementHistoriqueEntry entry) async {
    if (mac == null) return 'Adresse MAC du serveur introuvable.';
    if (entry.nouvelleCle == null) return 'Aucune clé associée à cette activation.';
    printingRecuId = entry.id;
    notifyListeners();
    try {
      final infiniDio = Dio();
      final response = await infiniDio.get(
        '$_infiniBaUrl/api/licence/recu',
        queryParameters: {'mac': mac, 'key': entry.nouvelleCle},
        options: Options(responseType: ResponseType.bytes),
      );
      final file = File('${Directory.systemTemp.path}/recu_abonnement_${entry.id}.pdf');
      await file.writeAsBytes(response.data as List<int>);
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
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return 'Aucun reçu disponible pour cette activation.';
      }
      return 'Impossible de joindre infini-software.cloud.';
    } catch (_) {
      return 'Erreur inattendue lors du téléchargement du reçu.';
    } finally {
      printingRecuId = null;
      notifyListeners();
    }
  }
}
