import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';
import 'appel_tab.dart';
import 'historique_tab.dart';
import 'stats_tab.dart';

/// Équivalent de Presences.vue (ecole_nginx/frontend/src/views/admin/
/// Presences.vue) — fonctionnalité absente du bureau (school_client),
/// reprise du web sur demande explicite : 3 onglets (Appel du jour,
/// Historique, Statistiques). Le web utilise de simples boutons qui
/// togglent `activeSub` ; on reprend ici le pill-switcher déjà utilisé pour
/// Finances (FinanceScreen) pour rester cohérent avec le reste de l'app.
class PresenceScreen extends StatefulWidget {
  const PresenceScreen({super.key});

  @override
  State<PresenceScreen> createState() => _PresenceScreenState();
}

enum _Tab { appel, historique, stats }

class _PresenceScreenState extends State<PresenceScreen> {
  _Tab _tab = _Tab.appel;

  Widget _buildSwitcher() {
    Widget pill(_Tab value, String label, IconData icon) {
      final selected = _tab == value;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: selected ? AppColors.hoverOverlay : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => setState(() => _tab = value),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    size: 15,
                    color: selected
                        ? AppColors.accentLight
                        : AppColors.textMuted,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: selected
                          ? AppColors.textPrimary
                          : AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          pill(_Tab.appel, 'Appel du jour', Icons.fact_check_outlined),
          pill(_Tab.historique, 'Historique', Icons.history),
          pill(_Tab.stats, 'Statistiques', Icons.insights_outlined),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Présences',
            subtitle: "Appel du jour, historique et statistiques d'assiduité",
            icon: Icons.fact_check_outlined,
            colorKey: 'sky',
          ),
          const SizedBox(height: 16),
          _buildSwitcher(),
          const SizedBox(height: 16),
          Expanded(
            child: switch (_tab) {
              _Tab.appel => AppelTab(),
              _Tab.historique => HistoriqueTab(),
              _Tab.stats => StatsTab(),
            },
          ),
        ],
      ),
    );
  }
}
