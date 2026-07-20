import 'dart:io';
import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';

import '../models/badge_layout.dart';
import 'badge_layout_seed_templates.dart';
import 'badge_layout_seed_templates_pro.dart';

/// Persistance locale des gabarits construits dans l'éditeur visuel de
/// badge (`screens/etudiant/badge_builder/`) — un fichier JSON par gabarit
/// dans `{appdata}/badge_layouts/`, calque du mécanisme de
/// `services/template_store.dart` mais pour des gabarits structurés (pas
/// une simple image). Les images de fond choisies par face sont copiées à
/// part dans `badge_layouts/images/` ; `BadgeSide.backgroundImagePath`
/// pointe vers ce chemin absolu.
class BadgeLayoutStore {
  BadgeLayoutStore._();
  static final BadgeLayoutStore instance = BadgeLayoutStore._();

  Future<Directory> _dir() async {
    final support = await getApplicationSupportDirectory();
    final dir = Directory('${support.path}/badge_layouts');
    if (!dir.existsSync()) dir.createSync(recursive: true);
    return dir;
  }

  Future<Directory> _imagesDir() async {
    final base = await _dir();
    final dir = Directory('${base.path}/images');
    if (!dir.existsSync()) dir.createSync(recursive: true);
    return dir;
  }

  // Compteur en plus de l'horodatage : la résolution réelle de l'horloge
  // système peut être plus grossière qu'une microseconde (observé sur
  // macOS), donc plusieurs appels synchrones rapprochés (ex. placer
  // plusieurs éléments d'un coup dans badge_builder_screen.dart) peuvent
  // renvoyer le MÊME horodatage — provoquant des `id` dupliqués, et donc
  // des clés Flutter dupliquées ("Duplicate keys found") dans le canevas.
  int _idCounter = 0;

  String newId() => '${DateTime.now().microsecondsSinceEpoch}_${_idCounter++}';

  /// Écrit une seule fois les 10 gabarits de démarrage
  /// (badge_layout_seed_templates.dart) — un fichier marqueur évite de les
  /// recréer aux lancements suivants, y compris si l'utilisateur en a
  /// supprimé depuis (une suppression volontaire doit rester définitive,
  /// pas réapparaître au prochain redémarrage).
  Future<void> _ensureSeedTemplates() async {
    final marker = File('${(await _dir()).path}/.badge_layouts_seeded');
    if (!marker.existsSync()) {
      for (final layout in buildSeedBadgeTemplates()) {
        await save(layout);
      }
      marker.writeAsStringSync('');
    }
    await _ensureProSeedTemplates();
  }

  /// Second lot de gabarits de démarrage (badge_layout_seed_templates_pro.dart)
  /// — 22 reproductions de modèles de carte professionnelle, ajoutées
  /// après coup. Sa PROPRE marque (distincte de celle ci-dessus) permet à
  /// ce lot d'apparaître même pour une installation qui avait déjà lancé
  /// l'app (donc déjà posé la marque du premier lot) avant l'ajout de ce
  /// fichier — sinon ce second lot ne serait JAMAIS écrit pour un poste
  /// déjà en service.
  Future<void> _ensureProSeedTemplates() async {
    final marker = File('${(await _dir()).path}/.badge_layouts_seeded_pro');
    if (marker.existsSync()) return;
    for (final layout in buildProSeedBadgeTemplates()) {
      await save(layout);
    }
    marker.writeAsStringSync('');
  }

  /// Liste tous les gabarits enregistrés, du plus récemment modifié au
  /// plus ancien. Un fichier JSON illisible/corrompu est ignoré plutôt que
  /// de faire échouer tout l'écran de sélection.
  Future<List<BadgeLayoutTemplate>> list() async {
    await _ensureSeedTemplates();
    final dir = await _dir();
    final layouts = <BadgeLayoutTemplate>[];
    for (final entity in dir.listSync()) {
      if (entity is! File || !entity.path.endsWith('.json')) continue;
      try {
        final layout = BadgeLayoutTemplate.fromJsonString(
          await entity.readAsString(),
        );
        layouts.add(layout);
      } catch (_) {
        continue;
      }
    }
    layouts.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    return layouts;
  }

  Future<BadgeLayoutTemplate?> read(String id) async {
    final file = File('${(await _dir()).path}/$id.json');
    if (!file.existsSync()) return null;
    return BadgeLayoutTemplate.fromJsonString(await file.readAsString());
  }

  /// Enregistre (crée ou remplace) un gabarit, en mettant à jour
  /// `updatedAt`.
  Future<void> save(BadgeLayoutTemplate layout) async {
    layout.updatedAt = DateTime.now();
    final file = File('${(await _dir()).path}/${layout.id}.json');
    await file.writeAsString(layout.toJsonString());
  }

  /// Supprime un gabarit et ses images de fond associées (recto/verso).
  Future<void> delete(String id) async {
    final file = File('${(await _dir()).path}/$id.json');
    if (file.existsSync()) file.deleteSync();
    final imagesDir = await _imagesDir();
    for (final side in ['recto', 'verso']) {
      final image = File('${imagesDir.path}/${id}_$side.jpg');
      if (image.existsSync()) image.deleteSync();
    }
  }

  /// Ouvre un sélecteur de fichier et copie l'image choisie comme fond de
  /// la face [isVerso] du gabarit [layoutId]. Retourne le chemin absolu à
  /// affecter à `BadgeSide.backgroundImagePath`, ou `null` si
  /// l'utilisateur a annulé la sélection.
  Future<String?> pickBackgroundImage({
    required String layoutId,
    required bool isVerso,
  }) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    final Uint8List? bytes = result?.files.single.bytes;
    if (bytes == null) return null;

    final side = isVerso ? 'verso' : 'recto';
    final file = File('${(await _imagesDir()).path}/${layoutId}_$side.jpg');
    await file.writeAsBytes(bytes);
    return file.path;
  }

  /// Ouvre un sélecteur de fichier et copie l'image choisie pour un élément
  /// `BadgeElementType.staticImage` (logo, signature scannée...) —
  /// [elementId] au lieu de [layoutId]/`isVerso` (voir [pickBackgroundImage])
  /// puisqu'un gabarit peut contenir plusieurs images de ce type.
  Future<String?> pickElementImage({required String elementId}) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    final Uint8List? bytes = result?.files.single.bytes;
    if (bytes == null) return null;

    final file = File('${(await _imagesDir()).path}/element_$elementId.jpg');
    await file.writeAsBytes(bytes);
    return file.path;
  }
}
