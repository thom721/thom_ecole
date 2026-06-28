import 'produit.dart';

double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Une ligne du panier en cours de saisie — équivalent d'une entrée de
/// `self.commande` (school_client, add_commande(), Controllers/Main.py:
/// 5357-5403), mais alimentée ici depuis un Produit déjà enregistré (clic
/// sur la liste de gauche) plutôt que tapée à la main à chaque vente.
class CartItem {
  CartItem({
    required this.nom,
    required this.category,
    required this.prix,
    required this.quantite,
    this.id,
    this.produitId,
    this.stockDisponible,
    this.status = 1,
  });

  factory CartItem.fromProduit(Produit produit, {required double quantite}) =>
      CartItem(
        nom: produit.nom,
        category: produit.category,
        prix: produit.prix,
        quantite: quantite,
        produitId: produit.id,
        stockDisponible: produit.quantiteStock,
      );

  /// Une ligne déjà enregistrée, chargée depuis GET v1/order-vente/{vente}
  /// (RVente.py show_order_items) pour l'édition d'une vente existante —
  /// `id` (l'OrderItem réel) permet à store_vente de la mettre à jour plutôt
  /// que d'en créer un doublon.
  factory CartItem.fromOrderItem(Map<String, dynamic> json) => CartItem(
    id: json['id']?.toString(),
    nom: json['nom']?.toString() ?? '',
    category: json['category']?.toString() ?? '',
    prix: _toDouble(json['prix']),
    quantite: _toDouble(json['quantite']),
    status: json['status'] == true || json['status'] == 1 ? 1 : 0,
    produitId: json['produit_id']?.toString(),
  );

  final String? id;
  final String nom;
  final String category;
  final double prix;
  double quantite;
  final String? produitId;
  // Pas final : une ligne chargée via fromOrderItem n'a pas le stock du
  // catalogue avant que VenteState.applyStockCaps() ne le résolve depuis
  // ProduitState (l'API order-vente/{vente} ne renvoie que le produit_id,
  // pas la fiche produit complète).
  double? stockDisponible;
  final int status;

  double get total => prix * quantite;

  Map<String, dynamic> toJson() => {
    if (id != null) 'id': id,
    'nom': nom,
    'category': category,
    'prix': prix,
    'quantite': quantite,
    'total': total,
    'status': status,
    if (produitId != null) 'produit_id': produitId,
  };
}

/// Une ligne de la liste des ventes déjà enregistrées — reflète VenteSchema
/// (ecole_nginx/app/Schemas/SVente.py:39-62), qui agrège déjà les
/// order_items d'une même vente (quantite/total sont des sommes).
class VenteRecord {
  VenteRecord({
    required this.id,
    required this.orderItemId,
    required this.nom,
    required this.quantite,
    required this.total,
    required this.utilisateur,
    required this.date,
    this.category,
    required this.etudiantId,
  });

  factory VenteRecord.fromJson(Map<String, dynamic> json) => VenteRecord(
    id: json['id'].toString(),
    orderItemId: json['order_itemId']?.toString() ?? '',
    nom: json['nom']?.toString() ?? '',
    quantite: _toDouble(json['quantite']),
    total: _toDouble(json['total']),
    utilisateur: json['utilisateur']?.toString() ?? '',
    date: json['date']?.toString() ?? '',
    category: json['category']?.toString(),
    etudiantId: json['etudiant_id']?.toString() ?? '',
  );

  final String id;
  final String orderItemId;
  final String nom;
  final double quantite;
  final double total;
  final String utilisateur;
  final String date;
  final String? category;
  final String etudiantId;
}
