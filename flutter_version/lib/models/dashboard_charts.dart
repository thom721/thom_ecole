/// Modèles pour les 2 panneaux de statistiques accessibles depuis le
/// Dashboard (DashboardStudentStats.vue / PaiementsStats.vue,
/// ecole_nginx/frontend/src/components) — fonctionnalités du frontend web
/// sans équivalent dans school_client, ajoutées sur demande explicite.

num _toNum(Object? v) {
  if (v == null) return 0;
  if (v is num) return v;
  return num.tryParse(v.toString()) ?? 0;
}

/// Une feuille du drill-down (niveau ou classe) — reflète les objets
/// `{niveau:{id,nom}, total, garcons, filles, classes:[...]}` et
/// `{classe:{id,nom}, total, garcons, filles}` de GET v1/stats/etudiants
/// (ecole_nginx/app/Routes/dashboard.py:285-417).
class EtudiantStatsNode {
  EtudiantStatsNode({
    required this.id,
    required this.nom,
    required this.total,
    required this.garcons,
    required this.filles,
    this.children = const [],
  });

  final String id;
  final String nom;
  final int total;
  final int garcons;
  final int filles;
  final List<EtudiantStatsNode> children;
}

/// Le niveau racine du drill-down : une année académique. `nom` n'utilise
/// PAS le champ `annee.libelle` renvoyé par le serveur — celui-ci vaut
/// toujours "—" côté backend (getattr sur des attributs `libelle`/`nom` qui
/// n'existent pas sur le modèle AnneeAcademique, qui n'a que
/// `annee_academique`) ; on résout plutôt le libellé nous-mêmes via les
/// données de référence déjà chargées (ReferenceDataState/ParametresState).
class EtudiantStatsAnnee extends EtudiantStatsNode {
  EtudiantStatsAnnee({
    required super.id,
    required super.nom,
    required super.total,
    required super.garcons,
    required super.filles,
    required super.children,
  });

  factory EtudiantStatsAnnee.fromJson(Map<String, dynamic> json, String Function(String) resolveAnneeLabel) {
    final anneeId = (json['annee'] as Map<String, dynamic>?)?['id']?.toString() ?? '';
    final niveaux = ((json['niveaux'] as List?) ?? const [])
        .map((n) => _niveauFromJson(n as Map<String, dynamic>))
        .toList();
    return EtudiantStatsAnnee(
      id: anneeId,
      nom: resolveAnneeLabel(anneeId),
      total: _toNum(json['total']).toInt(),
      garcons: _toNum(json['garcons']).toInt(),
      filles: _toNum(json['filles']).toInt(),
      children: niveaux,
    );
  }

  static EtudiantStatsNode _niveauFromJson(Map<String, dynamic> json) {
    final niveau = json['niveau'] as Map<String, dynamic>?;
    final classes = ((json['classes'] as List?) ?? const [])
        .map((c) => _classeFromJson(c as Map<String, dynamic>))
        .toList();
    return EtudiantStatsNode(
      id: niveau?['id']?.toString() ?? '',
      nom: niveau?['nom']?.toString() ?? '',
      total: _toNum(json['total']).toInt(),
      garcons: _toNum(json['garcons']).toInt(),
      filles: _toNum(json['filles']).toInt(),
      children: classes,
    );
  }

  static EtudiantStatsNode _classeFromJson(Map<String, dynamic> json) {
    final classe = json['classe'] as Map<String, dynamic>?;
    return EtudiantStatsNode(
      id: classe?['id']?.toString() ?? '',
      nom: classe?['nom']?.toString() ?? '',
      total: _toNum(json['total']).toInt(),
      garcons: _toNum(json['garcons']).toInt(),
      filles: _toNum(json['filles']).toInt(),
    );
  }
}

/// Un versement individuel — détail d'un mois (PaiementsStats.vue) ou
/// d'un jour, selon l'endpoint.
class PaiementVersementDetail {
  PaiementVersementDetail({required this.label, required this.depot, this.devise, this.employer, this.aide});

  factory PaiementVersementDetail.fromMonthJson(Map<String, dynamic> json) => PaiementVersementDetail(
        label: json['date']?.toString() ?? '',
        depot: _toNum(json['depot']),
        devise: json['devise']?.toString(),
        employer: json['employer']?.toString(),
        aide: json['aide']?.toString(),
      );

  factory PaiementVersementDetail.fromDayJson(Map<String, dynamic> json) => PaiementVersementDetail(
        label: json['heure']?.toString() ?? '',
        depot: _toNum(json['depot']),
        employer: json['employer']?.toString(),
      );

  final String label;
  final num depot;
  final String? devise;
  final String? employer;
  final String? aide;
}

/// Reflète un élément de `mois` dans GET v1/paiements/stats/annuel
/// (ecole_nginx/app/Routes/dashboard.py:1008-1099).
class PaiementMoisStat {
  PaiementMoisStat({
    required this.moisKey,
    required this.mois,
    required this.total,
    required this.nbVersements,
    required this.devise,
    required this.details,
  });

