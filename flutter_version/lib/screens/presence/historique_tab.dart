import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/presence_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';

String _currentMonthIso() {
  final now = DateTime.now();
  return '${now.year.toString().padLeft(4, '0')}-${now.month.toString().padLeft(2, '0')}';
}

/// Équivalent de l'onglet "Historique" de Presences.vue — trié côté
/// backend par taux croissant (les élèves les plus absents en premier).
/// Note : le backend renvoie "—" comme nom de classe si aucun filtre
/// `classe_id` n'est passé (bug réel de RPresences.py reproduit ici).
class HistoriqueTab extends StatefulWidget {
  const HistoriqueTab({super.key});

  @override
  State<HistoriqueTab> createState() => _HistoriqueTabState();
}

class _HistoriqueTabState extends State<HistoriqueTab> {
  String? _niveauId;
  String? _classeId;
  String? _anneeId;
  late final _moisController = TextEditingController(text: _currentMonthIso());

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await context.read<ReferenceDataState>().loadOnce();
      _load();
    });
  }

  @override
  void dispose() {
    _moisController.dispose();
    super.dispose();
  }

  void _load() {
    context.read<PresenceState>().loadHistorique(
      classeId: _classeId,
      anneeId: _anneeId,
      mois: _moisController.text.trim().isEmpty
          ? null
          : _moisController.text.trim(),
    );
  }

  Future<void> _pickMonth() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(
        () => _moisController.text =
            '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}',
      );
      _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    final refData = context.watch<ReferenceDataState>();
    final state = context.watch<PresenceState>();
    final classesForNiveau = refData.classesForNiveau(_niveauId);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _niveauId,
                decoration: const InputDecoration(labelText: 'Niveau'),
                items: refData.niveaux
                    .map(
                      (n) => DropdownMenuItem(value: n.id, child: Text(n.name)),
                    )
                    .toList(),
                onChanged: (v) => setState(() {
                  _niveauId = v;
                  _classeId = null;
                }),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _classeId,
                decoration: const InputDecoration(labelText: 'Classe'),
                items: classesForNiveau
                    .map(
                      (c) => DropdownMenuItem(
                        value: c.id,
                        child: Text(c.nomClasse),
                      ),
                    )
                    .toList(),
                onChanged: _niveauId == null
                    ? null
                    : (v) {
                        setState(() => _classeId = v);
                        _load();
                      },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _anneeId,
                decoration: const InputDecoration(
                  labelText: 'Année académique',
                ),
                items: refData.annees
                    .map(
                      (a) => DropdownMenuItem(value: a.id, child: Text(a.nom)),
                    )
                    .toList(),
                onChanged: (v) {
                  setState(() => _anneeId = v);
                  _load();
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: InkWell(
                onTap: _pickMonth,
                child: InputDecorator(
                  decoration: const InputDecoration(labelText: 'Mois'),
                  child: Text(_moisController.text),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (state.isLoadingHistorique)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (state.historiqueError != null)
          Expanded(
            child: Center(
              child: Text(
                state.historiqueError!,
                style: TextStyle(color: AppColors.textPrimary),
              ),
            ),
          )
        else
          Expanded(
            child: SingleChildScrollView(
              child: DataTableCard(
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('ÉLÈVE')),
                    DataColumn(label: Text('CLASSE')),
                    DataColumn(label: Text('ABSENCES')),
                    DataColumn(label: Text('TAUX DE PRÉSENCE')),
                  ],
                  rows: state.historique.map((h) {
                    final absColor = h.absences > 5
                        ? AppColors.danger
                        : h.absences > 2
                        ? const Color(0xFFFBBF24)
                        : AppColors.textPrimary;
                    final tauxColor = h.taux > 80
                        ? const Color(0xFF34D399)
                        : h.taux > 60
                        ? const Color(0xFFFBBF24)
                        : AppColors.danger;
                    return DataRow(
                      cells: [
                        DataCell(Text(h.nom)),
                        DataCell(Text(h.classe)),
                        DataCell(
                          Text(
                            '${h.absences}',
                            style: TextStyle(color: absColor),
                          ),
                        ),
                        DataCell(
                          Row(
                            children: [
                              Container(
                                width: 70,
                                height: 6,
                                decoration: BoxDecoration(
                                  color: AppColors.hoverOverlay,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: FractionallySizedBox(
                                  alignment: Alignment.centerLeft,
                                  widthFactor: (h.taux / 100).clamp(0, 1),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: tauxColor,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '${h.taux.toStringAsFixed(0)}%',
                                style: TextStyle(
                                  fontSize: 11.5,
                                  color: AppColors.textMuted,
                                ),
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
