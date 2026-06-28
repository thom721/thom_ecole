import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/log_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/badge_pill.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/section_header.dart';

/// Équivalent de logs() (school_client, Controllers/Main.py:4738-4863), onglet
/// "grafic_log" → GET v1/logs-graphic (ecole_nginx/app/Routes/RLog.py).
class LogScreen extends StatefulWidget {
  const LogScreen({super.key});

  @override
  State<LogScreen> createState() => _LogScreenState();
}

class _LogScreenState extends State<LogScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<LogState>().load();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _showDetail(String id) async {
    final state = context.read<LogState>();
    final detail = await state.fetchDetail(id);
    if (!mounted) return;
    if (detail == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Impossible de charger le détail de ce log.'),
        ),
      );
      return;
    }
    showDialog(
      context: context,
      builder: (_) => _LogDetailDialog(detail: detail),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<LogState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Log',
            subtitle:
                "Historique des actions (création / modification / suppression)",
            icon: Icons.history,
            colorKey: 'violet',
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                width: 220,
                child: TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search, size: 18),
                    hintText: 'Rechercher...',
                    isDense: true,
                  ),
                  onSubmitted: (v) {
                    state.search = v.isEmpty ? null : v;
                    state.load(page: 1);
                  },
                ),
              ),
              SizedBox(
                width: 180,
                child: DropdownButtonFormField<String>(
                  initialValue: state.action,
                  isDense: true,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Action'),
                  items: [
                    const DropdownMenuItem<String>(
                      value: null,
                      child: Text('Toutes'),
                    ),
                    ...kLogActions.entries.map(
                      (e) => DropdownMenuItem(
                        value: e.key,
                        child: Text(e.value, overflow: TextOverflow.ellipsis),
                      ),
                    ),
                  ],
                  onChanged: (v) {
                    state.action = v;
                    state.load(page: 1);
                  },
                ),
              ),
              SizedBox(
                width: 220,
                child: DropdownButtonFormField<String>(
                  initialValue: state.model,
                  isDense: true,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Model / Table'),
                  items: [
                    const DropdownMenuItem<String>(
                      value: null,
                      child: Text('Tous'),
                    ),
                    ...kLogModels.entries.map(
                      (e) => DropdownMenuItem(
                        value: e.value,
                        child: Text(e.key, overflow: TextOverflow.ellipsis),
                      ),
                    ),
                  ],
                  onChanged: (v) {
                    state.model = v;
                    state.load(page: 1);
                  },
                ),
              ),
              IconButton(
                tooltip: 'Rechercher',
                icon: const Icon(Icons.refresh, size: 18),
                onPressed: () => state.load(page: state.currentPage),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.errorMessage != null)
            Expanded(
              child: Center(
                child: Text(
                  state.errorMessage!,
                  style: TextStyle(color: AppColors.textPrimary),
                ),
              ),
            )
          else
            Expanded(
              child: SingleChildScrollView(
                child: DataTableCard(
                  currentPage: state.currentPage,
                  lastPage: state.lastPage,
                  onPageChange: (page) => state.load(page: page),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('UTILISATEUR')),
                      DataColumn(label: Text('AUTORISATION')),
                      DataColumn(label: Text('ACTION')),
                      DataColumn(label: Text('MODEL')),
                      DataColumn(label: Text('DATE')),
                    ],
                    rows: state.items.isEmpty
                        ? [
                            DataRow(
                              cells: [
                                DataCell(
                                  Text(
                                    'Aucun log trouvé',
                                    style: TextStyle(
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ),
                                const DataCell(Text('')),
                                const DataCell(Text('')),
                                const DataCell(Text('')),
                                const DataCell(Text('')),
                              ],
                            ),
                          ]
                        : state.items.map((log) {
                            return DataRow(
                              onSelectChanged: (_) => _showDetail(log.id),
                              cells: [
                                DataCell(
                                  Text(
                                    log.user,
                                    style: TextStyle(
                                      color: AppColors.textPrimary,
                                    ),
                                  ),
                                ),
                                DataCell(
                                  Text(
                                    log.authorizationId,
                                    style: TextStyle(
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ),
                                DataCell(
                                  BadgePill(
                                    label:
                                        kLogActions[log.action] ?? log.action,
                                    colorKey: log.action == 'create'
                                        ? 'emerald'
                                        : log.action == 'delete'
                                        ? 'rose'
                                        : 'amber',
                                  ),
                                ),
                                DataCell(
                                  Text(
                                    log.model,
                                    style: TextStyle(
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                ),
                                DataCell(
                                  Text(
                                    log.date,
                                    style: TextStyle(
                                      color: AppColors.textMuted,
                                      fontSize: 12,
                                    ),
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
      ),
    );
  }
}

class _LogDetailDialog extends StatelessWidget {
  const _LogDetailDialog({required this.detail});

  final LogDetail detail;

  Widget _row(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: TextStyle(fontSize: 12, color: AppColors.textMuted),
            ),
          ),
          Expanded(
            child: Text(
              value == null || value.isEmpty ? '—' : value,
              style: TextStyle(fontSize: 12.5, color: AppColors.textPrimary),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.panelBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560, maxHeight: 600),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Détail du log',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(
                        Icons.close,
                        color: AppColors.danger,
                        size: 18,
                      ),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const Divider(),
                _row('Action', kLogActions[detail.action] ?? detail.action),
                _row('Model', detail.modelType.split('\\').last),
                _row('Model ID', detail.modelId),
                _row('Raison', detail.reason),
                _row('IP', detail.ipAddress),
                _row('Navigateur', detail.userAgent),
                _row('Date', detail.createdAt),
                const SizedBox(height: 8),
                Text(
                  'Anciennes valeurs',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textMuted,
                  ),
                ),
                const SizedBox(height: 4),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.inputBg,
                    border: Border.all(color: AppColors.borderSubtle),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    detail.oldValues ?? '—',
                    style: TextStyle(
                      fontSize: 11.5,
                      color: AppColors.textMuted,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Nouvelles valeurs',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textMuted,
                  ),
                ),
                const SizedBox(height: 4),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.inputBg,
                    border: Border.all(color: AppColors.borderSubtle),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    detail.newValues ?? '—',
                    style: TextStyle(
                      fontSize: 11.5,
                      color: AppColors.textMuted,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
