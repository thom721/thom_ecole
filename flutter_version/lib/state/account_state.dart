import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';

/// Équivalent de la section "Mon profil" (ecole_nginx/frontend/src/views/
/// admin/adProfile.vue, get_my_profile()/updateUserProfile()/
/// updatePassword()) — absente du bureau (school_client n'a aucun
/// formulaire pour que l'utilisateur modifie lui-même nom/prénom/email/
/// username), donc reprise ici à l'identique du web puisque c'est la seule
/// référence existante pour cette fonctionnalité.
class AccountState extends ChangeNotifier {
  AccountState(this._apiClient);

  final ApiClient _apiClient;

  bool isLoading = false;
  bool isSubmittingProfile = false;
  bool isSubmittingPassword = false;
  String? loadError;
  String? profileError;
  String? passwordError;

  String nom = '';
  String prenom = '';
  String email = '';
  String username = '';

  bool hasPin = false;
  bool isLoadingPinStatus = false;
  bool isSubmittingPin = false;
  String? pinError;

  /// GET v1/personnel/{id} ou v1/professeur/{id} selon userable_type — même
  /// distinction que get_my_profile() côté web (`/personnel/${userable_id}`),
  /// étendue ici au cas Professeur puisque ce sont les deux seuls types
  /// autorisés à se connecter au bureau (cf. AuthState.login()).
  Future<void> load({
    required String userableId,
    required String userableType,
  }) async {
    isLoading = true;
    loadError = null;
    notifyListeners();
    try {
      final isProf = userableType.endsWith('\\Professeur');
      final response = await _apiClient.get(
        isProf ? 'professeur/$userableId' : 'personnel/$userableId',
      );
      final d =
          (response.data as Map<String, dynamic>)['data']
              as Map<String, dynamic>;
      nom = d['nom']?.toString() ?? '';
      prenom = d['prenom']?.toString() ?? '';
      email = d['email']?.toString() ?? '';
      username =
          (d['user'] as Map<String, dynamic>?)?['username']?.toString() ?? '';
    } catch (_) {
      loadError = 'Impossible de charger vos informations.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// PATCH v1/user/profile (RAcademic.py:1404) — `id` doit être le
  /// userable_id (Personnel.id ou Professeur.id), pas le User.id du token :
  /// la route le résout elle-même via `User.userable_id == data.id`.
  Future<String?> updateProfile({
    required String userableId,
    required String nom,
    required String prenom,
    required String email,
    required String username,
  }) async {
    isSubmittingProfile = true;
    profileError = null;
    notifyListeners();
    try {
      await _apiClient.dio.patch(
        'user/profile',
        data: {
          'id': userableId,
          'nom': nom,
          'prenom': prenom,
          'email': email,
          'username': username,
        },
      );
      this.nom = nom;
      this.prenom = prenom;
      this.email = email;
      this.username = username;
      return null;
    } catch (e) {
      final msg = _extractError(e);
      profileError = msg;
      return msg;
    } finally {
      isSubmittingProfile = false;
      notifyListeners();
    }
  }

  /// PUT v1/password-change-user-global (RAuth.py:451) — distinct de
  /// changePasswordFirstLogin() (AuthState), qui ne gère que le mot de passe
  /// temporaire de première connexion et n'exige pas l'ancien mot de passe.
  Future<String?> changePassword({
    required String currentPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    isSubmittingPassword = true;
    passwordError = null;
    notifyListeners();
    try {
      await _apiClient.dio.put(
        'password-change-user-global',
        data: {
          'current_password': currentPassword,
          'password': newPassword,
          'password_confirmation': confirmPassword,
        },
      );
      return null;
    } catch (e) {
      final msg = _extractError(e);
      passwordError = msg;
      return msg;
    } finally {
      isSubmittingPassword = false;
      notifyListeners();
    }
  }

  /// GET v1/user/pin-status (RAcademic.py) — ne renvoie jamais le hash, juste
  /// si un PIN est déjà défini, pour adapter le libellé "Définir"/"Modifier".
  Future<void> loadPinStatus() async {
    isLoadingPinStatus = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('user/pin-status');
      hasPin = (response.data as Map<String, dynamic>)['has_pin'] == true;
    } catch (_) {
      // silencieux : champ purement indicatif, pas bloquant pour le reste de la page
    } finally {
      isLoadingPinStatus = false;
      notifyListeners();
    }
  }

  /// PATCH v1/user/pin (RAcademic.py) — réservé aux rôles admin/Comptable
  /// côté serveur ; ce PIN sert ensuite à approuver, à la place d'un autre
  /// rôle, un retour de paiement ou une suppression de vente/dépense/
  /// transaction (POST v1/auth/autorisation-access-pin).
  Future<String?> setPin(String pin) async {
    isSubmittingPin = true;
    pinError = null;
    notifyListeners();
    try {
      await _apiClient.dio.patch('user/pin', data: {'pin': pin});
      hasPin = true;
      return null;
    } catch (e) {
      final msg = _extractError(e);
      pinError = msg;
      return msg;
    } finally {
      isSubmittingPin = false;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map) {
        final detail = data['detail'] ?? data['errors'] ?? data['message'];
        if (detail != null) return detail.toString();
      }
    }
    return 'Une erreur est survenue.';
  }
}
