import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/depense_state.dart';
import '../../state/loan_state.dart';
import '../../state/payroll_state.dart';
import '../../state/produit_state.dart';
import '../../state/transaction_state.dart';
import '../../state/vente_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';
import 'depense_tab.dart';
import 'loan_tab.dart';
import 'payroll_tab.dart';
import 'produit_tab.dart';
import 'transaction_tab.dart';
import 'vente_tab.dart';

/// Équivalent de la page Finances du bureau (school_client) : Vente,
/// Dépenses et Prêts (Controllers/Main.py:4711-4972, 5122-5295) — le web
/// (Tresorerie.vue) n'expose qu'un résumé en lecture des ventes/dépenses,
/// sans aucun formulaire de saisie ; on reprend donc le bureau comme
/// référence fonctionnelle pour ce module, avec un onglet "Produits" en
/// plus (demande explicite : les produits vendus doivent être enregistrés
/// — nom/catégorie/prix/stock — plutôt que tapés en texte libre à chaque
/// vente comme le fait add_commande() côté bureau).
class FinanceScreen extends StatefulWidget {
  const FinanceScreen({super.key});

  @override
  State<FinanceScreen> createState() => _FinanceScreenState();
}

enum _Tab { vente, produits, depenses, prets, payroll, transactions }

class _FinanceScreenState extends State<FinanceScreen> {
  _Tab _tab = _Tab.vente;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<VenteState>().load();
      context.read<ProduitState>().load();
      context.read<ProduitState>().loadCategories();
    });
  }

  void _select(_Tab tab) {
    setState(() => _tab = tab);
    switch (tab) {
      case _Tab.vente:
        context.read<VenteState>().load();
      case _Tab.produits:
        context.read<ProduitState>().load();
        context.read<ProduitState>().loadCategories();
      case _Tab.depenses:
        context.read<DepenseState>().load();
      case _Tab.prets:
        context.read<LoanState>().load();
        context.read<LoanState>().loadUserOptions();
      case _Tab.payroll:
        context.read<PayrollState>().load();
        context.read<PayrollState>().loadUserOptions();
      case _Tab.transactions:
        context.read<TransactionState>().load();
    }
  }

  Widget _buildSwitcher() {
    Widget pill(_Tab value, String label, IconData icon) {
      final selected = _tab == value;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: selected ? AppColors.hoverOverlay : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => _select(value),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    size: 15,
                    color: selected
                        ? AppColors.accentLight
                        : AppColors.textMuted,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: selected
                          ? AppColors.textPrimary
                          : AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          pill(_Tab.vente, 'Vente', Icons.point_of_sale_outlined),
          pill(_Tab.produits, 'Produits', Icons.inventory_2_outlined),
          pill(_Tab.depenses, 'Dépenses', Icons.payments_outlined),
          pill(_Tab.prets, 'Prêts', Icons.handshake_outlined),
          pill(_Tab.payroll, 'Payroll', Icons.account_balance_wallet_outlined),
          pill(
            _Tab.transactions,
            'Autre transaction',
            Icons.receipt_long_outlined,
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Finances',
            subtitle: 'Ventes, produits, dépenses et prêts',
            icon: Icons.account_balance_outlined,
            colorKey: 'emerald',
          ),
          const SizedBox(height: 16),
          _buildSwitcher(),
          const SizedBox(height: 16),
          Expanded(
            child: switch (_tab) {
              _Tab.vente => VenteTab(),
              _Tab.produits => ProduitTab(),
              _Tab.depenses => DepenseTab(),
              _Tab.prets => LoanTab(),
              _Tab.payroll => PayrollTab(),
              _Tab.transactions => TransactionTab(),
            },
          ),
        ],
      ),
    );
  }
}
