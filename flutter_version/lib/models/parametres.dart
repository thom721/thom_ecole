/// Modèles de la page "Paramètres" (school_client: btn_settings →
/// settings_page(), Controllers/Main.py:13384) — 6 entités de configuration,
/// dont le style de liste/formulaire reprend exactement
/// ecole_nginx/frontend/src/views/admin/Parametres.vue (seul fichier
/// réellement routé pour "Paramètres", cf. router/index.js — les autres
/// "Parametres*copy*.vue" sont du code mort).
library;

num _toNum(Object? v) {
  if (v is num) return v;
  if (v is String) return num.tryParse(v) ?? 0;
  return 0;
}

/// Reflète AnneeAcademiqueResponse (ecole_nginx app/Schemas/SAnneeAcademique.py)
/// — endpoints v1/anneeAcademique (GET liste/POST create-update,
/// v1/delete-anneeAcademique/{id}), confirmés utilisés par school_client
/// (Models/AsyncDataHandler.py:635-650).
class AnneeAcademiqueRecord {
  AnneeAcademiqueRecord({
    required this.id,
    required this.dateDebut,
    required this.dateFin,
    required this.anneeAcademique,
    required this.status,
  });

  factory AnneeAcademiqueRecord.fromJson(Map<String, dynamic> json) {
    return AnneeAcademiqueRecord(
      id: json['id']?.toString() ?? '',
      dateDebut: json['date_debut']?.toString() ?? '',
      dateFin: json['date_fin']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      status: json['status'] == true || json['status'] == 1,
    );
  }

  final String id;
  final String dateDebut;
  final String dateFin;
  final String anneeAcademique;
  final bool status;
}

/// Reflète la ligne renvoyée par GET v1/classes (app/Routes/RClasses.py:32-40)
/// — id, niveau (nom), niveau_id, nom_classe.
class ClasseRecord {
  ClasseRecord({
    required this.id,
    required this.niveauId,
    required this.niveauName,
    required this.nomClasse,
  });

  factory ClasseRecord.fromJson(Map<String, dynamic> json) {
    return ClasseRecord(
      id: json['id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      niveauName: json['niveau']?.toString() ?? '',
      nomClasse: json['nom_classe']?.toString() ?? '',
    );
  }

  final String id;
  final String niveauId;
  final String niveauName;
  final String nomClasse;
}

/// Reflète AnneeAcademiqueResponse côté facultés (ecole_nginx
/// app/Routes/RAcademic.py:149-167, endpoint v1/faculte) — mêmes champs que
/// v1/post-faculte attend en écriture (nom, nb_annee).
class FaculteRecord {
  FaculteRecord({
    required this.id,
    required this.nom,
    required this.nbAnnee,
    required this.status,
  });

  factory FaculteRecord.fromJson(Map<String, dynamic> json) {
    return FaculteRecord(
      id: json['id']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      nbAnnee: json['nb_annee']?.toString() ?? '',
      status: json['status'] == true || json['status'] == 1,
    );
  }

  final String id;
  final String nom;
  final String nbAnnee;
  final bool status;
}

/// Reflète la ligne paginée de GET v1/paramsExam (app/Routes/RParamExam.py:54-65)
/// — id, name (niveau), niveau_id, evaluation_par, annee_academique(_id).
class ParamExamRecord {
  ParamExamRecord({
    required this.id,
    required this.niveauId,
    required this.niveauName,
    required this.anneeAcademiqueId,
    required this.anneeAcademique,
    required this.evaluationPar,
  });

  factory ParamExamRecord.fromJson(Map<String, dynamic> json) {
    return ParamExamRecord(
      id: json['id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      niveauName: json['name']?.toString() ?? '',
      anneeAcademiqueId: json['annee_academique_id']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      evaluationPar: json['evaluation_par']?.toString() ?? '',
    );
  }

  final String id;
  final String niveauId;
  final String niveauName;
  final String anneeAcademiqueId;
  final String anneeAcademique;
  final String evaluationPar;
}

/// Reflète FraisInscriptionResponse (ecole_nginx app/Schemas/SInscription.py)
/// — endpoints v1/fraisDinscription (GET/POST), pas de DELETE exposé côté
/// frontend web (le bouton "Supprimer" du tab Frais n'a pas de handler dans
/// Parametres.vue — pas reproduit ici non plus).
class FraisInscriptionRecord {
  FraisInscriptionRecord({
    required this.id,
    required this.niveauId,
    required this.niveauName,
    required this.anneeAc,
    required this.anneeAcademique,
    required this.prix,
  });

