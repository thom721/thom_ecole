import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/parametres_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import 'tabs/annees_tab.dart';
import 'tabs/classes_tab.dart';
import 'tabs/examens_tab.dart';
import 'tabs/facultes_tab.dart';
import 'tabs/frais_divers_tab.dart';
import 'tabs/frais_tab.dart';
import 'tabs/paiements_tab.dart';

class _ParamTab {
  const _ParamTab(this.id, this.label, this.icon);
  final String id;
  final String label;
  final IconData icon;
}

const _tabs = [
  _ParamTab('exams', 'Examens', Icons.fact_check_outlined),
  _ParamTab('facultes', 'Facultés', Icons.school_outlined),
  _ParamTab('annees', 'Années', Icons.calendar_today_outlined),
  _ParamTab('classes', 'Classes', Icons.apartment_outlined),
  _ParamTab('paiements', 'Paiements', Icons.credit_card_outlined),
  _ParamTab('frais', 'Frais', Icons.receipt_long_outlined),
  _ParamTab('frais_divers', 'Frais Divers', Icons.receipt_outlined),
];

/// Équivalent de settings_page() (school_client, Controllers/Main.py:13384)
/// pour les DONNÉES/LOGIQUE — le STYLE (barre d'onglets pilule, cartes,
/// modales) reprend exactement ecole_nginx/frontend/src/views/admin/
/// Parametres.vue (seul fichier réellement routé pour "Paramètres").
class ParametresScreen extends StatefulWidget {
  const ParametresScreen({super.key});

  @override
  State<ParametresScreen> createState() => _ParametresScreenState();
}

class _ParametresScreenState extends State<ParametresScreen> {
  String _activeTab = 'exams';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      await context.read<ReferenceDataState>().loadOnce();
      if (!mounted) return;
      final state = context.read<ParametresState>();
      await Future.wait([
        state.loadExamens(),
        state.loadFacultes(),
        state.loadAnnees(),
        state.loadClasses(),
        state.loadPaiementParams(),
        state.loadFrais(),
        state.loadFraisDivers(),
      ]);
    });
  }

  Widget _buildTabContent(String id) {
    switch (id) {
      case 'exams':
        return ExamensTab();
      case 'facultes':
        return FacultesTab();
      case 'annees':
        return AnneesTab();
      case 'classes':
        return ClassesTab();
      case 'paiements':
        return PaiementsTab();
      case 'frais':
        return FraisTab();
      case 'frais_divers':
        return FraisDiversTab();
      default:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Paramètres Académiques',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          const SizedBox(height: 2),
          Text('Gérez les configurations de votre établissement',
              style: TextStyle(fontSize: 13, color: AppColors.textMuted)),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(16),
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: _tabs.map((tab) {
                  final selected = tab.id == _activeTab;
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Material(
                      color: selected ? AppColors.hoverOverlay : Colors.transparent,
                      borderRadius: BorderRadius.circular(12),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(12),
                        onTap: () => setState(() => _activeTab = tab.id),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(tab.icon, size: 15, color: selected ? AppColors.accentLight : AppColors.textMuted),
                              const SizedBox(width: 8),
                              Text(
                                tab.label,
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: selected ? AppColors.textPrimary : AppColors.textMuted,
                                ),
                              ),
                              if (selected) ...[
                                const SizedBox(width: 6),
                                Container(
                                  width: 6,
                                  height: 6,
                                  decoration: BoxDecoration(color: AppColors.accent, shape: BoxShape.circle),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(child: SingleChildScrollView(child: _buildTabContent(_activeTab))),
        ],
      ),
    );
  }
}
