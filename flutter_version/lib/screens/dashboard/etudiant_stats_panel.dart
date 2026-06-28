import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/dashboard_charts.dart';
import '../../state/dashboard_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';

const _garcons = Color(0xFF4F8EF7);
const _filles = Color(0xFFEC4899);

/// Équivalent de DashboardStudentStats.vue (ecole_nginx/frontend) :
/// répartition des élèves par année académique, avec drill-down
/// année → niveau → classe (KPI globaux + barre groupée + liste détail).
/// Fonctionnalité absente de school_client, ajoutée sur demande explicite.
class EtudiantStatsPanel extends StatefulWidget {
  const EtudiantStatsPanel({super.key});

  @override
  State<EtudiantStatsPanel> createState() => _EtudiantStatsPanelState();
}

class _EtudiantStatsPanelState extends State<EtudiantStatsPanel> {
  String? _selectedAnneeId;
  int _drillLevel = 0;
  int? _drillAnneeIndex;
  int? _drillNiveauIndex;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final ref = context.read<ReferenceDataState>();
    await context.read<DashboardState>().loadEtudiantStats(
          anneeId: _selectedAnneeId,
          resolveAnneeLabel: (id) =>
              ref.annees.where((a) => a.id == id).map((a) => a.nom).firstOrNull ?? '—',
        );
    if (!mounted) return;
    setState(() {
      _drillLevel = 0;
      _drillAnneeIndex = null;
      _drillNiveauIndex = null;
    });
  }

  List<EtudiantStatsNode> get _currentNodes {
    final stats = context.read<DashboardState>().etudiantStats;
    if (_drillLevel == 0 || _drillAnneeIndex == null) return stats;
    final annee = stats[_drillAnneeIndex!];
    if (_drillLevel == 1 || _drillNiveauIndex == null) return annee.children;
    return annee.children[_drillNiveauIndex!].children;
  }

  void _onBarTap(int index) {
    if (_drillLevel == 0) {
      setState(() {
        _drillAnneeIndex = index;
        _drillLevel = 1;
        _drillNiveauIndex = null;
      });
    } else if (_drillLevel == 1) {
      setState(() {
        _drillNiveauIndex = index;
        _drillLevel = 2;
      });
    }
  }

  void _goTo(int level) {
    setState(() {
      _drillLevel = level;
      if (level <= 1) _drillNiveauIndex = null;
      if (level == 0) _drillAnneeIndex = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardState>();
    final ref = context.watch<ReferenceDataState>();
    final stats = dashboard.etudiantStats;

    int total = 0, garcons = 0, filles = 0, niveauxCount = 0;
    for (final a in stats) {
      total += a.total;
      garcons += a.garcons;
      filles += a.filles;
      niveauxCount += a.children.length;
    }

    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  "Répartition des élèves par année, niveau et classe",
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
              ),
              SizedBox(
                width: 200,
                child: DropdownButtonFormField<String?>(
                  initialValue: _selectedAnneeId,
                  isDense: true,
                  decoration: const InputDecoration(labelText: 'Année'),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('Toutes les années')),
                    ...ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))),
                  ],
                  onChanged: (v) {
                    setState(() => _selectedAnneeId = v);
                    _load();
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (dashboard.isLoadingEtudiantStats)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (dashboard.etudiantStatsError != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Text(dashboard.etudiantStatsError!, style: const TextStyle(color: AppColors.danger)),
            )
          else if (stats.isEmpty)
            Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Text('Aucune donnée disponible', style: TextStyle(color: AppColors.textMuted)),
              ),
            )
          else ...[
            LayoutBuilder(builder: (context, constraints) {
              final cols = constraints.maxWidth >= 700 ? 4 : 2;
              final kpis = [
                _kpi('TOTAL ÉLÈVES', total.toString(), AppColors.textPrimary),
                _kpi('GARÇONS', garcons.toString(), _garcons, sub: '${_pct(garcons, total)}%'),
                _kpi('FILLES', filles.toString(), _filles, sub: '${_pct(filles, total)}%'),
                _kpi('ANNÉES', stats.length.toString(), AppColors.textPrimary, sub: '$niveauxCount niveaux'),
              ];
              return GridView.count(
                crossAxisCount: cols,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 2.1,
                children: kpis,
              );
            }),
            const SizedBox(height: 16),
            _buildBreadcrumb(stats),
            const SizedBox(height: 14),
            Row(
              children: [
                _legendDot(_garcons, 'Garçons'),
                const SizedBox(width: 14),
                _legendDot(_filles, 'Filles'),
                const Spacer(),
                if (_drillLevel < 2)
                  Text('Touchez une barre pour explorer →',
                      style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
              ],
            ),
            const SizedBox(height: 12),
            _buildChart(),
            const SizedBox(height: 16),
            _buildDetailList(),
          ],
        ],
      ),
    );
  }

  Widget _kpi(String label, String value, Color color, {String? sub}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.appBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label,
              style: TextStyle(
                  fontSize: 10, letterSpacing: 0.6, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
          if (sub != null)
            Text(sub, style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
        ],
      ),
    );
  }

  Widget _legendDot(Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 10, height: 10, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2))),
        const SizedBox(width: 6),
        Text(label, style: TextStyle(fontSize: 11, color: AppColors.textMuted)),
      ],
    );
  }

  Widget _buildBreadcrumb(List<EtudiantStatsAnnee> stats) {
    final crumbs = <Widget>[
      _crumb('Années', active: _drillLevel == 0, onTap: () => _goTo(0)),
    ];
    if (_drillLevel >= 1 && _drillAnneeIndex != null) {
      crumbs.add(Icon(Icons.chevron_right, size: 14, color: AppColors.textMuted));
      crumbs.add(_crumb(stats[_drillAnneeIndex!].nom, active: _drillLevel == 1, onTap: () => _goTo(1)));
    }
    if (_drillLevel >= 2 && _drillAnneeIndex != null && _drillNiveauIndex != null) {
      crumbs.add(Icon(Icons.chevron_right, size: 14, color: AppColors.textMuted));
      crumbs.add(_crumb(stats[_drillAnneeIndex!].children[_drillNiveauIndex!].nom, active: true, onTap: null));
    }
    return Wrap(crossAxisAlignment: WrapCrossAlignment.center, spacing: 4, children: crumbs);
  }

  Widget _crumb(String label, {required bool active, VoidCallback? onTap}) {
    return InkWell(
      onTap: onTap,
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12.5,
          fontWeight: FontWeight.w600,
          color: active ? AppColors.accentLight : AppColors.textMuted,
        ),
      ),
    );
  }

  Widget _buildChart() {
    final nodes = _currentNodes;
    if (nodes.isEmpty) {
      return SizedBox(
        height: 120,
        child: Center(child: Text('Aucune donnée', style: TextStyle(color: AppColors.textMuted))),
      );
    }
    final maxVal = nodes.map((n) => n.garcons > n.filles ? n.garcons : n.filles).fold(0, (a, b) => a > b ? a : b);
    return SizedBox(
      height: (nodes.length * 56).clamp(160, 420).toDouble(),
      child: BarChart(
        BarChartData(
          maxY: (maxVal == 0 ? 1 : maxVal) * 1.25,
          alignment: BarChartAlignment.spaceAround,
          barTouchData: BarTouchData(
            touchCallback: (event, response) {
              if (event is FlTapUpEvent && response?.spot != null) {
                _onBarTap(response!.spot!.touchedBarGroup.x);
              }
            },
          ),
          titlesData: FlTitlesData(
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  final i = value.toInt();
                  if (i < 0 || i >= nodes.length) return const SizedBox.shrink();
                  return Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(
                      nodes[i].nom,
                      style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          gridData: const FlGridData(show: false),
          barGroups: [
            for (var i = 0; i < nodes.length; i++)
              BarChartGroupData(x: i, barRods: [
                BarChartRodData(toY: nodes[i].garcons.toDouble(), color: _garcons, width: 12),
                BarChartRodData(toY: nodes[i].filles.toDouble(), color: _filles, width: 12),
              ]),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailList() {
    final nodes = _currentNodes;
    if (nodes.isEmpty) return const SizedBox.shrink();
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: nodes.map((n) {
          final pct = n.total == 0 ? 0.0 : n.garcons / n.total;
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              children: [
                SizedBox(
                  width: 110,
                  child: Text(n.nom,
                      style: TextStyle(fontSize: 13, color: AppColors.textPrimary), overflow: TextOverflow.ellipsis),
                ),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: pct,
                      minHeight: 8,
                      backgroundColor: _filles.withValues(alpha: 0.4),
                      valueColor: const AlwaysStoppedAnimation(_garcons),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Text('${n.garcons}G', style: const TextStyle(fontSize: 11, color: _garcons, fontWeight: FontWeight.w600)),
                const SizedBox(width: 6),
                Text('${n.filles}F', style: const TextStyle(fontSize: 11, color: _filles, fontWeight: FontWeight.w600)),
                const SizedBox(width: 10),
                SizedBox(
                  width: 28,
                  child: Text(n.total.toString(),
                      textAlign: TextAlign.right,
                      style: TextStyle(fontSize: 12, color: AppColors.textMuted, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

int _pct(int n, int total) => total == 0 ? 0 : ((n / total) * 100).round();

extension _FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull {
    final it = iterator;
    if (it.moveNext()) return it.current;
    return null;
  }
}
