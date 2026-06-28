/// Les colonnes JSON `paiement_details` (school_client/ecole_nginx) mêlent
/// des valeurs num et des valeurs str selon le point d'écriture (certains
/// champs sont sérialisés côté serveur comme chaînes) — on tolère les deux
/// plutôt que de planter avec un `as num?`.
num _toNum(Object? v) {
  if (v is num) return v;
  if (v is String) return num.tryParse(v) ?? 0;
  return 0;
}

/// Reflète PaiementResource (ecole_nginx app/Schemas/SPaiement.py) — une
/// ligne de la liste GET v1/paiement (un paiement = un étudiant pour une
/// année académique donnée).
class PaymentListItem {
  PaymentListItem({
    required this.id,
    required this.etudiantId,
    required this.identifiant,
    required this.nom,
    required this.prenom,
    required this.annee,
    required this.niveau,
    required this.classe,
  });

  factory PaymentListItem.fromJson(Map<String, dynamic> json) {
    return PaymentListItem(
      id: json['id']?.toString() ?? '',
      etudiantId: json['id_']?.toString() ?? '',
      identifiant: json['identifiant']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      annee: json['annee']?.toString() ?? '',
      niveau: json['niveaux']?.toString() ?? '',
      classe: json['classes']?.toString() ?? '',
    );
  }

  final String id;
  final String etudiantId;
  final String identifiant;
  final String nom;
  final String prenom;
  final String annee;
  final String niveau;
  final String classe;
}

/// Reflète StudentPaymentData (ecole_nginx app/Schemas/SPaiement.py) — le
/// contexte niveau/classe/année d'un étudiant, utilisé pour ensuite appeler
/// GET v1/next-payment-step (Routes/RPaiement.py:357).
class StudentPaymentContext {
  StudentPaymentContext({
    required this.studentId,
    required this.nom,
    required this.prenom,
    required this.identifiant,
    required this.nomClasse,
    required this.classeId,
    required this.niveauId,
    required this.niveauName,
    required this.anneeId,
    required this.anneeAcademique,
    this.faculteId,
  });

  factory StudentPaymentContext.fromJson(Map<String, dynamic> json) {
    return StudentPaymentContext(
      studentId: json['studentId']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      identifiant: json['identifiant']?.toString() ?? '',
      nomClasse: json['nom_classe']?.toString() ?? '',
      classeId: json['classeId']?.toString() ?? '',
      niveauId: json['niveauId']?.toString() ?? '',
      niveauName: json['name']?.toString() ?? '',
      anneeId: json['anneeId']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      faculteId: json['faculte_id']?.toString(),
    );
  }

  final String studentId;
  final String nom;
  final String prenom;
  final String identifiant;
  final String nomClasse;
  final String classeId;
  final String niveauId;
  final String niveauName;
  final String anneeId;
  final String anneeAcademique;
  final String? faculteId;
}

class Accessoire {
  Accessoire({required this.prix, required this.typeDaccessoire});

  factory Accessoire.fromJson(Map<String, dynamic> json) {
    return Accessoire(
      prix: _toNum(json['prix']).toDouble(),
      typeDaccessoire: json['type_daccessoire']?.toString() ?? '',
    );
  }

  final double prix;
  final String typeDaccessoire;
}

/// Une ligne d'échéance affichée dans le formulaire (équivalent des
/// "frame_echeance" générées dynamiquement dans Controllers/Main.py:12817-
/// 12889) : libellé ("1er Versement - (25000 GDES)" ou nom du mois), clé
/// brute (`Versement_1_<uuid>` ou `<mois>_<uuid>`), montant, et si elle est
/// déjà réglée (cochée/désactivée côté school_client).
class EcheanceRow {
  EcheanceRow({
    required this.key,
    required this.label,
    required this.montant,
    required this.paid,
  });

  final String key;
  final String label;
  final num montant;
  final bool paid;
}

/// Reflète PaymentInfoData (ecole_nginx app/Schemas/SPaiement.py) — réponse
/// de GET v1/next-payment-step (Routes/RPaiement.py:151) : configuration de
/// paiement de la classe + historique existant de l'étudiant le cas échéant.
class PaymentInfo {
  PaymentInfo({
    required this.studentId,
    required this.nom,
    required this.prenom,
    required this.aideFinanciere,
    required this.identifiant,
    required this.classeId,
    required this.nomClasse,
    required this.anneeAcademique,
    required this.anneeId,
    required this.echeance,
    required this.devise,
    required this.montantPar,
    required this.accessoires,
    required this.niveauName,
    required this.niveauId,
    required this.paiementDetails,
    required this.moisPayes,
  });

