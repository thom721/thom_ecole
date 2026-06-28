import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/presence_state.dart';
import '../../theme/app_theme.dart';

/// Équivalent de l'onglet "Statistiques" de Presences.vue — chargé
/// uniquement à l'ouverture de l'onglet (pas au montage de la page), comme
/// `watch(activeSub, ...)` côté web. "Retards" reste à 0 : le modèle
/// `Presence` n'a pas de notion de retard (cf. RPresences.py).
class StatsTab extends StatefulWidget {
  const StatsTab({super.key});

  @override
  State<StatsTab> createState() => _StatsTabState();
}

class _StatsTabState extends State<StatsTab> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PresenceState>().loadStats();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PresenceState>();

    if (state.isLoadingStats) {
      return const Center(child: CircularProgressIndicator());
    }
    if (state.statsError != null) {
      return Center(
        child: Text(
          state.statsError!,
          style: TextStyle(color: AppColors.textPrimary),
        ),
      );
    }
    final global = state.statsGlobal;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'Taux de présence',
                  value: '${global?.tauxPresence.toStringAsFixed(0) ?? 0}%',
                  colorKey: 'emerald',
                  icon: Icons.fact_check_outlined,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Élèves inscrits',
                  value: '${global?.totalInscrits ?? 0}',
                  colorKey: 'blue',
                  icon: Icons.groups_outlined,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: "Absents aujourd'hui",
                  value: '${global?.absents ?? 0}',
                  colorKey: 'rose',
                  icon: Icons.person_off_outlined,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  label: 'Retards',
                  value: 'N/A',
                  colorKey: 'amber',
                  icon: Icons.schedule_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.sidebarBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Présence par classe',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 12),
                if (state.statsClasses.isEmpty)
                  Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text(
                      "Aucune donnée de présence aujourd'hui.",
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  )
                else
                  ...state.statsClasses.map((c) {
                    final color = c.val > 85
                        ? const Color(0xFF34D399)
                        : c.val > 70
                        ? const Color(0xFFFBBF24)
                        : AppColors.danger;
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 140,
                            child: Text(
                              c.classe,
                              style: TextStyle(
                                fontSize: 12.5,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ),
                          Expanded(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: (c.val / 100).clamp(0, 1),
                                minHeight: 8,
                                backgroundColor: AppColors.hoverOverlay,
                                color: color,
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          SizedBox(
                            width: 90,
                            child: Text(
                              '${c.presents}/${c.total} (${c.val.toStringAsFixed(0)}%)',
                              textAlign: TextAlign.right,
                              style: TextStyle(
                                fontSize: 11.5,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.value,
    required this.colorKey,
    required this.icon,
  });

  final String label;
  final String value;
  final String colorKey;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final palette =
        AppColors.cardPalette[colorKey] ?? AppColors.cardPalette['blue']!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.sidebarBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: palette.bar.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, size: 18, color: palette.text),
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}
