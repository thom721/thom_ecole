import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';

/// Équivalent de template_badge_1()/template_badge_2()/template_certificat()/
/// template_diplome() (school_client, Controllers/Main.py:6817-6989) :
/// upload via QFileDialog, persisté en local. Le bureau écrit dans
/// `{appdata}/gestion_ecole/assets/icons/` — ici dans le dossier "Application
/// Support" de l'app (getApplicationSupportDirectory()/badge_templates/),
/// l'équivalent multi-plateforme le plus proche.
///
/// "template_badge_1"/"template_badge_2" sont réellement réutilisés pour
/// composer le badge (combo_template) et SONT validés (~1013-1015×639px,
/// la taille standard du badge). "template_certificat"/"template_diplome"
/// sont, à l'identique du bureau, uploadables mais jamais réutilisés
/// nulle part ailleurs (diplome_page()/certificat_page() ne contiennent
/// qu'une recherche + table, sans génération) — gardés ici uniquement pour
/// la parité visuelle de la page Profil, sans validation de taille.
class TemplateStore {
  TemplateStore._();
  static final TemplateStore instance = TemplateStore._();

  static const badgeKeys = {'template_badge_1', 'template_badge_2'};

  Future<Directory> _dir() async {
    final support = await getApplicationSupportDirectory();
    final dir = Directory('${support.path}/badge_templates');
    if (!dir.existsSync()) dir.createSync(recursive: true);
    return dir;
  }

  Future<Uint8List?> read(String key) async {
    final file = File('${(await _dir()).path}/$key.jpg');
    if (!file.existsSync()) return null;
    return file.readAsBytes();
  }

  /// Ouvre un sélecteur de fichier et persiste le choix sous [key]. Pour les
  /// templates de badge, vérifie la taille (≈1013-1015×639px) comme le fait
  /// template_badge_1()/template_badge_2() côté bureau. Retourne un message
  /// d'erreur, ou null si la sauvegarde a réussi (ou si l'utilisateur a
  /// annulé la sélection, comme côté bureau : "Aucune image sélectionnée").
  Future<String?> pickAndSave(String key) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg'],
      withData: true,
    );
    final bytes = result?.files.single.bytes;
    if (bytes == null) return null;

    if (badgeKeys.contains(key)) {
      final codec = await ui.instantiateImageCodec(bytes);
      final frame = await codec.getNextFrame();
      final w = frame.image.width;
      final h = frame.image.height;
      if (w < 1013 || w > 1015 || h != 639) {
        return 'Image refusée : taille attendue ≈1013-1015×639px (badge standard), reçu ${w}x$h.';
      }
    }

    final file = File('${(await _dir()).path}/$key.jpg');
    await file.writeAsBytes(bytes);
    return null;
  }
}
