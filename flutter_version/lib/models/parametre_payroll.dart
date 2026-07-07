double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Reflète ParametrePayrollSchema (ecole_nginx/app/Schemas/SParametrePayroll.py)
/// — taux horaire d'un cours pour une année académique, utilisé pour
/// calculer le montant dû d'un professeur payé à l'heure.
class ParametrePayroll {
  ParametrePayroll({
    required this.id,
    required this.coursId,
    required this.coursNom,
    required this.tauxHoraire,
    required this.anneeAcademique,
    required this.anneeAcademiqueLabel,
  });

  factory ParametrePayroll.fromJson(Map<String, dynamic> json) => ParametrePayroll(
    id: json['id'].toString(),
    coursId: json['cours_id']?.toString() ?? '',
    coursNom: json['cours_nom']?.toString() ?? '',
    tauxHoraire: _toDouble(json['taux_horaire']),
    anneeAcademique: json['annee_academique']?.toString() ?? '',
    anneeAcademiqueLabel: json['annee_academique_label']?.toString() ?? '',
  );

  final String id;
  final String coursId;
  final String coursNom;
  final double tauxHoraire;
  // AnneeAcademique.id — même convention que Programme.annee_academique.
  final String anneeAcademique;
  final String anneeAcademiqueLabel;
}

/// Cours enseigné par un professeur pour une année (GET
/// v1/professeur/{id}/cours-payroll) — tauxHoraire null si aucun
/// ParametrePayroll n'est encore configuré pour ce cours/cette année.
class CoursPayrollOption {
  CoursPayrollOption({
    required this.coursId,
    required this.coursNom,
    this.tauxHoraire,
  });

  factory CoursPayrollOption.fromJson(Map<String, dynamic> json) => CoursPayrollOption(
    coursId: json['cours_id']?.toString() ?? '',
    coursNom: json['cours_nom']?.toString() ?? '',
    tauxHoraire: json['taux_horaire'] == null ? null : _toDouble(json['taux_horaire']),
  );

  final String coursId;
  final String coursNom;
  final double? tauxHoraire;
}
