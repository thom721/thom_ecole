import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/dashboard_charts.dart';
import '../../state/dashboard_state.dart';
import '../../theme/app_theme.dart';

/// Équivalent de PaiementsStats.vue (ecole_nginx/frontend) : suivi des
/// encaissements par année académique → mois → jour, avec drill-down
/// journalier (graphique + tableau). Fonctionnalité absente de
/// school_client, ajoutée sur demande explicite.
class PaiementStatsPanel extends StatefulWidget {
  const PaiementStatsPanel({super.key});

  @override
  State<PaiementStatsPanel> createState() => _PaiementStatsPanelState();
}

class _PaiementStatsPanelState extends State<PaiementStatsPanel> {
  String? _selectedAnnee;
  String? _moisOuvert;
  late String _selectedMois = _currentMoisKey();
  // Tableaux repliés par défaut (showDetailMois/showTableJournalier dans
  // PaiementsStats.vue valent tous les deux `false` au départ).
  bool _showMoisTable = false;
  bool _showJournalierTable = false;

  static String _currentMoisKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}';
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final dashboard = context.read<DashboardState>();
      await dashboard.loadPaiementAnnees();
      if (!mounted) return;
      final annees = dashboard.paiementAnnees;
      if (annees.isNotEmpty) {
        setState(() => _selectedAnnee = annees.first);
        await _loadAnnuelThenJournalier(annees.first);
      }
    });
  }

  /// Équivalent de chargerStats() qui enchaîne automatiquement sur
  /// chargerJournalier() (PaiementsStats.vue:343) — le détail du mois en
  /// cours s'affiche donc sans action de l'utilisateur, comme sur le web.
  Future<void> _loadAnnuelThenJournalier(String annee) async {
    final dashboard = context.read<DashboardState>();
    await dashboard.loadPaiementAnnuel(annee);
    if (!mounted) return;
    final annuel = dashboard.paiementAnnuel;
    if (annuel == null || annuel.mois.isEmpty) return;
    final hasMois = annuel.mois.any((m) => m.moisKey == _selectedMois);
    final mois = hasMois ? _selectedMois : annuel.mois.last.moisKey;
    setState(() {
      _selectedMois = mois;
      _moisOuvert = mois;
    });
    await dashboard.loadPaiementJournalier(annee, mois);
  }

  Future<void> _onAnneeChanged(String? annee) async {
    setState(() {
      _selectedAnnee = annee;
      _moisOuvert = null;
    });
    if (annee != null) {
      await _loadAnnuelThenJournalier(annee);
    }
  }

  Future<void> _onMoisChanged(String? mois) async {
    if (mois == null || _selectedAnnee == null) return;
    setState(() {
      _selectedMois = mois;
      _moisOuvert = mois;
    });
    await context.read<DashboardState>().loadPaiementJournalier(
      _selectedAnnee!,
      mois,
    );
  }

  String _fmt(num n) => n.toStringAsFixed(2);

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardState>();
    final annuel = dashboard.paiementAnnuel;

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
          Text(
            'Suivi des encaissements par année et par mois',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          // Wrap plutôt que Row : sur une fenêtre étroite, les deux menus +
          // le bouton actualiser passent à la ligne au lieu de provoquer un
          // RenderFlex overflow (leurs largeurs fixes ne laissaient aucune
          // marge dans un Row classique).
          Wrap(
            alignment: WrapAlignment.end,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 10,
            runSpacing: 8,
            children: [
              SizedBox(
                width: 160,
                child: DropdownButtonFormField<String>(
                  initialValue: _selectedAnnee,
                  isDense: true,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Année'),
                  items: dashboard.paiementAnnees
                      .map(
                        (a) => DropdownMenuItem(
                          value: a,
                          child: Text(a, overflow: TextOverflow.ellipsis),
                        ),
                      )
                      .toList(),
                  onChanged: _onAnneeChanged,
                ),
              ),
              if (annuel != null && annuel.mois.isNotEmpty)
                SizedBox(
                  width: 170,
                  child: DropdownButtonFormField<String>(
                    initialValue:
                        annuel.mois.any((m) => m.moisKey == _selectedMois)
                        ? _selectedMois
                        : null,
                    isDense: true,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Mois'),
                    items: annuel.mois
                        .map(
                          (m) => DropdownMenuItem(
                            value: m.moisKey,
                            child: Text(
                              m.mois,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: _onMoisChanged,
                  ),
                ),
              IconButton(
                tooltip: 'Actualiser',
                icon: const Icon(Icons.refresh, size: 18),
                onPressed: _selectedAnnee == null
                    ? null
                    : () => _loadAnnuelThenJournalier(_selectedAnnee!),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (dashboard.isLoadingPaiementAnnuel)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (dashboard.paiementAnnuelError != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 20),
              child: Text(
                dashboard.paiementAnnuelError!,
                style: const TextStyle(color: AppColors.danger),
              ),
            )
          else if (annuel == null || annuel.mois.isEmpty)
            Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Text(
                  'Aucune donnée disponible',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ),
            )
          else ...[
            LayoutBuilder(
              builder: (context, constraints) {
                final cols = constraints.maxWidth >= 700 ? 4 : 2;
                final moyenne = annuel.nbMois > 0
                    ? annuel.totalAnnuel / annuel.nbMois
                    : 0;
                final kpis = [
                  _kpi(
                    'TOTAL ANNUEL',
                    _fmt(annuel.totalAnnuel),
                    AppColors.accentLight,
                    sub: annuel.devise,
                  ),
                  _kpi(
                    'MOIS ACTIFS',
                    annuel.nbMois.toString(),
                    AppColors.textPrimary,
                    sub: 'mois avec versements',
                  ),
                  _kpi(
                    'VERSEMENTS',
                    annuel.totalVersements.toString(),
                    AppColors.textPrimary,
                    sub: 'transactions totales',
                  ),
                  _kpi(
                    'MOY. / MOIS',
                    _fmt(moyenne),
                    AppColors.cardPalette['emerald']!.text,
                    sub: annuel.devise,
                  ),
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
              },
            ),
            const SizedBox(height: 18),
            InkWell(
              onTap: () => setState(() => _showMoisTable = !_showMoisTable),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  children: [
                    Icon(
                      _showMoisTable ? Icons.expand_more : Icons.chevron_right,
                      size: 18,
                      color: AppColors.textMuted,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Détail par mois',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (_showMoisTable) ...[
              const SizedBox(height: 4),
              _buildMoisTable(annuel),
            ],
            if (dashboard.isLoadingPaiementJournalier ||
                dashboard.paiementJournalier != null) ...[
              const SizedBox(height: 18),
              _buildJournalierPanel(dashboard, annuel),
            ],
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
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              letterSpacing: 0.6,
              fontWeight: FontWeight.w600,
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          if (sub != null)
            Text(
              sub,
              style: TextStyle(fontSize: 10, color: AppColors.textMuted),
            ),
        ],
      ),
    );
  }

  Widget _buildMoisTable(PaiementAnnuelStats annuel) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            color: AppColors.appBg,
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Text(
                    'MOIS',
                    style: TextStyle(
                      fontSize: 10.5,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    'VERSEMENTS',
                    style: TextStyle(
                      fontSize: 10.5,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    'TOTAL',
                    style: TextStyle(
                      fontSize: 10.5,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Expanded(
                  flex: 3,
                  child: Text(
                    '% DU TOTAL',
                    style: TextStyle(
                      fontSize: 10.5,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                SizedBox(width: 90),
              ],
            ),
          ),
          for (final m in annuel.mois) _moisRow(m, annuel),
        ],
      ),
    );
  }

  Widget _moisRow(PaiementMoisStat m, PaiementAnnuelStats annuel) {
    final open = _moisOuvert == m.moisKey;
    final pct = annuel.totalAnnuel == 0 ? 0.0 : (m.total / annuel.totalAnnuel);
    return Column(
      children: [
        InkWell(
          onTap: () => setState(() => _moisOuvert = open ? null : m.moisKey),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Row(
                    children: [
                      Icon(
                        open ? Icons.expand_more : Icons.chevron_right,
                        size: 16,
                        color: AppColors.textMuted,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          m.mois,
                          style: TextStyle(
                            fontSize: 13,
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w500,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    m.nbVersements.toString(),
                    style: TextStyle(
                      fontSize: 12.5,
                      color: AppColors.textMuted,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    '${_fmt(m.total)} ${m.devise}',
                    style: TextStyle(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.accentLight,
                    ),
                  ),
                ),
                Expanded(
                  flex: 3,
                  child: Row(
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(999),
                          child: LinearProgressIndicator(
                            value: pct,
                            minHeight: 6,
                            backgroundColor: AppColors.hoverOverlay,
                            valueColor: AlwaysStoppedAnimation(
                              AppColors.accent,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${(pct * 100).round()}%',
                        style: TextStyle(
                          fontSize: 11,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(
                  width: 90,
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                    ),
                    onPressed: () {
                      setState(() => _moisOuvert = m.moisKey);
                      context.read<DashboardState>().loadPaiementJournalier(
                        annuel.annee,
                        m.moisKey,
                      );
                    },
                    child: const Text(
                      'Détail jour',
                      style: TextStyle(fontSize: 11),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (open)
          Container(
            width: double.infinity,
            color: AppColors.appBg,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: m.details.map((d) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 130,
                        child: Text(
                          d.label,
                          style: TextStyle(
                            fontSize: 11,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          d.employer ?? '',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFFA0A8C0),
                          ),
                        ),
                      ),
                      if (d.aide != null && d.aide!.isNotEmpty)
                        Container(
                          margin: const EdgeInsets.only(right: 8),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.hoverOverlay,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            d.aide!,
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.textMuted,
                            ),
                          ),
                        ),
                      Text(
                        '+ ${_fmt(d.depot)} ${d.devise ?? ''}',
                        style: TextStyle(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w600,
                          color: AppColors.accentLight,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
      ],
    );
  }

  Widget _buildJournalierPanel(
    DashboardState dashboard,
    PaiementAnnuelStats annuel,
  ) {
    final jour = dashboard.paiementJournalier;
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.accent.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              children: [
                Container(
                  width: 5,
                  height: 16,
                  decoration: BoxDecoration(
                    color: AppColors.cardPalette['emerald']!.bar,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Détail journalier — ${jour?.mois ?? ''}',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textPrimary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                if (jour != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.cardPalette['emerald']!.bar.withValues(
                        alpha: 0.15,
                      ),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      '${_fmt(jour.total)} ${annuel.devise}',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.cardPalette['emerald']!.text,
                      ),
                    ),
                  ),
                IconButton(
                  icon: const Icon(Icons.close, size: 16),
                  onPressed: () =>
                      context.read<DashboardState>().clearPaiementJournalier(),
                ),
              ],
            ),
          ),
          if (dashboard.isLoadingPaiementJournalier)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 30),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (jour != null) ...[
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(height: 180, child: _journalierChart(jour)),
            ),
            InkWell(
              onTap: () =>
                  setState(() => _showJournalierTable = !_showJournalierTable),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  border: Border(
                    top: BorderSide(color: AppColors.borderSubtle),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      _showJournalierTable
                          ? Icons.expand_more
                          : Icons.chevron_right,
                      size: 16,
                      color: AppColors.textMuted,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Détail journalier',
                      style: TextStyle(
                        fontSize: 12.5,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (_showJournalierTable)
              Container(
                decoration: BoxDecoration(
                  border: Border(
                    top: BorderSide(color: AppColors.borderSubtle),
                  ),
                ),
                child: Column(
                  children: jour.jours.map((j) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                      decoration: BoxDecoration(
                        border: Border(
                          bottom: BorderSide(color: AppColors.borderSubtle),
                        ),
                      ),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 90,
                            child: Text(
                              j.date,
                              style: TextStyle(
                                fontSize: 12.5,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ),
                          Expanded(
                            child: Text(
                              '${j.nbVersements} versement(s)',
                              style: TextStyle(
                                fontSize: 12,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ),
                          Text(
                            '${_fmt(j.total)} ${annuel.devise}',
                            style: TextStyle(
                              fontSize: 12.5,
                              fontWeight: FontWeight.w600,
                              color: AppColors.accentLight,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ),
          ],
        ],
      ),
    );
  }

  /// Équivalent de dessinerChartJournalier() (PaiementsStats.vue) : un
  /// `type: 'line'` Chart.js — ligne verte avec aire remplie translucide et
  /// points pleins, pas un histogramme.
  /// Abrège un montant pour l'axe des montants (gauche) du graphique :
  /// 25580375 → "25,6M", 2300 → "2,3K", 850 → "850".
  static String _axisLabel(double v) {
    final sign = v < 0 ? '-' : '';
    final abs = v.abs();
    if (abs >= 1000000)
      return '$sign${(abs / 1000000).toStringAsFixed(1).replaceAll('.', ',')}M';
    if (abs >= 1000)
      return '$sign${(abs / 1000).toStringAsFixed(1).replaceAll('.', ',')}K';
    return '$sign${abs.toStringAsFixed(0)}';
  }

  Widget _journalierChart(PaiementJournalierStats jour) {
    if (jour.jours.isEmpty) {
      return Center(
        child: Text(
          'Aucun versement ce mois.',
          style: TextStyle(color: AppColors.textMuted),
        ),
      );
    }
    final emerald = AppColors.cardPalette['emerald']!.bar;
    final maxVal = jour.jours
        .map((j) => j.total)
        .fold(0.0, (a, b) => a > b ? a : b.toDouble());
    final maxY = maxVal == 0 ? 1.0 : maxVal * 1.2;
    // 4 lignes horizontales (donc 5 paliers, 0 inclus) — assez pour donner
    // des repères de montant sans surcharger un graphique de 180px de haut.
    final interval = maxY / 4;
    return LineChart(
      LineChartData(
        minY: 0,
        maxY: maxY,
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 44,
              interval: interval,
              getTitlesWidget: (value, meta) {
                if (value == meta.max) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: Text(
                    _axisLabel(value),
                    textAlign: TextAlign.right,
                    style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                  ),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final i = value.toInt();
                if (i < 0 || i >= jour.jours.length)
                  return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    jour.jours[i].date.substring(0, 2),
                    style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: interval,
          getDrawingHorizontalLine: (value) =>
              FlLine(color: AppColors.borderSubtle, strokeWidth: 1),
        ),
        lineTouchData: const LineTouchData(enabled: false),
        lineBarsData: [
          LineChartBarData(
            isCurved: true,
            curveSmoothness: 0.3,
            color: emerald,
            barWidth: 2,
            dotData: FlDotData(
              getDotPainter: (spot, percent, bar, index) =>
                  FlDotCirclePainter(radius: 5, color: emerald, strokeWidth: 0),
            ),
            belowBarData: BarAreaData(
              show: true,
              color: emerald.withValues(alpha: 0.12),
            ),
            spots: [
              for (var i = 0; i < jour.jours.length; i++)
                FlSpot(i.toDouble(), jour.jours[i].total.toDouble()),
            ],
          ),
        ],
      ),
    );
  }
}
