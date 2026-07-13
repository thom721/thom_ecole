import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/auth_state.dart';
import '../../state/theme_state.dart';
import '../../theme/app_theme.dart';
import '../shell/app_shell.dart';

/// Équivalent IDENTIQUE de la page "reset_password" (Resources/
/// main_school1.ui : label_89 "Réinitialiser Votre mot de passe",
/// password_for_reset, confirm_password, btn_reset_password) et de
/// reset_password()/reset_password_and_connect() (Controllers/Main.py +
/// Models/AsyncDataHandler.py, school_client) : un simple formulaire mot de
/// passe + confirmation, SANS code de vérification — c'est la SEULE
/// fonctionnalité de réinitialisation que possède le bureau (déclenchée
/// automatiquement après le login quand password_changed_at est vide,
/// jamais via un lien "mot de passe oublié" qui n'existe pas dans
/// school_client). Appelle PATCH v1/password-change-user, authentifié par
/// le token déjà sauvegardé par AuthState.login().
/// Fond/textes/champs réactifs au thème (voir LoginScreen) — seul l'accent
/// or (AppColors.loginGold) reste fixe comme couleur de marque.
class FirstLoginPasswordScreen extends StatefulWidget {
  const FirstLoginPasswordScreen({super.key});

  @override
  State<FirstLoginPasswordScreen> createState() =>
      _FirstLoginPasswordScreenState();
}

class _FirstLoginPasswordScreenState extends State<FirstLoginPasswordScreen> {
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _showPassword = false;
  bool _showConfirm = false;
  String? _fieldError;

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final password = _passwordController.text;
    final confirm = _confirmController.text;

    if (password.isEmpty || confirm.isEmpty) {
      setState(() => _fieldError = 'Veuillez remplir tous les champs.');
      return;
    }
    if (password != confirm) {
      setState(() => _fieldError = 'Les mots de passe ne correspondent pas.');
      return;
    }
    setState(() => _fieldError = null);

    final auth = context.read<AuthState>();
    final success = await auth.changePasswordFirstLogin(password, confirm);
    if (!mounted) return;
    if (success) {
      Navigator.of(
        context,
      ).pushReplacement(MaterialPageRoute(builder: (_) => const AppShell()));
    } else {
      setState(() {});
    }
  }

  InputDecoration _darkField({required String hint, Widget? suffixIcon}) {
    return InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(color: AppColors.textMuted.withValues(alpha: 0.7)),
      filled: true,
      fillColor: AppColors.inputBg,
      suffixIcon: suffixIcon,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: AppColors.borderSubtle),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: AppColors.borderSubtle),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.loginGold),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final themeState = context.watch<ThemeState>();

    return Scaffold(
      backgroundColor: AppColors.appBg,
      body: Stack(
        children: [
          Positioned(
            right: 16,
            top: 12,
            child: Tooltip(
              message: themeState.isDark
                  ? 'Passer au thème clair'
                  : 'Passer au thème sombre',
              child: InkWell(
                borderRadius: BorderRadius.circular(18),
                onTap: () => themeState.setDark(!themeState.isDark),
                child: Container(
                  width: 36,
                  height: 36,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: AppColors.cardBg,
                    shape: BoxShape.circle,
                    border: Border.all(color: AppColors.borderSubtle),
                  ),
                  child: Icon(
                    themeState.isDark
                        ? Icons.dark_mode_outlined
                        : Icons.light_mode_outlined,
                    color: AppColors.loginGold,
                    size: 18,
                  ),
                ),
              ),
            ),
          ),
          Center(
            child: SingleChildScrollView(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 24,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Équivalent de label_89.
                      Text(
                        'Réinitialiser Votre mot de passe',
                        textAlign: TextAlign.center,
                        style: AppTheme.serif(24),
                      ),
                      const SizedBox(height: 24),
                      // Équivalent de error_message_2.
                      if (_fieldError != null || auth.errorMessage != null) ...[
                        Text(
                          _fieldError ?? auth.errorMessage!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: AppColors.danger,
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                      // Équivalent de password_for_reset.
                      TextField(
                        controller: _passwordController,
                        obscureText: !_showPassword,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 13,
                        ),
                        decoration: _darkField(
                          hint: 'Mot de passe',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _showPassword
                                  ? Icons.visibility_off_outlined
                                  : Icons.visibility_outlined,
                              color: AppColors.textMuted,
                              size: 18,
                            ),
                            onPressed: () =>
                                setState(() => _showPassword = !_showPassword),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),
                      // Équivalent de confirm_password.
                      TextField(
                        controller: _confirmController,
                        obscureText: !_showConfirm,
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 13,
                        ),
                        decoration: _darkField(
                          hint: 'Confirmer le mot de passe',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _showConfirm
                                  ? Icons.visibility_off_outlined
                                  : Icons.visibility_outlined,
                              color: AppColors.textMuted,
                              size: 18,
                            ),
                            onPressed: () =>
                                setState(() => _showConfirm = !_showConfirm),
                          ),
                        ),
                        onSubmitted: (_) => _submit(),
                      ),
                      const SizedBox(height: 18),
                      // Équivalent de btn_reset_password ("Réinitialiser").
                      SizedBox(
                        height: 46,
                        child: OutlinedButton(
                          style:
                              OutlinedButton.styleFrom(
                                foregroundColor: AppColors.loginGold,
                                side: const BorderSide(
                                  color: AppColors.loginGold,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ).copyWith(
                                backgroundColor:
                                    WidgetStateProperty.resolveWith((states) {
                                      if (auth.isLoading)
                                        return AppColors.textMuted.withValues(
                                          alpha: 0.3,
                                        );
                                      if (states.contains(WidgetState.hovered))
                                        return AppColors.loginGold;
                                      return null;
                                    }),
                                foregroundColor:
                                    WidgetStateProperty.resolveWith((states) {
                                      if (states.contains(WidgetState.hovered))
                                        return AppColors.appBg;
                                      return AppColors.loginGold;
                                    }),
                              ),
                          onPressed: auth.isLoading ? null : _submit,
                          child: auth.isLoading
                              ? const SizedBox(
                                  height: 18,
                                  width: 18,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: AppColors.loginGold,
                                  ),
                                )
                              : const Text(
                                  'Réinitialiser',
                                  style: TextStyle(fontWeight: FontWeight.w700),
                                ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
