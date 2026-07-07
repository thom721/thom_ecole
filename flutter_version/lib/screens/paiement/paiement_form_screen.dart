import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/paiement.dart';
import '../../state/auth_state.dart';
import '../../state/paiement_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';

/// Équivalent du formulaire de paiement dynamique construit dans
/// Controllers/Main.py (lignes ~12700-13095, fonction non nommée appelée
/// après réception de next-payment-step, + valider_paiement()) :
/// - une ligne par échéance ("1er Versement - (montant devise)" ou nom du
///   mois), cochée/grisée si déjà payée — purement informatif, le serveur
///   alloue automatiquement le dépôt à la prochaine échéance non réglée
///   (voir payment_save_info(), RSavePaiement.py:232+) ;
/// - des cases accessoires (Maillot/Badge/Tenue de Sport/Initiale),
///   cochées/désactivées si déjà payées ;
/// - un champ "Montant versé" + bouton "Valider" → POST v1/post-payment-save ;
/// - une colonne de gauche (2/5) listant TOUTES les années académiques de
///   l'étudiant (AddPaiement.vue), pour les arriérés sur une année passée,
///   sous un en-tête fixe (avatar/identifiant/nom/classe — pris sur la
///   DERNIÈRE année, comme `firstInfo` côté Vue, qui ne change jamais
///   quand on clique sur une autre année) — PAS de panneau "historique des
///   versements" séparé, la vraie page web n'en affiche aucun ici.
///
/// Non repris dans cette première version (hors-scope, à faire dans un
/// prochain passage) : impression du reçu PDF (POST v1/print-recu), édition
/// du dernier paiement (index_paiement), et le recalcul visuel détaillé des
/// montants par palier de bourse (Bourse/1/4 Bourse/Démie Bourse) — le
/// serveur calcule déjà ces montants, on affiche tel quel ce qu'il renvoie.
class PaiementFormScreen extends StatefulWidget {
  const PaiementFormScreen({
    super.key,
    required this.etudiantId,
    required this.onBack,
  });

  final String etudiantId;
  final VoidCallback onBack;

  @override
  State<PaiementFormScreen> createState() => _PaiementFormScreenState();
}

