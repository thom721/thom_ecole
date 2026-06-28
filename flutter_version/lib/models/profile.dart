/// Reflète ProfileOut (ecole_nginx app/Schemas/SProfile.py) — le profil de
/// l'ÉCOLE (et non de l'utilisateur connecté). Équivalent de
/// Controllers/Main.py:profile()/save_profile() (school_client) : nom,
/// email, deux lignes de téléphone, adresse et logo. school_client ne gère
/// ni le profil personnel de l'utilisateur, ni le changement de mot de
/// passe, ni les rôles/permissions depuis cette page — uniquement présents
/// dans la version étendue du frontend web (adProfile.vue), donc pas
/// repris ici pour rester fidèle à la vraie portée de cette page.
class SchoolProfile {
  SchoolProfile({
    required this.id,
    required this.nom,
    required this.email,
    required this.ligne1,
    required this.ligne2,
    required this.adresse,
    required this.logoImageBase64,
  });

  factory SchoolProfile.fromJson(Map<String, dynamic> json) {
    return SchoolProfile(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      ligne1: json['ligne1']?.toString() ?? '',
      ligne2: json['ligne2']?.toString() ?? '',
      adresse: json['adresse']?.toString() ?? '',
      logoImageBase64: json['logo_image_base64']?.toString(),
    );
  }

  final String id;
  final String nom;
  final String email;
  final String ligne1;
  final String ligne2;
  final String adresse;
  final String? logoImageBase64;
}
