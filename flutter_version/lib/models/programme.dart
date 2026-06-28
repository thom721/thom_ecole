/// Reflète ProgrammeResponse (ecole_nginx/app/Schemas/programme_schema.py)
/// pour la liste/le détail — attention aux alias réels : la réponse renvoie
/// `Cours_id` (majuscule) et `class_` (avec underscore, sans alias Pydantic),
/// pas `cours_id`/`class` comme le laissait croire le web avant correction.
class Programme {
  Programme({
    required this.id,
    this.coursNom,
    this.coursId,
    this.niveauId,
    this.niveauName,
    this.professeurId,
    this.professeurNom,
    this.classeId,
    this.classeNom,
    this.faculteId,
    this.faculteNom,
    this.anneeAcademiqueId,
    this.anneeAcademiqueNom,
    this.coefficients,
    this.noteDePassage,
    this.session,
    this.heure,
    this.jours,
  });

  factory Programme.fromJson(Map<String, dynamic> json) {
    return Programme(
      id: json['id'].toString(),
      coursNom: json['cours']?.toString(),
      coursId: (json['coursId'] ?? json['Cours_id'])?.toString(),
      niveauId: json['niveau_id']?.toString(),
      niveauName: json['niveau_name']?.toString(),
      professeurId: (json['profId'] ?? json['professeur_id'])?.toString(),
      professeurNom: json['professeur']?.toString(),
      classeId: (json['classId'] ?? json['class_'])?.toString(),
      classeNom: json['classe']?.toString(),
      faculteId: json['faculte_id']?.toString(),
      faculteNom: json['fac_name']?.toString(),
      anneeAcademiqueId: json['annee_academique_id']?.toString(),
      anneeAcademiqueNom: json['annee_academique']?.toString(),
      coefficients: (json['coefficients'] as num?)?.toDouble(),
      noteDePassage: (json['note_de_passage'] as num?)?.toDouble(),
      session: json['session']?.toString(),
      heure: json['heure']?.toString(),
      jours: json['jours']?.toString(),
    );
  }

  final String id;
  final String? coursNom;
  final String? coursId;
  final String? niveauId;
  final String? niveauName;
  final String? professeurId;
  final String? professeurNom;
  final String? classeId;
  final String? classeNom;
  final String? faculteId;
  final String? faculteNom;
  final String? anneeAcademiqueId;
  final String? anneeAcademiqueNom;
  final double? coefficients;
  final double? noteDePassage;
  final String? session;
  final String? heure;
  final String? jours;
}

/// Entrée légère pour le combo professeur (GET v1/prof-for-combo).
class ProfesseurCombo {
  ProfesseurCombo({required this.id, required this.nom, required this.prenom});
  factory ProfesseurCombo.fromJson(Map<String, dynamic> json) => ProfesseurCombo(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
        prenom: json['prenom']?.toString() ?? '',
      );
  final String id;
  final String nom;
  final String prenom;

  String get fullName => '$nom $prenom';
}

/// Entrée légère pour le combo cours (GET v1/for-combo-cours).
class CoursCombo {
  CoursCombo({required this.id, required this.coursNom});
  factory CoursCombo.fromJson(Map<String, dynamic> json) => CoursCombo(
        id: json['id'].toString(),
        coursNom: json['cours_nom']?.toString() ?? '',
      );
  final String id;
  final String coursNom;
}
