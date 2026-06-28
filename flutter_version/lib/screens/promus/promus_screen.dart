import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../state/promus_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/section_header.dart';

/// Équivalent de promus_page() (school_client, Controllers/Main.py:11644+) :
/// recherche les élèves d'une classe pour une année donnée (avec moyenne
/// générale + statut Succès/Échec calculés côté serveur), puis les promeut
/// (ou redouble) vers une classe/année future. Feature 100% bureau.
class PromusScreen extends StatefulWidget {
  const PromusScreen({super.key});

  @override
  State<PromusScreen> createState() => _PromusScreenState();
}

class _PromusScreenState extends State<PromusScreen> {
  String? _anneeActuelle;
  String? _niveauActuel;
  String? _classeActuelle;

  String? _anneeFuture;
  String? _niveauFuture;
  String? _classeFuture;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReferenceDataState>().loadOnce();
    });
  }

  Future<void> _rechercher() async {
    if (_anneeActuelle == null || _niveauActuel == null || _classeActuelle == null) return;
    await context.read<PromusState>().rechercher(
          annee: _anneeActuelle!,
          niveau: _niveauActuel!,
          classe: _classeActuelle!,
        );
  }

  /// Équivalent de cancel_promus_to() → promus_page() (juste un reset).
  void _annuler() {
    setState(() {
      _anneeActuelle = null;
      _niveauActuel = null;
      _classeActuelle = null;
      _anneeFuture = null;
      _niveauFuture = null;
      _classeFuture = null;
    });
    context.read<PromusState>().reset();
  }

  Future<void> _promouvoir() async {
    if (_anneeActuelle == null ||
        _niveauActuel == null ||
        _classeActuelle == null ||
        _anneeFuture == null ||
        _niveauFuture == null ||
        _classeFuture == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sélectionnez la classe actuelle ET la classe future.')),
      );
      return;
    }
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Confirmation'),
        content: const Text(
            'Voulez-vous vraiment promouvoir cette classe ? Les élèves en échec redoubleront automatiquement.'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Non')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Oui')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final state = context.read<PromusState>();
    final ok = await state.promouvoir(
      anneeActuelle: _anneeActuelle!,
      niveauActuel: _niveauActuel!,
      classeActuelle: _classeActuelle!,
      anneeFuture: _anneeFuture!,
      niveauFuture: _niveauFuture!,
      classeFuture: _classeFuture!,
    );
    if (!mounted) return;
    if (ok) {
      final stats = state.lastStats;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(stats == null
            ? 'Promotion effectuée avec succès.'
            : '${stats['promus'] ?? 0} promu(s), ${stats['redoublants'] ?? 0} redoublant(s).'),
      ));
    } else {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(state.promoteError ?? 'Erreur lors de la promotion.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final ref = context.watch<ReferenceDataState>();
    final state = context.watch<PromusState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Promus',
            subtitle: "Promotion des élèves vers l'année académique suivante",
            icon: Icons.trending_up,
            colorKey: 'cyan',
          ),
          const SizedBox(height: 16),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _sectionCard(
                    title: 'Classe actuelle',
                    children: [
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _anneeActuelle,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Année Académique'),
                              items: ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
                              onChanged: (v) => setState(() => _anneeActuelle = v),
                            ),
                          ),
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _niveauActuel,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Cycle / niveau'),
                              items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
                              onChanged: (v) => setState(() {
                                _niveauActuel = v;
                                _classeActuelle = null;
                              }),
                            ),
                          ),
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _classeActuelle,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Classe'),
                              items: ref
                                  .classesForNiveau(_niveauActuel)
                                  .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                                  .toList(),
                              onChanged: (v) => setState(() => _classeActuelle = v),
                            ),
                          ),
                          FilledButton(
                            onPressed: state.isSearching ? null : _rechercher,
                            child: state.isSearching
                                ? const SizedBox(
                                    height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                : const Text('Rechercher'),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (state.hasSearched) ...[
                    if (state.searchError != null)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Text(state.searchError!, style: const TextStyle(color: AppColors.danger)),
                      )
                    else
                      DataTableCard(
                        child: DataTable(
                          columns: const [
                            DataColumn(label: Text('NOM')),
                            DataColumn(label: Text('PRÉNOM')),
                            DataColumn(label: Text('TOTAL N.')),
                            DataColumn(label: Text('TOTAL COÉFF')),
                            DataColumn(label: Text('MOY G.')),
                            DataColumn(label: Text('STATUT')),
                          ],
                          rows: state.resultats.isEmpty
                              ? [
                                  DataRow(cells: [
                                    DataCell(
                                        Text('Aucune donnée trouvée pour ces paramètres', style: TextStyle(color: AppColors.textMuted))),
                                    const DataCell(Text('')),
                                    const DataCell(Text('')),
                                    const DataCell(Text('')),
                                    const DataCell(Text('')),
                                    const DataCell(Text('')),
                                  ]),
                                ]
                              : state.resultats.map((e) {
                                  final color = e.succes ? const Color(0xFF34D399) : const Color(0xFFFB7185);
                                  return DataRow(cells: [
                                    DataCell(Text(e.nom, style: TextStyle(color: AppColors.textPrimary))),
                                    DataCell(Text(e.prenom, style: TextStyle(color: AppColors.textPrimary))),
                                    DataCell(Text(e.note.toStringAsFixed(2), style: TextStyle(color: AppColors.textMuted))),
                                    DataCell(Text(e.max.toStringAsFixed(2), style: TextStyle(color: AppColors.textMuted))),
                                    DataCell(Text(e.moyenne, style: TextStyle(color: color, fontWeight: FontWeight.w700))),
                                    DataCell(Text(e.status, style: TextStyle(color: color, fontWeight: FontWeight.w600))),
                                  ]);
                                }).toList(),
                        ),
                      ),
                    const SizedBox(height: 16),
                  ],
                  _sectionCard(
                    title: 'Promouvoir vers',
                    children: [
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: [
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _anneeFuture,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Année Académique'),
                              items: ref.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom))).toList(),
                              onChanged: (v) => setState(() => _anneeFuture = v),
                            ),
                          ),
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _niveauFuture,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Cycle / niveau'),
                              items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
                              onChanged: (v) => setState(() {
                                _niveauFuture = v;
                                _classeFuture = null;
                              }),
                            ),
                          ),
                          SizedBox(
                            width: 170,
                            child: DropdownButtonFormField<String>(
                              initialValue: _classeFuture,
                              isDense: true,
                              decoration: const InputDecoration(labelText: 'Classe'),
                              items: ref
                                  .classesForNiveau(_niveauFuture)
                                  .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                                  .toList(),
                              onChanged: (v) => setState(() => _classeFuture = v),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: _annuler,
                            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
                            child: const Text('Annuler'),
                          ),
                          const SizedBox(width: 8),
                          FilledButton(
                            onPressed: state.isPromoting ? null : _promouvoir,
                            child: state.isPromoting
                                ? const SizedBox(
                                    height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                : const Text('Promus'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionCard({required String title, required List<Widget> children}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }
}
