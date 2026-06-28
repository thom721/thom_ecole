import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/dashboard_stats.dart';
import '../../state/auth_state.dart';
import '../../state/dashboard_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import 'classe_students_dialog.dart';
import 'etudiant_stats_panel.dart';
import 'paiement_stats_panel.dart';

enum _ActiveSection { etudiant, paiement, classe }

/// Équivalent de dash_page()/show_data_in_dash() (Controllers/Main.py,
/// school_client) pour les DONNÉES de base (6 stats, masquage "********"
/// pour les rôles non admin/Comptable) — étendu, sur demande explicite, avec
/// les panneaux interactifs du frontend web (Dashboard.vue +
/// AdminDashComposante.vue + DashboardStudentStats.vue + PaiementsStats.vue,
/// ecole_nginx/frontend) : drill-down élèves, drill-down paiements, et liste
/// d'élèves par classe ("Gérer"). Un seul panneau actif à la fois, comme le
/// `openAccordionIndex` unique du web.
///
/// "Absences" et "Cours programmés" sont des valeurs littéralement codées en
/// dur (7 et 94) dans Dashboard.vue, sans aucun appel API derrière — repris
/// ici à l'identique (décoratifs, non cliquables) pour la parité visuelle
/// avec le web, sur demande explicite.
///
/// Volontairement omis : "Notes" (présent dans la version précédente de cet
/// écran, fidèle à school_client) — retiré, le champ correspondant n'étant
/// alimenté par aucun show_data_in_dash() et absent du frontend web.
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Le web ouvre le panneau Paiement par défaut au montage
  // (Dashboard.vue: onMounted -> openAccordionIndex.value = 3).
  _ActiveSection? _activeSection = _ActiveSection.paiement;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      final referenceData = context.read<ReferenceDataState>();
      final dashboard = context.read<DashboardState>();
      await referenceData.loadOnce();
      if (!mounted) return;
      await dashboard.load();
    });
  }

  void _toggle(_ActiveSection section) {
    setState(() => _activeSection = _activeSection == section ? null : section);
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardState>();
    final roles = context.watch<AuthState>().roles;
    final canSeeRealNumbers = roles.contains('admin') || roles.contains('Comptable');

    if (dashboard.isLoading && dashboard.stats == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (dashboard.errorMessage != null) {
      return Center(
        child: Text(dashboard.errorMessage!, style: TextStyle(color: AppColors.textPrimary)),
      );
    }
    final stats = dashboard.stats;
    if (stats == null) {
      return const SizedBox.shrink();
    }

    String mask(Object value) => canSeeRealNumbers ? value.toString() : '********';

    final cards = [
      _DashCard(
        title: 'Étudiant',
        value: mask(stats.etudiant),
        icon: Icons.groups_outlined,
        colorKey: 'blue',
        showExpand: true,
        expandEnabled: canSeeRealNumbers,
        active: _activeSection == _ActiveSection.etudiant,
        onExpand: () => _toggle(_ActiveSection.etudiant),
      ),
      _DashCard(
        title: 'Paiement',
        value: canSeeRealNumbers ? stats.paiement.toStringAsFixed(1) : '******',
        devise: stats.devise,
        icon: Icons.credit_card_outlined,
        colorKey: 'emerald',
        showExpand: true,
        expandEnabled: canSeeRealNumbers,
        active: _activeSection == _ActiveSection.paiement,
        onExpand: () => _toggle(_ActiveSection.paiement),
      ),
      _DashCard(
        title: 'Professeur',
        value: mask(stats.professeur),
        icon: Icons.workspace_premium_outlined,
        colorKey: 'violet',
        showExpand: true,
      ),
      _DashCard(
        title: 'Personnel',
        value: mask(stats.personnel),
        icon: Icons.badge_outlined,
        colorKey: 'cyan',
        showExpand: true,
      ),
      _DashCard(
        title: 'Classe',
        value: mask(stats.classes),
        icon: Icons.apartment_outlined,
        colorKey: 'amber',
        showExpand: true,
        expandEnabled: canSeeRealNumbers,
        active: _activeSection == _ActiveSection.classe,
        onExpand: () => _toggle(_ActiveSection.classe),
      ),
      // Décoratives, identiques au web (valeurs codées en dur, sans API).
      _DashCard(
        title: 'Absences',
        value: mask(7),
        icon: Icons.event_busy_outlined,
        colorKey: 'rose',
        showExpand: true,
      ),
      _DashCard(
        title: 'Cours',
        value: mask(stats.cours),
        icon: Icons.menu_book_outlined,
        colorKey: 'sky',
        showExpand: true,
      ),
      _DashCard(
        title: 'Cours programmés',
        value: mask(94),
        icon: Icons.calendar_month_outlined,
        colorKey: 'purple',
        showExpand: true,
      ),
    ];

    return RefreshIndicator(
      onRefresh: () => context.read<DashboardState>().load(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const _DashHeader(),
            const SizedBox(height: 20),
            LayoutBuilder(
              builder: (context, constraints) {
                final cols = constraints.maxWidth >= 1000
                    ? 4
                    : constraints.maxWidth >= 700
                        ? 2
                        : 1;
                return GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  // Hauteur fixe (et non un aspect ratio, qui fait varier la
                  // hauteur avec la largeur disponible) — AdminDashComposante.vue
                  // n'a pas de hauteur figée en CSS, mais sa hauteur intrinsèque
                  // (padding p-4 + contenu) est stable ; on la fige ici pour éviter
                  // tout overflow/écrasement du contenu à certaines largeurs.
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: cols,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    mainAxisExtent: 128,
                  ),
                  itemCount: cards.length,
                  itemBuilder: (context, index) => cards[index],
                );
              },
            ),
            if (_activeSection != null) ...[
              const SizedBox(height: 24),
              switch (_activeSection!) {
                _ActiveSection.etudiant => EtudiantStatsPanel(),
                _ActiveSection.paiement => PaiementStatsPanel(),
                _ActiveSection.classe => _ClasseDetailsTable(details: stats.classeDetails),
              },
            ],
          ],
        ),
      ),
    );
  }
}

