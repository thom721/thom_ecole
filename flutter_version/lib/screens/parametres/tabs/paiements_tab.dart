import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/parametres.dart';
import '../../../state/auth_state.dart';
import '../../../state/parametres_state.dart';
import '../../../state/reference_data_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/param_dialog.dart';
import '../../../widgets/param_tab_card.dart';

// Échéances réellement proposées par le bureau (Helper/Components/
// Payment_params.py:187 : `self.echeance.addItems(["mois", "Trimestre",
// "Versement", "Session"])`) — pas de "Controle" ici, contrairement à
// Parametres.vue (web).
const _echeanceOptions = ['mois', 'Trimestre', 'Versement', 'Session'];
// Devises réelles du bureau (Payment_params.py:270 : `["GDES", "USD"]`) —
// pas de "$HT", contrairement au web.
const _deviseOptions = ['GDES', 'USD'];
const _accessoireTypes = ['Maillot', 'Badge', 'Tenue de Sport', 'Initiale'];

// Clés mois acceptées par VERSEMENT_KEY_REGEX côté serveur
// (RPaiementParam.py:25-28) : minuscules, SANS accents.
const _moisCles = [
  'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
  'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre',
];

String _capitalize(String s) => s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';

/// Équivalent de list_months_between() (Payment_params.py:140-170).
List<String> _moisEntreDates(String dateDebut, String dateFin) {
  DateTime? start = DateTime.tryParse(dateDebut);
  DateTime? end = DateTime.tryParse(dateFin);
  if (start == null || end == null) return [];
  final result = <String>[];
  var cur = DateTime(start.year, start.month, 1);
  final last = DateTime(end.year, end.month, 1);
  while (!cur.isAfter(last)) {
    result.add(_moisCles[cur.month - 1]);
    cur = DateTime(cur.year, cur.month + 1, 1);
  }
  return result;
}

/// Onglet "Paiements" — la LISTE reste alignée sur Parametres.vue ; la MODALE
/// reproduit fidèlement le bureau réel (Helper/Components/Payment_params.py).
class PaiementsTab extends StatelessWidget {
  const PaiementsTab({super.key});

  Future<void> _confirmDelete(
      BuildContext context, ParametrePaiementRecord pp, ParametresState state) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer le paramètre de paiement "${pp.nomClasse} — ${pp.anneeAc}" ?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;
    final error = await state.deletePaiementParam(pp.id);
    if (!context.mounted) return;
    if (error != null) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
  }

  void _showDetail(BuildContext context, ParametrePaiementRecord pp) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Détails — Paramètre Paiement'),
        content: ParamDetailTable(rows: [
          ('Cycle', pp.niveauName),
          ('Classe', pp.nomClasse),
          ('Année', pp.anneeAc),
          ('Payer par', pp.echeance),
          ('Devise', pp.devise),
          if (pp.montant != null) ('Montant', '${pp.montant}'),
          if (pp.nbEcheance != null) ("Nb d'échéances", '${pp.nbEcheance}'),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Fermer')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    final subs = context.watch<AuthState>().visibleSubItems('settings');
    final canAjouter = subs == null || subs.contains('ajouter');
    final canModifier = subs == null || subs.contains('modifier');
    final canSupprimer = subs == null || subs.contains('supprimer');
    final canVoir = subs == null || subs.contains('voir');

    return ParamTabCard(
      title: 'Paramètres des Paiements',
      subtitle: 'Montants, échéances et devises par classe',
      canAdd: canAjouter,
      onAdd: () => showDialog(context: context, builder: (_) => const _PaiementParamFormDialog()),
      isLoading: state.paiementParamLoading,
      error: state.paiementParamError,
      emptyLabel: 'Aucun paramètre de paiement',
      emptyIcon: Icons.credit_card_outlined,
      currentPage: state.paiementParamCurrentPage,
      lastPage: state.paiementParamLastPage,
      onPageChange: (page) => context.read<ParametresState>().loadPaiementParams(page: page),
      columns: const [
        DataColumn(label: Text('MONTANT')),
        DataColumn(label: Text('CYCLE')),
        DataColumn(label: Text('CLASSE')),
        DataColumn(label: Text('PAIEMENT PAR')),
        DataColumn(label: Text('ANNÉE A.')),
        DataColumn(label: Text('')),
      ],
      rows: state.paiementParamsList.map((pp) {
        return DataRow(cells: [
          DataCell(
            pp.echeance == 'mois'
                ? Text.rich(TextSpan(children: [
                    TextSpan(
                        text: '${pp.montant} ',
                        style: TextStyle(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w700,
                            fontFamily: 'monospace')),
                    TextSpan(text: pp.devise, style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                  ]))
                : const BadgePill(label: 'Versements', colorKey: 'emerald'),
          ),
          DataCell(BadgePill(label: pp.niveauName, colorKey: 'purple')),
          DataCell(
              Text(pp.nomClasse, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600))),
          DataCell(BadgePill(label: pp.echeance, colorKey: 'sky')),
          DataCell(Text(pp.anneeAc, style: TextStyle(color: AppColors.textMuted))),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (canVoir)
                IconButton(
                  tooltip: 'Voir',
                  icon: const Icon(Icons.remove_red_eye_outlined, size: 16, color: Color(0xFF34D399)),
                  onPressed: () => _showDetail(context, pp),
                ),
              if (canModifier)
                IconButton(
                  tooltip: 'Modifier',
                  icon: Icon(Icons.edit_outlined, size: 16, color: AppColors.accentLight),
                  onPressed: () async {
                    final full = await context.read<ParametresState>().fetchPaiementParam(pp.id);
                    if (full != null && context.mounted) {
                      showDialog(
                          context: context,
                          builder: (_) => _PaiementParamFormDialog(record: full));
                    }
                  },
                ),
              if (canSupprimer)
                IconButton(
                  tooltip: 'Supprimer',
                  icon: const Icon(Icons.delete_outline, size: 16, color: AppColors.danger),
                  onPressed: () => _confirmDelete(context, pp, state),
                ),
            ],
          )),
        ]);
      }).toList(),
    );
  }
}

