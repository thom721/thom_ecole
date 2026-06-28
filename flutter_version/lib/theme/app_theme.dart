import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Palette & typographie reprises du frontend web Vue (ecole_nginx/frontend) :
/// AdminLayout.vue (bg #0f1117, sidebar #171b26, texte #e8eaf0/#7c83a0,
/// accent par défaut #4f8ef7) et Login.vue (bg #0d0d14, accent or #c9a84c,
/// police Playfair Display pour les titres + DM Sans pour le corps).
///
/// C'est une référence de STYLE uniquement (couleurs/police/disposition) —
/// la logique métier/permissions reste celle de school_client (PySide6), pas
/// celle de ce frontend web qui a des règles de rôles différentes.
///
/// La palette claire (_light) n'a pas d'équivalent réel (school_client et le
/// frontend web sont exclusivement sombres) — conçue ici sur la même
/// structure que _dark (mêmes rôles : fond/sidebar/carte/texte/accent), sur
/// demande explicite. AppColors expose des GETTERS (et non plus des
/// `static const`) qui délèguent à `_current` : ThemeState.setDark() change
/// `_current` puis notifie les listeners, ce qui force tout l'arbre de
/// widgets à se reconstruire et donc à relire ces getters.
class AppColors {
  AppColors._();

  static _Palette _current = _dark;

  static void setDark(bool isDark) {
    _current = isDark ? _dark : _light;
  }

  static bool get isDark => identical(_current, _dark);

  static Color get appBg => _current.appBg;
  static Color get sidebarBg => _current.sidebarBg;
  static Color get cardBg => _current.cardBg;
  static Color get panelBg => _current.panelBg;
  static Color get inputBg => _current.inputBg;

  static Color get borderSubtle => _current.borderSubtle;
  static Color get borderHover => _current.borderHover;
  static Color get hoverOverlay => _current.hoverOverlay;

  static Color get textPrimary => _current.textPrimary;
  static Color get textMuted => _current.textMuted;

  static Color get accent => _current.accent;
  static Color get accentLight => _current.accentLight;

  // Toujours sombre : page de connexion bureau (school_client), indépendante
  // du choix clair/sombre de l'application principale.
  static const loginBg = Color(0xFF0D0D14);
  static const loginGold = Color(0xFFC9A84C);

  static const danger = Color(0xFFE74C3C);

  // Palette des cartes du dashboard (AdminDashComposante.vue) : bar (couleur
  // vive, identique dans les deux thèmes) + texte (variante claire en sombre
  // pour contraster sur fond sombre, variante foncée en clair).
  static Map<String, _CardColor> get cardPalette => AppColors.isDark ? _darkCardPalette : _lightCardPalette;
}

const _darkCardPalette = <String, _CardColor>{
  'blue': _CardColor(Color(0xFF4F8EF7), Color(0xFF7AAEFF)),
  'emerald': _CardColor(Color(0xFF10B981), Color(0xFF34D399)),
  'violet': _CardColor(Color(0xFF8B5CF6), Color(0xFFA78BFA)),
  'amber': _CardColor(Color(0xFFF59E0B), Color(0xFFFBBF24)),
  'sky': _CardColor(Color(0xFF0EA5E9), Color(0xFF38BDF8)),
  'rose': _CardColor(Color(0xFFF43F5E), Color(0xFFFB7185)),
  'purple': _CardColor(Color(0xFFA855F7), Color(0xFFC084FC)),
  'cyan': _CardColor(Color(0xFF06B6D4), Color(0xFF22D3EE)),
};

const _lightCardPalette = <String, _CardColor>{
  'blue': _CardColor(Color(0xFF4F8EF7), Color(0xFF2E6BD6)),
  'emerald': _CardColor(Color(0xFF10B981), Color(0xFF0E9268)),
  'violet': _CardColor(Color(0xFF8B5CF6), Color(0xFF7C3AED)),
  'amber': _CardColor(Color(0xFFF59E0B), Color(0xFFB45309)),
  'sky': _CardColor(Color(0xFF0EA5E9), Color(0xFF0284C7)),
  'rose': _CardColor(Color(0xFFF43F5E), Color(0xFFBE123C)),
  'purple': _CardColor(Color(0xFFA855F7), Color(0xFF9333EA)),
  'cyan': _CardColor(Color(0xFF06B6D4), Color(0xFF0E7490)),
};

