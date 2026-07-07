double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Une ligne du bilan mensuel (GET v1/payroll/bilan-mensuel) — le Payroll
/// d'un professeur pour un mois/année donné s'il existe déjà, sinon
/// statut='Aucun' et les montants restent null.
class BilanMensuelRow {
  BilanMensuelRow({
    required this.professeurId,
    required this.nom,
    this.payrollId,
    this.montantDu,
    this.montantVerse,
    this.soldeRestant,
    required this.statut,
  });

  factory BilanMensuelRow.fromJson(Map<String, dynamic> json) => BilanMensuelRow(
    professeurId: json['professeur_id']?.toString() ?? '',
    nom: json['nom']?.toString() ?? '',
    payrollId: json['payroll_id']?.toString(),
    montantDu: json['montant_du'] == null ? null : _toDouble(json['montant_du']),
    montantVerse: json['montant_verse'] == null ? null : _toDouble(json['montant_verse']),
    soldeRestant: json['solde_restant'] == null ? null : _toDouble(json['solde_restant']),
    statut: json['statut']?.toString() ?? 'Aucun',
  );

  final String professeurId;
  final String nom;
  final String? payrollId;
  final double? montantDu;
  final double? montantVerse;
  final double? soldeRestant;
  final String statut;
}

/// Reflète PayrollVersementSchema (ecole_nginx/app/Schemas/SPayroll.py) —
/// un versement (partiel ou intégral) contre un Payroll.
class PayrollVersementRecord {
  PayrollVersementRecord({
    required this.id,
    required this.montant,
    required this.dateVersement,
    this.methodePaiement,
    this.note,
  });

  factory PayrollVersementRecord.fromJson(Map<String, dynamic> json) => PayrollVersementRecord(
    id: json['id'].toString(),
    montant: _toDouble(json['montant']),
    dateVersement: json['date_versement']?.toString() ?? '',
    methodePaiement: json['methode_paiement']?.toString(),
    note: json['note']?.toString(),
  );

  final String id;
  final double montant;
  final String dateVersement;
  final String? methodePaiement;
  final String? note;
}

/// Ligne de détail horaire (cours/heures/taux) figée au moment du calcul —
/// reflète l'entrée de `details_horaires` (JSON) sur Payroll.
class PayrollLigneHoraire {
  PayrollLigneHoraire({
    required this.coursId,
    required this.coursNom,
    required this.heures,
    required this.taux,
    required this.sousTotal,
  });

  factory PayrollLigneHoraire.fromJson(Map<String, dynamic> json) => PayrollLigneHoraire(
    coursId: json['cours_id']?.toString() ?? '',
    coursNom: json['cours_nom']?.toString() ?? '',
    heures: _toDouble(json['heures']),
    taux: _toDouble(json['taux']),
    sousTotal: _toDouble(json['sous_total']),
  );

  final String coursId;
  final String coursNom;
  final double heures;
  final double taux;
  final double sousTotal;
}

/// Reflète PayrollSchema (ecole_nginx/app/Schemas/SPayroll.py) — période de
/// salaire (mois/année) pour un Professeur/Personnel. `montant`/`montantDu`
/// est le total dû pour la période ; `remainingBalance`/`statut` reflètent
/// la progression au fil des versements (PayrollVersement), mirror du
/// module Prêts (LoanRecord/remainingBalance).
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
    required this.typeCalcul,
    this.montantDu,
    this.remainingBalance,
    this.detailsHoraires,
    this.heuresPointeesRef,
    this.versements = const [],
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
    typeCalcul: json['type_calcul']?.toString() ?? 'fixe',
    montantDu: json['montant_du'] == null ? null : _toDouble(json['montant_du']),
    remainingBalance: json['remaining_balance'] == null ? null : _toDouble(json['remaining_balance']),
    detailsHoraires: (json['details_horaires'] as List?)
        ?.map((e) => PayrollLigneHoraire.fromJson(e as Map<String, dynamic>))
        .toList(),
    heuresPointeesRef: json['heures_pointees_ref'] == null ? null : _toDouble(json['heures_pointees_ref']),
    versements: ((json['versements'] as List?) ?? const [])
        .map((e) => PayrollVersementRecord.fromJson(e as Map<String, dynamic>))
        .toList(),
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
  final String typeCalcul;
  final double? montantDu;
  final double? remainingBalance;
  final List<PayrollLigneHoraire>? detailsHoraires;
  final double? heuresPointeesRef;
  final List<PayrollVersementRecord> versements;
}
