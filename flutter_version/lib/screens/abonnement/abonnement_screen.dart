import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/abonnement_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/section_header.dart';

/// Équivalent de Abonnement.vue (ecole_nginx/frontend/src/views/admin) —
/// seule page réellement routée pour "Abonnement" (school_client n'a qu'un
/// widget construit dynamiquement, non relié à une .ui, voir AbonnementState).
class AbonnementScreen extends StatefulWidget {
  const AbonnementScreen({super.key});

  @override
  State<AbonnementScreen> createState() => _AbonnementScreenState();
}

class _AbonnementScreenState extends State<AbonnementScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AbonnementState>().load();
    });
  }

  String _fmtDate(String? iso) {
    if (iso == null) return '—';
    final d = DateTime.tryParse(iso);
    if (d == null) return iso;
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year} '
        '${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AbonnementState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Abonnement',
            subtitle: 'Statut de la licence et historique des activations',
            icon: Icons.workspace_premium_outlined,
            colorKey: 'amber',
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.errorMessage != null)
            Expanded(child: Center(child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary))))
          else
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    LayoutBuilder(builder: (context, constraints) {
                      final cols = constraints.maxWidth >= 700 ? 3 : 1;
                      return GridView.count(
                        crossAxisCount: cols,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        mainAxisSpacing: 16,
                        crossAxisSpacing: 16,
                        childAspectRatio: 2.6,
                        children: [
                          _statCard(
                            'Statut',
                            state.actif ? 'Actif' : 'Expiré / invalide',
                            state.actif ? const Color(0xFF34D399) : const Color(0xFFFB7185),
                          ),
                          _statCard('Clé actuelle', state.cleActuelle ?? '—', AppColors.textPrimary, mono: true),
                          _statCard(
                            'Expire le',
                            state.dateExpiration ?? '—',
                            AppColors.textPrimary,
                            sub: state.joursRestants == null
                                ? null
                                : state.joursRestants! >= 0
                                    ? '${state.joursRestants} jour(s) restant(s)'
                                    : 'Expiré depuis ${state.joursRestants!.abs()} jour(s)',
                            subColor: state.actif ? const Color(0xFF34D399) : const Color(0xFFFB7185),
                          ),
                        ],
                      );
                    }),
                    const SizedBox(height: 18),
                    Text('Historique des activations',
                        style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                    const SizedBox(height: 10),
                    DataTableCard(
                      child: DataTable(
                        columns: const [
                          DataColumn(label: Text('ACTIVÉ LE')),
                          DataColumn(label: Text('EXPIRE LE')),
                          DataColumn(label: Text('STATUT')),
                        ],
                        rows: state.historique.isEmpty
                            ? [
                                DataRow(cells: [
                                  DataCell(Text('Aucune activation trouvée',
                                      style: TextStyle(color: AppColors.textMuted))),
                                  const DataCell(Text('')),
                                  const DataCell(Text('')),
                                ]),
                              ]
                            : state.historique.map((h) {
                                return DataRow(cells: [
                                  DataCell(Text(_fmtDate(h.dateActivation),
                                      style: TextStyle(fontSize: 12.5, color: AppColors.textMuted))),
                                  DataCell(Text(h.dateExpiration ?? '—',
                                      style: TextStyle(fontSize: 12.5, color: AppColors.textMuted))),
                                  DataCell(Text(
                                    h.actif ? 'Actif' : 'Expiré',
                                    style: TextStyle(
                                      fontSize: 12.5,
                                      fontWeight: FontWeight.w600,
                                      color: h.actif ? const Color(0xFF34D399) : const Color(0xFFFB7185),
                                    ),
                                  )),
                                ]);
                              }).toList(),
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _statCard(String label, String value, Color valueColor, {bool mono = false, String? sub, Color? subColor}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label, style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
          const SizedBox(height: 6),
          Text(value,
              style: TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w600,
                color: valueColor,
                fontFamily: mono ? 'monospace' : null,
              )),
          if (sub != null) ...[
            const SizedBox(height: 4),
            Text(sub, style: TextStyle(fontSize: 11, color: subColor ?? AppColors.textMuted)),
          ],
        ],
      ),
    );
  }
}
