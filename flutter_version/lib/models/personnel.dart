/// Reflète PersonnelResponse (ecole_nginx app/Schemas/Academic.py:249-263).
class Personnel {
  Personnel({
    required this.id,
    required this.nom,
    required this.prenom,
    required this.sexe,
    required this.email,
    required this.telephone,
    required this.adresse,
    required this.statusLabel,
    this.userStatus,
    this.roleId,
    this.roleName,
  });

  factory Personnel.fromJson(Map<String, dynamic> json) {
    final user = json['user'] as Map<String, dynamic>?;
    final rawStatus = user?['status'];
    final roles = user?['roles'] as List?;
    final firstRole = (roles != null && roles.isNotEmpty) ? roles.first as Map<String, dynamic> : null;
    return Personnel(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      sexe: json['sexe']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      telephone: json['telephone']?.toString() ?? '',
      adresse: json['adresse']?.toString() ?? '',
      statusLabel: json['status_']?.toString() ?? 'Inactif',
      userStatus: rawStatus is num ? rawStatus.toInt() : null,
      roleId: firstRole?['id']?.toString(),
      roleName: firstRole?['name']?.toString(),
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final String sexe;
  final String email;
  final String telephone;
  final String adresse;
  final String statusLabel;
  final int? userStatus;
  // user.roles[0] (UserSchema.RoleSchema) — comme editPerso() (Administration
  // .vue:109) qui pré-remplit formPersonnel.role avec user.roles[0].id.
  final String? roleId;
  final String? roleName;
}
