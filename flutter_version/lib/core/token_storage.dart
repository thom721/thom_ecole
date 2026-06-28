import 'package:shared_preferences/shared_preferences.dart';

/// Équivalent de Helper/Token_manager.py (school_client) : persiste le
/// token Sanctum et l'email de l'utilisateur connecté entre les lancements.
class TokenStorage {
  static const _tokenKey = 'auth_token';
  static const _emailKey = 'user_email';

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<void> saveUserEmail(String email) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_emailKey, email);
  }

  Future<String?> getUserEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_emailKey);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_emailKey);
  }
}