class _AccessoireFormRow {
  _AccessoireFormRow({this.type, num? prix})
      : prixController = TextEditingController(text: prix == null ? '' : '$prix');
  String? type;
  final TextEditingController prixController;
}

class _PaiementParamFormDialog extends StatefulWidget {
  const _PaiementParamFormDialog({this.record});

  final ParametrePaiementRecord? record;

  @override
  State<_PaiementParamFormDialog> createState() => _PaiementParamFormDialogState();
}

class _PaiementParamFormDialogState extends State<_PaiementParamFormDialog> {
  String? _niveauId;
  String? _faculteId;
  String? _classeId;
  String? _anneeAcademiqueId;
  String? _echeance;
  String? _devise;
  int? _nbEcheance;
  final _fraisDentreController = TextEditingController();
  final _montantController = TextEditingController();
  Map<String, TextEditingController> _montantParControllers = {};
  List<_AccessoireFormRow> _accessoires = [];
  String? _error;

  bool get _isMois => _echeance == 'mois';

  String _echeanceLabel(String value) => value == 'mois' ? 'Mois' : value;

  @override
  void initState() {
    super.initState();
    final r = widget.record;
    if (r != null) {
      _niveauId = r.niveauId;
      _faculteId = r.faculteId;
      _classeId = r.classeId;
      _anneeAcademiqueId = r.anneeAcademiqueId;
      _echeance = r.echeance;
      _devise = r.devise;
      _nbEcheance = r.nbEcheance ?? 1;
      if (r.montant != null) _montantController.text = '${r.montant}';
      if (r.echeance == 'mois') {
        final sorted = r.montantPar.entries.toList()
          ..sort((a, b) {
            final ia = int.tryParse(a.key.split('_').elementAtOrNull(1) ?? '') ?? 0;
            final ib = int.tryParse(b.key.split('_').elementAtOrNull(1) ?? '') ?? 0;
            return ia.compareTo(ib);
          });
        if (sorted.isNotEmpty) _fraisDentreController.text = '${sorted.first.value}';
      } else {
        _montantParControllers = {
          for (final entry in r.montantPar.entries) entry.key: TextEditingController(text: '${entry.value}'),
        };
      }
      _accessoires = r.accessoires
          .map((a) => _AccessoireFormRow(type: a.typeDaccessoire, prix: a.prix))
          .toList();
    } else {
      _echeance = 'mois';
      _nbEcheance = 1;
    }
  }

