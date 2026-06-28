/// Reflète EtudiantResponseRead (ecole_nginx app/Schemas/Etudiants.py).
class Student {
  Student({
    required this.id,
    required this.identifiant,
    required this.nom,
    required this.prenom,
    required this.sexe,
    required this.dateDeNaissance,
    this.telephone,
    this.email,
    required this.adresse,
    this.religion,
    this.lieuDeNaissance,
    this.aideFinanciere = 'Aucune',
    this.nisu,
    this.dernierEtablissement,
    this.niveauId,
    this.classeActuelleId,
    this.anneeAcademiqueId,
    this.faculteId,
    this.nomResponsable,
    this.prenomResponsable,
    this.emailResponsable,
    this.relationResponsable,
    this.sexeResponsable,
    this.telephoneResponsable,
    this.metierResponsable,
    this.adresseResponsable,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id']?.toString() ?? '',
      identifiant: json['identifiant']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      sexe: json['sexe']?.toString() ?? '',
      dateDeNaissance: json['date_de_naissance']?.toString() ?? '',
      telephone: json['telephone']?.toString(),
      email: json['email']?.toString(),
      adresse: json['adresse']?.toString() ?? '',
      religion: json['religion']?.toString(),
      lieuDeNaissance: json['lieu_de_naissance']?.toString(),
      aideFinanciere: json['aide_financiere']?.toString() ?? 'Aucune',
      nisu: json['nisu']?.toString(),
      dernierEtablissement: json['dernier_etablissement']?.toString(),
    );
  }

  final String id;
  final String identifiant;
  final String nom;
  final String prenom;
  final String sexe;
  final String dateDeNaissance;
  final String? telephone;
  final String? email;
  final String adresse;
  final String? religion;
  final String? lieuDeNaissance;
  final String aideFinanciere;
  final String? nisu;
  final String? dernierEtablissement;

  // Présents seulement côté formulaire (pas renvoyés tels quels par la liste).
  final String? niveauId;
  final String? classeActuelleId;
  final String? anneeAcademiqueId;
  final String? faculteId;
  final String? nomResponsable;
  final String? prenomResponsable;
  final String? emailResponsable;
  final String? relationResponsable;
  final String? sexeResponsable;
  final String? telephoneResponsable;
  final String? metierResponsable;
  final String? adresseResponsable;
}

class Niveau {
  Niveau({required this.id, required this.name});
  factory Niveau.fromJson(Map<String, dynamic> json) =>
      Niveau(id: json['id'].toString(), name: json['name']?.toString() ?? '');
  final String id;
  final String name;
}

class Classe {
  Classe({required this.id, required this.niveauId, required this.nomClasse});
  factory Classe.fromJson(Map<String, dynamic> json) => Classe(
        id: json['id'].toString(),
        niveauId: json['niveau_id']?.toString() ?? '',
        nomClasse: json['nom_classe']?.toString() ?? '',
      );
  final String id;
  final String niveauId;
  final String nomClasse;
}

class AnneeAcademique {
  AnneeAcademique({required this.id, required this.nom});
  // GET v1/annee-academique (app/Routes/RAcademic.py, AnneeAcademiqueBase)
  // renvoie le champ `annee_academique` ("2024/2025"), pas `nom`.
  factory AnneeAcademique.fromJson(Map<String, dynamic> json) => AnneeAcademique(
        id: json['id'].toString(),
        nom: json['annee_academique']?.toString() ?? json['nom']?.toString() ?? '',
      );
  final String id;
  final String nom;
}

class Faculte {
  Faculte({required this.id, required this.nom});
  factory Faculte.fromJson(Map<String, dynamic> json) =>
      Faculte(id: json['id'].toString(), nom: json['nom']?.toString() ?? '');
  final String id;
  final String nom;
}