class _PaiementFormScreenState extends State<PaiementFormScreen> {
  final _montantController = TextEditingController();
  final Map<String, bool> _moisCoches = {};
  final Map<String, bool> _accessoiresCoches = {};
  bool _submitting = false;
  String? _submitError;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final state = context.read<PaiementState>();
    await state.loadPaymentInfo(widget.etudiantId);
    _syncChecksFromCurrentInfo(state);
  }

  /// Rechargement déclenché par un clic sur une autre année (colonne de
  /// gauche) : il faut ré-initialiser les cases cochées pour refléter les
  /// échéances déjà payées de CETTE année, sinon les coches de l'année
  /// précédente restent affichées par erreur.
  Future<void> _selectYear(int index) async {
    final state = context.read<PaiementState>();
    await state.selectYear(index);
    _syncChecksFromCurrentInfo(state);
  }

  void _syncChecksFromCurrentInfo(PaiementState state) {
    final info = state.currentInfo;
    if (info == null || !mounted) return;
    setState(() {
      _moisCoches.clear();
      _accessoiresCoches.clear();
      for (final row in info.echeanceRows) {
        if (row.paid) _moisCoches[row.key] = true;
      }
    });
  }

  @override
  void dispose() {
    _montantController.dispose();
    super.dispose();
  }

  /// True si le montant actuellement saisi est >= au solde restant dû —
  /// avertit avant validation plutôt que de bloquer (le serveur alloue de
  /// toute façon l'excédent, voir payment_save_info()).
  bool _montantDepasseSolde(PaymentInfo info) {
    final solde = info.soldeRestant;
    if (solde == null || solde <= 0) return false;
    final montant = double.tryParse(
      _montantController.text.replaceAll(',', '.'),
    );
    if (montant == null || montant <= 0) return false;
    return montant >= solde;
  }

  Future<void> _submit() async {
    final montant = double.tryParse(
      _montantController.text.replaceAll(',', '.'),
    );
    if (montant == null || montant <= 0) {
      setState(() => _submitError = 'Veuillez saisir un montant valide.');
      return;
    }
    setState(() {
      _submitting = true;
      _submitError = null;
    });
    final error = await context.read<PaiementState>().submitPayment(
      montantVerse: montant,
      moisCoches: _moisCoches,
      accessoiresCoches: _accessoiresCoches,
    );
    if (!mounted) return;
    setState(() => _submitting = false);
    if (error != null) {
      setState(() => _submitError = error);
      return;
    }
    _montantController.clear();
    // Impression automatique du reçu après enregistrement réussi — sautée
    // silencieusement si l'utilisateur n'a pas la permission "Imprimer
    // paiement" (l'API la refuserait de toute façon, RAcademic.py côté
    // serveur ; pas la peine d'afficher une erreur pour un effet
    // automatique, contrairement à un clic délibéré sur "Reçu").
    final state = context.read<PaiementState>();
    final receiptId = state.lastReceiptId;
    final receiptKey = state.lastReceiptKey;
    final canPrint = context.read<AuthState>().permissions.contains('Imprimer paiement');
    if (receiptId != null && receiptKey != null && canPrint) {
      final printError = await state.printRecu(receiptId, receiptKey.toString());
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            printError != null
                ? 'Paiement enregistré. Reçu : $printError'
                : 'Paiement enregistré. Reçu imprimé.',
          ),
        ),
      );
    } else if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Paiement enregistré.')));
    }
  }

  Future<void> _verifierStatut(PaiementState state) async {
    final error = await state.verifierStatut();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          error ?? "Statut vérifié — échéances et récapitulatif mis à jour avec l'aide financière actuelle.",
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PaiementState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              IconButton(
                icon: Icon(
                  Icons.arrow_back,
                  color: AppColors.textPrimary,
                ),
                onPressed: widget.onBack,
              ),
              const SizedBox(width: 4),
              const Expanded(
                child: SectionHeader(
                  title: 'Enregistrer un paiement',
                  subtitle: "Versement d'écolage pour un étudiant",
                  icon: Icons.credit_card_outlined,
                  colorKey: 'emerald',
                ),
              ),
            ],
          ),
          if (state.studentYears.isNotEmpty) _buildProfileHeader(state.studentYears.last),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (state.studentYears.isNotEmpty) ...[
                  Expanded(flex: 2, child: _buildYearList(state)),
                  const SizedBox(width: 24),
                ],
                Expanded(flex: 3, child: _buildRightPanel(state)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Équivalent du bloc `v-if="firstInfo"` en haut de AddPaiement.vue —
  /// fixe, ne change pas quand on clique sur une autre année.
  Widget _buildProfileHeader(StudentPaymentContext ctx) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 36,
                backgroundColor: AppColors.panelBg,
                child: Icon(Icons.person, size: 36, color: AppColors.textMuted),
              ),
              const SizedBox(width: 24),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    ctx.identifiant,
                    style: TextStyle(fontSize: 22, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${ctx.nom} ${ctx.prenom}',
                    style: TextStyle(fontSize: 15, color: AppColors.textMuted),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.accent.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      ctx.nomClasse,
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.accentLight),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 20),
          Divider(color: AppColors.borderSubtle, height: 1),
        ],
      ),
    );
  }

  /// Colonne de gauche (2/5 de la largeur) : toutes les années académiques
  /// de l'étudiant (AddPaiement.vue : `<aside class="w-2/5 ...
  /// overflow-y-auto">`) — un élève peut avoir un arriéré sur une année
  /// passée, donc on ne montre pas QUE l'année active.
  Widget _buildYearList(PaiementState state) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxHeight: 500),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (var i = 0; i < state.studentYears.length; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _YearButton(
                  label: state.studentYears[i].anneeAcademique,
                  selected: state.selectedYearIndex == i,
                  loading: state.isLoadingInfo && state.selectedYearIndex == i,
                  onTap: () => _selectYear(i),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildRightPanel(PaiementState state) {
    if (state.isLoadingInfo) {
      return const Center(child: CircularProgressIndicator());
    }
    if (state.infoError != null) {
      return Center(
        child: Text(
          state.infoError!,
          style: TextStyle(color: AppColors.textPrimary),
        ),
      );
    }
    if (state.currentInfo == null) {
      return Center(
        child: Text(
          'Aucune information de paiement à afficher.',
          style: TextStyle(color: AppColors.textMuted),
        ),
      );
    }
    return _buildContent(state.currentInfo!);
  }

  /// Pas de panneau "historique des versements" ici : la vraie page web
  /// (AddPaiement.vue) n'affiche QUE la colonne des années à gauche (2/5) +
  /// la carte "Paiement : `<année>`" (3/5), rien d'autre à droite.
  Widget _buildContent(PaymentInfo info) {
    return SingleChildScrollView(child: _buildPaymentCard(info));
  }

  Widget _buildPaymentCard(PaymentInfo info) {
    final state = context.read<PaiementState>();
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Équivalent de `<h3>Paiement : {{ année }}</h3>` — le nom/
          // identifiant de l'étudiant est déjà affiché une fois dans
          // _buildProfileHeader(), pas répété ici.
          Text(
            'Paiement : ${info.anneeAcademique}',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          if (info.statutModifie) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.cardPalette['blue']!.text.withValues(alpha: 0.1),
                border: Border.all(
                  color: AppColors.cardPalette['blue']!.text.withValues(alpha: 0.2),
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Le statut de cet élève a été modifié depuis son dernier paiement '
                    '(aide financière). Vérifiez le montant avant de valider.',
                    style: TextStyle(fontSize: 12, color: AppColors.cardPalette['blue']!.text),
                  ),
                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerRight,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.cardPalette['blue']!.text,
                        side: BorderSide(color: AppColors.cardPalette['blue']!.text),
                        minimumSize: const Size(0, 32),
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                      ),
                      onPressed: state.isVerifying || state.selectedYearIndex == null
                          ? null
                          : () => _verifierStatut(state),
                      child: state.isVerifying
                          ? const SizedBox(
                              height: 14,
                              width: 14,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Vérifier'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
          ],
          if (info.aideFinanciere != 'Aucune') ...[
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: AppColors.cardPalette['amber']!.bar.withValues(
                  alpha: 0.12,
                ),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                'Aide financière : ${info.aideFinanciere}',
                style: TextStyle(
                  fontSize: 11,
                  color: AppColors.cardPalette['amber']!.text,
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
          if (info.acquitte)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.cardPalette['emerald']!.text.withValues(alpha: 0.1),
                border: Border.all(
                  color: AppColors.cardPalette['emerald']!.text.withValues(alpha: 0.2),
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '✓ Acquitté — paiement complet',
                style: TextStyle(fontSize: 13, color: AppColors.cardPalette['emerald']!.text),
              ),
            )
          else if (info.avanceSurLabel != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.cardPalette['amber']!.text.withValues(alpha: 0.1),
                border: Border.all(
                  color: AppColors.cardPalette['amber']!.text.withValues(alpha: 0.2),
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                info.avanceSurLabel!,
                style: TextStyle(fontSize: 13, color: AppColors.cardPalette['amber']!.text),
              ),
            ),
          const SizedBox(height: 18),
          Text(
            'ÉCHÉANCES',
            style: TextStyle(
              fontSize: 11,
              letterSpacing: 1,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          ...info.echeanceRows.map(
            (row) => _EcheanceTile(
              row: row,
              checked: _moisCoches[row.key] ?? false,
              onChanged: row.paid
                  ? null
                  : (v) => setState(() => _moisCoches[row.key] = v ?? false),
            ),
          ),
          if (info.accessoires.isNotEmpty) ...[
            const SizedBox(height: 18),
            Text(
              'ACCESSOIRES',
              style: TextStyle(
                fontSize: 11,
                letterSpacing: 1,
                color: AppColors.textMuted,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            ...info.accessoires.map(
              (a) => _AccessoireTile(
                accessoire: a,
                checked: _accessoiresCoches[a.typeDaccessoire] ?? false,
                onChanged: (v) => setState(
                  () => _accessoiresCoches[a.typeDaccessoire] = v ?? false,
                ),
              ),
            ),
          ],
          Divider(height: 32, color: AppColors.borderSubtle),
          Text(
            'MONTANT VERSÉ',
            style: TextStyle(
              fontSize: 11,
              letterSpacing: 1,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _montantController,
            enabled: !info.acquitte,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            style: TextStyle(color: AppColors.textPrimary, fontSize: 16),
            decoration: InputDecoration(
              hintText: '0.00',
              suffixText: info.devise,
              suffixStyle: TextStyle(color: AppColors.textMuted),
            ),
            onChanged: (_) => setState(() {}),
            onSubmitted: (_) => _submit(),
          ),
          if (_montantDepasseSolde(info)) ...[
            const SizedBox(height: 10),
            Text(
              'Ce montant dépasse ce que l\'étudiant doit encore '
              '(solde restant : ${info.soldeRestant} ${info.devise}).',
              style: TextStyle(color: AppColors.cardPalette['amber']!.text, fontSize: 12),
            ),
          ],
          if (_submitError != null) ...[
            const SizedBox(height: 10),
            Text(
              _submitError!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          const SizedBox(height: 16),
          SizedBox(
            height: 46,
            child: FilledButton(
              onPressed: (_submitting || info.acquitte) ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(info.acquitte ? 'Déjà acquitté' : 'Valider'),
            ),
          ),
        ],
      ),
    );
  }

}

/// Bouton d'année dans la colonne de gauche (PaymentByComponents.vue) —
/// bordure bleue + texte bleu quand sélectionné, sinon neutre.
class _YearButton extends StatelessWidget {
  const _YearButton({
    required this.label,
    required this.selected,
    required this.loading,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final bool loading;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: selected
          ? AppColors.cardPalette['blue']!.bar.withValues(alpha: 0.1)
          : AppColors.cardBg,
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected
                  ? AppColors.cardPalette['blue']!.text
                  : AppColors.borderSubtle,
            ),
          ),
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: selected
                      ? AppColors.cardPalette['blue']!.text
                      : AppColors.textMuted,
                ),
              ),
              if (loading) ...[
                const SizedBox(width: 8),
                const SizedBox(
                  height: 12,
                  width: 12,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _EcheanceTile extends StatelessWidget {
  const _EcheanceTile({
    required this.row,
    required this.checked,
    required this.onChanged,
  });

  final EcheanceRow row;
  final bool checked;
  final ValueChanged<bool?>? onChanged;

  @override
  Widget build(BuildContext context) {
    final paidColor = AppColors.cardPalette['emerald']!.text;
    return Opacity(
      opacity: row.paid ? 0.55 : 1,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(
          children: [
            Expanded(
              child: RichText(
                text: TextSpan(
                  text: row.label,
                  style: TextStyle(
                    fontSize: 13,
                    color: row.paid ? paidColor : AppColors.textPrimary,
                  ),
                  children: row.paid
                      ? [
                          TextSpan(
                            text: '  ✓ payé',
                            style: TextStyle(fontSize: 11, color: paidColor),
                          ),
                        ]
                      : null,
                ),
              ),
            ),
            Checkbox(
              value: checked,
              onChanged: onChanged,
              activeColor: paidColor,
              fillColor: row.paid
                  ? WidgetStatePropertyAll(paidColor)
                  : null,
              checkColor: Colors.white,
            ),
          ],
        ),
      ),
    );
  }
}

class _AccessoireTile extends StatelessWidget {
  const _AccessoireTile({
    required this.accessoire,
    required this.checked,
    required this.onChanged,
  });

  final Accessoire accessoire;
  final bool checked;
  final ValueChanged<bool?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(
            child: Text(
              '${accessoire.typeDaccessoire} (${accessoire.prix.toStringAsFixed(0)})',
              style: TextStyle(
                fontSize: 13,
                color: AppColors.textPrimary,
              ),
            ),
          ),
          Checkbox(value: checked, onChanged: onChanged),
        ],
      ),
    );
  }
}