  @override
  void dispose() {
    _fraisDentreController.dispose();
    _montantController.dispose();
    for (final c in _montantParControllers.values) {
      c.dispose();
    }
    for (final a in _accessoires) {
      a.prixController.dispose();
    }
    super.dispose();
  }

  void _regenerateMontantParFields() {
    for (final c in _montantParControllers.values) {
      c.dispose();
    }
    _montantParControllers = {};
    if (_isMois || _nbEcheance == null || _anneeAcademiqueId == null) return;
    for (var i = 1; i <= _nbEcheance!; i++) {
      final key = '${_echeance}_${i}_$_anneeAcademiqueId';
      _montantParControllers[key] = TextEditingController();
    }
  }

  void _onEcheanceChanged(String? v) {
    setState(() {
      _echeance = v;
      _nbEcheance = 1;
      _regenerateMontantParFields();
    });
  }

  void _onNbEcheanceChanged(int? v) {
    setState(() {
      _nbEcheance = v;
      _regenerateMontantParFields();
    });
  }

  void _onAnneeChanged(String? v) {
    setState(() {
      _anneeAcademiqueId = v;
      _regenerateMontantParFields();
    });
  }

  void _addAccessoire() => setState(() => _accessoires.add(_AccessoireFormRow()));

  void _removeAccessoire(int index) => setState(() {
        _accessoires[index].prixController.dispose();
        _accessoires.removeAt(index);
      });

