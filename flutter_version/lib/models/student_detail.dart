import 'paiement.dart';

/// Modèles du profil complet d'un étudiant — onglet "Détails" de
/// Ajout_etudiant.vue (ecole_nginx/frontend), absent de school_client,
/// ajouté sur demande explicite ("comme le web"). Reflète EtudiantResponse
/// (ecole_nginx/app/Schemas/Etudiants.py:53-83), GET v1/etudiant/{id}.

/// Reflète ClasseEtudiantSchema — une inscription (étudiant × classe ×
/// année) avec ses relations dénormalisées pour l'affichage.
class ClasseEtudiantEntry {
  ClasseEtudiantEntry({
    required this.classesId,
    required this.niveauId,
    required this.anneeAcademiqueId,
    required this.createdAt,
    required this.nomClasse,
    required this.anneeLabel,
  });

  factory ClasseEtudiantEntry.fromJson(Map<String, dynamic> json) {
    final classes = json['classes'] as Map<String, dynamic>?;
    final annee = json['annee_academiques'] as Map<String, dynamic>?;
    return ClasseEtudiantEntry(
      classesId: json['classes_id']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      anneeAcademiqueId: json['annee_academique_id']?.toString() ?? '',
      createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ?? DateTime(1970),
      nomClasse: classes?['nom_classe']?.toString() ?? '',
      anneeLabel: annee?['annee_academique']?.toString() ?? '',
    );
  }

  final String classesId;
  final String niveauId;
  final String anneeAcademiqueId;
  final DateTime createdAt;
  final String nomClasse;
  final String anneeLabel;
}

/// Reflète PieceSoumiseResponse (ecole_nginx/app/Schemas/Etudiants.py:150-176).
class PieceSoumise {
  PieceSoumise({
    required this.typeDeDocument,
    required this.documentNumero,
    required this.dateExpiration,
    required this.status,
    required this.imageBase64,
  });

  factory PieceSoumise.fromJson(Map<String, dynamic> json) => PieceSoumise(
        typeDeDocument: json['type_de_document']?.toString() ?? '',
        documentNumero: json['document_numero']?.toString() ?? '',
        dateExpiration: json['document_date_dexpiration']?.toString() ?? '',
        status: json['document_status']?.toString() ?? '',
        // Le champ utilisé par Ajout_etudiant.vue pour la vignette
        // (`document_image_url`) n'existe pas dans PieceSoumiseResponse — la
        // vignette n'apparaît donc jamais côté web. On utilise ici le champ
        // réellement renvoyé.
        imageBase64: json['document_image_base64']?.toString(),
      );

  final String typeDeDocument;
  final String documentNumero;
  final String dateExpiration;
  final String status;
  final String? imageBase64;
}

/// Reflète un élément de `parcours` renvoyé par POST
/// v1/student-specific-details (ecole_nginx/app/Routes/Etudiants.py:889-958).
class ParcoursAnalyse {
  ParcoursAnalyse({
    required this.annee,
    required this.classe,
    required this.moyenneGen,
    this.topNom,
    this.topMoy,
    this.lowNom,
    this.lowMoy,
  });

  factory ParcoursAnalyse.fromJson(Map<String, dynamic> json) {
    final top = json['top'] as Map<String, dynamic>?;
    final low = json['low'] as Map<String, dynamic>?;
    return ParcoursAnalyse(
      annee: json['annee']?.toString() ?? '',
      classe: json['classe']?.toString() ?? '',
      moyenneGen: (json['moyenne_gen'] as num?)?.toDouble() ?? 0,
      topNom: top?['nom']?.toString(),
      topMoy: (top?['moy'] as num?)?.toDouble(),
      lowNom: low?['nom']?.toString(),
      lowMoy: (low?['moy'] as num?)?.toDouble(),
    );
  }

  final String annee;
  final String classe;
  final double moyenneGen;
  final String? topNom;
  final double? topMoy;
  final String? lowNom;
  final double? lowMoy;
}

/// Réponse de POST v1/student-specific-details pour un (classe, année)
/// donné : moyennes de l'année + suivi financier (même structure JSON que
/// paiement_details, réutilisée via PaymentDetail.fromRawInner).
class ParcoursDetails {
  ParcoursDetails({required this.analyses, required this.paiement});

