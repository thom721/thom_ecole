import 'dart:io';

/// Chemin de sortie d'un badge généré — `~/Desktop/badge/{année
/// académique}/{classe}/{nom complet}.{extension}`, sur demande explicite.
/// Différent de school_client (`Controllers/Main.py:6260`, qui écrit dans
/// `~/Desktop/Badges {classe}/{nom}.png`, un seul niveau de dossier, sans
/// séparation par année) : la structure à 3 niveaux est un choix assumé
/// pour la version Flutter, permis par `StudentDetail.anneeLabel`, une
/// donnée réelle mais non utilisée par le bureau à cette fin.
///
/// Les composants sont assainis : une année académique typique
/// ("2024/2025") romprait sinon la structure de dossiers en scindant
/// l'année en deux niveaux (`/` est un séparateur de chemin).
File badgeOutputFile({
  required String anneeLabel,
  required String classeName,
  required String fullName,
  required String extension,
}) {
  final dir = Directory(
    '${_homeDir()}/Desktop/badge/${_sanitize(anneeLabel)}/${_sanitize(classeName)}',
  );
  if (!dir.existsSync()) dir.createSync(recursive: true);
  return File('${dir.path}/${_sanitize(fullName)}.$extension');
}

/// `Platform.environment['HOME']` n'existe que sur macOS/Linux — Windows
/// expose le dossier utilisateur via `USERPROFILE` à la place. Sur macOS
/// SPÉCIFIQUEMENT, cette app étant en bac à sable (`com.apple.security.
/// app-sandbox`), `$HOME` est REDIRIGÉ par le système vers le conteneur de
/// l'app (`~/Library/Containers/{bundle-id}/Data`), PAS le vrai dossier
/// utilisateur — piégé une première fois par une vraie
/// `PathAccessException` ("Operation not permitted") en essayant d'écrire
/// dans ce faux "Desktop" à l'intérieur du conteneur. L'exception
/// d'entitlement `temporary-exception.files.home-relative-path.read-write`
/// (voir macos/Runner/*.entitlements) autorise l'écriture dans le VRAI
/// `~/Desktop`, mais seulement si on construit VRAIMENT ce chemin — d'où
/// `$USER`/`$LOGNAME` (l'identité du processus, jamais redirigée par le
/// bac à sable, contrairement au système de fichiers) plutôt que `$HOME`.
String _homeDir() {
  if (Platform.isWindows) {
    return Platform.environment['USERPROFILE'] ??
        Platform.environment['HOMEPATH'] ??
        '.';
  }
  if (Platform.isMacOS) {
    final user =
        Platform.environment['USER'] ?? Platform.environment['LOGNAME'];
    if (user != null && user.isNotEmpty) return '/Users/$user';
  }
  return Platform.environment['HOME'] ?? '.';
}

String _sanitize(String value) {
  final cleaned = value.replaceAll(RegExp(r'[\\/:*?"<>|]'), '-').trim();
  return cleaned.isEmpty ? 'Sans-nom' : cleaned;
}
