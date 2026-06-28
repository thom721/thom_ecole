import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/student.dart';
import '../../state/parametres_state.dart';
import '../../state/rapport_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';

const _moisOptions = [
  'Septembre', 'Octobre', 'Novembre', 'Décembre', 'Janvier', 'Février',
  'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août',
];

const _versementOptions = [
  '1er Versement', '2ème Versement', '3ème Versement', '4ème Versement',
];

/// Sentinelles attendues littéralement par le serveur (jamais null/omis) :
/// cf. RegisterRepport.py / PedagogicRepport.py ("Toutes les classes" pour
/// la classe administratif/pédagogique) et PaymentRepport.py ("All",
/// insensible à la casse, pour la classe financière).
const _sentinelToutesLesClasses = 'Toutes les classes';
const _sentinelClasseAll = 'All';
const _sentinelTousLesMois = 'Tous les mois';
const _sentinelTousLesVersements = 'tous les versements';

/// Équivalent de la section RAPPORT de school_client (Controllers/Main.py,
/// onglet "Rapport" du QStackedWidget) — DONNÉES/LOGIQUE : 5 rapports réels
/// (Global, Administratif/Registre, Pédagogique, Décision de fin d'année,
/// Financier), chacun POSTant un filtre vers un endpoint `print-*` qui
/// renvoie un PDF/Excel ouvert avec l'application par défaut du système
/// (RapportState, même schéma que PaiementState.printRecu()).
///
/// Le STYLE (cartes sombres, en-têtes à pastille colorée, grille 2 colonnes)
/// reprend ecole_nginx/frontend/src/views/admin/Rapport.vue — à l'exception
/// des sections "Présence" et "Disciplinaire" (absentes de school_client) et
/// des boutons "Excel" pour Global/Administratif/Pédagogique/Financier
/// (l'app de bureau ne les appelle jamais ; seul "Décision de fin d'année"
/// a un vrai export Excel côté bureau, via le flag `is_excel`). Le bouton
/// "Format Excel" du rapport Pédagogique est lui aussi omis : il appelle
/// v1/print-repport-pedagogique-exel, qui n'existe nulle part côté serveur.
class RapportScreen extends StatefulWidget {
  const RapportScreen({super.key});

  @override
  State<RapportScreen> createState() => _RapportScreenState();
}

class _RapportScreenState extends State<RapportScreen> {
  // Global
  String _globalType = 'Global';
  DateTime _globalDateDebut = DateTime.now();
  DateTime _globalDateFin = DateTime.now();

  // Financier — le champ "classe" est comparé au TEXTE de la classe (pas à
  // son id), cf. combo_financier_classe.currentText() dans Main.py.
  String _financierClasse = _sentinelClasseAll;
  String? _financierAnneeId;
  DateTime _financierDateFin = DateTime.now();
  String _financierVersement = _sentinelTousLesVersements;

  // Pédagogique + Décision de fin d'année (combos classe/année partagés
  // avec le bureau : combo_pedagogique_classe/annee).
  String? _pedagoCycle;
  String _pedagoClasse = _sentinelToutesLesClasses;
  String? _pedagoAnneeId;
  String _pedagoMois = _sentinelTousLesMois;

  // Administratif/Registre
  bool _adminIdentifiant = true;
  String? _adminCycle;
  String _adminClasse = _sentinelToutesLesClasses;
  String? _adminAnneeId;

  // Présence — export Excel uniquement (export-excel-presence, seule route
  // existante ; le bouton PDF du frontend web appelle print-present-repport
  // qui n'existe nulle part côté serveur).
  String _presenceClasse = _sentinelClasseAll;
  DateTime _presenceDateDebut = DateTime.now();
  DateTime _presenceDateFin = DateTime.now();

