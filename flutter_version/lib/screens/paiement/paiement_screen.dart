import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/paiement.dart';
import '../../models/student.dart';
import '../../state/paiement_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';
import 'paiement_detail_screen.dart';
import 'paiement_form_screen.dart';

/// Équivalent de paiement_page()/go_to_paiement_page() (Controllers/Main.py)
/// pour les DONNÉES — le STYLE (carte sombre, modal de recherche, table,
/// pagination) reprend Paiements.vue (ecole_nginx/frontend).
class PaiementScreen extends StatefulWidget {
  const PaiementScreen({super.key});

  @override
  State<PaiementScreen> createState() => _PaiementScreenState();
}

class _PaiementScreenState extends State<PaiementScreen> {
  final _searchController = TextEditingController();
  // Navigation interne (pas de Navigator.push) pour rester cohérent avec le
  // reste de l'app : AppShell garde toujours sa sidebar/topbar/footer, seul
  // le contenu de la page change (comme stackedWidget côté school_client).
  String? _selectedEtudiantId;
  // "Voir détail" (id du paiement) est un écran distinct de "Nouveau
  // Paiement" (id de l'étudiant) — équivalent de 'add-paiement' vs
  // 'paiement-detail' dans le router Vue (ecole_nginx/frontend/src/router).
  String? _selectedPaiementId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PaiementState>().loadList();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openStudentSearch() async {
    final selected = await showDialog<Student>(
      context: context,
      builder: (_) => const _StudentSearchDialog(),
    );
    if (selected != null && mounted) {
      setState(() => _selectedEtudiantId = selected.id);
    }
  }

  void _openDetail(PaymentListItem item) {
    setState(() => _selectedPaiementId = item.id);
  }

  void _backToList() {
    setState(() {
      _selectedEtudiantId = null;
      _selectedPaiementId = null;
      context.read<PaiementState>().loadList(page: context.read<PaiementState>().currentPage);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_selectedEtudiantId != null) {
      return PaiementFormScreen(etudiantId: _selectedEtudiantId!, onBack: _backToList);
    }
    if (_selectedPaiementId != null) {
      return PaiementDetailScreen(paiementId: _selectedPaiementId!, onBack: _backToList);
    }

    final state = context.watch<PaiementState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Paiements',
            subtitle: 'Suivi des versements et échéances',
            icon: Icons.credit_card_outlined,
            colorKey: 'emerald',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              PillButton(
                label: 'Nouveau Paiement',
                colorKey: 'sky',
                icon: Icons.add,
                onPressed: _openStudentSearch,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextField(
                  controller: _searchController,
                  style: TextStyle(color: AppColors.textPrimary, fontSize: 13),
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.search, color: AppColors.textMuted, size: 18),
                    hintText: 'Filtrer un paiement...',
                    isDense: true,
                  ),
                  onSubmitted: (v) => context.read<PaiementState>().loadList(page: 1, search: v),
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
                child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary)),
              ),
            )
          else
            Expanded(
              child: SingleChildScrollView(
                child: DataTableCard(
                  currentPage: state.currentPage,
                  lastPage: state.lastPage,
                  onPageChange: (page) => context.read<PaiementState>().loadList(page: page),
                  child: DataTable(
                    showCheckboxColumn: false,
                    columns: const [
                      DataColumn(label: Text('IDENTIFIANT')),
                      DataColumn(label: Text('NOM')),
                      DataColumn(label: Text('PRÉNOM')),
                      DataColumn(label: Text('ANNÉE')),
                      DataColumn(label: Text('CLASSE')),
                    ],
                    rows: state.payments.map((p) {
                      return DataRow(
                        onSelectChanged: (_) => _openDetail(p),
                        cells: [
                          DataCell(Text(p.identifiant)),
                          DataCell(Text(p.nom)),
                          DataCell(Text(p.prenom)),
                          DataCell(Text(p.annee)),
                          DataCell(Text(p.classe)),
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

/// Équivalent de la modale "Chercher l'étudiant" (Paiements.vue) — recherche
/// en direct via POST v1/live-student, puis push vers PaiementFormScreen.
class _StudentSearchDialog extends StatefulWidget {
  const _StudentSearchDialog();

  @override
  State<_StudentSearchDialog> createState() => _StudentSearchDialogState();
}

class _StudentSearchDialogState extends State<_StudentSearchDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    context.read<PaiementState>().clearSearch();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PaiementState>();

    return Dialog(
      backgroundColor: AppColors.panelBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 460, maxHeight: 480),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text("Chercher l'étudiant",
                        style: TextStyle(fontSize: 16, color: AppColors.textPrimary)),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppColors.danger, size: 18),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _controller,
                autofocus: true,
                style: TextStyle(color: AppColors.textPrimary, fontSize: 13),
                decoration: const InputDecoration(
                  hintText: 'Rechercher un étudiant (nom, identifiant...)',
                  isDense: true,
                ),
                onChanged: (v) => context.read<PaiementState>().searchStudents(v),
              ),
              const SizedBox(height: 12),
              if (state.isSearching)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (state.liveSearchResults.isNotEmpty)
                Flexible(
                  child: Container(
                    decoration: BoxDecoration(
                      color: AppColors.appBg,
                      border: Border.all(color: AppColors.borderSubtle),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: ListView.separated(
                      shrinkWrap: true,
                      itemCount: state.liveSearchResults.length,
                      separatorBuilder: (_, _) => Divider(height: 1, color: AppColors.borderSubtle),
                      itemBuilder: (context, index) {
                        final s = state.liveSearchResults[index];
                        return ListTile(
                          dense: true,
                          title: Text('${s.nom} ${s.prenom}',
                              style: TextStyle(color: AppColors.textPrimary, fontSize: 13)),
                          subtitle: Text(s.identifiant,
                              style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                          onTap: () => Navigator.of(context).pop(s),
                        );
                      },
                    ),
                  ),
                )
              else if (_controller.text.trim().length > 1)
                Padding(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  child: Text('Aucun étudiant trouvé...', style: TextStyle(color: AppColors.textMuted)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
