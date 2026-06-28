double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Reflète TransactionResponse (ecole_nginx/app/Routes/RTransaction.py) —
/// équivalent de autre_transaction()/sauvegarder_other_transaction()
/// (school_client, Controllers/Main.py:5013-5119).
class OtherTransactionRecord {
  OtherTransactionRecord({
    required this.id,
    required this.description,
    this.descriptionSupplementaire,
    required this.montant,
    required this.userId,
    this.utilisateur,
    this.etudiantId,
    this.etudiantNom,
    this.etudiantPrenom,
    required this.date,
  });

  factory OtherTransactionRecord.fromJson(Map<String, dynamic> json) {
    final etudiant = json['etudiant'] as Map<String, dynamic>?;
    return OtherTransactionRecord(
      id: json['id'].toString(),
      description: json['description']?.toString() ?? '',
      descriptionSupplementaire: json['description_supplementaire']?.toString(),
      montant: _toDouble(json['montant']),
      userId: json['user_id']?.toString() ?? '',
      utilisateur: json['utilisateur']?.toString(),
      etudiantId: etudiant?['id']?.toString(),
      etudiantNom: etudiant?['nom']?.toString(),
      etudiantPrenom: etudiant?['prenom']?.toString(),
      date: json['date']?.toString() ?? '',
    );
  }

  final String id;
  final String description;
  final String? descriptionSupplementaire;
  final double montant;
  final String userId;
  final String? utilisateur;
  final String? etudiantId;
  final String? etudiantNom;
  final String? etudiantPrenom;
  final String date;

  String get displayDescription =>
      description == 'Autre' && (descriptionSupplementaire?.isNotEmpty ?? false)
      ? descriptionSupplementaire!
      : description;

  String get etudiantLabel => (etudiantNom == null && etudiantPrenom == null)
      ? '—'
      : '${etudiantNom ?? ''} ${etudiantPrenom ?? ''}'.trim();
}
