/// Reflète PointagePersonneSchema (ecole_nginx/app/Schemas/SPointage.py) —
/// une ligne du jour pour un membre du personnel (Professeur ou Personnel).
class PointagePersonne {
  PointagePersonne({
    required this.userId,
    required this.nom,
    required this.prenom,
    required this.type,
    this.heureArrivee,
    this.heureDepart,
  });

  factory PointagePersonne.fromJson(Map<String, dynamic> json) => PointagePersonne(
    userId: json['user_id']?.toString() ?? '',
    nom: json['nom']?.toString() ?? '',
    prenom: json['prenom']?.toString() ?? '',
    type: json['type']?.toString() ?? '',
    heureArrivee: json['heure_arrivee']?.toString(),
    heureDepart: json['heure_depart']?.toString(),
  );

  final String userId;
  final String nom;
  final String prenom;
  final String type;
  final String? heureArrivee;
  final String? heureDepart;

  String get fullName => '$nom $prenom';
  bool get estProfesseur => type == 'App\\Models\\Professeur';
}

class PointageHistoriqueEntry {
  PointageHistoriqueEntry({
    required this.date,
    this.heureArrivee,
    this.heureDepart,
    this.dureeHeures,
  });

  factory PointageHistoriqueEntry.fromJson(Map<String, dynamic> json) => PointageHistoriqueEntry(
    date: json['date']?.toString() ?? '',
    heureArrivee: json['heure_arrivee']?.toString(),
    heureDepart: json['heure_depart']?.toString(),
    dureeHeures: json['duree_heures'] == null
        ? null
        : (json['duree_heures'] as num).toDouble(),
  );

  final String date;
  final String? heureArrivee;
  final String? heureDepart;
  final double? dureeHeures;
}
