double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Reflète PayrollSchema (ecole_nginx/app/Schemas/SPayroll.py) — versement
/// ponctuel de salaire à un Professeur/Personnel pour une période (mois +
/// année) donnée. Fonctionnalité absente du bureau et du web, ajoutée sur
/// demande explicite, sans notion de "salaire de base".
class PayrollRecord {
  PayrollRecord({
    required this.id,
    required this.userId,
    required this.user,
    required this.montant,
    required this.mois,
    required this.annee,
    required this.methodePaiement,
    required this.statut,
    this.dateVersement,
    required this.date,
  });

  factory PayrollRecord.fromJson(Map<String, dynamic> json) => PayrollRecord(
    id: json['id'].toString(),
    userId: json['user_id']?.toString() ?? '',
    user: json['user']?.toString() ?? '',
    montant: _toDouble(json['montant']),
    mois: json['mois']?.toString() ?? '',
    annee: json['annee']?.toString() ?? '',
    methodePaiement: json['methode_paiement']?.toString() ?? '',
    statut: json['statut']?.toString() ?? '',
    dateVersement: json['date_versement']?.toString(),
    date: json['date']?.toString() ?? '',
  );

  final String id;
  final String userId;
  final String user;
  final double montant;
  final String mois;
  final String annee;
  final String methodePaiement;
  final String statut;
  final String? dateVersement;
  final String date;
}
