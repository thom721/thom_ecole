import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/api_client.dart';
import 'core/token_storage.dart';
import 'state/abonnement_state.dart';
import 'state/account_state.dart';
import 'state/auth_state.dart';
import 'state/cours_state.dart';
import 'state/dashboard_state.dart';
import 'state/depense_state.dart';
import 'state/loan_state.dart';
import 'state/log_state.dart';
import 'state/paiement_state.dart';
import 'state/parametres_state.dart';
import 'state/note_state.dart';
import 'state/payroll_state.dart';
import 'state/personnel_state.dart';
import 'state/presence_state.dart';
import 'state/produit_state.dart';
import 'state/professeur_state.dart';
import 'state/profile_state.dart';
import 'state/programme_state.dart';
import 'state/promus_state.dart';
import 'state/rapport_state.dart';
import 'state/reference_data_state.dart';
import 'state/role_permission_state.dart';
import 'state/students_state.dart';
import 'state/theme_state.dart';
import 'state/transaction_state.dart';
import 'state/vente_state.dart';
import 'screens/login/login_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const SchoolClientApp());
}

class SchoolClientApp extends StatelessWidget {
  const SchoolClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    final tokenStorage = TokenStorage();
    final apiClient = ApiClient(tokenStorage);

    return MultiProvider(
      providers: [
        Provider<TokenStorage>.value(value: tokenStorage),
        Provider<ApiClient>.value(value: apiClient),
        ChangeNotifierProvider(
          create: (_) => AuthState(apiClient, tokenStorage),
        ),
        ChangeNotifierProvider(create: (_) => DashboardState(apiClient)),
        ChangeNotifierProvider(create: (_) => ReferenceDataState(apiClient)),
        ChangeNotifierProvider(create: (_) => StudentsState(apiClient)),
        ChangeNotifierProvider(create: (_) => PaiementState(apiClient)),
        ChangeNotifierProvider(create: (_) => ParametresState(apiClient)),
        ChangeNotifierProvider(create: (_) => ProfileState(apiClient)),
        ChangeNotifierProvider(create: (_) => ProfesseurState(apiClient)),
        ChangeNotifierProvider(create: (_) => PersonnelState(apiClient)),
        ChangeNotifierProvider(create: (_) => CoursState(apiClient)),
        ChangeNotifierProvider(create: (_) => ProgrammeState(apiClient)),
        ChangeNotifierProvider(create: (_) => NoteState(apiClient)),
        ChangeNotifierProvider(create: (_) => RolePermissionState(apiClient)),
        ChangeNotifierProvider(create: (_) => RapportState(apiClient)),
        ChangeNotifierProvider(create: (_) => ProduitState(apiClient)),
        ChangeNotifierProvider(create: (_) => VenteState(apiClient)),
        ChangeNotifierProvider(create: (_) => DepenseState(apiClient)),
        ChangeNotifierProvider(create: (_) => LoanState(apiClient)),
        ChangeNotifierProvider(create: (_) => PayrollState(apiClient)),
        ChangeNotifierProvider(create: (_) => TransactionState(apiClient)),
        ChangeNotifierProvider(create: (_) => PresenceState(apiClient)),
        ChangeNotifierProvider(create: (_) => AbonnementState(apiClient)),
        ChangeNotifierProvider(create: (_) => LogState(apiClient)),
        ChangeNotifierProvider(create: (_) => PromusState(apiClient)),
        ChangeNotifierProvider(create: (_) => AccountState(apiClient)),
        ChangeNotifierProvider(create: (_) => ThemeState()..load()),
      ],
      child: Consumer<ThemeState>(
        builder: (context, themeState, _) => MaterialApp(
          title: 'Lekol360',
          theme: themeState.isDark ? AppTheme.dark : AppTheme.light,
          debugShowCheckedModeBanner: false,
          home: const LoginScreen(),
        ),
      ),
    );
  }
}
