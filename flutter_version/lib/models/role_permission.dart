/// Reflète RoleResponse/PermissionResponse (ecole_nginx
/// app/Schemas/SRolePermission.py) — équivalent de role_page()/
/// permission_page() (school_client, Controllers/Main.py:6348-6393) :
/// school_client ne permet QUE d'assigner des rôles/permissions déjà
/// existants (seedés en base) à un utilisateur — pas d'en créer/supprimer.
class RoleRecord {
  RoleRecord({required this.id, required this.name});
  factory RoleRecord.fromJson(Map<String, dynamic> json) =>
      RoleRecord(id: json['id']?.toString() ?? '', name: json['name']?.toString() ?? '');
  final String id;
  final String name;
}

class PermissionRecord {
  PermissionRecord({required this.id, required this.name});
  factory PermissionRecord.fromJson(Map<String, dynamic> json) =>
      PermissionRecord(id: json['id']?.toString() ?? '', name: json['name']?.toString() ?? '');
  final String id;
  final String name;
}

/// Une ligne de GET v1/fetch-data-with-role (app/Routes/RRolePermission.py:
/// 202-251) — un professeur ou personnel, avec ses rôles déjà assignés.
class RoleSearchUser {
  RoleSearchUser({required this.id, required this.nom, required this.prenom, required this.roleIds});

  factory RoleSearchUser.fromJson(Map<String, dynamic> json) {
    return RoleSearchUser(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      roleIds: ((json['roles'] as List?) ?? const []).map((e) => e.toString()).toSet(),
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final Set<String> roleIds;
}

/// Une ligne de GET v1/fetch-data-with-permission (app/Routes/
/// RRolePermission.py:125-199) — permissions directes + héritées des rôles.
class PermissionSearchUser {
  PermissionSearchUser({required this.id, required this.nom, required this.prenom, required this.permissionIds});

  factory PermissionSearchUser.fromJson(Map<String, dynamic> json) {
    return PermissionSearchUser(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      permissionIds: ((json['permissions'] as List?) ?? const []).map((e) => e.toString()).toSet(),
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final Set<String> permissionIds;
}
