import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/parametre_payroll.dart';

/// Taux horaire par cours/année — GET/POST/PUT/DELETE v1/parametre-payroll
/// (ecole_nginx/app/Routes/RParametrePayroll.py). Fonctionnalité ajoutée
/// sur demande explicite pour le payroll horaire des professeurs.
class ParametrePayrollState extends ChangeNotifier {
  ParametrePayrollState(this._apiClient);

  final ApiClient _apiClient;

  List<ParametrePayroll> items = [];
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? deletingId;

  /// (id, nom) de tous les cours — GET v1/cours sans pagination, pour le
  /// dropdown du formulaire d'ajout de taux.
  List<(String, String)> coursOptionsForDropdown = [];
  bool isLoadingCours = false;

  Future<void> loadAllCours() async {
    if (coursOptionsForDropdown.isNotEmpty) return;
    isLoadingCours = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('cours');
      final data = response.data;
      final list = data is List ? data : (data as Map<String, dynamic>)['data'] as List? ?? const [];
      coursOptionsForDropdown = list
          .map((e) => (
                (e as Map<String, dynamic>)['id'].toString(),
                e['cours_nom']?.toString() ?? '',
              ))
          .toList();
    } catch (_) {
      coursOptionsForDropdown = [];
    } finally {
      isLoadingCours = false;
      notifyListeners();
    }
  }

  Future<void> load({String? anneeAcademique}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('parametre-payroll', query: {
        if (anneeAcademique != null) 'annee_academique': anneeAcademique,
      });
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => ParametrePayroll.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      errorMessage = 'Impossible de charger les taux horaires.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> create({
    required String coursId,
    required double tauxHoraire,
    required String anneeAcademique,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('parametre-payroll', data: {
        'cours_id': coursId,
        'taux_horaire': tauxHoraire,
        'annee_academique': anneeAcademique,
      });
      await load();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> update(String id, double tauxHoraire) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.dio.put('parametre-payroll/$id', data: {'taux_horaire': tauxHoraire});
      await load();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> delete(String id) async {
    deletingId = id;
    notifyListeners();
    try {
      await _apiClient.dio.delete('parametre-payroll/$id');
      items.removeWhere((p) => p.id == id);
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
      if (data is Map && data['detail'] != null) return data['detail'].toString();
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
