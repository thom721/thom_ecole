import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/produit.dart';

/// Catalogue de produits — CRUD sur GET/POST/PUT/DELETE v1/produits
/// (ecole_nginx/app/Routes/RProduit.py), une nouveauté ajoutée pour cette
/// app (ni le bureau ni le web ne persistaient de fiche produit).
class ProduitState extends ChangeNotifier {
  ProduitState(this._apiClient);

  final ApiClient _apiClient;

  List<Produit> items = [];
  bool isLoading = false;
  String? errorMessage;
  bool isSubmitting = false;
  String? deletingId;

  List<CategorieProduit> categories = [];
  bool isLoadingCategories = false;
  bool isSubmittingCategory = false;

  Future<void> loadCategories() async {
    isLoadingCategories = true;
    notifyListeners();
    try {
      final response = await _apiClient.get('categories-produits');
      categories = ((response.data as List?) ?? const [])
          .map((e) => CategorieProduit.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      // Liste vide en cas d'échec.
    } finally {
      isLoadingCategories = false;
      notifyListeners();
    }
  }

  /// Équivalent de la demande explicite "on devait être capable d'ajouter
  /// une catégorie aussi" : POST v1/categories-produits, puis recharge la
  /// liste pour que la nouvelle catégorie soit immédiatement sélectionnable.
  Future<String?> createCategory(String nom) async {
    isSubmittingCategory = true;
    notifyListeners();
    try {
      await _apiClient.post('categories-produits', data: {'nom': nom});
      await loadCategories();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmittingCategory = false;
      notifyListeners();
    }
  }

  Future<void> load({String? search}) async {
    isLoading = true;
    errorMessage = null;
    notifyListeners();
    try {
      final response = await _apiClient.get(
        'produits',
        query: {
          'per_page': 200,
          if (search != null && search.isNotEmpty) 'search': search,
        },
      );
      final data = response.data as Map<String, dynamic>;
      items = ((data['data'] as List?) ?? const [])
          .map((e) => Produit.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      errorMessage = 'Impossible de charger la liste des produits.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> create({
    required String nom,
    required String category,
    required double prix,
    required double quantiteStock,
    String? description,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.post(
        'produits',
        data: {
          'nom': nom,
          'category': category,
          'prix': prix,
          'quantite_stock': quantiteStock,
          'description': description,
        },
      );
      await load();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> update(
    String id, {
    required String nom,
    required String category,
    required double prix,
    required double quantiteStock,
    String? description,
  }) async {
    isSubmitting = true;
    notifyListeners();
    try {
      await _apiClient.dio.put(
        'produits/$id',
        data: {
          'nom': nom,
          'category': category,
          'prix': prix,
          'quantite_stock': quantiteStock,
          'description': description,
        },
      );
      await load();
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      isSubmitting = false;
      notifyListeners();
    }
  }

  Future<String?> delete(String id) async {
    deletingId = id;
    notifyListeners();
    try {
      await _apiClient.dio.delete('produits/$id');
      items.removeWhere((p) => p.id == id);
      return null;
    } catch (e) {
      return _extractError(e);
    } finally {
      deletingId = null;
      notifyListeners();
    }
  }

  String _extractError(Object e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
      return 'Impossible de contacter le serveur.';
    }
    return 'Erreur inattendue : $e';
  }
}
