import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/produit.dart';
import '../../state/produit_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/param_dialog.dart';
import '../../widgets/pill_button.dart';

/// Catalogue de produits — nouveauté demandée explicitement (voir
/// lib/models/produit.dart) : nom, catégorie, prix unitaire, quantité en
/// stock, description.
class ProduitTab extends StatefulWidget {
  const ProduitTab({super.key});

  @override
  State<ProduitTab> createState() => _ProduitTabState();
}

class _ProduitTabState extends State<ProduitTab> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _openForm({Produit? produit}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _ProduitFormDialog(initial: produit),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            produit == null ? 'Produit ajouté.' : 'Produit modifié.',
          ),
        ),
      );
    }
  }

  Future<void> _confirmDelete(Produit produit) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le produit "${produit.nom}" ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<ProduitState>().delete(produit.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ProduitState>();
    final q = _searchController.text.trim().toLowerCase();
    final visible = q.isEmpty
        ? state.items
        : state.items
              .where(
                (p) =>
                    p.nom.toLowerCase().contains(q) ||
                    p.category.toLowerCase().contains(q),
              )
              .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            PillButton(
              label: 'Ajouter un produit',
              colorKey: 'amber',
              icon: Icons.add,
              onPressed: () => _openForm(),
            ),
            const Spacer(),
            SizedBox(
              width: 280,
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search, size: 18),
                  hintText: 'Rechercher un produit...',
                  isDense: true,
                ),
                onChanged: (_) => setState(() {}),
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
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('NOM')),
                    DataColumn(label: Text('CATÉGORIE')),
                    DataColumn(label: Text('PRIX')),
                    DataColumn(label: Text('STOCK')),
                    DataColumn(label: Text('')),
                  ],
                  rows: visible.map((p) {
                    final isDeleting = state.deletingId == p.id;
                    return DataRow(
                      cells: [
                        DataCell(Text(p.nom)),
                        DataCell(Text(p.category)),
                        DataCell(Text('${p.prix.toStringAsFixed(2)} GDES')),
                        DataCell(
                          Text(
                            p.quantiteStock == p.quantiteStock.roundToDouble()
                                ? p.quantiteStock.toStringAsFixed(0)
                                : p.quantiteStock.toStringAsFixed(2),
                            style: TextStyle(
                              color: p.quantiteStock <= 0
                                  ? AppColors.danger
                                  : AppColors.textPrimary,
                            ),
                          ),
                        ),
                        DataCell(
                          isDeleting
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : Row(
                                  children: [
                                    IconButton(
                                      tooltip: 'Modifier',
                                      icon: Icon(
                                        Icons.edit_outlined,
                                        size: 17,
                                        color: AppColors.accentLight,
                                      ),
                                      onPressed: () => _openForm(produit: p),
                                    ),
                                    IconButton(
                                      tooltip: 'Supprimer',
                                      icon: const Icon(
                                        Icons.delete_outline,
                                        size: 17,
                                        color: AppColors.danger,
                                      ),
                                      onPressed: () => _confirmDelete(p),
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

class _ProduitFormDialog extends StatefulWidget {
  const _ProduitFormDialog({this.initial});

  final Produit? initial;

  @override
  State<_ProduitFormDialog> createState() => _ProduitFormDialogState();
}

class _ProduitFormDialogState extends State<_ProduitFormDialog> {
  late final _nomController = TextEditingController(
    text: widget.initial?.nom ?? '',
  );
  late final _prixController = TextEditingController(
    text: widget.initial?.prix.toString() ?? '',
  );
  late final _stockController = TextEditingController(
    text: widget.initial?.quantiteStock.toString() ?? '0',
  );
  late final _descController = TextEditingController(
    text: widget.initial?.description ?? '',
  );
  late String? _category = widget.initial?.category;
  String? _error;

  @override
  void dispose() {
    _nomController.dispose();
    _prixController.dispose();
    _stockController.dispose();
    _descController.dispose();
    super.dispose();
  }

  /// Équivalent de la demande explicite "on devait être capable d'ajouter
  /// une catégorie aussi" — invite + POST v1/categories-produits, puis
  /// sélectionne immédiatement la catégorie créée.
  Future<void> _addCategory() async {
    final controller = TextEditingController();
    final nom = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Nouvelle catégorie'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Nom de la catégorie'),
          onSubmitted: (v) => Navigator.of(context).pop(v.trim()),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: const Text('Ajouter'),
          ),
        ],
      ),
    );
    if (!mounted || nom == null || nom.isEmpty) return;
    final error = await context.read<ProduitState>().createCategory(nom);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    } else {
      setState(() => _category = nom);
    }
  }

  Future<void> _submit() async {
    final nom = _nomController.text.trim();
    final prix = double.tryParse(_prixController.text.trim());
    final stock = double.tryParse(_stockController.text.trim());

    if (nom.isEmpty ||
        _category == null ||
        _category!.isEmpty ||
        prix == null ||
        prix <= 0 ||
        stock == null ||
        stock < 0) {
      setState(
        () => _error = 'Nom, catégorie, prix (> 0) et stock sont requis.',
      );
      return;
    }

    setState(() => _error = null);
    final state = context.read<ProduitState>();
    final error = widget.initial == null
        ? await state.create(
            nom: nom,
            category: _category!,
            prix: prix,
            quantiteStock: stock,
            description: _descController.text.trim().isEmpty
                ? null
                : _descController.text.trim(),
          )
        : await state.update(
            widget.initial!.id,
            nom: nom,
            category: _category!,
            prix: prix,
            quantiteStock: stock,
            description: _descController.text.trim().isEmpty
                ? null
                : _descController.text.trim(),
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
    final state = context.watch<ProduitState>();
    // Garde la catégorie actuelle du produit dans la liste même si elle a
    // depuis été supprimée de la table gérée (en édition).
    final categoryNames = state.categories.map((c) => c.nom).toList();
    if (_category != null && !categoryNames.contains(_category)) {
      categoryNames.insert(0, _category!);
    }

    return ParamDialogShell(
      title: widget.initial == null
          ? 'Ajouter un produit'
          : 'Modifier le produit',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: _nomController,
            decoration: const InputDecoration(labelText: 'Nom du produit'),
          ),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: state.isLoadingCategories
                    ? const Padding(
                        padding: EdgeInsets.symmetric(vertical: 14),
                        child: LinearProgressIndicator(minHeight: 2),
                      )
                    : DropdownButtonFormField<String>(
                        initialValue: categoryNames.contains(_category)
                            ? _category
                            : null,
                        decoration: const InputDecoration(
                          labelText: 'Catégorie',
                        ),
                        items: categoryNames
                            .map(
                              (c) => DropdownMenuItem(value: c, child: Text(c)),
                            )
                            .toList(),
                        onChanged: (v) => setState(() => _category = v),
                      ),
              ),
              const SizedBox(width: 8),
              IconButton(
                tooltip: 'Ajouter une catégorie',
                icon: Icon(
                  Icons.add_circle_outline,
                  color: AppColors.accentLight,
                ),
                onPressed: state.isSubmittingCategory ? null : _addCategory,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _prixController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(labelText: 'Prix unitaire'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _stockController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Quantité en stock',
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _descController,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Description (optionnel)',
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          ParamDialogActions(
            isEdit: widget.initial != null,
            submitting: state.isSubmitting,
            onSubmit: _submit,
          ),
        ],
      ),
    );
  }
}
