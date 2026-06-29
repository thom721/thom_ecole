import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import '../core/api_client.dart';
import '../core/token_storage.dart';
import '../models/user.dart';

/// Équivalent de Controllers/Main.py se_connecter()/handle_login_response()
/// (school_client) : appelle v1/auth/login, garde l'utilisateur/rôles/
/// permissions en mémoire pour la session, et pilote l'affichage de la
/// coquille de navigation.
class AuthState extends ChangeNotifier {
  AuthState(this._apiClient, this._tokenStorage);

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  AppUser? user;
  List<String> roles = [];
  List<String> permissions = [];
  /// null → onglets déterminés par roleNavItems (ancien comportement ou
  /// admin avec accessible_tabs non configuré). Liste → onglets restreints
  /// au sous-ensemble retourné par le serveur (tab_ids dans la réponse login).
  List<String>? _accessibleTabs;
  bool isLoading = false;
  String? errorMessage;

  /// Équivalent de self.access_key (Controllers/Main.py:279, 1551) :
  /// code de statut extrait de heart_autos.descript ("{user_id}--{code}"),
  /// écrit exclusivement par infini-software via POST /activate-state.
  /// Vaut "22" quand l'installation est autorisée, autre valeur (ex: "23")
  /// quand révoquée. Non initialisé = "0" (bloque les impressions).
  String _accessKey = '0';

  /// Équivalent de self.access_key_info (Main.py:280, 1552) :
  /// même code extrait de users.client_infos (3ème segment UUID, 2 premiers
  /// caractères), mis à jour au même moment par la même opération infini-software.
  /// Les deux doivent être "22" pour que canPrintNonReceipt() laisse passer.
  String _accessKeyInfo = '0';

  /// Vrai quand les deux codes sont "22" — équivalent du test
  /// `access_key == '22' and access_key_info == access_key` (Main.py:3739).
  /// Seuls les reçus court-circuitent ce test (voir print_gate.dart).
  bool get isLicenseAuthorized =>
      _accessKey == '22' && _accessKeyInfo == _accessKey;

  /// Équivalent de get_client_autorisation() (Main.py:1455-1462) :
  /// extrait les 2 premiers caractères du 3ème segment du UUID client_infos.
  static String _extractClientCode(String clientInfos) {
    final parts = clientInfos.split('-');
    if (parts.length < 3) return '0';
    final seg = parts[2];
    return seg.length >= 2 ? seg.substring(0, 2) : '0';
  }

  bool get isLoggedIn => user != null;

  /// Mêmes boutons que roles_boutons dans Controllers/Main.py connect_buttons()
  /// — quels éléments du menu latéral chaque rôle peut voir. "presences" est
  /// une exception : absent du bureau, repris du web (Presences.vue) où
  /// `canAccessPresences` n'autorise que admin/Responsable pédagogique/teacher
  /// (cf. PRESENCE_ROLES, ecole_nginx/app/Routes/RPresences.py).
  static const Map<String, List<String>> roleNavItems = {
    'admin': [
      'home',
      'admin',
      'etudiant',
      'paiement',
      'prof',
      'cours',
      'promus',
      'rapport',
      'vente',
      'profile',
      'settings',
      'actualiser',
      'notes',
      'log',
      'abonnement',
      'presences',
    ],
    'teacher': ['notes', 'actualiser', 'presences', 'profile'],
    'Caissier': [
      'paiement',
      'vente',
      'rapport',
      'etudiant',
      'actualiser',
      'profile',
    ],
    'Responsable financier': [
      'paiement',
      'vente',
      'rapport',
      'etudiant',
      'actualiser',
      'profile',
    ],
    'Responsable des admissions': ['etudiant', 'actualiser', 'profile'],
    'Responsable pédagogique': [
      'rapport',
      'home',
      'cours',
      'etudiant',
      'settings',
      'notes',
      'actualiser',
      'promus',
      'presences',
      'profile',
    ],
    // "abonnement" demandé explicitement pour ce rôle, même si le web
    // (AdminLayout.vue shouldShowMenuItem) ne le réserve qu'à `isAdmin` —
    // déviation volontaire de la parité web sur instruction utilisateur.
    'Comptable': [
      'vente',
      'rapport',
      'home',
      'etudiant',
      'settings',
      'paiement',
      'actualiser',
      'profile',
      'abonnement',
    ],
    // Équivalent du rôle "user" de base côté web (isBaseUser) : aucun accès
    // sauf Profile (AdminLayout.vue shouldShowMenuItem(), ligne 196-200).
    'user': ['profile'],
  };

  /// Équivalent de isBaseUser (ecole_nginx/frontend/src/stores/auth.js:23-28)
  /// : seul le rôle générique "user", sans aucun autre rôle métier — ce
  /// profil ne voit que l'onglet "Mon compte" dans ProfileScreen.
  bool get isBaseUser => roles.length == 1 && roles.contains('user');

  /// Retourne les IDs de sous-onglets visibles pour un onglet parent (ex:
  /// 'vente', 'profile', 'settings'). null = pas de restriction (tout visible).
  /// Quand accessible_tabs contient au moins une entrée "parentId.sousId", seuls
  /// ces sous-onglets sont montrés ; si aucune entrée de ce préfixe n'existe le
  /// parent est entièrement libre (aucune restriction de sous-onglets).
  Set<String>? visibleSubItems(String parentId) {
    if (_accessibleTabs == null) return null;
    final prefix = '$parentId.';
    final sub = _accessibleTabs!
        .where((id) => id.startsWith(prefix))
        .map((id) => id.substring(prefix.length))
        .toSet();
    return sub.isEmpty ? null : sub;
  }

