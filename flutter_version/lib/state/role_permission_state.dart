import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/role_permission.dart';

/// Équivalent de role_page()/permission_page() (school_client, Controllers/
/// Main.py:6348-6393 + 6395-6796) : assignation de rôles à un utilisateur,
/// et de permissions à un rôle OU à un utilisateur (jamais les deux à la
/// fois, cf. AssignPermissionRequest.validate_role_or_user,
/// RRolePermission.py:282-296).
class RolePermissionState extends ChangeNotifier {
  RolePermissionState(this._apiClient);

  final ApiClient _apiClient;

  List<RoleRecord> roles = [];
  List<PermissionRecord> permissions = [];
  bool isLoadingLists = false;

  List<RoleSearchUser> roleSearchResults = [];
  bool isSearchingForRole = false;

  List<PermissionSearchUser> permissionSearchResults = [];
  bool isSearchingForPermission = false;

  Set<String> permissionsForSelectedRole = {};
  bool isLoadingRolePermissions = false;

  bool isAssigningRoles = false;
  bool isAssigningPermissions = false;

  Future<void> loadLists() async {
    if (roles.isNotEmpty && permissions.isNotEmpty) return;
    isLoadingLists = true;
    notifyListeners();
    try {
      final results = await Future.wait([
        _apiClient.get('role'),
        _apiClient.get('permission'),
      ]);
      roles = ((results[0].data as Map<String, dynamic>)['data'] as List? ?? const [])
          .map((e) => RoleRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      permissions = ((results[1].data as Map<String, dynamic>)['data'] as List? ?? const [])
          .map((e) => PermissionRecord.fromJson(e as Map<String, dynamic>))
          .toList();
    } finally {
      isLoadingLists = false;
      notifyListeners();
    }
  }

  /// Équivalent de set_table_refresh_data_for_live_search_role().
  Future<void> searchUsersForRole(String query) async {
    if (query.trim().isEmpty) {
      roleSearchResults = [];
      notifyListeners();
      return;
    }
    isSearchingForRole = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('fetch-data-with-role', query: {'data': query});
      final data = (response.data as Map<String, dynamic>)['data'] as List? ?? const [];
      roleSearchResults = data.map((e) => RoleSearchUser.fromJson(e as Map<String, dynamic>)).toList();
    } catch (_) {
      roleSearchResults = [];
    } finally {
      isSearchingForRole = false;
      notifyListeners();
    }
  }

  /// Équivalent de set_table_refresh_data_for_live_search_permission().
  Future<void> searchUsersForPermission(String query) async {
    if (query.trim().isEmpty) {
      permissionSearchResults = [];
      notifyListeners();
      return;
    }
    isSearchingForPermission = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('fetch-data-with-permission', query: {'data': query});
      final data = (response.data as Map<String, dynamic>)['data'] as List? ?? const [];
      permissionSearchResults =
          data.map((e) => PermissionSearchUser.fromJson(e as Map<String, dynamic>)).toList();
    } catch (_) {
      permissionSearchResults = [];
    } finally {
      isSearchingForPermission = false;
      notifyListeners();
    }
  }

  /// Équivalent de fetch_role_with_permission() → GET
  /// v1/get-permission-by-role/{role}.
  Future<void> loadPermissionsForRole(String roleId) async {
    isLoadingRolePermissions = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('get-permission-by-role/$roleId');
      final data = (response.data as Map<String, dynamic>)['permis'] as List? ?? const [];
      permissionsForSelectedRole = data.map((e) => (e as Map<String, dynamic>)['id'].toString()).toSet();
    } catch (_) {
      permissionsForSelectedRole = {};
    } finally {
      isLoadingRolePermissions = false;
      notifyListeners();
    }
  }

  /// Équivalent de send_selected_roles() → POST v1/assign-role-to-user.
  Future<String?> assignRolesToUser({required String userId, required Set<String> roleIds}) async {
    isAssigningRoles = true;
    notifyListeners();
    try {
      await _apiClient.post('assign-role-to-user', data: {
        'user_id': userId,
        'role': roleIds.toList(),
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isAssigningRoles = false;
      notifyListeners();
    }
  }

  /// Équivalent de send_selected_permissions() → POST
  /// v1/assign-permission-to-role, en mode "rôle" (role renseigné, pas
  /// user_id).
  Future<String?> assignPermissionsToRole({required String roleId, required Set<String> permissionIds}) {
    return _assignPermissions(role: roleId, permissionIds: permissionIds);
  }

  /// Même endpoint, en mode "utilisateur" (user_id renseigné, pas role).
  Future<String?> assignPermissionsToUser({required String userId, required Set<String> permissionIds}) {
    return _assignPermissions(userId: userId, permissionIds: permissionIds);
  }

  Future<String?> _assignPermissions({
    String? role,
    String? userId,
    required Set<String> permissionIds,
  }) async {
    isAssigningPermissions = true;
    notifyListeners();
    try {
      await _apiClient.post('assign-permission-to-role', data: {
        'role': role,
        'user_id': userId,
        'permission': permissionIds.toList(),
      });
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isAssigningPermissions = false;
      notifyListeners();
    }
  }

  bool isUpdatingTabs = false;

  /// Met à jour les onglets accessibles pour un rôle.
  /// [tabIds] = null → accès à tous les onglets (reset).
  Future<String?> updateRoleTabs(String roleId, List<String>? tabIds) async {
    isUpdatingTabs = true;
    notifyListeners();
    try {
      await _apiClient.dio.patch(
        'roles/$roleId/tabs',
        data: {'accessible_tabs': tabIds},
      );
      // Mettre à jour le cache local
      final idx = roles.indexWhere((r) => r.id == roleId);
      if (idx != -1) {
        roles[idx] = RoleRecord(
          id: roles[idx].id,
          name: roles[idx].name,
          accessibleTabs: tabIds,
        );
      }
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isUpdatingTabs = false;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map) {
        final detail = data['detail'];
        if (detail is Map && detail['errors'] != null) {
          final errors = detail['errors'];
          if (errors is Map) {
            return errors.values.expand((v) => v is List ? v : [v]).join('\n');
          }
        }
        if (detail != null) return detail.toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
