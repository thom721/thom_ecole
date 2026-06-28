import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/cours.dart';
import '../../state/cours_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';

const _typeMatiereOptions = ['Base', 'Orale'];

class _CoursRow {
  _CoursRow({this.id, String coursNom = '', this.niveauId, this.typeMatiere = 'Base', String? noteDePassage, String? coefficients})
      : coursNom = TextEditingController(text: coursNom),
        noteDePassage = TextEditingController(text: noteDePassage),
        coefficients = TextEditingController(text: coefficients);

  factory _CoursRow.fromCours(Cours c) => _CoursRow(
        id: c.id,
        coursNom: c.coursNom,
        niveauId: c.niveauId,
        typeMatiere: _typeMatiereOptions.contains(c.typeMatiere) ? c.typeMatiere : 'Base',
        noteDePassage: c.noteDePassage,
        coefficients: c.coefficients,
      );

  final String? id;
  final TextEditingController coursNom;
  String? niveauId;
  String typeMatiere;
  final TextEditingController noteDePassage;
  final TextEditingController coefficients;

  void dispose() {
    coursNom.dispose();
    noteDePassage.dispose();
    coefficients.dispose();
  }
}

/// Équivalent de add_cours_page()/add_cours_line()/enregistrer_cours()
/// (school_client, Controllers/Main.py:9645-10006, 10227-10246) : une page
/// dédiée (pas une simple modale) où l'on peut ajouter plusieurs lignes de
/// cours dynamiquement ("Ajouter une ligne", self.cours_dictionary) et les
/// enregistrer toutes en un seul envoi (POST v1/cours, {"CoursesObject":
/// [...]}). En édition (clic "Modifier" depuis la liste — réellement câblé
/// via le routeur de réponses asynchrones, endpoint `v1/cours/{id}`, pas
/// via on_row_clicked_cours qui est mort), la page s'ouvre avec UNE ligne
/// préremplie ; l'utilisateur peut quand même ajouter d'autres lignes
/// vierges dans le même envoi. Chaque ligne existante (avec id) a un bouton
/// "Supprimer de la base" qui la supprime réellement (GET
/// v1/delete-cours/{id}) ; "Supprimer" retire juste la ligne du formulaire.
class CoursFormScreen extends StatefulWidget {
  const CoursFormScreen({super.key, this.initial});

  final Cours? initial;

  @override
  State<CoursFormScreen> createState() => _CoursFormScreenState();
}

class _CoursFormScreenState extends State<CoursFormScreen> {
  late List<_CoursRow> _rows;
  String? _error;

  bool get _isEdit => widget.initial != null;

  @override
  void initState() {
    super.initState();
    _rows = [
      if (widget.initial != null) _CoursRow.fromCours(widget.initial!) else _newRow(),
    ];
  }

  /// Sur le bureau, niveau_id n'est jamais affiché dans add_cours_line()
  /// (Main.py:9929/9974, `# row_layout.addWidget(niveau_id, 0, 0)` reste
  /// commenté) — seul `cours_nom` et `type_matiere` sont visibles. Le combo
  /// niveau existe quand même et garde sa valeur par défaut (le premier
  /// niveau de la liste) lors de l'envoi. Reproduit ici à l'identique : pas
  /// de sélecteur niveau visible, mais une valeur par défaut est tout de
  /// même envoyée pour rester cohérent avec le contrat serveur.
  _CoursRow _newRow() {
    final niveaux = context.read<ReferenceDataState>().niveaux;
    return _CoursRow(niveauId: niveaux.isNotEmpty ? niveaux.first.id : null);
  }

  @override
  void dispose() {
    for (final r in _rows) {
      r.dispose();
    }
    super.dispose();
  }

  void _addRow() => setState(() => _rows.add(_newRow()));

  void _removeRow(_CoursRow row) {
    setState(() {
      _rows.remove(row);
      row.dispose();
    });
  }

  Future<void> _deleteFromDb(_CoursRow row) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer définitivement le cours "${row.coursNom.text}" ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Supprimer')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<CoursState>().delete(row.id!);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
      return;
    }
    _removeRow(row);
  }

  /// Seul `cours_nom` est validé côté UI, comme sur le bureau (seul champ
  /// visible) — niveau_id/coefficients/note_de_passage voyagent avec leur
  /// valeur par défaut sans contrôle ici ; le serveur peut les rejeter
  /// (RCours.py:206-218) si le niveau par défaut ne convient pas, l'erreur
  /// remontera alors telle quelle.
  Future<void> _submit() async {
    final items = <Map<String, dynamic>>[];
    for (final row in _rows) {
      if (row.coursNom.text.trim().isEmpty) {
        setState(() => _error = 'Le nom du cours est requis pour chaque ligne.');
        return;
      }
      items.add({
        if (row.id != null) 'id': row.id,
        'cours_nom': row.coursNom.text.trim(),
        'niveau_id': row.niveauId,
        'type_matiere': row.typeMatiere,
        'note_de_passage': row.noteDePassage.text.trim().isEmpty ? null : row.noteDePassage.text.trim(),
        'coefficients': row.coefficients.text.trim().isEmpty ? null : row.coefficients.text.trim(),
      });
    }

    setState(() => _error = null);
    final error = await context.read<CoursState>().save(items);
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<CoursState>();

    return Scaffold(
      backgroundColor: AppColors.appBg,
      appBar: AppBar(
        backgroundColor: AppColors.appBg,
        elevation: 0,
        title: Text(_isEdit ? 'Modifier un cours' : 'Ajouter des cours'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Vous pouvez ajouter plusieurs lignes pour enregistrer plusieurs cours à la fois.',
              style: TextStyle(fontSize: 12.5, color: AppColors.textMuted),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: AppColors.sidebarBg,
                  border: Border.all(color: AppColors.borderSubtle),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      for (final row in _rows) ...[
                        _buildRow(row),
                        Divider(height: 24, color: AppColors.borderSubtle),
                      ],
                      TextButton.icon(
                        onPressed: _addRow,
                        icon: const Icon(Icons.add, size: 16),
                        label: const Text('Ajouter une ligne'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12.5)),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${_rows.length} matière${_rows.length > 1 ? 's' : ''}',
                    style: TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
                FilledButton(
                  onPressed: state.isSubmitting ? null : _submit,
                  child: state.isSubmitting
                      ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : Text(_isEdit ? 'Modifier' : 'Enregistrer tout'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Seuls `cours_nom` et `type_matiere` sont visibles, comme dans
  /// add_cours_line() (Main.py:9975-9978) — niveau_id/coefficients/
  /// note_de_passage ne sont pas affichés (voir _newRow()/_CoursRow).
  Widget _buildRow(_CoursRow row) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: TextField(controller: row.coursNom, decoration: const InputDecoration(labelText: 'Nom du cours')),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: DropdownButtonFormField<String>(
            initialValue: row.typeMatiere,
            decoration: const InputDecoration(labelText: 'Type de matière'),
            items: _typeMatiereOptions.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
            onChanged: (v) => setState(() => row.typeMatiere = v ?? row.typeMatiere),
          ),
        ),
        const SizedBox(width: 8),
        IconButton(
          tooltip: 'Supprimer cette ligne',
          icon: Icon(Icons.close, size: 18, color: AppColors.textMuted),
          onPressed: _rows.length > 1 ? () => _removeRow(row) : null,
        ),
        if (row.id != null)
          IconButton(
            tooltip: 'Supprimer de la base',
            icon: const Icon(Icons.delete_forever_outlined, size: 18, color: AppColors.danger),
            onPressed: () => _deleteFromDb(row),
          ),
      ],
    );
  }
}