  factory PaiementMoisStat.fromJson(Map<String, dynamic> json) => PaiementMoisStat(
        moisKey: json['mois_key']?.toString() ?? '',
        mois: json['mois']?.toString() ?? '',
        total: _toNum(json['total']),
        nbVersements: _toNum(json['nb_versements']).toInt(),
        devise: json['devise']?.toString() ?? '',
        details: ((json['details'] as List?) ?? const [])
            .map((d) => PaiementVersementDetail.fromMonthJson(d as Map<String, dynamic>))
            .toList(),
      );

  final String moisKey;
  final String mois;
  final num total;
  final int nbVersements;
  final String devise;
  final List<PaiementVersementDetail> details;
}

/// Reflète GET v1/paiements/stats/annuel — totaux par mois pour une année
/// académique donnée.
class PaiementAnnuelStats {
  PaiementAnnuelStats({
    required this.annee,
    required this.devise,
    required this.totalAnnuel,
    required this.nbMois,
    required this.mois,
  });

  factory PaiementAnnuelStats.fromJson(Map<String, dynamic> json) => PaiementAnnuelStats(
        annee: json['annee']?.toString() ?? '',
        devise: json['devise']?.toString() ?? '',
        totalAnnuel: _toNum(json['total_annuel']),
        nbMois: _toNum(json['nb_mois']).toInt(),
        mois: ((json['mois'] as List?) ?? const [])
            .map((m) => PaiementMoisStat.fromJson(m as Map<String, dynamic>))
            .toList(),
      );

  final String annee;
  final String devise;
  final num totalAnnuel;
  final int nbMois;
  final List<PaiementMoisStat> mois;

  int get totalVersements => mois.fold(0, (s, m) => s + m.nbVersements);
}

/// Reflète un élément de `jours` dans GET v1/paiements/stats/journalier.
class PaiementJourStat {
  PaiementJourStat({required this.date, required this.total, required this.nbVersements, required this.details});

  factory PaiementJourStat.fromJson(Map<String, dynamic> json) => PaiementJourStat(
        date: json['date']?.toString() ?? '',
        total: _toNum(json['total']),
        nbVersements: _toNum(json['nb_versements']).toInt(),
        details: ((json['depot_details'] as List?) ?? const [])
            .map((d) => PaiementVersementDetail.fromDayJson(d as Map<String, dynamic>))
            .toList(),
      );

  final String date;
  final num total;
  final int nbVersements;
  final List<PaiementVersementDetail> details;
}

/// Reflète GET v1/paiements/stats/journalier (ecole_nginx/app/Routes/
/// dashboard.py:1114-1168) — drill-down jour par jour pour un mois donné.
class PaiementJournalierStats {
  PaiementJournalierStats({required this.mois, required this.total, required this.jours});

  factory PaiementJournalierStats.fromJson(Map<String, dynamic> json) => PaiementJournalierStats(
        mois: json['mois']?.toString() ?? '',
        total: _toNum(json['total']),
        jours: ((json['jours'] as List?) ?? const [])
            .map((j) => PaiementJourStat.fromJson(j as Map<String, dynamic>))
            .toList(),
      );

  final String mois;
  final num total;
  final List<PaiementJourStat> jours;
}

/// Reflète EtudiantClasseResponse (ecole_nginx/app/Schemas/
/// ClassesByStudent.py:36-53) — une ligne de la modale "Gérer" d'une classe
/// (équivalent de show_student_number_in_classes()/on_row_clicked_class_show(),
/// Controllers/Main.py:7332-7350, et du dialogue "Liste des élèves de la
/// classe" construit dans handle_request_completion() pour
/// "v1/student-with-classe", Controllers/Main.py:2883+).
class ClasseStudentRow {
  ClasseStudentRow({
    required this.id,
    required this.identifiant,
    required this.nom,
    required this.prenom,
    required this.sexe,
    required this.idClsEtudiant,
    required this.statusClsEtudiant,
  });

  factory ClasseStudentRow.fromJson(Map<String, dynamic> json) => ClasseStudentRow(
        id: json['id']?.toString() ?? '',
        identifiant: json['identifiant']?.toString() ?? '',
        nom: json['nom']?.toString() ?? '',
        prenom: json['prenom']?.toString() ?? '',
        sexe: json['sexe']?.toString() ?? '',
        idClsEtudiant: json['id_cls_etudiant']?.toString() ?? '',
        statusClsEtudiant: json['status_cls_etudiant'] == true,
      );

  final String id;
  final String identifiant;
  final String nom;
  final String prenom;
  final String sexe;

  /// UUID de l'enregistrement classes_etudiants (colonne cachée côté
  /// bureau, `setColumnHidden(5, True)`) — c'est cet id, pas celui de
  /// l'étudiant, qu'attend PATCH v1/update-etudiant-classe.
  final String idClsEtudiant;

  /// Colonne cachée côté bureau (`setColumnHidden(6, True)`), lue pour
  /// initialiser la case "Actif".
  final bool statusClsEtudiant;
}
