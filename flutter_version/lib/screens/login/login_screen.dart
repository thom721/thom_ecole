import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/ip_storage.dart';
import '../../state/auth_state.dart';
import '../../theme/app_theme.dart';
import '../shell/app_shell.dart';
import 'first_login_password_screen.dart';

const _gold = Color(0xFFC9A84C);
const _loginBg = Color(0xFF0D0D14);
const _inputBg = Color(0xFF111111);
const _inputBorder = Color(0xFF222222);
const _mutedText = Color(0xFF7C7C7C);

/// Équivalent IDENTIQUE de connexion_page (Resources/main_school1.ui) et de
/// se_connecter()/handle_login_response() (Controllers/Main.py,
/// school_client) : un seul formulaire (email_2/password_2/btn_connexion),
/// pas de sélecteur de rôle — login_as est toujours 'as_desktop' et seuls
/// Personnel/Professeur sont autorisés (les étudiants n'ont pas le droit
/// de se connecter au bureau, voir AuthState.login()). Aucune fonctionnalité
/// "mot de passe oublié" : school_client n'en a pas, seulement la
/// réinitialisation automatique de première connexion (voir
/// FirstLoginPasswordScreen, qui reprend reset_password de la même .ui).
/// Seules les couleurs/police (fond sombre, accent or, Playfair Display)
/// restent une référence de STYLE reprise du reste de l'app (voir AppTheme).
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _ipController = TextEditingController();
  final _ipStorage = IpStorage();
  bool _obscurePassword = true;
  bool _showIpPanel = false;
  String? _ipMessage;

  @override
  void initState() {
    super.initState();
    _ipStorage.getServerIp().then((ip) {
      if (ip != null && mounted) {
        setState(() => _ipController.text = ip);
      }
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _ipController.dispose();
    super.dispose();
  }

  Future<void> _saveServerIp() async {
    final ip = _ipController.text.trim();
    final ipv4 = RegExp(r'^(\d{1,3}\.){3}\d{1,3}$');
    if (!ipv4.hasMatch(ip)) {
      setState(() => _ipMessage = 'Adresse IP invalide.');
      return;
    }
    await _ipStorage.saveServerIp(ip);
    // Équivalent de add_or_update_host() (Controllers/Main.py:4009-4057) :
    // met à jour /etc/hosts avec l'entrée aplekol360.local → ip.
    // Sur Mac/Linux, élève les privilèges via osascript/pkexec si nécessaire
    // (équivalent de run_as_admin(), Main.py:3597-3613).
    final hostsError = await _ipStorage.addOrUpdateHost(ip);
    setState(() {
      _ipMessage = hostsError == null
          ? 'IP enregistrée et fichier hosts mis à jour (aplekol360.local → $ip).'
          : 'IP enregistrée. Fichier hosts : $hostsError';
    });
  }

  Future<void> _submit() async {
    final auth = context.read<AuthState>();
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      auth.errorMessage = 'Veuillez remplir tous les champs.';
      setState(() {});
      return;
    }

    final success = await auth.login(email, password);
    if (!mounted) return;
    if (success) {
      final mustReset = auth.user?.mustResetPassword ?? false;
      if (mustReset) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const FirstLoginPasswordScreen()),
        );
      } else {
        Navigator.of(
          context,
        ).pushReplacement(MaterialPageRoute(builder: (_) => const AppShell()));
      }
    } else {
      setState(() {});
    }
  }

  InputDecoration _darkField({required String hint, Widget? suffixIcon}) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(color: Color(0xFF333333)),
      filled: true,
      fillColor: _inputBg,
      suffixIcon: suffixIcon,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: _inputBorder),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: _inputBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: _gold),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();

    return Scaffold(
      backgroundColor: _loginBg,
      body: Column(
        children: [
          // Équivalent de header_connexion/label_connect_3.
          Container(
            height: 48,
            alignment: Alignment.center,
            child: const Text(
              'Application de gestion des écoles',
              style: TextStyle(
                color: _mutedText,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(
            child: Center(
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
                        // Équivalent de logo/image_3.
                        Center(
                          child: Container(
                            width: 64,
                            height: 64,
                            alignment: Alignment.center,
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.06),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.school,
                              color: _gold,
                              size: 30,
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'Connexion',
                          textAlign: TextAlign.center,
                          style: AppTheme.serif(26),
                        ),
                        const SizedBox(height: 24),
                        if (auth.errorMessage != null) ...[
                          Text(
                            auth.errorMessage!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              color: AppColors.danger,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        // Équivalent de email_2 — accepte aussi un nom
                        // d'utilisateur, comme le champ "Identifiant / Email"
                        // du web (Login.vue) : le backend résout déjà l'un ou
                        // l'autre (ServiceAuth.find_user_by_credentials()).
                        TextField(
                          controller: _emailController,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                          ),
                          decoration: _darkField(
                            hint: 'Email ou nom d’utilisateur',
                          ),
                          keyboardType: TextInputType.text,
                          autofillHints: const [AutofillHints.username],
                        ),
                        const SizedBox(height: 14),
                        // Équivalent de password_2.
                        TextField(
                          controller: _passwordController,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                          ),
                          decoration: _darkField(
                            hint: 'Password',
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_off_outlined
                                    : Icons.visibility_outlined,
                                color: const Color(0xFF444444),
                                size: 18,
                              ),
                              onPressed: () => setState(
                                () => _obscurePassword = !_obscurePassword,
                              ),
                            ),
                          ),
                          obscureText: _obscurePassword,
                          onSubmitted: (_) => _submit(),
                        ),
                        const SizedBox(height: 8),
                        // Équivalent de show_frame_ip.
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () => setState(() {
                              _showIpPanel = !_showIpPanel;
                              _ipMessage = null;
                            }),
                            child: Text(
                              'show ip',
                              style: const TextStyle(
                                color: _mutedText,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                        // Équivalent de frame_238 (label_76/input_change_ip/change_ip).
                        if (_showIpPanel) ...[
                          const Text(
                            "Modifier l'ip",
                            style: TextStyle(color: _mutedText, fontSize: 12),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _ipController,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 13,
                                  ),
                                  decoration: _darkField(hint: '192.168.0.110'),
                                ),
                              ),
                              const SizedBox(width: 8),
                              OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: _gold,
                                  side: const BorderSide(color: _gold),
                                ),
                                onPressed: _saveServerIp,
                                child: const Text('Modifier'),
                              ),
                            ],
                          ),
                          if (_ipMessage != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              _ipMessage!,
                              style: const TextStyle(
                                fontSize: 11,
                                color: Color(0xFFF59E0B),
                              ),
                            ),
                          ],
                        ],
                        const SizedBox(height: 18),
                        // Équivalent de btn_connexion ("Valider"), même style
                        // outline/hover-rempli que la QSS (#btn_connexion).
                        SizedBox(
                          height: 46,
                          child: OutlinedButton(
                            style:
                                OutlinedButton.styleFrom(
                                  foregroundColor: _gold,
                                  side: const BorderSide(color: _gold),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ).copyWith(
                                  backgroundColor:
                                      WidgetStateProperty.resolveWith((states) {
                                        if (auth.isLoading)
                                          return const Color(0xFF333333);
                                        if (states.contains(
                                          WidgetState.hovered,
                                        ))
                                          return _gold;
                                        return null;
                                      }),
                                  foregroundColor:
                                      WidgetStateProperty.resolveWith((states) {
                                        if (states.contains(
                                          WidgetState.hovered,
                                        ))
                                          return _loginBg;
                                        return _gold;
                                      }),
                                ),
                            onPressed: auth.isLoading ? null : _submit,
                            child: auth.isLoading
                                ? const SizedBox(
                                    height: 18,
                                    width: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: _gold,
                                    ),
                                  )
                                : const Text(
                                    'Valider',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                          ),
                        ),
                      ],
                    ),
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
