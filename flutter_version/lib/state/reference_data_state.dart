import 'package:flutter/foundation.dart';
import '../core/api_client.dart';
import '../models/student.dart';

/// Listes de référence chargées une fois (niveau_index, classes_show_check,
/// annee_academique, get_all_faculte dans Controllers/Main.py
/// connect_buttons()) et partagées par toutes les pages qui en ont besoin
/// (Étudiants, Paiement, Cours...).
class ReferenceDataState extends ChangeNotifier {
  ReferenceDataState(this._apiClient);

  final ApiClient _apiClient;

  List<Niveau> niveaux = [];
  List<Classe> classes = [];
  List<AnneeAcademique> annees = [];
  List<Faculte> facultes = [];
  bool isLoaded = false;

  List<Classe> classesForNiveau(String? niveauId) {
    if (niveauId == null) return const [];
    return classes.where((c) => c.niveauId == niveauId).toList();
  }

  Future<void> loadOnce() async {
    if (isLoaded) return;
    await _load();
    isLoaded = true;
    notifyListeners();
  }

  /// Équivalent de actualiser_page() (Controllers/Main.py:13371-13381) :
  /// recharge ces listes de référence à la demande (bouton "Actualiser" de
  /// la sidebar), même si elles sont déjà chargées — contrairement à
  /// loadOnce() qui ne fait rien après le premier chargement.
  Future<void> refresh() async {
    await _load();
    notifyListeners();
  }

  Future<void> _load() async {
    await Future.wait([
      _apiClient.get('niveau').then((r) {
        niveaux = ((r.data['data'] as List?) ?? const [])
            .map((e) => Niveau.fromJson(e as Map<String, dynamic>))
            .toList();
      }),
      _apiClient.get('cl-load-asses_').then((r) {
        classes = ((r.data['data'] as List?) ?? const [])
            .map((e) => Classe.fromJson(e as Map<String, dynamic>))
            .toList();
      }),
      _apiClient.get('annee-academique').then((r) {
        annees = ((r.data['data'] as List?) ?? const [])
            .map((e) => AnneeAcademique.fromJson(e as Map<String, dynamic>))
            .toList();
      }),
      _apiClient.get('get-all-faculte').then((r) {
        facultes = ((r.data['data'] as List?) ?? const [])
            .map((e) => Faculte.fromJson(e as Map<String, dynamic>))
            .toList();
      }),
    ]);
  }
}
