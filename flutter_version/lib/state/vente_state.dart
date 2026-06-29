import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../core/dual_auth.dart';
import '../models/produit.dart';
import '../models/student.dart';
import '../models/vente.dart';

/// Équivalent de vente_page()/add_vente()/add_commande()/commander()
/// (school_client, Controllers/Main.py:4711-5491), avec une différence
/// explicitement demandée : les lignes du panier sont ajoutées depuis un
/// catalogue de produits enregistrés (ProduitState), pas tapées en texte
/// libre à chaque vente — voir CartItem (lib/models/vente.dart).
class VenteState extends ChangeNotifier {
  VenteState(this._apiClient);

  final ApiClient _apiClient;

  List<VenteRecord> items = [];
  int currentPage = 1;
  int lastPage = 1;
  String searchTerm = '';
  bool isLoading = false;
  String? errorMessage;

  // Panier en cours de saisie.
  final List<CartItem> cart = [];
  String? etudiantId;
  String? etudiantLabel;
  bool isSubmitting = false;

  /// Non nul quand le panier édite une vente déjà enregistrée (clic sur une
  /// ligne du tableau) plutôt que d'en composer une nouvelle — détermine si
  /// submit() envoie 'id' (branche update de store_vente, RVente.py:133) et
  /// si la suppression d'une ligne doit passer par delete-order_item.
  String? editingVenteId;
  bool isLoadingCart = false;

  double get cartTotal => cart.fold(0, (sum, item) => sum + item.total);

  List<Student> liveSearchResults = [];
  bool isSearchingStudent = false;

  Future<void> load({int page = 1, String? search}) async {
    isLoading = true;
    errorMessage = null;
    if (search != null) searchTerm = search;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'vente',
        query: {'page': page, if (searchTerm.isNotEmpty) 'search': searchTerm},
      );
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => VenteRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      final meta = data['meta'] as Map<String, dynamic>?;
      currentPage = (meta?['current_page'] as num?)?.toInt() ?? 1;
      lastPage = (meta?['last_page'] as num?)?.toInt() ?? 1;
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des ventes.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  /// Équivalent de on_row_clicked_live_sell() : recherche en direct via
  /// POST v1/live-student, pour rattacher la vente à un étudiant.
  Future<void> searchStudents(String query) async {
    if (query.trim().length < 2) {
      liveSearchResults = [];
      notifyListeners();
      return;
    }
    isSearchingStudent = true;
    notifyListeners();
    try {
      final response = await _apiClient.post(
        'live-student',
        data: {'val': query},
      );
      final data = response.data as Map<String, dynamic>;
      liveSearchResults = ((data['data'] as List?) ?? const [])
          .map((e) => Student.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      liveSearchResults = [];
    } finally {
      isSearchingStudent = false;
      notifyListeners();
    }
  }

  void selectStudent(Student s) {
    etudiantId = s.id;
    etudiantLabel = '${s.nom} ${s.prenom}';
    liveSearchResults = [];
    notifyListeners();
  }

  void clearStudent() {
    etudiantId = null;
    etudiantLabel = null;
    notifyListeners();
  }

  /// Clic sur un produit de la liste de gauche : l'ajoute au panier (ou
  /// augmente sa quantité s'il y est déjà), sans jamais dépasser le stock
  /// disponible.
  void addProduitToCart(Produit produit) {
    for (final item in cart) {
      if (item.produitId == produit.id) {
        incrementQty(item);
        return;
      }
    }
    cart.add(CartItem.fromProduit(produit, quantite: 1));
    notifyListeners();
  }

  void incrementQty(CartItem item) {
    if (item.stockDisponible != null &&
        item.quantite >= item.stockDisponible!) {
      return;
    }
    item.quantite += 1;
    notifyListeners();
  }

  void decrementQty(CartItem item) {
    if (item.quantite <= 1) {
      cart.remove(item);
    } else {
      item.quantite -= 1;
    }
    notifyListeners();
  }

  /// Saisie directe d'une quantité décimale (ex: 2.5 mètres de tissu),
  /// pour les produits qui ne se vendent pas à l'unité entière.
  void setQty(CartItem item, double value) {
    if (value <= 0) {
      cart.remove(item);
    } else if (item.stockDisponible != null && value > item.stockDisponible!) {
      item.quantite = item.stockDisponible!;
    } else {
      item.quantite = value;
    }
    notifyListeners();
  }

  void removeFromCart(CartItem item) {
    cart.remove(item);
    notifyListeners();
  }

  void clearCart() {
    cart.clear();
    etudiantId = null;
    etudiantLabel = null;
    editingVenteId = null;
    notifyListeners();
  }

  /// Équivalent de on_row_clicked_vente_()/vente_show() (school_client,
  /// Controllers/Main.py:5240-5253 et 2438-2448) : clic sur une ligne de
  /// table_vente → GET v1/order-vente/{vente} → panier rouvert avec les
  /// lignes déjà enregistrées, prêt pour modification.
  Future<String?> loadForEdit(VenteRecord vente) async {
    isLoadingCart = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('order-vente/${vente.id}');
      final data = (response.data as Map<String, dynamic>)['data'] as List?;
      cart
        ..clear()
        ..addAll(
          (data ?? const []).map(
            (e) => CartItem.fromOrderItem(e as Map<String, dynamic>),
          ),
        );
      etudiantId = vente.etudiantId;
      etudiantLabel = vente.nom;
      editingVenteId = vente.id;
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isLoadingCart = false;
      notifyListeners();
    }
  }

