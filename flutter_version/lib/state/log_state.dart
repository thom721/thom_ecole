import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

/// Libellés affichés == self.actions (Controllers/Main.py:631-635).
const kLogActions = {
  'create': 'Créer',
  'update': 'Mise à jour',
  'delete': 'Supprimer',
};

/// Libellés affichés == self.models (Controllers/Main.py:649-687) — la
/// valeur est le `model_type` PHP réellement stocké dans la table `logs`
/// (et donc filtrable via `?model=`), repris à l'identique malgré le
/// rebranchement FastAPI/SQLAlchemy du backend.
const kLogModels = {
  'Année académique': r'App\Models\AnneeAcademique',
  'Classe': r'App\Models\Classe',
  'Etudiants classe': r'App\Models\ClassesEtudiant',
  'Cours': r'App\Models\Cours',
  'Note': r'App\Models\CoursEtudiant',
  'Dépenses': r'App\Models\Depense',
  'Etudiant faculté': r'App\Models\EtudiantFaculte',
  'Etudiants': r'App\Models\Etudiant',
  'Faculté': r'App\Models\Faculte',
  "Frais d'inscription": r'App\Models\FraisDInscription',
  'Frais divers': r'App\Models\FraisDivers',
  'Niveaux': r'App\Models\Niveau',
  'Paiements': r'App\Models\Paiement',
  'Paramètre de paiement': r'App\Models\ParametrePaiement',
  'Paramètre des examens': r'App\Models\ParamExam',
  'Permissions': r'App\Models\Permission',
  'Personnels': r'App\Models\Personnel',
  'Professeurs': r'App\Models\Professeur',
  'Profiles': r'App\Models\Profile',
  'Programmes': r'App\Models\Programme',
  'Utilisateur': r'App\Models\User',
  'Ventes': r'App\Models\Vente',
};

class LogEntry {
  LogEntry({
    required this.id,
    required this.user,
    required this.authorizationId,
    required this.action,
    required this.model,
    required this.date,
  });

  factory LogEntry.fromJson(Map<String, dynamic> json) {
    return LogEntry(
      id: json['id']?.toString() ?? '',
      user: json['user']?.toString() ?? '',
      authorizationId: json['authorization_id']?.toString() ?? '',
      action: json['action']?.toString() ?? '',
      model: json['model']?.toString() ?? '',
      date: json['date']?.toString() ?? '',
    );
  }

  final String id;
  final String user;
  final String authorizationId;
  final String action;
  final String model;
  final String date;
}

class LogDetail {
  LogDetail({
    required this.id,
    required this.action,
    required this.modelType,
    required this.modelId,
    required this.oldValues,
    required this.newValues,
    required this.ipAddress,
    required this.userAgent,
    required this.createdAt,
    required this.reason,
  });

  factory LogDetail.fromJson(Map<String, dynamic> json) {
    return LogDetail(
      id: json['id']?.toString() ?? '',
      action: json['action']?.toString() ?? '',
      modelType: json['model_type']?.toString() ?? '',
      modelId: json['model_id']?.toString() ?? '',
      oldValues: json['old_values']?.toString(),
      newValues: json['new_values']?.toString(),
      ipAddress: json['ip_address']?.toString(),
      userAgent: json['user_agent']?.toString(),
      createdAt: json['created_at']?.toString(),
      reason: json['reason']?.toString(),
    );
  }

  final String id;
  final String action;
  final String modelType;
  final String modelId;
  final String? oldValues;
  final String? newValues;
  final String? ipAddress;
  final String? userAgent;
  final String? createdAt;
  final String? reason;
}

/// Équivalent de logs()/go_to_log_page()/set_table_refresh_data_log()
/// (school_client, Controllers/Main.py:4738-4863) → GET v1/logs-graphic
/// (ecole_nginx/app/Routes/RLog.py) — uniquement l'onglet "grafic_log"
/// (table + filtres), pas "console_log" (vue debug temps réel sans
/// équivalent utilisateur clair, volontairement omise).
class LogState extends ChangeNotifier {
  LogState(this._apiClient);

  final ApiClient _apiClient;

  List<LogEntry> items = [];
  int currentPage = 1;
  int lastPage = 1;
  bool isLoading = false;
  String? errorMessage;

  String? search;
  String? action;
  String? model;

  Future<void> load({int page = 1}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'logs-graphic',
        query: {
          'page': page,
          if (search != null && search!.isNotEmpty) 'search': search,
          if (action != null) 'action': action,
          if (model != null) 'model': model,
        },
      );
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => LogEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = e is DioException
          ? (e.response?.data is Map
                    ? e.response?.data['detail']?.toString()
                    : null) ??
                'Impossible de charger les logs.'
          : 'Impossible de charger les logs.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<LogDetail?> fetchDetail(String id) async {
    try {
      final response = await _apiClient.get('logs-graphic-show/$id');
      final data = (response.data as Map<String, dynamic>)['data'];
      return data == null
          ? null
          : LogDetail.fromJson(data as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }
}