  Future<void> _submit(ParametresState state) async {
    if (_niveauId == null || _classeId == null || _echeance == null || _devise == null || _anneeAcademiqueId == null) {
      setState(() => _error = 'Cycle, classe, échéance, devise et année sont requis.');
      return;
    }
    num? montant;
    final montantPar = <String, num>{};
    if (_isMois) {
      final annee = state.annees.where((a) => a.id == _anneeAcademiqueId).firstOrNull;
      if (annee == null) {
        setState(() => _error = 'Année académique introuvable.');
        return;
      }
      montant = num.tryParse(_montantController.text.replaceAll(',', '.'));
      if (montant == null || montant <= 0) {
        setState(() => _error = 'Montant obligatoire pour une échéance mensuelle.');
        return;
      }
      final fraisDentre = num.tryParse(_fraisDentreController.text.replaceAll(',', '.')) ?? 0;
      final mois = _moisEntreDates(annee.dateDebut, annee.dateFin);
      if (mois.isEmpty) {
        setState(() => _error = "Impossible de déterminer les mois de cette année académique.");
        return;
      }
      for (var i = 0; i < mois.length; i++) {
        final key = '${mois[i]}_${i + 1}_$_anneeAcademiqueId';
        montantPar[key] = i == 0 ? fraisDentre : montant;
      }
    } else {
      if (_nbEcheance == null || _montantParControllers.isEmpty) {
        setState(() => _error = "Nombre d'échéances requis.");
        return;
      }
      for (final entry in _montantParControllers.entries) {
        final v = num.tryParse(entry.value.text.replaceAll(',', '.'));
        if (v == null || v <= 0) {
          setState(() => _error = 'Chaque montant doit être un nombre supérieur à 0.');
          return;
        }
        montantPar[entry.key] = v;
      }
    }

    final accessoires = <AccessoireConfig>[];
    for (final a in _accessoires) {
      if (a.type == null || a.prixController.text.trim().isEmpty) continue;
      final prix = num.tryParse(a.prixController.text.replaceAll(',', '.'));
      if (prix == null || prix <= 0) {
        setState(() => _error = 'Le prix de chaque accessoire doit être supérieur à 0.');
        return;
      }
      accessoires.add(AccessoireConfig(typeDaccessoire: a.type!, prix: prix));
    }

    setState(() => _error = null);
    final error = await context.read<ParametresState>().submitPaiementParam(
          id: widget.record?.id,
          niveauId: _niveauId!,
          faculteId: _faculteId,
          classeId: _classeId!,
          echeance: _echeance!,
          devise: _devise!,
          anneeAcademiqueId: _anneeAcademiqueId!,
          nbEcheance: _nbEcheance,
          montant: montant,
          montantPar: montantPar,
          accessoires: accessoires,
        );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ParametresState>();
    final ref = context.watch<ReferenceDataState>();
    final niveauName = ref.niveaux.where((n) => n.id == _niveauId).firstOrNull?.name;
    final showFaculte = niveauName == 'Universitaire' || niveauName == 'Technique';

    final anneeSelectionnee = state.annees.where((a) => a.id == _anneeAcademiqueId).firstOrNull;
    final premierMois = anneeSelectionnee == null
        ? null
        : _moisEntreDates(anneeSelectionnee.dateDebut, anneeSelectionnee.dateFin).firstOrNull;

    return ParamDialogShell(
      title: 'Paramètres de Paiement',
      width: 720,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _niveauId,
            decoration: const InputDecoration(labelText: 'Cycle / niveau / Section'),
            items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
            onChanged: (v) => setState(() {
              _niveauId = v;
              if (widget.record == null) {
                _classeId = null;
                _faculteId = null;
                _devise = null;
                _montantController.clear();
              }
            }),
          ),
          if (showFaculte) ...[
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _faculteId,
              decoration: const InputDecoration(labelText: "Faculté / Domaine d'étude"),
              items: ref.facultes.map((f) => DropdownMenuItem(value: f.id, child: Text(f.nom))).toList(),
              onChanged: (v) => setState(() => _faculteId = v),
            ),
          ],
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _classeId,
            decoration: const InputDecoration(labelText: 'Classe'),
            items: ref
                .classesForNiveau(_niveauId)
                .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                .toList(),
            onChanged: (v) => setState(() => _classeId = v),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _anneeAcademiqueId,
            decoration: const InputDecoration(labelText: 'Année Académique'),
            items:
                state.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.anneeAcademique))).toList(),
            onChanged: _onAnneeChanged,
          ),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _echeance,
                  decoration: const InputDecoration(labelText: 'Payer par'),
                  items: _echeanceOptions
                      .map((e) => DropdownMenuItem(value: e, child: Text(_echeanceLabel(e))))
                      .toList(),
                  onChanged: _onEcheanceChanged,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<int>(
                  initialValue: _nbEcheance,
                  decoration: InputDecoration(labelText: "Nbres de ${_echeance ?? 'Payer par'}"),
                  items: [1, 2, 3, 4, 5].map((n) => DropdownMenuItem(value: n, child: Text('$n'))).toList(),
                  onChanged: _onNbEcheanceChanged,
                ),
              ),
            ],
          ),
          if (!_isMois && _montantParControllers.isNotEmpty) ...[
            const SizedBox(height: 12),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: _montantParControllers.entries.toList().asMap().entries.map((indexed) {
                final index = indexed.key;
                final controller = indexed.value.value;
                return SizedBox(
                  width: 140,
                  child: TextField(
                    controller: controller,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(labelText: '${_echeance ?? ''} ${index + 1}'),
                  ),
                );
              }).toList(),
            ),
          ],
          const SizedBox(height: 16),
          Row(
            children: [
              Text('Accessoires',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              const Spacer(),
              TextButton.icon(
                onPressed: _addAccessoire,
                icon: const Icon(Icons.add, size: 14),
                label: const Text('Ajouter Accessoire'),
              ),
            ],
          ),
          ...List.generate(_accessoires.length, (index) {
            final row = _accessoires[index];
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: row.type,
                      decoration: const InputDecoration(labelText: 'Type'),
                      items:
                          _accessoireTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                      onChanged: (v) => setState(() => row.type = v),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: row.prixController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(labelText: 'Prix'),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 16, color: AppColors.danger),
                    onPressed: () => _removeAccessoire(index),
                  ),
                ],
              ),
            );
          }),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_isMois) ...[
                Expanded(
                  child: TextField(
                    controller: _fraisDentreController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText:
                          'Frais d\'entre (+) ${premierMois == null ? 'Premier mois' : _capitalize(premierMois)}',
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _montantController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(labelText: 'Montant'),
                  ),
                ),
                const SizedBox(width: 12),
              ],
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _devise,
                  decoration: const InputDecoration(labelText: 'Devise'),
                  items: _deviseOptions.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
                  onChanged: (v) => setState(() => _devise = v),
                ),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
          ],
          ParamDialogActions(
            isEdit: widget.record != null,
            submitting: state.paiementParamSubmitting,
            onSubmit: () => _submit(state),
          ),
        ],
      ),
    );
  }
}
