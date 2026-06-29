import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/auth_state.dart';
import '../../state/dashboard_state.dart';
import '../../state/reference_data_state.dart';
import '../../state/theme_state.dart';
import '../../theme/app_theme.dart';
import '../abonnement/abonnement_screen.dart';
import '../administration/administration_screen.dart';
import '../cours/cours_screen.dart';
import '../dashboard/dashboard_screen.dart';
import '../etudiant/etudiant_screen.dart';
import '../finance/finance_screen.dart';
import '../log/log_screen.dart';
import '../login/login_screen.dart';
import '../notes/notes_screen.dart';
import '../paiement/paiement_screen.dart';
import '../presence/presence_screen.dart';
import '../parametres/parametres_screen.dart';
import '../placeholder/placeholder_screen.dart';
import '../professeur/professeur_screen.dart';
import '../profile/profile_screen.dart';
import '../promus/promus_screen.dart';
import '../rapport/rapport_screen.dart';

/// Contenu (libellés/ordre) repris du menu latéral de school_client
/// (Resources/main_school1.ui:frame_6 — ex: btn_left_vente s'affiche
/// "Finances", pas "Vente"). Le STYLE (sidebar sombre, icônes, disposition,
/// responsivité) reprend AdminLayout.vue du frontend web
/// (ecole_nginx/frontend) — voir AppColors pour la palette.
class NavItem {
  const NavItem(this.id, this.label, this.icon);
  final String id;
  final String label;
  final IconData icon;
}

const List<NavItem> kMainNavItems = [
  NavItem('home', 'Dashbord', Icons.grid_view_outlined),
  NavItem('admin', 'Administration', Icons.admin_panel_settings_outlined),
  NavItem('etudiant', 'Etudiant', Icons.school_outlined),
  NavItem('promus', 'Promus', Icons.trending_up),
  NavItem('prof', 'Professeur', Icons.person_outline),
  NavItem('cours', 'Cours', Icons.menu_book_outlined),
  NavItem('notes', 'Notes', Icons.grade_outlined),
  NavItem('presences', 'Présences', Icons.fact_check_outlined),
  NavItem('paiement', 'Paiement', Icons.credit_card_outlined),
  NavItem('vente', 'Finances', Icons.account_balance_outlined),
  NavItem('rapport', 'Rapport', Icons.bar_chart_outlined),
  NavItem('profile', 'Profile', Icons.badge_outlined),
];

const List<NavItem> kSecondaryNavItems = [
  NavItem('settings', 'Paramètres', Icons.settings_outlined),
  NavItem('log', 'Log', Icons.history),
  NavItem('actualiser', 'Actualiser', Icons.refresh),
  NavItem('a_propos', 'A Propos', Icons.info_outline),
  NavItem('abonnement', 'Abonnement', Icons.workspace_premium_outlined),
];

const List<NavItem> kAllNavItems = [...kMainNavItems, ...kSecondaryNavItems];

class NavSubItem {
  const NavSubItem(this.id, this.label, this.icon);
  /// Format "parentId.sousId" — même format utilisé dans accessible_tabs.
  final String id;
  final String label;
  final IconData icon;
}

/// Sous-onglets configurables par rôle. La clé est l'ID de l'onglet parent.
/// L'ID de chaque sous-onglet suit le format "parentId.sousId" pour être
/// stocké directement dans accessible_tabs sans collision avec les IDs
/// d'onglets principaux.
const Map<String, List<NavSubItem>> kSubNavItems = {
  'home': [
    NavSubItem('home.suivi_paiement', 'Suivi de paiement', Icons.show_chart_outlined),
    NavSubItem('home.stats_etudiant', 'Statistiques étudiants', Icons.groups_outlined),
    NavSubItem('home.classes', 'Détail des classes', Icons.apartment_outlined),
  ],
  'etudiant': [
    NavSubItem('etudiant.badge', 'Générer badge', Icons.badge_outlined),
  ],
  'vente': [
    NavSubItem('vente.vente', 'Vente', Icons.point_of_sale_outlined),
    NavSubItem('vente.produits', 'Produits', Icons.inventory_2_outlined),
    NavSubItem('vente.depenses', 'Dépenses', Icons.payments_outlined),
    NavSubItem('vente.prets', 'Prêts', Icons.handshake_outlined),
    NavSubItem('vente.payroll', 'Payroll', Icons.account_balance_wallet_outlined),
    NavSubItem('vente.transactions', 'Autre transaction', Icons.receipt_long_outlined),
  ],
  'profile': [
    NavSubItem('profile.ecole', "Profil de l'école", Icons.apartment_outlined),
    NavSubItem('profile.compte', 'Mon compte', Icons.manage_accounts_outlined),
    NavSubItem('profile.roles', 'Rôles', Icons.group_outlined),
    NavSubItem('profile.permissions', 'Permissions', Icons.lock_outline),
    NavSubItem('profile.vues', 'Vues', Icons.visibility_outlined),
  ],
  'settings': [
    NavSubItem('settings.exams', 'Examens', Icons.fact_check_outlined),
    NavSubItem('settings.facultes', 'Facultés', Icons.school_outlined),
    NavSubItem('settings.annees', 'Années', Icons.calendar_today_outlined),
    NavSubItem('settings.classes', 'Classes', Icons.apartment_outlined),
    NavSubItem('settings.paiements', 'Paiements', Icons.credit_card_outlined),
    NavSubItem('settings.frais', 'Frais', Icons.receipt_long_outlined),
    NavSubItem('settings.frais_divers', 'Frais Divers', Icons.receipt_outlined),
    NavSubItem('settings.ajouter', 'Ajouter', Icons.add_circle_outline),
    NavSubItem('settings.modifier', 'Modifier', Icons.edit_outlined),
    NavSubItem('settings.supprimer', 'Supprimer', Icons.delete_outline),
    NavSubItem('settings.voir', 'Voir détails', Icons.remove_red_eye_outlined),
  ],
};

