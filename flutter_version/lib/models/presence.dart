/// Reflète la réponse de GET /api/v1/classes/{classe_id}/etudiants
/// (ecole_nginx/app/Routes/RPresences.py) — élève d'une classe pour
/// l'appel du jour, avec sa valeur de présence du jour (null = non marqué).
class PresenceStudent {
  PresenceStudent({
    required this.id,
    required this.nom,
    required this.prenom,
    this.matricule,
    this.valeur,
  });

  factory PresenceStudent.fromJson(Map<String, dynamic> json) =>
      PresenceStudent(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
        prenom: json['prenom']?.toString() ?? '',
        matricule: json['matricule']?.toString(),
      );

  final String id;
  final String nom;
  final String prenom;
  final String? matricule;
  bool? valeur;

  String get fullName => '$nom $prenom';

  String get initiales {
    final n = nom.isNotEmpty ? nom[0] : '';
    final p = prenom.isNotEmpty ? prenom[0] : '';
    return '$n$p'.toUpperCase();
  }
}

/// Reflète une ligne de GET /api/v1/presences/historique.
class PresenceHistoriqueRecord {
  PresenceHistoriqueRecord({
    required this.id,
    required this.nom,
    required this.classe,
    required this.absences,
    required this.retards,
    required this.taux,
  });

  factory PresenceHistoriqueRecord.fromJson(Map<String, dynamic> json) =>
      PresenceHistoriqueRecord(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
        classe: json['classe']?.toString() ?? '—',
        absences: (json['absences'] as num?)?.toInt() ?? 0,
        retards: (json['retards'] as num?)?.toInt() ?? 0,
        taux: (json['taux'] as num?)?.toDouble() ?? 0,
      );

  final String id;
  final String nom;
  final String classe;
  final int absences;
  final int retards;
  final double taux;
}

/// Reflète la clé "classes" de GET /api/v1/stats-presence-aujourdhui.
class PresenceClasseStat {
  PresenceClasseStat({
    required this.classe,
    required this.presents,
    required this.total,
    required this.val,
  });

  factory PresenceClasseStat.fromJson(Map<String, dynamic> json) =>
      PresenceClasseStat(
        classe: json['classe']?.toString() ?? '',
        presents: (json['presents'] as num?)?.toInt() ?? 0,
        total: (json['total'] as num?)?.toInt() ?? 0,
        val: (json['val'] as num?)?.toDouble() ?? 0,
      );

  final String classe;
  final int presents;
  final int total;
  final double val;
}

/// Reflète la clé "global" de GET /api/v1/stats-presence-aujourdhui — pas
/// de notion de retard dans le modèle (Presence.valeur est un Boolean),
/// donc toujours 0 (cf. RPresences.py).
class PresenceStatsGlobal {
  PresenceStatsGlobal({
    required this.tauxPresence,
    required this.totalInscrits,
    required this.absents,
    required this.retards,
  });

  factory PresenceStatsGlobal.fromJson(Map<String, dynamic> json) =>
      PresenceStatsGlobal(
        tauxPresence: (json['taux_presence'] as num?)?.toDouble() ?? 0,
        totalInscrits: (json['total_inscrits'] as num?)?.toInt() ?? 0,
        absents: (json['absents'] as num?)?.toInt() ?? 0,
        retards: (json['retards'] as num?)?.toInt() ?? 0,
      );

  final double tauxPresence;
  final int totalInscrits;
  final int absents;
  final int retards;
}
