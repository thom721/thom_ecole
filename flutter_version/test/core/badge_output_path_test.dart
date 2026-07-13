import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/core/badge_output_path.dart';

void main() {
  tearDown(() {
    // Chaque test crée réellement l'arborescence de dossiers (nécessaire :
    // badgeOutputFile() appelle Directory.createSync avant de renvoyer le
    // File) — nettoyée pour ne pas polluer le Bureau réel de la machine
    // qui exécute la suite.
    final home = Platform.isWindows
        ? (Platform.environment['USERPROFILE'] ?? Platform.environment['HOMEPATH'] ?? '.')
        : (Platform.environment['HOME'] ?? '.');
    final dir = Directory('$home/Desktop/badge');
    if (dir.existsSync()) dir.deleteSync(recursive: true);
  });

  test('construit badge/année/classe/nom.extension sur le Bureau de l\'utilisateur', () {
    final file = badgeOutputFile(
      anneeLabel: '2024-2025',
      classeName: '6e Année B',
      fullName: 'Jean Dupont',
      extension: 'png',
    );
    expect(file.path, endsWith('Desktop/badge/2024-2025/6e Année B/Jean Dupont.png'));
    expect(file.parent.existsSync(), isTrue, reason: 'le dossier doit être créé, pas seulement le chemin calculé');
    // Régression : sur macOS, une app en bac à sable voit `$HOME` REDIRIGÉ
    // vers son conteneur (`~/Library/Containers/{bundle-id}/Data`), pas le
    // vrai dossier utilisateur — écrire là-dedans lève une
    // `PathAccessException` ("Operation not permitted") en usage réel, une
    // fois l'exception d'entitlement accordée pour le VRAI `~/Desktop`
    // (voir macos/Runner/*.entitlements) mais pas pour le conteneur.
    expect(file.path, isNot(contains('Containers')), reason: 'ne doit jamais pointer vers le conteneur sandboxé de l\'app');
  });

  test('assainit les composants contenant des séparateurs de chemin (ex. "2024/2025")', () {
    final file = badgeOutputFile(
      anneeLabel: '2024/2025',
      classeName: '6e/B',
      fullName: 'Jean/Dupont',
      extension: 'pdf',
    );
    // Un "/" non assaini scinderait "2024/2025" en DEUX niveaux de
    // dossiers ("2024" puis "2025") au lieu d'un seul — vérifié en comptant
    // les segments du chemin entre "badge" et le nom de fichier.
    final parts = file.path.split(Platform.pathSeparator);
    final badgeIndex = parts.indexOf('badge');
    expect(badgeIndex, greaterThanOrEqualTo(0));
    // badge / <année> / <classe> / <fichier> = 3 segments après "badge".
    expect(parts.length - badgeIndex, 4);
    expect(file.path, isNot(contains('2024/2025')));
  });

  test('un composant vide après assainissement retombe sur un nom générique plutôt qu\'un dossier vide', () {
    final file = badgeOutputFile(anneeLabel: '', classeName: '   ', fullName: '///', extension: 'png');
    expect(file.path, contains('Sans-nom'));
  });
}
