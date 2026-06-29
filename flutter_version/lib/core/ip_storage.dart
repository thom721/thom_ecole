import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';

/// Équivalent de Helper/Ip_manager.py (school_client) : persiste l'adresse
/// IP du serveur saisie manuellement par l'utilisateur.
class IpStorage {
  static const _ipKey = 'server_ip';
  static const _domain = 'aplekol360.local';

  Future<void> saveServerIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_ipKey, ip);
  }

  Future<String?> getServerIp() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_ipKey);
  }

  /// Équivalent de add_or_update_host() (Controllers/Main.py:4009-4057) :
  /// écrit l'entrée `<ip>\taplekol360.local` dans le fichier hosts système.
  /// Sur Mac/Linux, si l'écriture directe échoue (droits insuffisants),
  /// élève via osascript (Mac) ou pkexec (Linux) — équivalent de run_as_admin()
  /// (Main.py:3597-3613 + ShellExecuteW "runas" Windows).
  /// Retourne null en cas de succès, ou un message d'erreur.
  Future<String?> addOrUpdateHost(String ip) async {
    final hostsPath = Platform.isWindows
        ? r'C:\Windows\System32\drivers\etc\hosts'
        : '/etc/hosts';

    // 1. Lire le contenu actuel
    final hostsFile = File(hostsPath);
    List<String> lines;
    try {
      lines = await hostsFile.readAsLines();
    } catch (e) {
      return 'Impossible de lire $hostsPath : $e';
    }

    // 2. Reconstruire : remplacer l'entrée existante ou ajouter
    bool found = false;
    final newLines = <String>[];
    for (final line in lines) {
      if (line.contains(_domain) && !line.trimLeft().startsWith('#')) {
        newLines.add('$ip\t$_domain');
        found = true;
      } else {
        newLines.add(line);
      }
    }
    if (!found) newLines.add('$ip\t$_domain');

    final newContent = '${newLines.join('\n')}\n';

    // 3. Essai d'écriture directe
    try {
      await hostsFile.writeAsString(newContent);
      return null;
    } on PathAccessException {
      return _writeWithElevation(hostsPath, newContent);
    } catch (e) {
      return "Erreur d'écriture dans $hostsPath : $e";
    }
  }

  /// Élévation de privilèges selon la plateforme —
  /// équivalent de run_as_admin() (Main.py:3597) sur chaque OS.
  Future<String?> _writeWithElevation(String hostsPath, String content) async {
    if (Platform.isMacOS) {
      // Directory.systemTemp (/tmp) toujours accessible, contrairement au
      // répertoire sandbox de getTemporaryDirectory() qui n'existe pas encore
      // au premier lancement (PathNotFoundException errno=2).
      final tmp = File('${Directory.systemTemp.path}/hosts_lekol360');
      await tmp.writeAsString(content);
      final script =
          "do shell script \"cp '${tmp.path}' '$hostsPath'\" with administrator privileges";
      final result = await Process.run('osascript', ['-e', script]);
      await tmp.delete().catchError((_) => tmp);
      if (result.exitCode != 0) {
        return 'Mise à jour du fichier hosts annulée ou refusée.';
      }
      return null;
    } else if (Platform.isLinux) {
      final tmp = File('/tmp/hosts_lekol360');
      await tmp.writeAsString(content);
      final result = await Process.run('pkexec', ['cp', tmp.path, hostsPath]);
      await tmp.delete().catchError((_) => tmp);
      if (result.exitCode != 0) {
        return "Permission refusée. Relancez l'application avec sudo si pkexec n'est pas disponible.";
      }
      return null;
    } else if (Platform.isWindows) {
      // Équivalent de ShellExecuteW("runas") : PowerShell avec élévation
      final tmp = File('${Directory.systemTemp.path}\\hosts_lekol360');
      await tmp.writeAsString(content);
      final result = await Process.run('powershell', [
        '-Command',
        'Start-Process -Verb RunAs -FilePath cmd.exe -ArgumentList "/c copy /Y \\"${tmp.path}\\" \\"$hostsPath\\""',
      ]);
      if (result.exitCode != 0) {
        return "Relancez l'application en tant qu'administrateur pour mettre à jour le fichier hosts.";
      }
      return null;
    }
    return 'Système non supporté.';
  }
}
