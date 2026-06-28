double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Catalogue de produits vendables — nouveauté demandée explicitement par
/// l'utilisateur : ni le bureau (school_client, qui ne fait que taper un
/// nom/catégorie en texte libre à chaque vente, voir add_commande()) ni le
/// web n'ont jamais persisté de fiche produit. Reflète ProduitSchema
/// (ecole_nginx/app/Schemas/SProduit.py).
class Produit {
  Produit({
    required this.id,
    required this.nom,
    required this.category,
    required this.prix,
    required this.quantiteStock,
    this.description,
  });

  factory Produit.fromJson(Map<String, dynamic> json) => Produit(
    id: json['id'].toString(),
    nom: json['nom']?.toString() ?? '',
    category: json['category']?.toString() ?? '',
    prix: _toDouble(json['prix']),
    quantiteStock: _toDouble(json['quantite_stock']),
    description: json['description']?.toString(),
  );

  final String id;
  final String nom;
  final String category;
  final double prix;
  final double quantiteStock;
  final String? description;
}

/// Reflète CategorieProduitSchema (ecole_nginx/app/Schemas/
/// SCategorieProduit.py) — liste de catégories réellement gérable (créée
/// sur demande explicite : "on devait être capable d'ajouter une
/// catégorie aussi"), distincte de `categories` (Communauté), qui n'a
/// aucun rapport avec les produits.
class CategorieProduit {
  CategorieProduit({required this.id, required this.nom});

  factory CategorieProduit.fromJson(Map<String, dynamic> json) =>
      CategorieProduit(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
      );

  final String id;
  final String nom;
}
