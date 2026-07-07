import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/pointage.dart';
import '../../state/pointage_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';

/// Pointage (arrivée/départ) du personnel (Professeur/Personnel) — nouvel
/// onglet ajouté sur demande explicite, sert de source d'heures fiable
/// pour le payroll horaire des professeurs (voir finance/payroll_tab.dart).
/// Comme l'appel des élèves (appel_tab.dart), c'est l'admin/réception qui
/// pointe pour chaque personne — pas de self-service.
class PointageTab extends StatefulWidget {
  const PointageTab({super.key});

  @override
  State<PointageTab> createState() => _PointageTabState();
}

class _PointageTabState extends State<PointageTab> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PointageState>().loadPersonnel();
    });
  }

  Future<void> _pointerArrivee(PointagePersonne p) async {
    final error = await context.read<PointageState>().pointerArrivee(p.userId);
    if (!mounted || error == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  Future<void> _pointerDepart(PointagePersonne p) async {
    final error = await context.read<PointageState>().pointerDepart(p.userId);
    if (!mounted || error == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _openHistorique(PointagePersonne p) {
    showDialog<void>(
      context: context,
      builder: (_) => _HistoriqueDialog(personne: p),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PointageState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (state.isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (state.errorMessage != null)
          Expanded(
            child: Center(
              child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary)),
            ),
          )
        else
          Expanded(
            child: SingleChildScrollView(
              child: DataTableCard(
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('PERSONNEL')),
                    DataColumn(label: Text('TYPE')),
                    DataColumn(label: Text('ARRIVÉE')),
                    DataColumn(label: Text('DÉPART')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.personnel.map((p) {
                    final isPointing = state.pointingId == p.userId;
                    return DataRow(
                      cells: [
                        DataCell(Text(p.fullName)),
                        DataCell(Text(p.estProfesseur ? 'Professeur' : 'Personnel')),
                        DataCell(Text(p.heureArrivee ?? '—')),
                        DataCell(Text(p.heureDepart ?? '—')),
                        DataCell(
                          isPointing
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : Row(
                                  children: [
                                    TextButton(
                                      onPressed: p.heureArrivee != null ? null : () => _pointerArrivee(p),
                                      child: const Text('Arrivée'),
                                    ),
                                    TextButton(
                                      onPressed: p.heureArrivee == null || p.heureDepart != null
                                          ? null
                                          : () => _pointerDepart(p),
                                      child: const Text('Départ'),
                                    ),
                                    IconButton(
                                      tooltip: 'Historique',
                                      icon: const Icon(Icons.history, size: 17),
                                      onPressed: () => _openHistorique(p),
                                    ),
                                  ],
                                ),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _HistoriqueDialog extends StatefulWidget {
  const _HistoriqueDialog({required this.personne});

  final PointagePersonne personne;

  @override
  State<_HistoriqueDialog> createState() => _HistoriqueDialogState();
}

class _HistoriqueDialogState extends State<_HistoriqueDialog> {
  late int _mois = DateTime.now().month;
  late int _annee = DateTime.now().year;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  void _load() {
    context.read<PointageState>().loadHistorique(
          userId: widget.personne.userId,
          mois: _mois,
          annee: _annee,
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PointageState>();

    return ParamDialogShell(
      title: 'Historique — ${widget.personne.fullName}',
      width: 560,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _mois,
                  decoration: const InputDecoration(labelText: 'Mois'),
                  items: List.generate(
                    12,
                    (i) => DropdownMenuItem(value: i + 1, child: Text('${i + 1}')),
                  ),
                  onChanged: (v) {
                    setState(() => _mois = v ?? _mois);
                    _load();
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _annee,
                  decoration: const InputDecoration(labelText: 'Année'),
                  items: List.generate(
                    5,
                    (i) {
                      final year = DateTime.now().year - i;
                      return DropdownMenuItem(value: year, child: Text('$year'));
                    },
                  ),
                  onChanged: (v) {
                    setState(() => _annee = v ?? _annee);
                    _load();
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (state.isLoadingHistorique)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Center(child: CircularProgressIndicator()),
            )
          else ...[
            Text(
              'Total : ${state.historiqueTotalHeures.toStringAsFixed(2)} h',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 300,
              child: state.historique.isEmpty
                  ? Center(
                      child: Text('Aucun pointage pour cette période.',
                          style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                    )
                  : ListView.separated(
                      itemCount: state.historique.length,
                      separatorBuilder: (_, _) => Divider(height: 8, color: AppColors.borderSubtle),
                      itemBuilder: (context, index) {
                        final e = state.historique[index];
                        return Row(
                          children: [
                            Expanded(child: Text(e.date, style: TextStyle(color: AppColors.textPrimary, fontSize: 13))),
                            Text('${e.heureArrivee ?? '—'} → ${e.heureDepart ?? '—'}',
                                style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                            const SizedBox(width: 10),
                            Text(
                              e.dureeHeures != null ? '${e.dureeHeures!.toStringAsFixed(2)} h' : '—',
                              style: TextStyle(color: AppColors.textPrimary, fontSize: 12.5, fontWeight: FontWeight.w500),
                            ),
                          ],
                        );
                      },
                    ),
            ),
          ],
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Fermer'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
