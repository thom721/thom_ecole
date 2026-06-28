/// Reflète CoursResponse (ecole_nginx app/Schemas/cours_schema.py:41-61).
class Cours {
  Cours({
    required this.id,
    required this.coursNom,
    required this.typeMatiere,
    this.noteDePassage,
    this.coefficients,
    this.niveauId,
    this.date,
  });

  factory Cours.fromJson(Map<String, dynamic> json) {
    return Cours(
      id: json['id']?.toString() ?? '',
      coursNom: json['cours_nom']?.toString() ?? '',
      typeMatiere: json['type_matiere']?.toString() ?? '',
      noteDePassage: json['note_de_passage']?.toString(),
      coefficients: json['coefficients']?.toString(),
      niveauId: json['niveau_id']?.toString(),
      date: json['date']?.toString(),
    );
  }

  final String id;
  final String coursNom;
  final String typeMatiere;
  final String? noteDePassage;
  final String? coefficients;
  final String? niveauId;
  final String? date;
}
