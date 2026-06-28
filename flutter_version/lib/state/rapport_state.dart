import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

/// Équivalent de la section RAPPORT de Controllers/Main.py (school_client) :
/// print_global_report(), administratif_imprimer(), pedagogique_imprimer(),
/// print_desicion_de_fin_dannee[_excel](), financier_imprimer() — chacune
/// poste un filtre JSON vers un endpoint `print-*` qui renvoie un PDF/Excel
/// en flux binaire (cf. Models/AsyncDataHandler.py:769-824). Pas de
/// visionneuse intégrée côté bureau : on télécharge dans un fichier
/// temporaire puis on l'ouvre avec l'application par défaut du système,
/// comme PaiementState.printRecu().
///
/// Volontairement absents/limités (non présents dans school_client, confirmé
/// via Controllers/Main.py + Models/AsyncDataHandler.py + grep exhaustif sur
/// ecole_nginx) :
/// - "Disciplinaire" : aucune route/modèle/schéma backend nulle part — pure
///   carte "Bientôt" côté frontend web, reprise à l'identique côté UI.
/// - "Présence" : pas de PDF (le bouton web appelle print-present-repport,
///   qui n'existe nulle part) — seul l'export Excel (export-excel-presence,
///   RExcelExport.py) est une route réelle, donc seule celle-ci est exposée.
/// - Export Excel pour Global/Administratif/Pédagogique/Financier : le
///   bureau n'a aucun bouton ni méthode pour ces exports (seules les routes
///   web /export-excel-* existent, jamais appelées par l'app de bureau).
/// - Bouton "Format Excel" du rapport Pédagogique : appelle
///   v1/print-repport-pedagogique-exel, qui n'existe nulle part dans
///   ecole_nginx/app/Routes — bouton mort côté bureau, donc omis ici.
class RapportState extends ChangeNotifier {
  RapportState(this._apiClient);

  final ApiClient _apiClient;

  bool isPrintingGlobal = false;
  bool isPrintingAdministratif = false;
  bool isPrintingPedagogique = false;
  bool isPrintingDecision = false;
  bool isPrintingFinancier = false;
  bool isPrintingPresence = false;

  /// Équivalent de print_global_report() → POST v1/print-global-repport.
  Future<String?> printGlobalReport({
    required String type,
    required DateTime dateDebut,
    required DateTime dateFin,
  }) {
    isPrintingGlobal = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'print-global-repport',
      data: {
        'date_debut': _formatDate(dateDebut),
        'date_fin': _formatDate(dateFin),
        'type': type,
      },
      fileName: 'rapport_global.pdf',
    ).whenComplete(() {
      isPrintingGlobal = false;
      notifyListeners();
    });
  }

  /// Équivalent de administratif_imprimer() → POST v1/print-repport-register.
  Future<String?> printAdministratifReport({
    required bool identifiant,
    required String classe,
    required String anneeAc,
    required String cycle,
  }) {
    isPrintingAdministratif = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'print-repport-register',
      data: {
        'identifiant': identifiant,
        'classe': classe,
        'annee_ac': anneeAc,
        'cycle': cycle,
      },
      fileName: 'rapport_administratif.pdf',
    ).whenComplete(() {
      isPrintingAdministratif = false;
      notifyListeners();
    });
  }

  /// Équivalent de pedagogique_imprimer() → POST v1/print-repport-pedagogique.
  Future<String?> printPedagogiqueReport({
    required bool identifiant,
    required String classe,
    required String anneeAc,
    required String cycle,
    required String mois,
  }) {
    isPrintingPedagogique = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'print-repport-pedagogique',
      data: {
        'identifiant': identifiant,
        'classe': classe,
        'annee_ac': anneeAc,
        'cycle': cycle,
        'mois': mois,
      },
      fileName: 'rapport_pedagogique.pdf',
    ).whenComplete(() {
      isPrintingPedagogique = false;
      notifyListeners();
    });
  }

  /// Équivalent de print_desicion_de_fin_dannee[_excel]() → POST
  /// v1/print-repport-decision (même endpoint, `is_excel` choisit le format).
  Future<String?> printDecisionFinAnnee({
    required String classe,
    required String anneeAc,
    required bool isExcel,
  }) {
    isPrintingDecision = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'print-repport-decision',
      data: {
        'classe': classe,
        'annee_ac': anneeAc,
        'is_excel': isExcel,
      },
      fileName: isExcel ? 'decision_fin_annee.xlsx' : 'decision_fin_annee.pdf',
    ).whenComplete(() {
      isPrintingDecision = false;
      notifyListeners();
    });
  }

  /// Équivalent de financier_imprimer() → POST v1/print-rapport-paiement.
  /// `anneeAcademiqueId` est transmis dans le champ `date_debut` : le
  /// bureau réutilise ce champ pour l'UUID de l'année académique active
  /// plutôt que pour une vraie date (PaymentRepport.py résout
  /// AnneeAcademique.id == date_debut côté serveur).
  Future<String?> printFinancierReport({
    required String classe,
    required String anneeAcademiqueId,
    required DateTime dateFin,
    required String versement,
  }) {
    isPrintingFinancier = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'print-rapport-paiement',
      data: {
        'classe': classe,
        'date_debut': anneeAcademiqueId,
        'date_fin': _formatDate(dateFin),
        'versement': versement,
      },
      fileName: 'rapport_financier.pdf',
    ).whenComplete(() {
      isPrintingFinancier = false;
      notifyListeners();
    });
  }

  /// Équivalent du bouton "Présences" du frontend web → POST
  /// v1/export-excel-presence (RExcelExport.py:745-778). `classe` est
  /// transmis pour respecter le schéma `ExcelPresenceReq`, mais le serveur
  /// ne l'utilise actuellement pas dans sa requête SQL (filtre ignoré côté
  /// backend, pas une limitation introduite ici).
  Future<String?> printPresenceExcel({
    required String classe,
    required DateTime dateDebut,
    required DateTime dateFin,
  }) {
    isPrintingPresence = true;
    notifyListeners();
    return _downloadAndOpen(
      endpoint: 'export-excel-presence',
      data: {
        'classe': classe,
        'date_debut': _formatDate(dateDebut),
        'date_fin': _formatDate(dateFin),
      },
      fileName: 'rapport_presence.xlsx',
    ).whenComplete(() {
      isPrintingPresence = false;
      notifyListeners();
    });
  }

  Future<String?> _downloadAndOpen({
    required String endpoint,
    required Map<String, dynamic> data,
    required String fileName,
  }) async {
    try {
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
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  String _formatDate(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

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
