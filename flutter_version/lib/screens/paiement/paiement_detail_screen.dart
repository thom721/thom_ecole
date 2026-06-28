import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/dual_auth.dart';
import '../../models/paiement.dart';
import '../../state/paiement_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';

/// Équivalent de DetaisPaiement.vue (ecole_nginx/frontend/src/views/admin) :
/// dossier de paiement déjà enregistré (récapitulatif des échéances +
/// historique des versements, avec actions "Retourner"/"Reçu") — distinct de
/// PaiementFormScreen, qui sert à ENREGISTRER un nouveau versement.
class PaiementDetailScreen extends StatefulWidget {
  const PaiementDetailScreen({
    super.key,
    required this.paiementId,
    required this.onBack,
  });

  final String paiementId;
  final VoidCallback onBack;

  @override
  State<PaiementDetailScreen> createState() => _PaiementDetailScreenState();
}

class _PaiementDetailScreenState extends State<PaiementDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PaiementState>().loadDetail(widget.paiementId);
    });
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
                icon: Icon(Icons.arrow_back, color: AppColors.textPrimary),
                onPressed: widget.onBack,
              ),
              const SizedBox(width: 4),
              const Expanded(
                child: SectionHeader(
                  title: 'Dossier de paiement',
                  subtitle: 'Récapitulatif et historique des versements',
                  icon: Icons.credit_card_outlined,
                  colorKey: 'emerald',
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.isLoadingDetail)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.detailError != null)
            Expanded(
              child: Center(
                child: Text(
                  state.detailError!,
                  style: TextStyle(color: AppColors.textPrimary),
                ),
              ),
            )
          else if (state.currentDetail == null)
            const Expanded(child: SizedBox.shrink())
          else
            Expanded(
              child: _buildContent(context, state, state.currentDetail!),
            ),
        ],
      ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    PaiementState state,
    PaymentDetail detail,
  ) {
    final etudiant = detail.detailsEtudiant;
    final global = detail.globalInfo;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.1),
                    border: Border.all(
                      color: AppColors.accent.withValues(alpha: 0.2),
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.credit_card, color: AppColors.accentLight),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'DOSSIER DE PAIEMENT',
                        style: TextStyle(
                          fontSize: 10,
                          letterSpacing: 1,
                          color: AppColors.textMuted,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.accent.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              etudiant['identifiant']?.toString() ?? '',
                              style: TextStyle(
                                color: AppColors.accentLight,
                                fontSize: 12,
                                fontFamily: 'monospace',
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            '${etudiant['prenom'] ?? ''} ${etudiant['nom'] ?? ''}',
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                if (global != null && global.totalAnnuel > 0)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        'TOTAL ANNUEL',
                        style: TextStyle(
                          fontSize: 10,
                          letterSpacing: 1,
                          color: AppColors.textMuted,
                        ),
                      ),
                      Text(
                        '${global.totalAnnuel} ${global.devise}',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (global.aideFinanciere.isNotEmpty)
                        Container(
                          margin: const EdgeInsets.only(top: 4),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.cardPalette['purple']!.bar
                                .withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            global.aideFinanciere,
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.cardPalette['purple']!.text,
                            ),
                          ),
                        ),
                    ],
                  ),
              ],
            ),
          ),
          if (detail.checkEcheance.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildRecap(detail),
          ],
          const SizedBox(height: 16),
          Text(
            'HISTORIQUE DES VERSEMENTS',
            style: TextStyle(
              fontSize: 11,
              letterSpacing: 1,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          if (detail.versements.isEmpty)
            Padding(
              padding: EdgeInsets.symmetric(vertical: 30),
              child: Center(
                child: Text(
                  'Aucun paiement enregistré.',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ),
            )
          else
            ...detail.versements.map(
              (v) => _VersementCard(detail: detail, versement: v, state: state),
            ),
        ],
      ),
    );
  }

  Widget _buildRecap(PaymentDetail detail) {
    final entries = detail.checkEcheance.entries.toList();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.panelBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'RÉCAPITULATIF DES VERSEMENTS',
            style: TextStyle(
              fontSize: 10,
              letterSpacing: 1,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: List.generate(entries.length, (idx) {
              final label = entries[idx].key;
              final montant = entries[idx].value;
              final status = detail.versementStatusLabel(idx + 1);
              final color = _statusColor(status);
              return Container(
                width: 170,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.05),
                  border: Border.all(color: color.withValues(alpha: 0.25)),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            label,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.textMuted,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 1,
                          ),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            status,
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                              color: color,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '$montant',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  static Color _statusColor(String status) {
    switch (status) {
      case 'Acquitte':
        return AppColors.cardPalette['emerald']!.text;
      case 'Avance':
        return AppColors.cardPalette['amber']!.text;
      case 'Retourne':
        return AppColors.danger;
      default:
        return AppColors.textMuted;
    }
  }
}

class _VersementCard extends StatelessWidget {
  const _VersementCard({
    required this.detail,
    required this.versement,
    required this.state,
  });

  final PaymentDetail detail;
  final VersementInfo versement;
  final PaiementState state;

  @override
  Widget build(BuildContext context) {
    // Pas de filtre de rôle ici : le backend (DualAuthChecker) décide seul —
    // un rôle sans la permission "Supprimer paiement" reçoit un 202 et doit
    // faire approuver l'action via le PIN d'un admin/Comptable (voir
    // _confirmReturn ci-dessous et lib/core/dual_auth.dart).
    final isLastPayment = versement.dateKey == detail.lastNonReturnedKey;
    final borderColor = versement.isRetourne
        ? AppColors.danger.withValues(alpha: 0.2)
        : versement.isFinalAcquitte
        ? AppColors.cardPalette['emerald']!.text.withValues(alpha: 0.15)
        : AppColors.borderSubtle;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: AppColors.appBg,
              border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              children: [
                Container(
                  width: 22,
                  height: 22,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color:
                        (versement.isRetourne
                                ? AppColors.danger
                                : AppColors.cardPalette['emerald']!.text)
                            .withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '${versement.index + 1}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: versement.isRetourne
                          ? AppColors.danger
                          : AppColors.cardPalette['emerald']!.text,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  versement.dateKey,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                    fontFamily: 'monospace',
                  ),
                ),
                const SizedBox(width: 10),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    versement.versementLabel,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.accentLight,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const Spacer(),
                if (versement.aideFinanciere.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(right: 6),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.cardPalette['purple']!.bar.withValues(
                        alpha: 0.12,
                      ),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      versement.aideFinanciere,
                      style: TextStyle(
                        fontSize: 10,
                        color: AppColors.cardPalette['purple']!.text,
                      ),
                    ),
                  ),
                _StatusBadge(
                  label: versement.isRetourne
                      ? 'Retourné'
                      : (versement.isFinalAcquitte ? 'Acquitté' : 'Validé'),
                  color: versement.isRetourne
                      ? AppColors.danger
                      : AppColors.cardPalette['emerald']!.text,
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 16,
                  runSpacing: 6,
                  children: [
                    if (versement.employer.isNotEmpty)
                      _LabelValue('Caissier', versement.employer),
                    if (versement.editBy.isNotEmpty &&
                        versement.editBy != versement.employer)
                      _LabelValue('Modifié par', versement.editBy),
                    _LabelValue(
                      'Cumul versé',
                      '${versement.totalVerse} ${versement.devise}',
                      valueColor: AppColors.accentLight,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildTable(),
                if (versement.statusPaiement.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: versement.statusPaiement.map((sp) {
                      final isAcqt = sp.startsWith('Acqt:');
                      final color = isAcqt
                          ? AppColors.cardPalette['emerald']!.text
                          : AppColors.cardPalette['amber']!.text;
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 5,
                        ),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.1),
                          border: Border.all(
                            color: color.withValues(alpha: 0.2),
                          ),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${isAcqt ? 'Acquitté' : 'Avance sur'} : ${sp.replaceFirst('Acqt: ', '').replaceFirst('Avns: ', '')}',
                          style: TextStyle(
                            fontSize: 11,
                            color: color,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
                if (versement.avanceVal > 0 &&
                    !versement.hasVersementKey(versement.versementNum) &&
                    detail.versementStatusMap[versement.versementNum] !=
                        'acquitte') ...[
                  const SizedBox(height: 10),
                  _Alert(
                    color: AppColors.cardPalette['amber']!.text,
                    icon: Icons.warning_amber_rounded,
                    text:
                        'Avance de ${versement.avanceVal} ${versement.devise} — reportée comme avance sur ${versement.versementLabel}.',
                  ),
                ],
                if (versement.isRetourne &&
                    (versement.details['return_by']?.toString().isNotEmpty ??
                        false)) ...[
                  const SizedBox(height: 10),
                  _Alert(
                    color: AppColors.danger,
                    icon: Icons.undo,
                    text: [
                      'Retourné par ${versement.details['return_by']}',
                      if ((versement.details['authorized_by']
                              ?.toString()
                              .isNotEmpty ??
                          false))
                        'Autorisé par ${versement.details['authorized_by']}',
                      if ((versement.details['commentaire']
                              ?.toString()
                              .isNotEmpty ??
                          false))
                        'Raison : ${versement.details['commentaire']}',
                    ].join(' — '),
                  ),
                ],
                if (versement.remise > 0) ...[
                  const SizedBox(height: 10),
                  _Alert(
                    color: AppColors.cardPalette['purple']!.text,
                    icon: Icons.local_offer_outlined,
                    text:
                        'Remise accordée de ${versement.remise} ${versement.devise}',
                  ),
                ],
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: AppColors.borderSubtle)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (isLastPayment && !versement.isRetourne)
                  TextButton.icon(
                    onPressed: state.returningKey == versement.dateKey
                        ? null
                        : () => _confirmReturn(context),
                    icon: state.returningKey == versement.dateKey
                        ? const SizedBox(
                            height: 14,
                            width: 14,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.undo, size: 16),
                    label: const Text('Retourner'),
                    style: TextButton.styleFrom(
                      foregroundColor: AppColors.danger,
                    ),
                  ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: state.printingKey == versement.index.toString()
                      ? null
                      : () => _printRecu(context),
                  icon: state.printingKey == versement.index.toString()
                      ? const SizedBox(
                          height: 14,
                          width: 14,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.receipt_long_outlined, size: 16),
                  label: const Text('Reçu'),
                  style: TextButton.styleFrom(
                    foregroundColor: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _printRecu(BuildContext context) async {
    // GeneratePDFRecuRequest.key (paiement_recu.py:20) est un INDEX entier
    // dans la liste triée chronologiquement (info_items[request.key]), pas
    // la clé date elle-même — contrairement à `index` côté Returns.py
    // (DeletePaiementRequest), qui lui attend bien la clé date brute. Passer
    // `versement.dateKey` ici échouait la validation Pydantic (422) à chaque
    // appel, masqué jusqu'ici par le bug de décodage des réponses en octets
    // (voir _extractError).
    final error = await state.printRecu(detail.id, versement.index.toString());
    if (!context.mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  Future<void> _confirmReturn(BuildContext context) async {
    final raison = await showReasonDialog(
      context: context,
      title: 'Retourner ce paiement ?',
      message:
          'Cette action est irréversible. Le paiement sera marqué comme retourné. Indiquez la raison du retour.',
      confirmLabel: 'Oui, retourner',
    );
    if (raison == null) return;
    if (!context.mounted) return;
    final error = await runWithPinApproval(
      context: context,
      permission: 'Supprimer paiement',
      action: ({approvalToken}) => state.returnPaiement(
        detail.id,
        versement.dateKey,
        raison: raison,
        approvalToken: approvalToken,
      ),
    );
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(error ?? 'Paiement retourné avec succès.')),
    );
  }

  Widget _buildTable() {
    final hasRemise = versement.remise > 0;
    final balanceDisplayed = versement.hasVersementKey(versement.index + 1)
        ? 0
        : versement.balance;
    final balanceColor = versement.balance > 0
        ? AppColors.danger
        : (versement.balance == 0 && versement.isFinalAcquitte)
        ? AppColors.cardPalette['emerald']!.text
        : AppColors.textMuted;

    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Table(
        columnWidths: const {
          0: FlexColumnWidth(1.3),
          1: FlexColumnWidth(1),
          2: FlexColumnWidth(1),
          3: FlexColumnWidth(1),
          4: FlexColumnWidth(1),
        },
        children: [
          TableRow(
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.borderSubtle)),
            ),
            children: [
              _th('VERSEMENT'),
              _th('MONTANT DÛ'),
              _th('DÉPOSÉ'),
              _th('AVANCE'),
              if (hasRemise) _th('REMISE') else _th('BALANCE'),
            ],
          ),
          TableRow(
            children: [
              _td(
                Text(
                  versement.versementLabel,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.accentLight,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              _td(_amount('${versement.montantDu}', versement.devise)),
              _td(_amount('${versement.depot}', versement.devise)),
              _td(
                versement.avanceVal > 0 &&
                        !versement.hasVersementKey(versement.versementNum) &&
                        detail.versementStatusMap[versement.versementNum] !=
                            'acquitte'
                    ? _amount(
                        '${versement.avanceVal}',
                        versement.devise,
                        color: AppColors.cardPalette['amber']!.text,
                      )
                    : Text('--', style: TextStyle(color: AppColors.textMuted)),
              ),
              _td(
                hasRemise
                    ? _amount(
                        '${versement.remise}',
                        versement.devise,
                        color: AppColors.cardPalette['purple']!.text,
                      )
                    : _amount(
                        '$balanceDisplayed',
                        versement.devise,
                        color: balanceColor,
                      ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _th(String label) => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
    child: Text(
      label,
      style: TextStyle(
        fontSize: 9.5,
        letterSpacing: 0.5,
        color: AppColors.textMuted,
        fontWeight: FontWeight.w700,
      ),
    ),
  );

  Widget _td(Widget child) => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
    child: child,
  );

  Widget _amount(String value, String devise, {Color? color}) {
    return RichText(
      text: TextSpan(
        children: [
          TextSpan(
            text: value,
            style: TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w700,
              color: color ?? AppColors.textPrimary,
            ),
          ),
          TextSpan(
            text: ' $devise',
            style: TextStyle(fontSize: 10.5, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.2)),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _LabelValue extends StatelessWidget {
  const _LabelValue(this.label, this.value, {this.valueColor});

  final String label;
  final String value;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label  ',
          style: TextStyle(fontSize: 12, color: AppColors.textMuted),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: valueColor ?? AppColors.textPrimary,
          ),
        ),
      ],
    );
  }
}

class _Alert extends StatelessWidget {
  const _Alert({required this.color, required this.icon, required this.text});

  final Color color;
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        border: Border.all(color: color.withValues(alpha: 0.2)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 15, color: color),
          const SizedBox(width: 8),
          Expanded(
            child: Text(text, style: TextStyle(fontSize: 12, color: color)),
          ),
        ],
      ),
    );
  }
}
