/// Sous-ensemble du "user" renvoyé par POST v1/auth/login (voir
/// app/Routes/RAuth.py côté ecole_nginx) — uniquement les champs utilisés
/// par la coquille de navigation et le tableau de bord pour l'instant.
class AppUser {
  AppUser({
    required this.id,
    required this.email,
    required this.status,
    required this.userableType,
    required this.userableId,
    required this.passwordChangedAt,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      userableType: json['userable_type']?.toString() ?? '',
      userableId: json['userable_id']?.toString() ?? '',
      passwordChangedAt: json['password_changed_at']?.toString() ?? '',
    );
  }

  final String id;
  final String email;
  final String status;
  final String userableType;

  /// Personnel.id ou Professeur.id (selon userableType) — distinct du
  /// User.id ci-dessus, requis par PATCH v1/user/profile (voir AccountState).
  final String userableId;

  /// Vide tant que l'utilisateur n'a jamais changé son mot de passe initial
  /// (Routes/RAuth.py user_data_generate() : `user.password_changed_at or ""`)
  /// — même condition que Login.vue (`user.password_changed_at == ''`) pour
  /// forcer le passage par l'écran de réinitialisation "première connexion".
  final String passwordChangedAt;

  bool get mustResetPassword => passwordChangedAt.isEmpty;
}