const _sidebarExpandedWidth = 240.0;
// 68 pile suffisait en théorie pour le logo replié (36 + 16+16 de padding)
// mais la bordure droite du conteneur (BorderSide, 1px) est automatiquement
// retranchée de la largeur de contenu disponible par Container — ce qui
// provoquait un RenderFlex overflow de 1px sur l'en-tête de la sidebar.
const _sidebarCollapsedWidth = 70.0;
const _collapseBreakpoint = 1280.0;

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  String _currentPageId = 'home';
  bool _collapsed = false;

  /// _navTile() n'a pas accès à la variable locale `collapsed` calculée
  /// dans build() (qui combine _collapsed ET la largeur de fenêtre) — sans
  /// ce getter, les tuiles de nav restaient en disposition "étendue" (icône
  /// + libellé) même quand la fenêtre repassait sous _collapseBreakpoint et
  /// que la sidebar elle-même rétrécissait à _sidebarCollapsedWidth, ce qui
  /// ne laissait plus aucune marge pour le Row et provoquait un
  /// RenderFlex overflow (~1px, le pire cas dépendant des arrondis de
  /// l'AnimatedContainer).
  bool get _isCollapsed =>
      _collapsed || MediaQuery.of(context).size.width < _collapseBreakpoint;

  Widget _buildPage(String id) {
    switch (id) {
      case 'home':
        return DashboardScreen();
      case 'admin':
        return AdministrationScreen();
      case 'etudiant':
        return EtudiantScreen();
      case 'prof':
        return ProfesseurScreen();
      case 'cours':
        return CoursScreen();
      case 'notes':
        return NotesScreen();
      case 'presences':
        return PresenceScreen();
      case 'paiement':
        return PaiementScreen();
      case 'vente':
        return FinanceScreen();
      case 'settings':
        return ParametresScreen();
      case 'profile':
        return ProfileScreen();
      case 'rapport':
        return RapportScreen();
      case 'promus':
        return PromusScreen();
      case 'log':
        return LogScreen();
      case 'abonnement':
        return AbonnementScreen();
      default:
        final item = kAllNavItems.firstWhere((e) => e.id == id);
        return PlaceholderScreen(title: item.label);
    }
  }

  Future<void> _logout(AuthState auth) async {
    await auth.logout();
    if (mounted) {
      Navigator.of(
        context,
      ).pushReplacement(MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  /// Équivalent de actualiser_page() (Controllers/Main.py:13371-13381) :
  /// "Actualiser" n'est PAS une page (contrairement à 'a_propos', qui ouvre
  /// une boîte de dialogue) — elle recharge les données de référence
  /// partagées sans changer la page affichée, donc on ne touche pas à
  /// _currentPageId ici.
  Future<void> _actualiser() async {
    await context.read<ReferenceDataState>().refresh();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Données actualisées.')),
    );
  }

  void _select(String id) {
    if (id == 'actualiser') {
      _actualiser();
      return;
    }
    setState(() => _currentPageId = id);
    if (id == 'home') {
      context.read<DashboardState>().load();
    } else if (id == 'a_propos') {
      showAboutDialog(
        context: context,
        applicationName: 'Lekol360',
        applicationVersion: '1.0.1',
      );
    }
  }

  Widget _navTile(NavItem item) {
    final selected = item.id == _currentPageId;
    final tile = Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 1),
      decoration: BoxDecoration(
        color: selected
            ? AppColors.accent.withValues(alpha: 0.13)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          hoverColor: AppColors.hoverOverlay,
          onTap: () => _select(item.id),
          child: Padding(
            padding: _isCollapsed
                ? const EdgeInsets.symmetric(vertical: 11)
                : const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
            child: Row(
              mainAxisAlignment: _isCollapsed
                  ? MainAxisAlignment.center
                  : MainAxisAlignment.start,
              children: [
                Icon(
                  item.icon,
                  size: 18,
                  color: selected ? AppColors.accent : AppColors.sidebarTextMuted,
                ),
                if (!_isCollapsed) ...[
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      item.label,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 13.5,
                        color: selected
                            ? AppColors.accent
                            : AppColors.sidebarTextMuted,
                        fontWeight: selected
                            ? FontWeight.w600
                            : FontWeight.normal,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
    return _isCollapsed ? Tooltip(message: item.label, child: tile) : tile;
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    // Forcer la reconstruction de tout l'arbre de pages quand le thème
    // bascule : AppColors n'est plus `static const` (lib/theme/app_theme.dart)
    // mais les écrans renvoyés par _buildPage() ne sont plus `const`
    // (sinon Flutter réutilise l'instance précédente sans rappeler build()
    // et les couleurs ne se rafraîchiraient jamais).
    final themeState = context.watch<ThemeState>();
    final visible = auth.visibleNavItems;
    final mainItems = kMainNavItems
        .where((e) => visible.contains(e.id))
        .toList();
    final secondaryItems = kSecondaryNavItems
        .where((e) => e.id == 'a_propos' || visible.contains(e.id))
        .toList();
    final currentLabel = kAllNavItems
        .firstWhere((e) => e.id == _currentPageId)
        .label;

    final narrow = MediaQuery.of(context).size.width < _collapseBreakpoint;
    final collapsed = _collapsed || narrow;
    final sidebarWidth = collapsed
        ? _sidebarCollapsedWidth
        : _sidebarExpandedWidth;

    return Scaffold(
      backgroundColor: AppColors.appBg,
      body: Column(
        children: [
          Expanded(
            child: Row(
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  width: sidebarWidth,
                  decoration: BoxDecoration(
                    color: AppColors.sidebarBg,
                    border: Border(
                      right: BorderSide(color: AppColors.sidebarBorder),
                    ),
                  ),
                  // En-tête et pied (profil) fixes, seule la nav défile dans
                  // l'Expanded+SingleChildScrollView ci-dessous — gardait
                  // tout en un seul bloc défilant auparavant, mais l'en-tête
                  // doit rester visible quel que soit le défilement de la
                  // nav.
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Container(height: 3, color: AppColors.accent),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 18,
                        ),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(color: AppColors.sidebarBorder),
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: collapsed
                              ? MainAxisAlignment.center
                              : MainAxisAlignment.start,
                          children: [
                            Container(
                              width: 36,
                              height: 36,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                color: AppColors.accent,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Text(
                                'L',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 17,
                                ),
                              ),
                            ),
                            if (!collapsed) ...[
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text('Lekol360',
                                        style: AppTheme.serif(15, color: AppColors.sidebarText)),
                                    Text(
                                      'Espace Admin',
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: AppColors.sidebarTextMuted,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      Expanded(
                        child: SingleChildScrollView(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                if (!collapsed)
                                  Padding(
                                    padding: EdgeInsets.fromLTRB(16, 4, 16, 6),
                                    child: Text(
                                      'NAVIGATION',
                                      style: TextStyle(
                                        fontSize: 10,
                                        letterSpacing: 1.2,
                                        color: AppColors.sidebarTextMuted,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ...mainItems.map(_navTile),
                                if (secondaryItems.isNotEmpty) ...[
                                  if (!collapsed)
                                    Padding(
                                      padding: EdgeInsets.fromLTRB(
                                        16,
                                        16,
                                        16,
                                        6,
                                      ),
                                      child: Text(
                                        'GESTION',
                                        style: TextStyle(
                                          fontSize: 10,
                                          letterSpacing: 1.2,
                                          color: AppColors.sidebarTextMuted,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    )
                                  else
                                    Divider(
                                      height: 16,
                                      color: AppColors.sidebarBorder,
                                    ),
                                  ...secondaryItems.map(_navTile),
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                      _ThemeToggleTile(
                        collapsed: collapsed,
                        isDark: themeState.isDark,
                        onToggle: () => context.read<ThemeState>().toggle(),
                      ),
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          border: Border(
                            top: BorderSide(color: AppColors.sidebarBorder),
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: collapsed
                              ? MainAxisAlignment.center
                              : MainAxisAlignment.start,
                          children: [
                            Container(
                              width: 34,
                              height: 34,
                              alignment: Alignment.center,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [AppColors.accent, Color(0xFF6EE7B7)],
                                ),
                              ),
                              child: Text(
                                (auth.user?.email ?? '?').characters.first
                                    .toUpperCase(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                            if (!collapsed) ...[
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  auth.user?.email ?? '',
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                    fontSize: 12.5,
                                    color: AppColors.sidebarText,
                                  ),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _TopBar(
                        currentLabel: currentLabel,
                        collapsed: _collapsed,
                        onToggleCollapse: narrow
                            ? null
                            : () => setState(() => _collapsed = !_collapsed),
                        onLogout: () => _logout(auth),
                      ),
                      Expanded(
                        child: Container(
                          color: AppColors.appBg,
                          child: _buildPage(_currentPageId),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 10),
            decoration: BoxDecoration(
              color: AppColors.appBg,
              border: Border(top: BorderSide(color: AppColors.borderSubtle)),
            ),
            alignment: Alignment.center,
            child: Text(
              'Lekol360 © ${DateTime.now().year} · Version 1.0.1',
              style: TextStyle(fontSize: 11, color: AppColors.textMuted),
            ),
          ),
        ],
      ),
    );
  }
}

/// Sélecteur clair/sombre — fonctionnalité Flutter sans équivalent réel
/// (school_client et le frontend web sont exclusivement sombres). Reprend le
/// style des tuiles de nav (_navTile) pour rester visuellement cohérent.
class _ThemeToggleTile extends StatelessWidget {
  const _ThemeToggleTile({
    required this.collapsed,
    required this.isDark,
    required this.onToggle,
  });

  final bool collapsed;
  final bool isDark;
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) {
    final icon = isDark ? Icons.dark_mode_outlined : Icons.light_mode_outlined;
    final tile = Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 1),
      decoration: BoxDecoration(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          hoverColor: AppColors.hoverOverlay,
          onTap: onToggle,
          child: Padding(
            padding: collapsed
                ? const EdgeInsets.symmetric(vertical: 11)
                : const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
            child: Row(
              mainAxisAlignment: collapsed
                  ? MainAxisAlignment.center
                  : MainAxisAlignment.start,
              children: [
                Icon(icon, size: 18, color: AppColors.sidebarTextMuted),
                if (!collapsed) ...[
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      isDark ? 'Thème sombre' : 'Thème clair',
                      style: const TextStyle(
                        fontSize: 13.5,
                        color: AppColors.sidebarTextMuted,
                      ),
                    ),
                  ),
                  Switch(
                    value: isDark,
                    onChanged: (_) => onToggle(),
                    activeThumbColor: AppColors.accent,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
    return collapsed
        ? Tooltip(message: 'Thème clair / sombre', child: tile)
        : tile;
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({
    required this.currentLabel,
    required this.collapsed,
    required this.onToggleCollapse,
    required this.onLogout,
  });

  final String currentLabel;
  final bool collapsed;
  final VoidCallback? onToggleCollapse;
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.appBg,
        border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: Row(
        children: [
          if (onToggleCollapse != null)
            IconButton(
              icon: Icon(
                collapsed ? Icons.menu : Icons.menu_open,
                color: AppColors.textPrimary,
              ),
              onPressed: onToggleCollapse,
            ),
          const SizedBox(width: 4),
          Text(
            'Lekol360',
            style: TextStyle(fontSize: 13, color: AppColors.textMuted),
          ),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 8),
            child: Text('/', style: TextStyle(color: AppColors.textMuted)),
          ),
          Text(
            currentLabel,
            style: TextStyle(
              fontSize: 13,
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          PopupMenuButton<String>(
            color: AppColors.panelBg,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: AppColors.borderHover),
            ),
            offset: const Offset(0, 44),
            itemBuilder: (context) => [
              PopupMenuItem(
                enabled: false,
                child: Text(
                  auth.user?.email ?? '',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 12.5,
                  ),
                ),
              ),
              const PopupMenuDivider(),
              PopupMenuItem(
                value: 'logout',
                onTap: onLogout,
                child: const Row(
                  children: [
                    Icon(Icons.logout, size: 16, color: AppColors.danger),
                    SizedBox(width: 8),
                    Text(
                      'Se déconnecter',
                      style: TextStyle(color: AppColors.danger),
                    ),
                  ],
                ),
              ),
            ],
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 30,
                  height: 30,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [AppColors.accent, Color(0xFF6EE7B7)],
                    ),
                  ),
                  child: Text(
                    (auth.user?.email ?? '?').characters.first.toUpperCase(),
                    style: TextStyle(
                      color: AppColors.appBg,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.expand_more, size: 18, color: AppColors.textMuted),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
