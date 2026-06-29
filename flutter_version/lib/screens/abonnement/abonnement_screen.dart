import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../state/abonnement_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/section_header.dart';

/// Équivalent de la page Abonnement dans school_client (Controllers/Main.py:
/// 4245-4311) : affiche le statut de la licence, un bouton "Renouveler" qui
/// ouvre infini-software.cloud dans le navigateur (visible quand
/// jours_restants <= 15, même logique que btn_abonnement_renouveler.setVisible),
/// et un bouton "Vérifier" qui déclenche LicenceSyncWorker (synchronisation
/// automatique depuis infini-software.cloud/api/licence/derniere-cle).
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

  Future<void> _ouvrirRenouvellement(AbonnementState state) async {
    final url = state.renewalUrl;
    if (url == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Adresse MAC du serveur introuvable. Actualisez la page d\'abonnement.'),
      ));
      return;
    }
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Impossible d\'ouvrir : $url'),
        ));
      }
    }
  }

  Future<void> _syncFromInfini(AbonnementState state) async {
    final error = await state.syncFromInfini();
    if (!mounted) return;
    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Licence synchronisée avec succès.'),
        backgroundColor: Color(0xFF34D399),
      ));
    } else if (state.syncMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(state.syncMessage!),
      ));
    }
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
                    const SizedBox(height: 16),
                    // Barre de renouvellement — visible quand jours_restants <= 15
                    // (même logique que btn_abonnement_renouveler.setVisible(),
                    // Controllers/Main.py:4311) ou quand expiré.
                    if (state.showRenewButton) ...[
                      _renewalBar(state),
                      const SizedBox(height: 16),
                    ],
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

  /// Barre de renouvellement : bouton "Renouveler" (ouvre infini-software dans
  /// le navigateur, équivalent de _ouvrir_renouvellement / QDesktopServices.
  /// openUrl, Main.py:4286-4295) + bouton "Vérifier" (LicenceSyncWorker).
  Widget _renewalBar(AbonnementState state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFFB7185).withValues(alpha: 0.08),
        border: Border.all(color: const Color(0xFFFB7185).withValues(alpha: 0.4)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_rounded, color: Color(0xFFFB7185), size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              state.actif
                  ? 'Votre abonnement expire bientôt (${state.joursRestants} jour(s)).'
                  : 'Abonnement expiré.',
              style: TextStyle(fontSize: 13, color: AppColors.textPrimary),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton.icon(
            onPressed: state.isSyncing ? null : () => _syncFromInfini(state),
            icon: state.isSyncing
                ? const SizedBox(
                    width: 13,
                    height: 13,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.sync, size: 15),
            label: const Text('Vérifier'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              textStyle: const TextStyle(fontSize: 12),
            ),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: () => _ouvrirRenouvellement(state),
            icon: const Icon(Icons.open_in_new, size: 15),
            label: const Text('Renouveler'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              textStyle: const TextStyle(fontSize: 12),
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
