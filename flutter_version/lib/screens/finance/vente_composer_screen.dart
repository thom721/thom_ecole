import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/dual_auth.dart';
import '../../models/vente.dart';
import '../../state/auth_state.dart';
import '../../state/produit_state.dart';
import '../../state/vente_state.dart';
import '../../theme/app_theme.dart';

/// Équivalent de add_vente()/add_commande()/commander() (school_client,
/// Controllers/Main.py:5299-5491), explicitement remanié sur demande :
/// catalogue de produits enregistrés à gauche (clic = ajout au panier),
/// panier à droite avec quantité +/- par ligne et total — au lieu de la
/// saisie en texte libre nom/catégorie/prix à chaque ligne sur le bureau.
///
/// [editing] reproduit on_row_clicked_vente_()/vente_show() (Main.py:
/// 5240-5253) : clic sur une ligne déjà enregistrée → ce même panneau
/// rouvert avec ses lignes chargées, prêt pour modification.
class VenteComposerScreen extends StatefulWidget {
  const VenteComposerScreen({super.key, this.editing});

  final VenteRecord? editing;

  @override
  State<VenteComposerScreen> createState() => _VenteComposerScreenState();
}

class _VenteComposerScreenState extends State<VenteComposerScreen> {
  final _produitSearchController = TextEditingController();
  final _studentSearchController = TextEditingController();
  String? _categoryFilter;
  String? _error;

