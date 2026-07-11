/// Reflète AnnulationArriereResponse (ecole_nginx app/Schemas/
/// SAnnulationArriere.py) — une dérogation manuelle et réversible au
/// blocage d'arriéré d'année précédente (voir RSavePaiement.py:
/// _check_arrears_previous_year). Ne représente jamais une modification de
/// Paiement.paiement_details — l'historique de paiement reste intact.
class AnnulationArriere {
  AnnulationArriere({
    required this.id,
    required this.etudiantId,
    required this.anneeAcademiqueId,
    required this.anneeAcademique,
    required this.typeAnnulation,
    required this.montantAnnule,
    required this.ordonnePar,
    required this.ordonneParFonction,
    required this.executantNom,
    this.executantRole,
    required this.raison,
    required this.statut,
    this.annuleLe,
    this.annuleRaison,
    this.createdAt,
  });

  factory AnnulationArriere.fromJson(Map<String, dynamic> json) {
    return AnnulationArriere(
      id: json['id']?.toString() ?? '',
      etudiantId: json['etudiant_id']?.toString() ?? '',
      anneeAcademiqueId: json['annee_academique_id']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      typeAnnulation: json['type_annulation']?.toString() ?? '',
      montantAnnule: (json['montant_annule'] as num?)?.toDouble() ?? 0,
      ordonnePar: json['ordonne_par']?.toString() ?? '',
      ordonneParFonction: json['ordonne_par_fonction']?.toString() ?? '',
      executantNom: json['executant_nom']?.toString() ?? '',
      executantRole: json['executant_role']?.toString(),
      raison: json['raison']?.toString() ?? '',
      statut: json['statut']?.toString() ?? '',
      annuleLe: json['annule_le']?.toString(),
      annuleRaison: json['annule_raison']?.toString(),
      createdAt: json['created_at']?.toString(),
    );
  }

  final String id;
  final String etudiantId;
  final String anneeAcademiqueId;
  final String anneeAcademique;
  final String typeAnnulation;
  final double montantAnnule;
  final String ordonnePar;
  final String ordonneParFonction;
  final String executantNom;
  final String? executantRole;
  final String raison;
  final String statut;
  final String? annuleLe;
  final String? annuleRaison;
  final String? createdAt;

  bool get estActive => statut == 'actif';
}