  factory PaymentInfo.fromJson(Map<String, dynamic> json) {
    final montantParRaw = json['montant_par'];
    final montantPar = <String, Map<String, num>>{};
    if (montantParRaw is Map) {
      for (final entry in montantParRaw.entries) {
        final inner = entry.value;
        if (inner is Map) {
          montantPar[entry.key.toString()] = inner.map(
            (k, v) => MapEntry(k.toString(), _toNum(v)),
          );
        }
      }
    }

    final accessoiresRaw = json['accessoires'];
    final accessoires = <Accessoire>[];
    if (accessoiresRaw is List) {
      for (final a in accessoiresRaw) {
        if (a is Map<String, dynamic>) accessoires.add(Accessoire.fromJson(a));
      }
    }

    final paiementDetailsRaw = json['paiement_details'];
    final paiementDetails = paiementDetailsRaw is Map
        ? Map<String, dynamic>.from(paiementDetailsRaw)
        : <String, dynamic>{};

    // `mois` au niveau racine (colonne Paiement.mois) est doublement
    // enveloppé en base — {"mois": {"Versement_1_xxx": 29500, ...}} — alors
    // que paiement_details.paiement_details.mois est la map À PLAT
    // directement utilisable (confirmé en base + lu par PaymentDetails.vue
    // via `d.paiement_details?.mois`, jamais le champ racine). Utiliser le
    // champ racine ici ferait passer moisPayes = {"mois"} et aucune échéance
    // ne serait jamais détectée comme payée.
    final innerDetailsRaw = paiementDetails['paiement_details'];
    final innerDetails = innerDetailsRaw is Map ? innerDetailsRaw : const {};
    final moisRaw = innerDetails['mois'];
    final moisPayes = <String>{};
    if (moisRaw is Map) {
      moisPayes.addAll(moisRaw.keys.map((k) => k.toString()));
    }

    return PaymentInfo(
      studentId: json['studentId']?.toString() ?? '',
      nom: json['nom']?.toString() ?? '',
      prenom: json['prenom']?.toString() ?? '',
      aideFinanciere: json['aide_financiere']?.toString() ?? 'Aucune',
      identifiant: json['identifiant']?.toString() ?? '',
      classeId: json['classeId']?.toString() ?? '',
      nomClasse: json['nom_classe']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      anneeId: json['id']?.toString() ?? '',
      echeance: json['echeance']?.toString() ?? '',
      devise: json['devise']?.toString() ?? '',
      montantPar: montantPar,
      accessoires: accessoires,
      niveauName: json['name']?.toString() ?? '',
      niveauId: json['id_niveau']?.toString() ?? '',
      paiementDetails: paiementDetails,
      moisPayes: moisPayes,
    );
  }

  final String studentId;
  final String nom;
  final String prenom;
  final String aideFinanciere;
  final String identifiant;
  final String classeId;
  final String nomClasse;
  final String anneeAcademique;
  final String anneeId;
  final String echeance;
  final String devise;
  final Map<String, Map<String, num>> montantPar;
  final List<Accessoire> accessoires;
  final String niveauName;
  final String niveauId;
  final Map<String, dynamic> paiementDetails;
  final Set<String> moisPayes;

  /// Équivalent du tri + libellé construits dans Controllers/Main.py:12810-
  /// 12843 : "1er/2ème/3ème Versement - (montant devise)" pour les échéances
  /// "Versement"/"Trimestre"/etc., ou le nom du mois pour echeance == "mois".
  List<EcheanceRow> get echeanceRows {
    final schedule = montantPar[echeance] ?? const {};
    final entries = schedule.entries.toList()
      ..sort((a, b) {
        final ai = int.tryParse(a.key.split('_')[1]) ?? 0;
        final bi = int.tryParse(b.key.split('_')[1]) ?? 0;
        return ai.compareTo(bi);
      });

    return List.generate(entries.length, (idx) {
      final entry = entries[idx];
      final paid = moisPayes.contains(entry.key);
      if (echeance == 'mois') {
        final moisName = entry.key.split('_').first;
        return EcheanceRow(
          key: entry.key,
          label: '$moisName ($devise)',
          montant: entry.value,
          paid: paid,
        );
      }
      final suffix = idx == 0 ? 'er' : 'ème';
      return EcheanceRow(
        key: entry.key,
        label: '${idx + 1}$suffix $echeance - (${entry.value} $devise)',
        montant: entry.value,
        paid: paid,
      );
    });
  }

