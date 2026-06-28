/// `Programme.coefficients`/`note_de_passage` sont des colonnes String côté
/// serveur (app/Models/MRelations.py:165-166) ; `cours-etudiant-add-note`
/// renvoie `list_cours` comme des dicts bruts (non validés par un schéma
/// Pydantic, juste `Dict[str, Any]`), donc ces champs y arrivent en chaîne
/// ("2", "60"), pas en nombre — un `as num?` direct plante avec "type
/// 'String' is not a subtype of type 'num?'". On passe donc toujours par
/// `num.tryParse()` après conversion en chaîne.
double? _toDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString());
}

/// Reflète CoursEtudiantResponse (ecole_nginx/app/Schemas/cours_etudiant.py) —
/// une ligne de la liste "Notes" (un étudiant inscrit dans le module notes
/// pour une année académique donnée).
class CoursEtudiantRecord {
  CoursEtudiantRecord({
    required this.id,
    required this.identifiant,
    required this.fname,
    required this.lname,
    required this.anneeAcademique,
    this.niveauName,
    this.classeId,
    this.nomClasse,
    this.evaluationPar,
    this.facName,
  });

  factory CoursEtudiantRecord.fromJson(Map<String, dynamic> json) {
    return CoursEtudiantRecord(
      id: json['id'].toString(),
      identifiant: json['identifiant']?.toString() ?? '',
      fname: json['fname']?.toString() ?? '',
      lname: json['lname']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      niveauName: json['name']?.toString(),
      classeId: json['classe']?.toString(),
      nomClasse: json['nom_classe']?.toString(),
      evaluationPar: json['evaluation_par']?.toString(),
      facName: json['fac_name']?.toString(),
    );
  }

  final String id;
  final String identifiant;
  final String fname;
  final String lname;
  final String anneeAcademique;
  final String? niveauName;
  final String? classeId;
  final String? nomClasse;
  final String? evaluationPar;
  final String? facName;
}

/// Un étudiant retourné par POST v1/cours-etudiant-add-note (EtudiantNoteData).
class NoteSearchStudent {
  NoteSearchStudent({required this.id, required this.nom, required this.prenom, required this.identifiant});

  factory NoteSearchStudent.fromJson(Map<String, dynamic> json) => NoteSearchStudent(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
        prenom: json['prenom']?.toString() ?? '',
        identifiant: json['identifiant']?.toString() ?? '',
      );

  final String id;
  final String nom;
  final String prenom;
  final String identifiant;

  /// Saisie locale, jamais renvoyée par le serveur.
  double? note;
}

/// Infos du cours initialement recherché (CoursNoteData).
class NoteCoursInfo {
  NoteCoursInfo({
    required this.coursNom,
    this.session,
    this.noteDePassage,
    this.nomClasse,
    this.coefficients,
    this.typeMatiere,
    this.professeurId,
  });

  factory NoteCoursInfo.fromJson(Map<String, dynamic> json) => NoteCoursInfo(
        coursNom: json['cours_nom']?.toString() ?? '',
        session: json['session']?.toString(),
        noteDePassage: _toDouble(json['note_de_passage']),
        nomClasse: json['nom_classe']?.toString(),
        coefficients: _toDouble(json['coefficients']),
        typeMatiere: json['type_matiere']?.toString(),
        professeurId: json['professeur_id']?.toString(),
      );

  final String coursNom;
  final String? session;
  final double? noteDePassage;
  final String? nomClasse;
  final double? coefficients;
  final String? typeMatiere;
  final String? professeurId;
}

/// Une entrée de `list_cours` (les autres matières du programme de la classe,
/// pour le sélecteur "Changer de matière").
class NoteListCoursItem {
  NoteListCoursItem({
    required this.id,
    required this.coursNom,
    this.noteDePassage,
    this.coefficients,
    this.typeMatiere,
    this.professeurId,
  });

  factory NoteListCoursItem.fromJson(Map<String, dynamic> json) => NoteListCoursItem(
        id: json['id'].toString(),
        coursNom: json['cours_nom']?.toString() ?? '',
        noteDePassage: _toDouble(json['note_de_passage']),
        coefficients: _toDouble(json['coefficients']),
        typeMatiere: json['type_matiere']?.toString(),
        professeurId: json['professeur_id']?.toString(),
      );

  final String id;
  final String coursNom;
  final double? noteDePassage;
  final double? coefficients;
  final String? typeMatiere;
  final String? professeurId;
}

/// Résultat complet de POST v1/cours-etudiant-add-note (AddNoteResponse.datas).
class NoteSearchResult {
  NoteSearchResult({
    required this.students,
    required this.cours,
    required this.session,
    required this.listCours,
    required this.annee,
  });

  factory NoteSearchResult.fromJson(Map<String, dynamic> json) {
    return NoteSearchResult(
      students: ((json['result'] as List?) ?? const [])
          .map((e) => NoteSearchStudent.fromJson(e as Map<String, dynamic>))
          .toList(),
      cours: NoteCoursInfo.fromJson((json['cours'] as Map<String, dynamic>?) ?? const {}),
      session: json['session']?.toString(),
      listCours: ((json['list_cours'] as List?) ?? const [])
          .map((e) => NoteListCoursItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      annee: json['annee']?.toString() ?? '',
    );
  }

  final List<NoteSearchStudent> students;
  final NoteCoursInfo cours;
  final String? session;
  final List<NoteListCoursItem> listCours;
  final String annee;
}
