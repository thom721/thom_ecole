double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Reflète DepenseSchema (ecole_nginx/app/Schemas/SVente.py:69-84) —
/// équivalent de depense_page()/enregistrer_depense() (school_client,
/// Controllers/Main.py:5122-5295) : une dépense simple (description + prix).
class DepenseRecord {
  DepenseRecord({
    required this.id,
    required this.description,
    required this.prix,
    this.userName,
    required this.date,
  });

  factory DepenseRecord.fromJson(Map<String, dynamic> json) => DepenseRecord(
        id: json['id'].toString(),
        description: json['description']?.toString() ?? '',
        prix: _toDouble(json['prix']),
        userName: json['user_name']?.toString(),
        date: json['date']?.toString() ?? '',
      );

  final String id;
  final String description;
  final double prix;
  final String? userName;
  final String date;
}