  Map<String, dynamic> get _inner {
    final inner = paiementDetails['paiement_details'];
    return inner is Map
        ? Map<String, dynamic>.from(inner)
        : <String, dynamic>{};
  }

  /// Historique des versements déjà encaissés (paiement_details.info_paiement),
  /// trié chronologiquement — équivalent de show_payment() (Controllers/
  /// Main.py:9010-9090).
  List<MapEntry<String, dynamic>> get historique {
    final info = _inner['info_paiement'];
    if (info is! Map) return const [];
    final entries = info.entries
        .map((e) => MapEntry(e.key.toString(), e.value))
        .toList();
    entries.sort((a, b) => _parseDate(a.key).compareTo(_parseDate(b.key)));
    return entries;
  }

  /// Équivalent de `latest_entry` (PaymentDetails.vue, initPaymentLogic()) :
  /// le dernier versement encaissé qui n'a pas été "retourné" — sert à
  /// déterminer la bannière (acquitté / avance / rien).
  MapEntry<String, dynamic>? get _latestEntry {
    final entries = historique;
    for (var i = entries.length - 1; i >= 0; i--) {
      final value = entries[i].value;
      final status = value is Map ? value['status'] : null;
      if (status != 'retourné') return entries[i];
    }
    return null;
  }

  /// True si le dernier versement encaissé couvre déjà le montant annuel
  /// total — affiche le bandeau vert "✓ Acquitté" au lieu du formulaire de
  /// saisie (PaymentDetails.vue : `status.value = true`).
  bool get acquitte {
    final entry = _latestEntry;
    if (entry == null) return false;
    final value = entry.value;
    if (value is! Map) return false;
    final totalAnnuel = _toNum(value['total_annuel']);
    final totalVerse = _toNum(value['total_verse']);
    return totalAnnuel > 0 && totalVerse >= totalAnnuel;
  }

  /// Libellé de la bannière orange "Avance de X GDES sur le Nème Versement"
  /// (PaymentDetails.vue) — null si acquitté ou si aucun versement encaissé.
  /// Note : le "+2" dans le calcul de l'index n'est pas une faute de frappe
  /// de notre part — c'est exactement la formule du composant Vue réel,
  /// reproduite pour rester cohérent avec ce que voit déjà le caissier côté
  /// web.
  String? get avanceSurLabel {
    final entry = _latestEntry;
    if (entry == null || acquitte) return null;
    final value = entry.value;
    if (value is! Map) return null;
    final avanceMontant = _toNum(value['depot_et_avance'] ?? 0);

    if (moisPayes.isEmpty) {
      return 'Avance de $avanceMontant $devise sur le 1er Versement';
    }
    final latestPay = (moisPayes.toList()..sort()).last;
    final parts = latestPay.split('_');
    final type = parts.isNotEmpty ? parts[0] : 'Versement';
    final idx = (int.tryParse(parts.length > 1 ? parts[1] : '0') ?? 0) + 2;
    final suffix = idx == 1 ? 'er' : 'ème';
    return 'Avance de $avanceMontant $devise sur le $idx$suffix $type';
  }

  static DateTime _parseDate(String s) {
    final parts = s.split(' ');
    final dmy = parts[0].split('-');
    final hm = parts.length > 1 ? parts[1].split(':') : ['0', '0'];
    return DateTime(
      int.parse(dmy[2]),
      int.parse(dmy[1]),
      int.parse(dmy[0]),
      int.parse(hm[0]),
      int.parse(hm[1]),
    );
  }
}

/// Une transaction de l'historique (équivalent de `versementsInfo`, calculé
/// dans DetaisPaiement.vue:62-97) — un paiement encaissé à une date donnée,
/// enrichi pour l'affichage.
class VersementInfo {
  VersementInfo({
    required this.dateKey,
    required this.details,
    required this.index,
    required this.versementNum,
    required this.versementLabel,
    required this.montantDu,
    required this.avanceVal,
    required this.statusPaiement,
    required this.isRetourne,
    required this.isFinalAcquitte,
    required this.depot,
    required this.totalVerse,
    required this.balance,
    required this.devise,
    required this.remise,
    required this.employer,
    required this.editBy,
    required this.aideFinanciere,
    required this.totalAnnuel,
  });

  final String dateKey;
  final Map<String, dynamic> details;
  final int index;
  final int versementNum;
  final String versementLabel;
  final num montantDu;
  final num avanceVal;
  final List<String> statusPaiement;
  final bool isRetourne;
  final bool isFinalAcquitte;
  final num depot;
  final num totalVerse;
  final num balance;
  final String devise;
  final num remise;
  final String employer;
  final String editBy;
  final String aideFinanciere;
  final num totalAnnuel;

