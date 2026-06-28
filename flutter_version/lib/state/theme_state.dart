import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/app_theme.dart';

/// Bascule clair/sombre — nouvelle fonctionnalité Flutter sans équivalent
/// dans school_client ni ecole_nginx/frontend (les deux sont exclusivement
/// sombres) : palette claire conçue ici sur la même structure que
/// AppColors.dark (lib/theme/app_theme.dart). Le choix est persisté via
/// shared_preferences et appliqué immédiatement à toute l'app (AppColors
/// expose désormais des getters dynamiques au lieu de `static const`).
class ThemeState extends ChangeNotifier {
  static const _prefsKey = 'theme_is_dark';

  bool _isDark = true;
  bool get isDark => _isDark;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _isDark = prefs.getBool(_prefsKey) ?? true;
    AppColors.setDark(_isDark);
    notifyListeners();
  }

  Future<void> setDark(bool value) async {
    if (_isDark == value) return;
    _isDark = value;
    AppColors.setDark(value);
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefsKey, value);
  }

  Future<void> toggle() => setDark(!_isDark);
}