  bool _defaultsApplied = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await Future.wait([
        context.read<ReferenceDataState>().loadOnce(),
        context.read<ParametresState>().loadAnnees(),
      ]);
      if (!mounted) return;
      _applyDefaultsOnce();
    });
  }

  void _applyDefaultsOnce() {
    if (_defaultsApplied) return;
    final ref = context.read<ReferenceDataState>();
    final params = context.read<ParametresState>();
    final activeAnnee = params.annees.where((a) => a.status).firstOrNull ??
        params.annees.firstOrNull;
    setState(() {
      _pedagoCycle ??= ref.niveaux.firstOrNull?.id;
      _adminCycle ??= ref.niveaux.firstOrNull?.id;
      _pedagoAnneeId ??= activeAnnee?.id;
      _adminAnneeId ??= activeAnnee?.id;
      _financierAnneeId ??= activeAnnee?.id;
      _defaultsApplied = true;
    });
  }

  Future<void> _pickDate(DateTime initial, void Function(DateTime) onPicked) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) setState(() => onPicked(picked));
  }

  String _fmt(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  Future<void> _run(Future<String?> Function() action) async {
    final error = await action();
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      setState(() => _error = null);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rapport généré et ouvert.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final ref = context.watch<ReferenceDataState>();
    final params = context.watch<ParametresState>();
    final rapport = context.watch<RapportState>();

    if (!ref.isLoaded && params.annees.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Rapports',
            subtitle: 'Générez et imprimez vos rapports académiques',
            icon: Icons.bar_chart_outlined,
            colorKey: 'blue',
          ),
          const SizedBox(height: 20),
          if (_error != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.danger.withValues(alpha: 0.08),
                border: Border.all(color: AppColors.danger.withValues(alpha: 0.3)),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
            ),
            const SizedBox(height: 16),
          ],
          LayoutBuilder(
            builder: (context, constraints) {
              final twoCols = constraints.maxWidth >= 760;
              final global = _buildGlobalCard(rapport);
              final financier = _buildFinancierCard(ref, params, rapport);
              if (!twoCols) {
                return Column(children: [global, const SizedBox(height: 16), financier]);
              }
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: global),
                  const SizedBox(width: 16),
                  Expanded(child: financier),
                ],
              );
            },
          ),
          const SizedBox(height: 16),
          _buildPedagogiqueCard(ref, params, rapport),
          const SizedBox(height: 16),
          LayoutBuilder(
            builder: (context, constraints) {
              final twoCols = constraints.maxWidth >= 760;
              final administratif = _buildAdministratifCard(ref, params, rapport);
              final disciplinaire = _buildDisciplinaireCard();
              if (!twoCols) {
                return Column(children: [administratif, const SizedBox(height: 16), disciplinaire]);
              }
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: administratif),
                  const SizedBox(width: 16),
                  Expanded(child: disciplinaire),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _card({required Widget child}) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      clipBehavior: Clip.antiAlias,
      child: child,
    );
  }

  Widget _cardHeader(String title, String subtitle, IconData icon, String colorKey) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
      ),
      child: SectionHeader(title: title, subtitle: subtitle, icon: icon, colorKey: colorKey),
    );
  }

  Widget _label(String text) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Text(
          text.toUpperCase(),
          style: TextStyle(
            fontSize: 11,
            letterSpacing: 0.6,
            fontWeight: FontWeight.w600,
            color: AppColors.textMuted,
          ),
        ),
      );

  Widget _dateField(String labelText, DateTime value, void Function(DateTime) onPicked) {
    return InkWell(
      onTap: () => _pickDate(value, onPicked),
      borderRadius: BorderRadius.circular(10),
      child: InputDecorator(
        decoration: const InputDecoration(),
        child: Text(_fmt(value), style: TextStyle(color: AppColors.textPrimary, fontSize: 13)),
      ),
    );
  }

  Widget _printButton({
    required String label,
    required bool loading,
    required VoidCallback? onPressed,
    IconData icon = Icons.print_outlined,
    Color? color,
  }) {
    return FilledButton.icon(
      onPressed: loading ? null : onPressed,
      style: color != null ? FilledButton.styleFrom(backgroundColor: color) : null,
      icon: loading
          ? const SizedBox(
              height: 14,
              width: 14,
              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
            )
          : Icon(icon, size: 16),
      label: Text(label),
    );
  }

  // ── Rapport Global ──────────────────────────────────────────────────
  Widget _buildGlobalCard(RapportState rapport) {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Rapport Global', "Vue d'ensemble des données", Icons.bar_chart_outlined, 'blue'),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _label('Type de rapport'),
                DropdownButtonFormField<String>(
                  initialValue: _globalType,
                  items: const ['Global', 'Livres', 'Tissus', 'Fournitures', 'Arriéré']
                      .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                      .toList(),
                  onChanged: (v) => setState(() => _globalType = v ?? _globalType),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _label('Début'),
                          _dateField('Début', _globalDateDebut, (d) => _globalDateDebut = d),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _label('Fin'),
                          _dateField('Fin', _globalDateFin, (d) => _globalDateFin = d),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                Align(
                  alignment: Alignment.centerRight,
                  child: _printButton(
                    label: 'Imprimer',
                    loading: rapport.isPrintingGlobal,
                    onPressed: () => _run(() => rapport.printGlobalReport(
                          type: _globalType,
                          dateDebut: _globalDateDebut,
                          dateFin: _globalDateFin,
                        )),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Rapport Financier ───────────────────────────────────────────────
  Widget _buildFinancierCard(ReferenceDataState ref, ParametresState params, RapportState rapport) {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Rapports Financiers', 'Paiements et versements des élèves', Icons.payments_outlined, 'emerald'),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _label('Classe'),
                DropdownButtonFormField<String>(
                  initialValue: _financierClasse,
                  items: [
                    const DropdownMenuItem(value: _sentinelClasseAll, child: Text('Toutes les classes')),
                    ...ref.classes.map((c) => DropdownMenuItem(value: c.nomClasse, child: Text(c.nomClasse))),
                  ],
                  onChanged: (v) => setState(() => _financierClasse = v ?? _financierClasse),
                ),
                const SizedBox(height: 14),
                _label('Année académique'),
                DropdownButtonFormField<String>(
                  initialValue: _financierAnneeId,
                  items: params.annees
                      .map((a) => DropdownMenuItem(value: a.id, child: Text(a.anneeAcademique)))
                      .toList(),
                  onChanged: (v) => setState(() => _financierAnneeId = v),
                ),
                const SizedBox(height: 14),
                _label('Versement'),
                DropdownButtonFormField<String>(
                  initialValue: _financierVersement,
                  items: [
                    const DropdownMenuItem(
                        value: _sentinelTousLesVersements, child: Text('Tous les versements')),
                    ..._versementOptions.map((v) => DropdownMenuItem(value: v, child: Text(v))),
                  ],
                  onChanged: (v) => setState(() => _financierVersement = v ?? _financierVersement),
                ),
                if (_financierVersement != _sentinelTousLesVersements) ...[
                  const SizedBox(height: 14),
                  _label('Date de fin (filtre du versement)'),
                  _dateField('Fin', _financierDateFin, (d) => _financierDateFin = d),
                ],
                const SizedBox(height: 18),
                Align(
                  alignment: Alignment.centerRight,
                  child: _printButton(
                    label: 'Imprimer',
                    loading: rapport.isPrintingFinancier,
                    onPressed: _financierAnneeId == null
                        ? null
                        : () => _run(() => rapport.printFinancierReport(
                              classe: _financierClasse,
                              anneeAcademiqueId: _financierAnneeId!,
                              dateFin: _financierDateFin,
                              versement: _financierVersement,
                            )),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Rapport Pédagogique + Décision de fin d'année ──────────────────
  Widget _buildPedagogiqueCard(ReferenceDataState ref, ParametresState params, RapportState rapport) {
    final classesForCycle = ref.classesForNiveau(_pedagoCycle);
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Rapports Pédagogiques', 'Évaluations mensuelles et annuelles, et décision de fin d\'année',
              Icons.school_outlined, 'violet'),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                LayoutBuilder(builder: (context, constraints) {
                  final cols = constraints.maxWidth >= 760 ? 4 : (constraints.maxWidth >= 460 ? 2 : 1);
                  final fields = [
                    _pedagogiqueCycleField(ref),
                    _pedagogiqueClasseField(classesForCycle),
                    _pedagogiqueAnneeField(params),
                    _pedagogiqueMoisField(),
                  ];
                  return Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: fields
                        .map((f) => SizedBox(
                              width: (constraints.maxWidth - (cols - 1) * 12) / cols,
                              child: f,
                            ))
                        .toList(),
                  );
                }),
                const SizedBox(height: 16),
                Divider(color: AppColors.borderSubtle, height: 1),
                const SizedBox(height: 14),
                Align(
                  alignment: Alignment.centerRight,
                  child: _printButton(
                    label: 'Imprimer Bulletin Pédagogique',
                    loading: rapport.isPrintingPedagogique,
                    icon: Icons.school_outlined,
                    onPressed: (_pedagoCycle == null || _pedagoAnneeId == null)
                        ? null
                        : () => _run(() => rapport.printPedagogiqueReport(
                              identifiant: false,
                              classe: _pedagoClasse,
                              anneeAc: _pedagoAnneeId!,
                              cycle: _pedagoCycle!,
                              mois: _pedagoMois,
                            )),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  "DÉCISION DE FIN D'ANNÉE",
                  style: TextStyle(
                    fontSize: 11,
                    letterSpacing: 0.6,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textMuted,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Utilise la classe et l\'année académique sélectionnées ci-dessus (une classe précise doit être '
                  'choisie, "Toutes les classes" n\'est pas pris en charge ici).',
                  style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    _printButton(
                      label: 'Excel',
                      icon: Icons.grid_on_outlined,
                      loading: rapport.isPrintingDecision,
                      color: AppColors.cardPalette['emerald']!.bar,
                      onPressed: (_pedagoClasse == _sentinelToutesLesClasses || _pedagoAnneeId == null)
                          ? null
                          : () => _run(() => rapport.printDecisionFinAnnee(
                                classe: _pedagoClasse,
                                anneeAc: _pedagoAnneeId!,
                                isExcel: true,
                              )),
                    ),
                    const SizedBox(width: 10),
                    _printButton(
                      label: 'PDF',
                      loading: rapport.isPrintingDecision,
                      onPressed: (_pedagoClasse == _sentinelToutesLesClasses || _pedagoAnneeId == null)
                          ? null
                          : () => _run(() => rapport.printDecisionFinAnnee(
                                classe: _pedagoClasse,
                                anneeAc: _pedagoAnneeId!,
                                isExcel: false,
                              )),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _pedagogiqueCycleField(ReferenceDataState ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _label('Cycle'),
        DropdownButtonFormField<String>(
          initialValue: _pedagoCycle,
          items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
          onChanged: (v) => setState(() {
            _pedagoCycle = v;
            _pedagoClasse = _sentinelToutesLesClasses;
          }),
        ),
      ],
    );
  }

  Widget _pedagogiqueClasseField(List<Classe> classesForCycle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _label('Classe'),
        DropdownButtonFormField<String>(
          initialValue: _pedagoClasse,
          items: [
            const DropdownMenuItem(value: _sentinelToutesLesClasses, child: Text('Toutes les classes')),
            ...classesForCycle.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))),
          ],
          onChanged: (v) => setState(() => _pedagoClasse = v ?? _pedagoClasse),
        ),
      ],
    );
  }

  Widget _pedagogiqueAnneeField(ParametresState params) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _label('Année académique'),
        DropdownButtonFormField<String>(
          initialValue: _pedagoAnneeId,
          items:
              params.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.anneeAcademique))).toList(),
          onChanged: (v) => setState(() => _pedagoAnneeId = v),
        ),
      ],
    );
  }

  Widget _pedagogiqueMoisField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _label('Mois'),
        DropdownButtonFormField<String>(
          initialValue: _pedagoMois,
          items: [
            const DropdownMenuItem(value: _sentinelTousLesMois, child: Text('Tous les mois')),
            ..._moisOptions.map((m) => DropdownMenuItem(value: m, child: Text(m))),
          ],
          onChanged: (v) => setState(() => _pedagoMois = v ?? _pedagoMois),
        ),
      ],
    );
  }

  // ── Rapport Administratif / Registre ────────────────────────────────
  Widget _buildAdministratifCard(ReferenceDataState ref, ParametresState params, RapportState rapport) {
    final classesForCycle = ref.classesForNiveau(_adminCycle);
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Rapports Administratifs', 'Registres et présences', Icons.folder_open_outlined, 'amber'),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                LayoutBuilder(builder: (context, constraints) {
                  final twoCols = constraints.maxWidth >= 460;
                  Widget cycleField = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _label('Cycle'),
                      DropdownButtonFormField<String>(
                        initialValue: _adminCycle,
                        items: ref.niveaux.map((n) => DropdownMenuItem(value: n.id, child: Text(n.name))).toList(),
                        onChanged: (v) => setState(() {
                          _adminCycle = v;
                          _adminClasse = _sentinelToutesLesClasses;
                        }),
                      ),
                    ],
                  );
                  Widget classeField = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _label('Classe'),
                      DropdownButtonFormField<String>(
                        initialValue: _adminClasse,
                        items: [
                          const DropdownMenuItem(
                              value: _sentinelToutesLesClasses, child: Text('Toutes les classes')),
                          ...classesForCycle.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))),
                        ],
                        onChanged: (v) => setState(() => _adminClasse = v ?? _adminClasse),
                      ),
                    ],
                  );
                  if (!twoCols) {
                    return Column(children: [cycleField, const SizedBox(height: 12), classeField]);
                  }
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: cycleField),
                      const SizedBox(width: 12),
                      Expanded(child: classeField),
                    ],
                  );
                }),
                const SizedBox(height: 12),
                _label('Année académique'),
                DropdownButtonFormField<String>(
                  initialValue: _adminAnneeId,
                  items:
                      params.annees.map((a) => DropdownMenuItem(value: a.id, child: Text(a.anneeAcademique))).toList(),
                  onChanged: (v) => setState(() => _adminAnneeId = v),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Checkbox(
                      value: _adminIdentifiant,
                      onChanged: (v) => setState(() => _adminIdentifiant = v ?? true),
                    ),
                    Text('Avec identifiant', style: TextStyle(fontSize: 13, color: AppColors.textMuted)),
                    const Spacer(),
                    _printButton(
                      label: 'Imprimer Registre',
                      loading: rapport.isPrintingAdministratif,
                      icon: Icons.folder_open_outlined,
                      color: AppColors.cardPalette['amber']!.bar,
                      onPressed: (_adminCycle == null || _adminAnneeId == null)
                          ? null
                          : () => _run(() => rapport.printAdministratifReport(
                                identifiant: _adminIdentifiant,
                                classe: _adminClasse,
                                anneeAc: _adminAnneeId!,
                                cycle: _adminCycle!,
                              )),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                Divider(color: AppColors.borderSubtle, height: 1),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Container(
                      width: 4,
                      height: 11,
                      decoration: BoxDecoration(
                        color: AppColors.cardPalette['sky']!.bar.withValues(alpha: 0.6),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'PRÉSENCE DES ÉLÈVES',
                      style: TextStyle(
                        fontSize: 11,
                        letterSpacing: 0.6,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _label('Classe'),
                DropdownButtonFormField<String>(
                  initialValue: _presenceClasse,
                  items: [
                    const DropdownMenuItem(value: _sentinelClasseAll, child: Text('Toutes les classes')),
                    ...ref.classes.map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse))),
                  ],
                  onChanged: (v) => setState(() => _presenceClasse = v ?? _presenceClasse),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _label('Début'),
                          _dateField('Début', _presenceDateDebut, (d) => _presenceDateDebut = d),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _label('Fin'),
                          _dateField('Fin', _presenceDateFin, (d) => _presenceDateFin = d),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Align(
                  alignment: Alignment.centerRight,
                  child: _printButton(
                    label: 'Excel Présences',
                    icon: Icons.grid_on_outlined,
                    loading: rapport.isPrintingPresence,
                    color: AppColors.cardPalette['sky']!.bar,
                    onPressed: () => _run(() => rapport.printPresenceExcel(
                          classe: _presenceClasse,
                          dateDebut: _presenceDateDebut,
                          dateFin: _presenceDateFin,
                        )),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Reprend à l'identique le placeholder "Bientôt" de Rapport.vue : aucune
  /// route/modèle/schéma "disciplinaire" n'existe nulle part dans
  /// ecole_nginx (grep exhaustif sur Models/Schemas/Routes), donc rien de
  /// réel à brancher derrière — carte purement informative, sans action.
  Widget _buildDisciplinaireCard() {
    Widget comingSoonRow(String label) {
      return Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.02),
          border: Border.all(color: AppColors.borderSubtle),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: const BoxDecoration(color: Color(0xFF3D4D62), shape: BoxShape.circle),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(label, style: TextStyle(fontSize: 13, color: AppColors.textMuted)),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
                borderRadius: BorderRadius.circular(999),
              ),
              child: const Text(
                'Bientôt',
                style: TextStyle(fontSize: 10, fontWeight: FontWeight.w500, color: Color(0xFF3D4D62)),
              ),
            ),
          ],
        ),
      );
    }

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _cardHeader('Rapports Disciplinaires', 'Incidents, sanctions et comportements',
              Icons.report_problem_outlined, 'rose'),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                comingSoonRow('Rapport des incidents et sanctions'),
                comingSoonRow('Rapport du comportement des élèves'),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.05),
                    border: Border.all(color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.15)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.info_outline,
                          size: 16, color: AppColors.cardPalette['amber']!.text.withValues(alpha: 0.7)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Ces modules sont en attente de données disciplinaires.',
                          style: TextStyle(
                              fontSize: 11, color: AppColors.cardPalette['amber']!.text.withValues(alpha: 0.6)),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

extension _FirstOrNull<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