class _DashHeader extends StatelessWidget {
  const _DashHeader();

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.accent.withValues(alpha: 0.1),
            border: Border.all(color: AppColors.accent.withValues(alpha: 0.2)),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(Icons.grid_view_outlined, size: 18, color: AppColors.accentLight),
        ),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tableau de bord',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            Text("Vue d'ensemble de l'établissement",
                style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
          ],
        ),
      ],
    );
  }
}

class _DashCard extends StatelessWidget {
  const _DashCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.colorKey,
    this.devise,
    this.showExpand = false,
    this.expandEnabled = false,
    this.active = false,
    this.onExpand,
  });

  final String title;
  final String value;
  final String? devise;
  final IconData icon;
  final String colorKey;
  final bool showExpand;
  final bool expandEnabled;
  final bool active;
  final VoidCallback? onExpand;

  @override
  Widget build(BuildContext context) {
    final palette = AppColors.cardPalette[colorKey]!;
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: active ? palette.bar.withValues(alpha: 0.5) : AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Stack(
        children: [
          // Barre d'accent sur toute la hauteur de la card, comme
          // AdminDashComposante.vue:8-11 (`top-0 left-0 w-1 h-full
          // rounded-l-2xl`) — pas une barre courte décalée du haut.
          Positioned(
            left: 0,
            top: 0,
            bottom: 0,
            child: Container(width: 4, color: palette.bar),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 14, 14, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title.toUpperCase(),
                        style: TextStyle(
                          fontSize: 10,
                          letterSpacing: 1.1,
                          fontWeight: FontWeight.w600,
                          color: palette.text,
                        ),
                      ),
                    ),
                    if (showExpand)
                      SizedBox(
                        width: 24,
                        height: 24,
                        child: IconButton(
                          padding: EdgeInsets.zero,
                          iconSize: 14,
                          style: IconButton.styleFrom(
                            backgroundColor: active ? palette.bar.withValues(alpha: 0.18) : AppColors.hoverOverlay,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          icon: Icon(active ? Icons.remove : Icons.add, color: palette.text),
                          onPressed: expandEnabled ? onExpand : null,
                        ),
                      ),
                  ],
                ),
                const Spacer(),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: palette.bar.withValues(alpha: 0.1),
                        border: Border.all(color: palette.bar.withValues(alpha: 0.2)),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(icon, size: 16, color: palette.text),
                    ),
                    const Spacer(),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          value,
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        if (devise != null)
                          Text(devise!, style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Équivalent de show_student_number_in_classes() (Controllers/Main.py:7332-
/// 7343) : colonnes "Niveau / Cycle", "Classe", "Nb Eleve", "Prof" — pas de
/// colonne Id visible (sur demande explicite), même si le bureau en montre
/// une (elle ne sert là-bas qu'à retrouver la ligne cliquée, voir
/// ClasseDetail.classeId, toujours utilisé en interne pour "Gérer").
/// Source des lignes : classeDetails dans la réponse GET v1/dashboard
/// (ecole_nginx app/Schemas/Dashboard.py).
///
/// Le bouton "Gérer" reprend le VRAI clic de ligne du bureau
/// (on_row_clicked_class_show(), Controllers/Main.py:7346 → GET
/// v1/student-with-classe) : voir showClasseStudentsDialog().
class _ClasseDetailsTable extends StatelessWidget {
  const _ClasseDetailsTable({required this.details});

  final List<ClasseDetail> details;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.1),
                  border: Border.all(color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.2)),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.apartment_outlined, size: 16, color: Color(0xFFFBBF24)),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Détails des Classes',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                  Text('Répartition des étudiants par classe.',
                      style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: const [
                DataColumn(label: Text('NIVEAU / CYCLE')),
                DataColumn(label: Text('CLASSE')),
                DataColumn(label: Text('NB ELEVE')),
                DataColumn(label: Text('PROF')),
                DataColumn(label: Text('')),
              ],
              rows: details.map((d) {
                return DataRow(cells: [
                  DataCell(Text(d.niveauName)),
                  DataCell(Text(d.nomClasse)),
                  DataCell(Text(d.etudiantCount.toString())),
                  DataCell(Text(d.professeur ?? '-')),
                  DataCell(
                    TextButton(
                      onPressed: () => showClasseStudentsDialog(
                        context,
                        classeId: d.classeId,
                        anneeId: d.anneeAcademiqueId,
                        nomClasse: d.nomClasse,
                      ),
                      child: const Text('Gérer'),
                    ),
                  ),
                ]);
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