  /// L'API order-vente/{vente} ne renvoie que le produit_id de chaque ligne,
  /// pas la fiche produit complète — sans cette résolution depuis le
  /// catalogue déjà chargé (ProduitState, lu par l'écran appelant), une
  /// ligne rechargée en édition n'a aucun plafond de stock (`+`/saisie
  /// manuelle de quantité illimités), contrairement à une ligne ajoutée
  /// depuis le catalogue dans la même session.
  void applyStockCaps(List<Produit> produits) {
    for (final item in cart) {
      if (item.produitId == null) continue;
      for (final produit in produits) {
        if (produit.id == item.produitId) {
          item.stockDisponible = produit.quantiteStock;
          break;
        }
      }
    }
    notifyListeners();
  }

  /// Équivalent de commander() → POST v1/vente. Quand [editingVenteId] est
  /// renseigné, la requête inclut 'id' et passe par la branche update de
  /// store_vente (RVente.py:133), protégée par verify_dual_auth("Modifier
  /// paiement") — d'où le support d'un [approvalToken] à rejouer sur 202.
  Future<String?> submit(String userId, {String? approvalToken}) async {
    if (cart.isEmpty) return 'Le panier est vide.';
    if (etudiantId == null) return 'Veuillez sélectionner un étudiant.';

    isSubmitting = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.post(
        'vente',
        data: {
          if (editingVenteId != null) 'id': editingVenteId,
          'user_id': userId,
          'etudiant_id': etudiantId,
          'items': cart.map((c) => c.toJson()).toList(),
        },
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      // Dio ne lève jamais d'exception pour un 202 (2xx = succès par défaut,
      // voir _defaultValidateStatus) : DualAuthChecker doit donc être
      // détecté ici, sur la réponse, pas dans le catch ci-dessous.
      if (response.statusCode == 202) return kApprovalRequiredError;
      final data = response.data as Map<String, dynamic>?;
      _lastVenteId = data?['id']?.toString();
      clearCart();
      await load(page: 1);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  /// Équivalent (corrigé) de delete_vente()/delete_order() : le bureau
  /// appelle à tort `GET v1/vente-delete`, alors que la vraie route est
  /// `DELETE /api/v1/order_item` (RVente.py:215-216) — on utilise donc le
  /// vrai contrat backend, pas l'appel cassé du bureau.
  Future<String?> deleteOrderItem(
    String orderItemId,
    String venteId, {
    required String raison,
    String? approvalToken,
  }) async {
    try {
      final response = await _apiClient.dio.delete(
        'order_item',
        queryParameters: {
          'vente': orderItemId,
          'vente_id': venteId,
          'raison': raison,
        },
        options: approvalToken == null
            ? null
            : Options(headers: {'X-Approval-Token': approvalToken}),
      );
      if (response.statusCode == 202) return kApprovalRequiredError;
      cart.removeWhere((c) => c.id == orderItemId);
      await load(page: currentPage);
      return null;
    } catch (e) {
      return _extractError(e);
    }
  }

  String? printingId;
  String? _lastVenteId;
  String? get lastVenteId => _lastVenteId;

  /// Équivalent de imprimer_vente() → GET v1/print-recu-vente/{id}
  /// (VenteRecu.py), ouvert avec le lecteur PDF par défaut du système (motif
  /// de PaiementState.printRecu()/NoteState.printBulletin()).
  Future<String?> printRecu(String venteId) async {
    printingId = venteId;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get(
        'print-recu-vente/$venteId',
        options: Options(responseType: ResponseType.bytes),
      );
      final file = File('${Directory.systemTemp.path}/vente_recu_$venteId.pdf');
      await file.writeAsBytes(response.data as List<int>);
      if (Platform.isMacOS) {
        await Process.run('open', [file.path]);
      } else if (Platform.isWindows) {
        await Process.run('cmd', ['/c', 'start', '', file.path]);
      } else if (Platform.isLinux) {
        await Process.run('xdg-open', [file.path]);
      }
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      printingId = null;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      var data = e.response?.data;
      // Les requêtes en `responseType: ResponseType.bytes` (printRecu)
      // reçoivent toujours des octets bruts, même sur une erreur — sans ce
      // décodage, le vrai message JSON du serveur était masqué par le
      // message générique ci-dessous.
      if (data is List<int>) {
        try {
          data = jsonDecode(utf8.decode(data));
        } catch (_) {
          // corps non-JSON : on garde les octets bruts, le fallback
          // générique s'applique.
        }
      }
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