  Set<String> get visibleNavItems {
    // Quand le serveur envoie tab_ids (liste non-null), on l'utilise directement.
    // Quand tab_ids est null (au moins un rôle = accès total), on retombe sur
    // la map statique pour la rétrocompatibilité.
    if (_accessibleTabs != null) return _accessibleTabs!.toSet();
    final items = <String>{};
    for (final role in roles) {
      items.addAll(roleNavItems[role] ?? const []);
    }
    return items;
  }

  /// Équivalent de la double extraction dans handle_authorization_success()
  /// (Main.py:1548-1552) : lit les deux codes de statut écrits exclusivement
  /// par infini-software via POST /activate-state → get_all_user().
  void _parseAccessKeys(Map<String, dynamic> userJson) {
    // access_key ← heart_auto['descript'].split('--')[1]  (Main.py:1550-1551)
    final heartAuto = userJson['heart_auto'] as Map<String, dynamic>?;
    final descript = heartAuto?['descript']?.toString() ?? '';
    final parts = descript.split('--');
    _accessKey = parts.length >= 2 ? parts[1] : '0';

    // access_key_info ← get_client_autorisation(client_infos)  (Main.py:1552)
    final clientInfos = userJson['client_infos']?.toString() ?? '';
    _accessKeyInfo = _extractClientCode(clientInfos);
  }

  Future<bool> login(String email, String password) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.post(
        'auth/login',
        data: {
          'email': email,
          'password': password,
          'device_name': 'flutter-desktop-app',
          // Même valeur spéciale que school_client (Models/AsyncDataHandler.py
          // login()) : côté serveur, ServiceAuth.find_user_by_credentials()
          // accepte n'importe quel userable_type quand login_as=="as_desktop"
          // (au lieu de devoir correspondre exactement).
          'login_as': 'as_desktop',
        },
      );

      final data = response.data as Map<String, dynamic>;
      final userJson = data['user'] as Map<String, dynamic>?;

      if (userJson == null) {
        errorMessage = 'Les informations de connexion sont incorrectes !';
        return false;
      }
      if (userJson['status']?.toString() != '1') {
        errorMessage = "Votre compte n'est pas actif !";
        return false;
      }
      final userableType = userJson['userable_type']?.toString() ?? '';
      if (!userableType.endsWith('\\Personnel') &&
          !userableType.endsWith('\\Professeur')) {
        errorMessage =
            "Votre compte n'est pas autorisé à vous connecter au serveur.";
        return false;
      }

      user = AppUser.fromJson(userJson);
      roles = ((data['roles'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList();
      permissions = ((data['permissions'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList();
      final tabIds = data['tab_ids'] as List?;
      _accessibleTabs = tabIds?.map((e) => e.toString()).toList();
      _parseAccessKeys(userJson);

      await _tokenStorage.saveToken(data['token']?.toString() ?? '');
      await _tokenStorage.saveUserEmail(email);

      return true;
    } on DioException catch (e) {
      final detail = e.response?.data is Map
          ? (e.response?.data as Map)['detail']?.toString()
          : null;
      errorMessage = detail ?? 'Impossible de contacter le serveur.';
      return false;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de reset_password()/reset_password_and_connect()
  /// (Controllers/Main.py + Models/AsyncDataHandler.py, school_client) :
  /// SEUL flux de réinitialisation que possède le bureau — déclenché
  /// automatiquement à la "première connexion", un simple formulaire mot
  /// de passe + confirmation, SANS code OTP et sans lien "mot de passe
  /// oublié" (qui n'existe pas dans school_client). Appelle PATCH
  /// v1/password-change-user, protégé par le token déjà sauvegardé par
  /// login() ci-dessus — le serveur
  /// identifie l'utilisateur via ce token (Depends(get_current_user),
  /// Routes/RAuth.py), pas via le user_id du payload. La réponse a la même
  /// forme que /auth/login (user_data_generate()) donc on la retraite de
  /// la même façon, ce qui correspond au réel handle_login_response()
  /// appelé une seconde fois par le bureau après ce changement.
  Future<bool> changePasswordFirstLogin(
    String password,
    String passwordConfirm,
  ) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.dio.patch(
        'password-change-user',
        data: {
          'password': password,
          'password_confirm': passwordConfirm,
          'user_id': user?.id,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final userJson = data['user'] as Map<String, dynamic>?;
      if (userJson == null) {
        errorMessage = 'Réponse inattendue du serveur.';
        return false;
      }

      user = AppUser.fromJson(userJson);
      roles = ((data['roles'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList();
      permissions = ((data['permissions'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList();
      final tabIdsChange = data['tab_ids'] as List?;
      _accessibleTabs = tabIdsChange?.map((e) => e.toString()).toList();
      _parseAccessKeys(userJson);

      await _tokenStorage.saveToken(data['token']?.toString() ?? '');
      return true;
    } on DioException catch (e) {
      final responseData = e.response?.data;
      if (responseData is Map) {
        errorMessage =
            (responseData['errors'] ??
                    responseData['error'] ??
                    responseData['detail'])
                ?.toString() ??
            'Impossible de contacter le serveur.';
      } else {
        errorMessage = 'Impossible de contacter le serveur.';
      }
      return false;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    user = null;
    roles = [];
    permissions = [];
    _accessibleTabs = null;
    _accessKey = '0';
    _accessKeyInfo = '0';
    await _tokenStorage.clear();
    notifyListeners();
  }
}
