import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/vente.dart';
import '../../state/vente_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/pill_button.dart';
import 'vente_composer_screen.dart';

/// Équivalent de vente_index (school_client, set_table_refresh_data_vente(),
/// Controllers/Main.py:5139-5181) : liste paginée des ventes déjà
/// enregistrées, avec un bouton vers la composition d'une nouvelle vente
/// (équivalent de add_vente(), ouvert ici comme une page dédiée).
class VenteTab extends StatefulWidget {
  const VenteTab({super.key});

  @override
  State<VenteTab> createState() => _VenteTabState();
}

class _VenteTabState extends State<VenteTab> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openComposer({VenteRecord? editing}) async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => VenteComposerScreen(editing: editing)),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            editing == null ? 'Vente enregistrée.' : 'Vente modifiée.',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<VenteState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Nouvelle vente',
              colorKey: 'emerald',
              icon: Icons.add_shopping_cart_outlined,
              onPressed: _openComposer,
            ),
            const Spacer(),
            SizedBox(
              width: 260,
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 18),
                  hintText: 'Rechercher (élève, utilisateur, #)...',
                  isDense: true,
                ),
                onSubmitted: (v) =>
                    context.read<VenteState>().load(page: 1, search: v),
              ),
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
                onPageChange: (page) =>
                    context.read<VenteState>().load(page: page),
                child: DataTable(
                  showCheckboxColumn: false,
                  columns: const [
                    DataColumn(label: Text('#')),
                    DataColumn(label: Text('ÉLÈVE')),
                    DataColumn(label: Text('QUANTITÉ')),
                    DataColumn(label: Text('TOTAL')),
                    DataColumn(label: Text('UTILISATEUR')),
                    DataColumn(label: Text('DATE')),
                    DataColumn(label: Text('')),
                  ],
                  rows: state.items.map((v) {
                    final isPrinting = state.printingId == v.id;
                    return DataRow(
                      onSelectChanged: (_) => _openComposer(editing: v),
                      cells: [
                        DataCell(Text(v.orderItemId)),
                        DataCell(Text(v.nom)),
                        DataCell(Text('${v.quantite}')),
                        DataCell(Text(v.total.toStringAsFixed(2))),
                        DataCell(Text(v.utilisateur)),
                        DataCell(Text(v.date)),
                        DataCell(
                          isPrinting
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : IconButton(
                                  tooltip: 'Imprimer le reçu',
                                  icon: Icon(
                                    Icons.picture_as_pdf_outlined,
                                    size: 17,
                                    color: AppColors.accentLight,
                                  ),
                                  onPressed: () => context
                                      .read<VenteState>()
                                      .printRecu(v.id),
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