  factory ParcoursDetails.fromJson(Map<String, dynamic> json) {
    final paiementRaw = json['paiement_details'];
    return ParcoursDetails(
      analyses: ((json['parcours'] as List?) ?? const [])
          .map((e) => ParcoursAnalyse.fromJson(e as Map<String, dynamic>))
          .toList(),
      paiement: PaymentDetail.fromRawInner(paiementRaw is Map ? Map<String, dynamic>.from(paiementRaw) : const {}),
    );
  }

  final List<ParcoursAnalyse> analyses;
  final PaymentDetail paiement;
}

/// Profil complet — GET v1/etudiant/{id} (StudentShowResponse.data).
class StudentDetail {
  StudentDetail({
    required this.id,
    required this.identifiant,
    required this.nom,
    required this.prenom,
    required this.sexe,
    required this.dateDeNaissance,
    required this.telephone,
    required this.email,
    required this.adresse,
    required this.lieuDeNaissance,
    required this.photoBase64,
    required this.userStatus,
    required this.nomResponsable,
    required this.prenomResponsable,
    required this.emailResponsable,
    required this.relationResponsable,
    required this.sexeResponsable,
    required this.telephoneResponsable,
    required this.metierResponsable,
    required this.adresseResponsable,
    required this.classesEtudiant,
    required this.piecesSoumises,
  });

  factory StudentDetail.fromJson(Map<String, dynamic> json) {
    // `responsable` est typé Optional[ResponsableResponse] mais avec un
    // défaut `[]` côté backend (incohérence du schéma d'origine) — on
    // accepte donc aussi bien un objet qu'une liste (premier élément).
    Map<String, dynamic>? responsable;
    final responsableRaw = json['responsable'];
    if (responsableRaw is Map) {
      responsable = Map<String, dynamic>.from(responsableRaw);
    } else if (responsableRaw is List && responsableRaw.isNotEmpty) {
      responsable = responsableRaw.first as Map<String, dynamic>;
    }

    final user = json['user'] as Map<String, dynamic>?;

    return StudentDetail(
      id: json['id']?.toString() ?? '',
      identifiant: json['identifiant']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      sexe: json['sexe']?.toString() ?? '',
      dateDeNaissance: json['date_de_naissance']?.toString() ?? '',
      telephone: json['telephone']?.toString(),
      email: json['email']?.toString(),
      adresse: json['adresse']?.toString() ?? '',
      lieuDeNaissance: json['lieu_de_naissance']?.toString(),
      photoBase64: json['photo_base64']?.toString(),
      userStatus: user?['status']?.toString(),
      nomResponsable: responsable?['nom_responsable']?.toString(),
      prenomResponsable: responsable?['prenom_responsable']?.toString(),
      emailResponsable: responsable?['email_responsable']?.toString(),
      relationResponsable: responsable?['relation_responsable']?.toString(),
      sexeResponsable: responsable?['sexe_responsable']?.toString(),
      telephoneResponsable: responsable?['telephone_responsable']?.toString(),
      metierResponsable: responsable?['metier_responsable']?.toString(),
      adresseResponsable: responsable?['adresse_responsable']?.toString(),
      classesEtudiant: ((json['classes_etudiant'] as List?) ?? const [])
          .map((e) => ClasseEtudiantEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
      piecesSoumises: ((json['pieces_soumises'] as List?) ?? const [])
          .map((e) => PieceSoumise.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  final String id;
  final String identifiant;
  final String nom;
  final String prenom;
  final String sexe;
  final String dateDeNaissance;
  final String? telephone;
  final String? email;
  final String adresse;
  final String? lieuDeNaissance;
  final String? photoBase64;
  final String? userStatus;
  final String? nomResponsable;
  final String? prenomResponsable;
  final String? emailResponsable;
  final String? relationResponsable;
  final String? sexeResponsable;
  final String? telephoneResponsable;
  final String? metierResponsable;
  final String? adresseResponsable;
  final List<ClasseEtudiantEntry> classesEtudiant;
  final List<PieceSoumise> piecesSoumises;

  /// Équivalent de `classe_actuelle_` (Ajout_etudiant.vue) : la classe la
  /// plus récente, triée par date de création (faute de champ "actif").
  ClasseEtudiantEntry? get classeActuelle {
    if (classesEtudiant.isEmpty) return null;
    final sorted = [...classesEtudiant]..sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return sorted.first;
  }
}