  @override
  void initState() {
    super.initState();
    final editing = widget.editing;
    if (editing != null) {
      _studentSearchController.text = editing.nom;
    }
    // clearCart()/loadForEdit() appellent notifyListeners() — les déclencher
    // depuis initState() lève "setState() called during build" puisque ce
    // widget est encore en cours de construction. Reporté après le premier
    // frame (addPostFrameCallback), comme tout ChangeNotifier mutable doit
    // l'être quand on l'amorce depuis initState().
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) return;
      final venteState = context.read<VenteState>();
      venteState.clearCart();
      if (editing != null) {
        await venteState.loadForEdit(editing);
        if (!mounted) return;
        venteState.applyStockCaps(context.read<ProduitState>().items);
      }
    });
  }

  @override
  void dispose() {
    _produitSearchController.dispose();
    _studentSearchController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final userId = context.read<AuthState>().user?.id;
    if (userId == null) return;
    setState(() => _error = null);
    final isEditing = widget.editing != null;
    final error = await runWithPinApproval(
      context: context,
      permission: isEditing ? 'Modifier paiement' : 'Ajouter paiement',
      action: ({approvalToken}) => context.read<VenteState>().submit(
        userId,
        approvalToken: approvalToken,
      ),
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final produitState = context.watch<ProduitState>();
    final venteState = context.watch<VenteState>();

    final categories =
        produitState.items.map((p) => p.category).toSet().toList()..sort();
    final visibleProduits = produitState.items.where((p) {
      if (_categoryFilter != null && p.category != _categoryFilter) {
        return false;
      }
      final q = _produitSearchController.text.trim().toLowerCase();
      if (q.isEmpty) return true;
      return p.nom.toLowerCase().contains(q);
    }).toList();

    return Scaffold(
      backgroundColor: AppColors.appBg,
      appBar: AppBar(
        backgroundColor: AppColors.appBg,
        elevation: 0,
        title: Text(
          widget.editing == null ? 'Nouvelle vente' : 'Modifier la vente',
        ),
      ),
      body: venteState.isLoadingCart
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 3,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _produitSearchController,
                                decoration: const InputDecoration(
                                  prefixIcon: Icon(Icons.search, size: 18),
                                  hintText: 'Rechercher un produit...',
                                  isDense: true,
                                ),
                                onChanged: (_) => setState(() {}),
                              ),
                            ),
                            const SizedBox(width: 12),
                            SizedBox(
                              width: 200,
                              child: DropdownButtonFormField<String>(
                                initialValue: _categoryFilter,
                                decoration: const InputDecoration(
                                  labelText: 'Catégorie',
                                  isDense: true,
                                ),
                                items: [
                                  const DropdownMenuItem(
                                    value: null,
                                    child: Text('Toutes'),
                                  ),
                                  ...categories.map(
                                    (c) => DropdownMenuItem(
                                      value: c,
                                      child: Text(c),
                                    ),
                                  ),
                                ],
                                onChanged: (v) =>
                                    setState(() => _categoryFilter = v),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Expanded(
                          child: produitState.isLoading
                              ? const Center(child: CircularProgressIndicator())
                              : visibleProduits.isEmpty
                              ? Center(
                                  child: Text(
                                    'Aucun produit. Enregistrez-en depuis l\'onglet Produits.',
                                    style: TextStyle(
                                      color: AppColors.textMuted,
                                    ),
                                  ),
                                )
                              : GridView.builder(
                                  gridDelegate:
                                      const SliverGridDelegateWithFixedCrossAxisCount(
                                        crossAxisCount: 3,
                                        mainAxisSpacing: 12,
                                        crossAxisSpacing: 12,
                                        mainAxisExtent: 108,
                                      ),
                                  itemCount: visibleProduits.length,
                                  itemBuilder: (context, index) {
                                    final p = visibleProduits[index];
                                    final ruptureStock = p.quantiteStock <= 0;
                                    return Material(
                                      color: AppColors.cardBg,
                                      borderRadius: BorderRadius.circular(14),
                                      child: InkWell(
                                        borderRadius: BorderRadius.circular(14),
                                        onTap: ruptureStock
                                            ? null
                                            : () => venteState.addProduitToCart(
                                                p,
                                              ),
                                        child: Container(
                                          padding: const EdgeInsets.all(12),
                                          decoration: BoxDecoration(
                                            border: Border.all(
                                              color: AppColors.borderSubtle,
                                            ),
                                            borderRadius: BorderRadius.circular(
                                              14,
                                            ),
                                          ),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                p.nom,
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                                style: TextStyle(
                                                  fontSize: 13,
                                                  fontWeight: FontWeight.w600,
                                                  color: AppColors.textPrimary,
                                                ),
                                              ),
                                              const SizedBox(height: 2),
                                              Text(
                                                p.category,
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  color: AppColors.textMuted,
                                                ),
                                              ),
                                              const Spacer(),
                                              Text(
                                                '${p.prix.toStringAsFixed(2)} GDES',
                                                style: TextStyle(
                                                  fontSize: 13,
                                                  fontWeight: FontWeight.bold,
                                                  color: AppColors.accentLight,
                                                ),
                                              ),
                                              Text(
                                                ruptureStock
                                                    ? 'Rupture de stock'
                                                    : 'Stock: ${_formatQty(p.quantiteStock)}',
                                                style: TextStyle(
                                                  fontSize: 10.5,
                                                  color: ruptureStock
                                                      ? AppColors.danger
                                                      : AppColors.textMuted,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    );
                                  },
                                ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 20),
                  SizedBox(
                    width: 360,
                    child: _CartPanel(
                      studentSearchController: _studentSearchController,
                      error: _error,
                      onSubmit: _submit,
                      isEditing: widget.editing != null,
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _CartPanel extends StatelessWidget {
  const _CartPanel({
    required this.studentSearchController,
    required this.error,
    required this.onSubmit,
    required this.isEditing,
  });

  final TextEditingController studentSearchController;
  final String? error;
  final VoidCallback onSubmit;
  final bool isEditing;

  @override
  Widget build(BuildContext context) {
    final venteState = context.watch<VenteState>();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.sidebarBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Panier',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          if (venteState.etudiantLabel != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.hoverOverlay,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.person_outline,
                    size: 16,
                    color: AppColors.accentLight,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      venteState.etudiantLabel!,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 12.5,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.close,
                      size: 15,
                      color: AppColors.textMuted,
                    ),
                    onPressed: () {
                      venteState.clearStudent();
                      studentSearchController.clear();
                    },
                  ),
                ],
              ),
            )
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: studentSearchController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search, size: 18),
                    hintText: 'Rechercher un élève...',
                    isDense: true,
                  ),
                  onChanged: (v) =>
                      context.read<VenteState>().searchStudents(v),
                ),
                if (venteState.liveSearchResults.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 6),
                    constraints: const BoxConstraints(maxHeight: 180),
                    decoration: BoxDecoration(
                      color: AppColors.cardBg,
                      border: Border.all(color: AppColors.borderHover),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: ListView.builder(
                      shrinkWrap: true,
                      itemCount: venteState.liveSearchResults.length,
                      itemBuilder: (context, index) {
                        final s = venteState.liveSearchResults[index];
                        return ListTile(
                          dense: true,
                          title: Text(
                            '${s.nom} ${s.prenom}',
                            style: TextStyle(
                              fontSize: 12.5,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          subtitle: Text(
                            s.identifiant,
                            style: TextStyle(
                              fontSize: 11,
                              color: AppColors.textMuted,
                            ),
                          ),
                          onTap: () {
                            venteState.selectStudent(s);
                            studentSearchController.text =
                                '${s.nom} ${s.prenom}';
                          },
                        );
                      },
                    ),
                  ),
              ],
            ),
          const SizedBox(height: 12),
          Divider(color: AppColors.borderSubtle),
          Expanded(
            child: venteState.cart.isEmpty
                ? Center(
                    child: Text(
                      'Cliquez sur un produit pour l\'ajouter.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 12.5,
                        color: AppColors.textMuted,
                      ),
                    ),
                  )
                : ListView.separated(
                    itemCount: venteState.cart.length,
                    separatorBuilder: (_, _) =>
                        Divider(height: 12, color: AppColors.borderSubtle),
                    itemBuilder: (context, index) =>
                        _CartLine(item: venteState.cart[index]),
                  ),
          ),
          Divider(color: AppColors.borderSubtle),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '${venteState.cartTotal.toStringAsFixed(2)} GDES',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: AppColors.accentLight,
                ),
              ),
            ],
          ),
          if (error != null) ...[
            const SizedBox(height: 8),
            Text(
              error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          const SizedBox(height: 12),
          FilledButton(
            onPressed: venteState.isSubmitting ? null : onSubmit,
            child: venteState.isSubmitting
                ? const SizedBox(
                    height: 16,
                    width: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(
                    isEditing
                        ? 'Enregistrer les modifications'
                        : 'Passer la commande',
                  ),
          ),
        ],
      ),
    );
  }
}

