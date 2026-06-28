/// Reflète ClasseDetailResponse (ecole_nginx app/Schemas/Dashboard.py) —
/// une ligne de la table affichée par toggle_show_students()/
/// show_student_number_in_classes() (Controllers/Main.py:7320-7343) quand on
/// clique sur le "+" de la carte Classe.
class ClasseDetail {
  ClasseDetail({
    required this.classeId,
    required this.niveauName,
    required this.nomClasse,
    required this.etudiantCount,
    required this.anneeAcademiqueId,
    this.professeur,
  });

  factory ClasseDetail.fromJson(Map<String, dynamic> json) {
    return ClasseDetail(
      classeId: json['classe_id']?.toString() ?? '',
      niveauName: json['niveau_name']?.toString() ?? '',
      nomClasse: json['nom_classe']?.toString() ?? '',
      etudiantCount: (json['etudiant_count'] as num?)?.toInt() ?? 0,
      anneeAcademiqueId: json['annee_academique_id']?.toString() ?? '',
      professeur: json['professeur']?.toString(),
    );
  }

  final String classeId;
  final String niveauName;
  final String nomClasse;
  final int etudiantCount;
  final String anneeAcademiqueId;
  final String? professeur;
}

/// Reflète DashboardResponse (ecole_nginx app/Routes/dashboard.py GET /dashboard).
class DashboardStats {
  DashboardStats({
    required this.etudiant,
    required this.personnel,
    required this.cours,
    required this.professeur,
    required this.faculte,
    required this.classes,
    required this.paiement,
    required this.devise,
    required this.classeDetails,
    this.idAnnee,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      etudiant: (json['etudiant'] as num?)?.toInt() ?? 0,
      personnel: (json['personnel'] as num?)?.toInt() ?? 0,
      cours: (json['cours'] as num?)?.toInt() ?? 0,
      professeur: (json['professeur'] as num?)?.toInt() ?? 0,
      faculte: (json['faculte'] as num?)?.toInt() ?? 0,
      classes: (json['classes'] as num?)?.toInt() ?? 0,
      paiement: (json['paiement'] as num?)?.toDouble() ?? 0.0,
      devise: json['devise']?.toString() ?? '',
      idAnnee: json['id_annee']?.toString(),
      classeDetails: ((json['classeDetails'] as List?) ?? const [])
          .map((e) => ClasseDetail.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  final int etudiant;
  final int personnel;
  final int cours;
  final int professeur;
  final int faculte;
  final int classes;
  final double paiement;
  final String devise;
  final String? idAnnee;
  final List<ClasseDetail> classeDetails;
}