class _Palette {
  const _Palette({
    required this.appBg,
    required this.sidebarBg,
    required this.cardBg,
    required this.panelBg,
    required this.inputBg,
    required this.borderSubtle,
    required this.borderHover,
    required this.hoverOverlay,
    required this.textPrimary,
    required this.textMuted,
    required this.accent,
    required this.accentLight,
  });

  final Color appBg;
  final Color sidebarBg;
  final Color cardBg;
  final Color panelBg;
  final Color inputBg;
  final Color borderSubtle;
  final Color borderHover;
  final Color hoverOverlay;
  final Color textPrimary;
  final Color textMuted;
  final Color accent;
  final Color accentLight;
}

const _dark = _Palette(
  appBg: Color(0xFF0F1117),
  sidebarBg: Color(0xFF171B26),
  cardBg: Color(0xFF161B26),
  panelBg: Color(0xFF1E2335),
  inputBg: Color(0xFF161B22),
  borderSubtle: Color(0x12FFFFFF), // white 7%
  borderHover: Color(0x1FFFFFFF), // white 12%
  hoverOverlay: Color(0x0DFFFFFF), // white 5%
  textPrimary: Color(0xFFE8EAF0),
  textMuted: Color(0xFF7C83A0),
  accent: Color(0xFF4F8EF7),
  accentLight: Color(0xFF7AAEFF),
);

const _light = _Palette(
  appBg: Color(0xFFF4F5F8),
  sidebarBg: Color(0xFFFFFFFF),
  cardBg: Color(0xFFFFFFFF),
  panelBg: Color(0xFFEEF0F5),
  inputBg: Color(0xFFFFFFFF),
  borderSubtle: Color(0x14000000), // black 8%
  borderHover: Color(0x21000000), // black 13%
  hoverOverlay: Color(0x0A000000), // black 4%
  textPrimary: Color(0xFF1A1E2A),
  textMuted: Color(0xFF6B7280),
  accent: Color(0xFF2E6BD6),
  accentLight: Color(0xFF4F8EF7),
);

class _CardColor {
  const _CardColor(this.bar, this.text);
  final Color bar;
  final Color text;
}

class AppTheme {
  AppTheme._();

  static TextStyle serif(double size, {FontWeight weight = FontWeight.bold, Color? color}) {
    return GoogleFonts.playfairDisplay(
      fontSize: size,
      fontWeight: weight,
      color: color ?? AppColors.textPrimary,
    );
  }

  static ThemeData get dark => _themeFor(Brightness.dark, AppColors.cardBg);

  static ThemeData get light => _themeFor(Brightness.light, AppColors.cardBg);

  static ThemeData _themeFor(Brightness brightness, Color surface) {
    final base = ThemeData(brightness: brightness, useMaterial3: true);
    final textTheme = GoogleFonts.dmSansTextTheme(base.textTheme).apply(
      bodyColor: AppColors.textPrimary,
      displayColor: AppColors.textPrimary,
    );

    return base.copyWith(
      scaffoldBackgroundColor: AppColors.appBg,
      textTheme: textTheme,
      colorScheme: base.colorScheme.copyWith(
        primary: AppColors.accent,
        surface: AppColors.cardBg,
      ),
      dividerColor: AppColors.borderSubtle,
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.inputBg,
        hintStyle: TextStyle(color: AppColors.textMuted.withValues(alpha: 0.6)),
        labelStyle: TextStyle(color: AppColors.textMuted),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: AppColors.borderSubtle),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: AppColors.borderSubtle),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: AppColors.accent),
        ),
      ),
      dataTableTheme: DataTableThemeData(
        headingTextStyle: TextStyle(
          color: AppColors.textMuted,
          fontWeight: FontWeight.w600,
          fontSize: 11,
          letterSpacing: 0.6,
        ),
        dataTextStyle: TextStyle(color: AppColors.textPrimary.withValues(alpha: 0.85), fontSize: 13),
        headingRowColor: const WidgetStatePropertyAll(Colors.transparent),
        dataRowColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.hovered)) return AppColors.hoverOverlay;
          return Colors.transparent;
        }),
      ),
    );
  }
}
