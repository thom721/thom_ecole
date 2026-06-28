import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/profile.dart';

/// Équivalent de profile()/save_profile() (school_client, Controllers/
/// Main.py:6285-6346, 6799-6810) : GET v1/get-profile (un seul profil
/// d'école en base) puis POST v1/profile pour l'enregistrer.
class ProfileState extends ChangeNotifier {
  ProfileState(this._apiClient);

  final ApiClient _apiClient;

  SchoolProfile? profile;
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;

  Future<void> load() async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get('get-profile');
      final data = (response.data as Map<String, dynamic>)['data'];
      profile = data == null ? null : SchoolProfile.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      errorMessage = _extractError(e);
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// `logoImageDataUri` doit être un data-URI complet ("data:image/png;
  /// base64,...") tel que produit par choisir_image_profile() côté
  /// school_client (Controllers/Main.py:convertir_image_en_base64) — null
  /// si l'utilisateur n'a pas changé le logo.
  Future<String?> submit({
    required String nom,
    required String email,
    required String ligne1,
    required String ligne2,
    required String adresse,
    String? logoImageDataUri,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post('profile', data: {
        'id': profile?.id,
        'nom': nom,
        'email': email,
        'ligne1': ligne1,
        'ligne2': ligne2,
        'adresse': adresse,
        'logo_image_path': logoImageDataUri,
        'logo_image_base64': logoImageDataUri,
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