String _formatQty(double v) =>
    v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(2);

class _CartLine extends StatelessWidget {
  const _CartLine({required this.item});

  final CartItem item;

  Future<void> _editQty(BuildContext context) async {
    final controller = TextEditingController(text: _formatQty(item.quantite));
    final venteState = context.read<VenteState>();
    final value = await showDialog<double>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Quantité'),
        content: TextField(
          controller: controller,
          autofocus: true,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: const InputDecoration(labelText: 'Quantité (ex: 2.5)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(
              context,
            ).pop(double.tryParse(controller.text.trim())),
            child: const Text('OK'),
          ),
        ],
      ),
    );
    if (value == null) return;
    if (item.id != null && value <= 0) {
      if (!context.mounted) return;
      await _removeOrDelete(context);
    } else {
      venteState.setQty(item, value);
    }
  }

  /// Ligne déjà enregistrée (item.id non nul) : sa suppression doit passer
  /// par DELETE v1/order_item (raison 20-150 + PIN si la permission
  /// "Supprimer paiement" manque), pas juste être retirée du panier local —
  /// sinon décrémenter la quantité à 0 deviendrait une suppression sans
  /// autorisation. Une ligne pas encore enregistrée se retire simplement.
  Future<void> _removeOrDelete(BuildContext context) async {
    final venteState = context.read<VenteState>();
    final venteId = venteState.editingVenteId;
    if (item.id == null || venteId == null) {
      venteState.removeFromCart(item);
      return;
    }
    final raison = await showReasonDialog(
      context: context,
      title: 'Supprimer cette ligne de vente ?',
      message:
          'Supprimer "${item.nom}" de cette vente ? Indiquez la raison de la suppression.',
      confirmLabel: 'Supprimer',
    );
    if (raison == null || !context.mounted) return;
    final error = await runWithPinApproval(
      context: context,
      permission: 'Supprimer paiement',
      action: ({approvalToken}) => venteState.deleteOrderItem(
        item.id!,
        venteId,
        raison: raison,
        approvalToken: approvalToken,
      ),
    );
    if (error != null && context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final venteState = context.read<VenteState>();
    final atStockLimit =
        item.stockDisponible != null && item.quantite >= item.stockDisponible!;

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                item.nom,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '${item.prix.toStringAsFixed(2)} GDES · ${item.total.toStringAsFixed(2)} GDES',
                style: TextStyle(fontSize: 11, color: AppColors.textMuted),
              ),
            ],
          ),
        ),
        IconButton(
          icon: Icon(
            Icons.remove_circle_outline,
            size: 18,
            color: AppColors.textMuted,
          ),
          onPressed: () {
            if (item.id != null && item.quantite <= 1) {
              _removeOrDelete(context);
            } else {
              venteState.decrementQty(item);
            }
          },
        ),
        InkWell(
          onTap: () => _editQty(context),
          child: Text(
            _formatQty(item.quantite),
            style: TextStyle(fontSize: 13, color: AppColors.textPrimary),
          ),
        ),
        IconButton(
          icon: Icon(
            Icons.add_circle_outline,
            size: 18,
            color: atStockLimit ? AppColors.textMuted : AppColors.accentLight,
          ),
          onPressed: atStockLimit ? null : () => venteState.incrementQty(item),
        ),
        IconButton(
          icon: const Icon(
            Icons.delete_outline,
            size: 17,
            color: AppColors.danger,
          ),
          onPressed: () => _removeOrDelete(context),
        ),
      ],
    );
  }
}