  /// Équivalent de `hasVersementKey()` (DetaisPaiement.vue:200-205).
  bool hasVersementKey(int n) {
    return details.keys.any((k) {
      final parts = k.split('_');
      return parts[0] == 'Versement' &&
          parts.length > 1 &&
          int.tryParse(parts[1]) == n;
    });
  }
}

/// Reflète PaiementResourceShow (ecole_nginx app/Schemas/SPaiement.py) —
/// réponse de GET v1/paiement/{id} : le dossier de paiement complet d'un
/// étudiant pour une année académique. Équivalent côté UI de
/// DetaisPaiement.vue (ecole_nginx/frontend/src/views/admin).
class PaymentDetail {
  PaymentDetail({
    required this.id,
    required this.etudiantId,
    required this.anneeAcademique,
    required this.niveauId,
    required this.classeId,
    required this.paiementDetails,
  });

  /// Équivalent du `paiement_details` interne (déjà dépouillé de son
  /// enveloppe `{paiement_details: {...}}`) — reçu tel quel par POST
  /// v1/student-specific-details (`p = paiement_info.get("paiement_details")`,
  /// ecole_nginx/app/Routes/Etudiants.py:958), à la différence de
  /// PaymentDetail.fromJson qui lit la colonne complète d'un Paiement.
  factory PaymentDetail.fromRawInner(Map<String, dynamic> inner) {
    return PaymentDetail(
      id: '',
      etudiantId: '',
      anneeAcademique: '',
      niveauId: '',
      classeId: '',
      paiementDetails: {'paiement_details': inner},
    );
  }

  factory PaymentDetail.fromJson(Map<String, dynamic> json) {
    final paiementDetailsRaw = json['paiement_details'];
    return PaymentDetail(
      id: json['id']?.toString() ?? '',
      etudiantId: json['etudiant_id']?.toString() ?? '',
      anneeAcademique: json['annee_academique']?.toString() ?? '',
      niveauId: json['niveau_id']?.toString() ?? '',
      classeId: json['classe']?.toString() ?? '',
      paiementDetails: paiementDetailsRaw is Map
          ? Map<String, dynamic>.from(paiementDetailsRaw)
          : <String, dynamic>{},
    );
  }

  final String id;
  final String etudiantId;
  final String anneeAcademique;
  final String niveauId;
  final String classeId;
  final Map<String, dynamic> paiementDetails;

  Map<String, dynamic> get _inner {
    final inner = paiementDetails['paiement_details'];
    return inner is Map
        ? Map<String, dynamic>.from(inner)
        : <String, dynamic>{};
  }

  Map<String, dynamic> get detailsEtudiant {
    final d = _inner['details_etudiant'];
    return d is Map ? Map<String, dynamic>.from(d) : <String, dynamic>{};
  }

  /// "1er Versement" → montant attendu, etc. — récapitulatif de l'échéancier
  /// (`check_echeance`, posé à la création par RSavePaiement.py).
  Map<String, num> get checkEcheance {
    final d = _inner['check_echeance'];
    if (d is! Map) return const {};
    return d.map((k, v) => MapEntry(k.toString(), _toNum(v)));
  }

  Map<String, dynamic> get _infoPaiementRaw {
    final d = _inner['info_paiement'];
    return d is Map ? Map<String, dynamic>.from(d) : <String, dynamic>{};
  }

  Set<String> get moisAcquittes {
    final d = _inner['mois'];
    return d is Map ? d.keys.map((k) => k.toString()).toSet() : <String>{};
  }

  static String _ordinal(int n) => n == 1
      ? '$n'
            'er'
      : '$n'
            'ème';

  static DateTime _parseDateKey(String s) {
    final m = RegExp(r'^(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2})').firstMatch(s);
    if (m == null) return DateTime(1970);
    return DateTime(
      int.parse(m.group(3)!),
      int.parse(m.group(2)!),
      int.parse(m.group(1)!),
      int.parse(m.group(4)!),
      int.parse(m.group(5)!),
    );
  }

  static int? _numFromLabel(String label) {
    final m = RegExp(r'^(\d+)').firstMatch(label);
    return m != null ? int.parse(m.group(1)!) : null;
  }

