import 'package:shared_preferences/shared_preferences.dart';

/// Équivalent de Helper/Ip_manager.py (school_client) : persiste l'adresse
/// IP du serveur saisie manuellement par l'utilisateur.
///
/// Contrairement à school_client, qui modifie directement le fichier hosts
/// de la machine (Controllers/Main.py::add_or_update_host(), ce qui exige
/// des droits administrateur — d'où le "sudo" nécessaire sur Mac/Linux), ça
/// n'est PAS encore fait ici : la valeur est juste mémorisée pour l'instant.
class IpStorage {
  static const _ipKey = 'server_ip';

  Future<void> saveServerIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_ipKey, ip);
  }

  Future<String?> getServerIp() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_ipKey);
  }
}
