/// Reflète ProfesseurResponse (ecole_nginx app/Schemas/Academic.py:178-192).
class Professeur {
  Professeur({
    required this.id,
    required this.nom,
    required this.prenom,
    required this.sexe,
    required this.email,
    required this.telephone,
    required this.adresse,
    this.matiereEnseignee,
    required this.statusLabel,
    this.userStatus,
    this.typePaiement = 'fixe',
    this.salaireFixe,
    this.personnelId,
  });

  factory Professeur.fromJson(Map<String, dynamic> json) {
    final user = json['user'] as Map<String, dynamic>?;
    final rawStatus = user?['status'];
    return Professeur(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      sexe: json['sexe']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      telephone: json['telephone']?.toString() ?? '',
      adresse: json['adresse']?.toString() ?? '',
      matiereEnseignee: json['matiere_enseignee']?.toString(),
      statusLabel: json['status_']?.toString() ?? 'Inactif',
      userStatus: rawStatus is num ? rawStatus.toInt() : null,
      typePaiement: json['type_paiement']?.toString() ?? 'fixe',
      salaireFixe: json['salaire_fixe'] == null
          ? null
          : (json['salaire_fixe'] as num).toDouble(),
      personnelId: json['personnel_id']?.toString(),
    );
  }

  final String id;
  final String nom;
  final String prenom;
  final String sexe;
  final String email;
  final String telephone;
  final String adresse;
  final String? matiereEnseignee;
  final String statusLabel;
  // Reflète user.status (UserSchema.UserResponse) : 1=actif, 0=inactif,
  // null=pas encore de compte utilisateur — distinction reprise du badge à
  // 3 couleurs de Professeur.vue (vert/orange/rose).
  final int? userStatus;
  // 'fixe' ou 'horaire' — détermine si le payroll utilise salaireFixe ou le
  // calcul heures × taux (ParametrePayroll), voir payroll_tab.dart.
  final String typePaiement;
  final double? salaireFixe;
  // Non-null si cette fiche est la "casquette enseignante" d'un Personnel
  // (rôle teacher/Enseignant) plutôt qu'un professeur autonome — voir
  // RAcademic.py:_sync_shadow_professeur.
  final String? personnelId;

  bool get isLinkedToPersonnel => personnelId != null;
}