  factory FraisInscriptionRecord.fromJson(Map<String, dynamic> json) {
    return FraisInscriptionRecord(
      id: json['id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      niveauName: json['niveau']?.toString() ?? '',
      anneeAc: json['anneeAc']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      prix: _toNum(json['prix']),
    );
  }

  final String id;
  final String niveauId;
  final String niveauName;
  final String anneeAc;
  final String anneeAcademique;
  final num prix;
}

/// Reflète FraisDiversResponse — feature 100% bureau (school_client:
/// Helper/Components/Frais_divers.py, endpoints v1/frais-divers-store|index|
/// show-frais-divers|delete-frais_divers, RInscription.py), absente du
/// frontend web. `description` est toujours vide ici : ni get_frais_divers()
/// (RInscription.py:392-402) ni get_frais_inscription() (lignes 434-444) ne
/// renvoient ce champ (ils reconstruisent leur réponse à la main en omettant
/// `description`), donc même le bureau réel affiche un champ Description
/// vierge en édition malgré la valeur enregistrée en base.
class FraisDiversRecord {
  FraisDiversRecord({
    required this.id,
    required this.niveauId,
    required this.niveauName,
    required this.anneeAcId,
    required this.anneeAcademique,
    required this.prix,
    required this.description,
  });

  factory FraisDiversRecord.fromJson(Map<String, dynamic> json) {
    return FraisDiversRecord(
      id: json['id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      niveauName: json['niveau']?.toString() ?? '',
      anneeAcId: json['anneeAc']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      prix: _toNum(json['prix']),
      description: json['description']?.toString() ?? '',
    );
  }

  final String id;
  final String niveauId;
  final String niveauName;
  final String anneeAcId;
  final String anneeAcademique;
  final num prix;
  final String description;
}

class AccessoireConfig {
  AccessoireConfig({required this.typeDaccessoire, required this.prix});

  factory AccessoireConfig.fromJson(Map<String, dynamic> json) {
    return AccessoireConfig(
      typeDaccessoire: json['type_daccessoire']?.toString() ?? '',
      prix: _toNum(json['prix']),
    );
  }

  Map<String, dynamic> toJson() => {'type_daccessoire': typeDaccessoire, 'prix': prix};

  final String typeDaccessoire;
  final num prix;
}

/// Reflète la ligne renvoyée par GET v1/parametrePaiement (app/Routes/
/// RPaiementParam.py:138-172) — la config de paiement (échéance/montants/
/// accessoires) d'une classe pour une année académique donnée. C'est la
/// même structure `montant_par` (clé `<echeance>_<index>_<annee-uuid>`) que
/// celle déjà consommée en lecture par PaymentInfo (lib/models/paiement.dart).
class ParametrePaiementRecord {
  ParametrePaiementRecord({
    required this.id,
    required this.niveauId,
    required this.niveauName,
    required this.faculteId,
    required this.classeId,
    required this.nomClasse,
    required this.anneeAcademiqueId,
    required this.anneeAc,
    required this.echeance,
    required this.devise,
    required this.nbEcheance,
    required this.montant,
    required this.montantPar,
    required this.accessoires,
  });

  factory ParametrePaiementRecord.fromJson(Map<String, dynamic> json) {
    final montantParRaw = json['montant_par'];
    final montantPar = <String, num>{};
    // Le GET liste renvoie `montant_par` déjà sérialisé en str(dict) côté
    // serveur (RPaiementParam.py:158) — seul le GET par id renvoie un vrai
    // objet JSON exploitable ; on ne tente donc de le parser que si c'est
    // une Map (cas du formulaire d'édition, alimenté via le détail).
    if (montantParRaw is Map) {
      for (final entry in montantParRaw.entries) {
        final inner = entry.value;
        if (inner is Map) {
          for (final e in inner.entries) {
            montantPar[e.key.toString()] = _toNum(e.value);
          }
        }
      }
    }

    final accessoiresRaw = json['accessoires'];
    final accessoires = <AccessoireConfig>[];
    if (accessoiresRaw is List) {
      for (final a in accessoiresRaw) {
        if (a is Map<String, dynamic>) accessoires.add(AccessoireConfig.fromJson(a));
      }
    }

    return ParametrePaiementRecord(
      id: json['id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      niveauName: json['niveau_name']?.toString() ?? '',
      faculteId: json['faculte_id']?.toString(),
      classeId: json['classe']?.toString() ?? '',
      nomClasse: json['nom_classe']?.toString() ?? '',
      anneeAcademiqueId: json['anneeAcademique']?.toString() ?? '',
      anneeAc: json['anneeAc']?.toString() ?? '',
      echeance: json['echeance']?.toString() ?? '',
      devise: json['devise']?.toString() ?? '',
      nbEcheance: (json['nb_echeance'] as num?)?.toInt(),
      montant: json['montant'] == null ? null : _toNum(json['montant']),
      montantPar: montantPar,
      accessoires: accessoires,
    );
  }

  final String id;
  final String niveauId;
  final String niveauName;
  final String? faculteId;
  final String classeId;
  final String nomClasse;
  final String anneeAcademiqueId;
  final String anneeAc;
  final String echeance;
  final String devise;
  final int? nbEcheance;
  final num? montant;
  final Map<String, num> montantPar;
  final List<AccessoireConfig> accessoires;
}