  /// Équivalent de `versementsInfo` (DetaisPaiement.vue:62-97) : historique
  /// trié chronologiquement (les clés JSON ne préservent pas l'ordre
  /// d'insertion), enrichi pour l'affichage.
  List<VersementInfo> get versements {
    final entries = _infoPaiementRaw.entries.toList()
      ..sort((a, b) => _parseDateKey(a.key).compareTo(_parseDateKey(b.key)));
    final echeances = checkEcheance;

    return List.generate(entries.length, (index) {
      final dateKey = entries[index].key;
      final detailsRaw = entries[index].value;
      final details = detailsRaw is Map
          ? Map<String, dynamic>.from(detailsRaw)
          : <String, dynamic>{};

      final versementKey = details.keys.firstWhere(
        (k) => k.startsWith('Versement_'),
        orElse: () => '',
      );
      final versementNum = versementKey.isNotEmpty
          ? int.tryParse(versementKey.split('_')[1]) ?? (index + 1)
          : index + 1;
      final versementLabel = '${_ordinal(versementNum)} Versement';
      final montantDu = echeances[versementLabel] ?? 0;

      num avanceVal = 0;
      final avanceRaw = details['avance'];
      if (avanceRaw is String) {
        avanceVal = avanceRaw
            .split('+')
            .fold<num>(0, (s, p) => s + (int.tryParse(p.trim()) ?? 0));
      } else if (avanceRaw is num) {
        avanceVal = avanceRaw;
      }

      final statusPaiementRaw = details['status_paiement'];
      final statusPaiement = statusPaiementRaw is List
          ? statusPaiementRaw.map((e) => e.toString()).toList()
          : <String>[];

      return VersementInfo(
        dateKey: dateKey,
        details: details,
        index: index,
        versementNum: versementNum,
        versementLabel: versementLabel,
        montantDu: montantDu,
        avanceVal: avanceVal,
        statusPaiement: statusPaiement,
        isRetourne: (details['return_by'] ?? '').toString().isNotEmpty,
        isFinalAcquitte: details['status'] == 'Acquitte',
        depot: _toNum(details['depot']),
        totalVerse: _toNum(details['total_verse']),
        balance: _toNum(details['balance']),
        devise: details['devise']?.toString() ?? 'GDES',
        remise: _toNum(details['remise']),
        employer: details['employer']?.toString() ?? '',
        editBy: details['edit_by']?.toString() ?? '',
        aideFinanciere: details['aide_financiere']?.toString() ?? '',
        totalAnnuel: _toNum(details['total_annuel']),
      );
    });
  }

  VersementInfo? get globalInfo =>
      versements.isNotEmpty ? versements.first : null;

  /// Équivalent de `versementStatusMap` (DetaisPaiement.vue:101-132) : statut
  /// par numéro de versement, fusion des clés `mois` acquittées et des
  /// libellés "Acqt:"/"Avns:" inscrits dans `status_paiement`.
  Map<int, String> get versementStatusMap {
    final map = <int, String>{};
    for (final key in moisAcquittes) {
      final parts = key.split('_');
      if (parts.length > 1) {
        final n = int.tryParse(parts[1]);
        if (n != null) map[n] = 'acquitte';
      }
    }
    for (final v in versements) {
      for (final sp in v.statusPaiement) {
        if (sp.startsWith('Acqt:')) {
          final n = _numFromLabel(sp.replaceFirst('Acqt: ', ''));
          if (n != null) map[n] = v.isRetourne ? 'retourne' : 'acquitte';
        }
        if (sp.startsWith('Avns:')) {
          final n = _numFromLabel(sp.replaceFirst('Avns: ', ''));
          if (n != null && !map.containsKey(n)) map[n] = 'avance';
        }
      }
    }
    return map;
  }

  String versementStatusLabel(int n) {
    switch (versementStatusMap[n]) {
      case 'acquitte':
        return 'Acquitte';
      case 'avance':
        return 'Avance';
      case 'retourne':
        return 'Retourne';
      default:
        return 'En attente';
    }
  }

  /// Clé du dernier versement non retourné — seul celui-ci peut être
  /// "retourné" (Returns.py:supprimer_dernier_paiement n'autorise que la
  /// dernière transaction).
  String? get lastNonReturnedKey {
    final sorted = _infoPaiementRaw.keys.toList()
      ..sort((a, b) => _parseDateKey(a).compareTo(_parseDateKey(b)));
    for (var i = sorted.length - 1; i >= 0; i--) {
      final entry = _infoPaiementRaw[sorted[i]];
      final status = entry is Map ? entry['status'] : null;
      if (status != 'retourné') return sorted[i];
    }
    return null;
  }
}
