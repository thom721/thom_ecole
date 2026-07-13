import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/dual_auth.dart';
import '../../models/annulation_arriere.dart';
import '../../models/paiement.dart';
import '../../state/annulation_arriere_state.dart';
import '../../state/auth_state.dart';
import '../../state/role_permission_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/param_dialog.dart';

/// Dérogation manuelle et réversible au blocage d'arriéré d'une année
/// précédente (voir RSavePaiement.py:_check_arrears_previous_year côté
/// backend) — miroir du même écran côté web (Paiements.vue). Affiche
/// l'attestation + case à cocher obligatoire, puis le formulaire (ordonné
/// par / montant / raison), ou le résumé + révocation si une dérogation
/// est déjà active pour ce paiement.
Future<void> showDerogationArriereDialog(
  BuildContext context,
  PaymentListItem paiement,
) {
  return showDialog(
    context: context,
    builder: (_) => _DerogationArriereDialog(paiement: paiement),
  );
}

class _DerogationArriereDialog extends StatefulWidget {
  const _DerogationArriereDialog({required this.paiement});

  final PaymentListItem paiement;

  @override
  State<_DerogationArriereDialog> createState() => _DerogationArriereDialogState();
}

class _DerogationArriereDialogState extends State<_DerogationArriereDialog> {
  bool _isLoading = true;
  AnnulationArriere? _existing;
  double? _soldeRestant;
  String? _devise;

  bool _accepteContrat = false;
  final _ordonneParController = TextEditingController();
  String? _ordonneParFonction;
  final _montantController = TextEditingController();
  final _raisonController = TextEditingController();
  String _typeAnnulation = 'total';
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  @override
  void dispose() {
    _ordonneParController.dispose();
    _montantController.dispose();
    _raisonController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final rolesState = context.read<RolePermissionState>();
    final futures = <Future>[
      context.read<AnnulationArriereState>().fetchContext(widget.paiement.id),
      if (rolesState.roles.isEmpty) rolesState.loadLists(),
    ];
    final results = await Future.wait(futures);
    if (!mounted) return;
    final ctx = results.first as ({double? soldeRestant, String? devise, AnnulationArriere? existing});
    setState(() {
      _existing = ctx.existing;
      _soldeRestant = ctx.soldeRestant;
      _devise = ctx.devise;
      _isLoading = false;
    });
  }

  Future<void> _submit() async {
    if (!_accepteContrat) return;
    if (_ordonneParController.text.trim().isEmpty || (_ordonneParFonction ?? '').isEmpty) {
      setState(() => _error = "Le nom et la fonction de l'ordonnateur sont requis.");
      return;
    }
    final raison = _raisonController.text.trim();
    if (raison.length < 20 || raison.length > 150) {
      setState(() => _error = 'La raison doit contenir entre 20 et 150 caractères.');
      return;
    }
    double? montant;
    if (_typeAnnulation == 'partiel') {
      montant = double.tryParse(_montantController.text.replaceAll(',', '.'));
      if (montant == null || montant <= 0) {
        setState(() => _error = 'Indiquez un montant valide.');
        return;
      }
    }

    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppColors.panelBg,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Confirmer la dérogation', style: TextStyle(color: AppColors.textPrimary)),
        content: Text(
          "Cette action lève le blocage d'arriéré pour cet étudiant sur cette année. Elle reste réversible.",
          style: TextStyle(color: AppColors.textMuted),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Oui, accorder la dérogation'),
          ),
        ],
      ),
    );
    if (confirm != true || !mounted) return;

    setState(() => _error = null);
    final error = await context.read<AnnulationArriereState>().creer(
      paiementId: widget.paiement.id,
      typeAnnulation: _typeAnnulation,
      montantAnnule: montant,
      ordonnePar: _ordonneParController.text.trim(),
      ordonneParFonction: _ordonneParFonction ?? '',
      raison: raison,
      contratAccepte: _accepteContrat,
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
      return;
    }
    Navigator.of(context).pop();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Dérogation accordée.')),
    );
  }

  Future<void> _revoke() async {
    final raison = await showReasonDialog(
      context: context,
      title: 'Révoquer cette dérogation ?',
      message: "Le blocage d'arriéré sera rétabli pour cet étudiant sur cette année.",
      confirmLabel: 'Oui, révoquer',
    );
    if (raison == null || !mounted) return;

    final error = await context.read<AnnulationArriereState>().revoquer(
      annulationId: _existing!.id,
      raison: raison,
    );
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
      return;
    }
    Navigator.of(context).pop();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Dérogation révoquée.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final annulationState = context.watch<AnnulationArriereState>();
    final executantName = context.watch<AuthState>().user?.email ?? '';

    return ParamDialogShell(
      title: "Dérogation d'arriéré — ${widget.paiement.nom} ${widget.paiement.prenom} (${widget.paiement.annee})",
      width: 620,
      child: _isLoading
          ? const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(child: CircularProgressIndicator()),
            )
          : _existing != null
              ? _buildExisting(annulationState)
              : _buildForm(annulationState, executantName),
    );
  }

  Widget _buildExisting(AnnulationArriereState state) {
    final existing = _existing!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.1),
            border: Border.all(color: AppColors.cardPalette['amber']!.bar.withValues(alpha: 0.25)),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Dérogation active pour ${existing.anneeAcademique}',
                  style: TextStyle(fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
              const SizedBox(height: 6),
              Text(
                'Montant annulé : ${existing.montantAnnule} GDES (${existing.typeAnnulation})\n'
                'Ordonné par : ${existing.ordonnePar} (${existing.ordonneParFonction})\n'
                "Exécuté par : ${existing.executantNom}${existing.executantRole != null ? ' — ${existing.executantRole}' : ''}\n"
                'Motif : ${existing.raison}',
                style: TextStyle(fontSize: 12.5, color: AppColors.textMuted),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
              onPressed: state.isSubmitting ? null : _revoke,
              child: state.isSubmitting
                  ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Révoquer la dérogation'),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildForm(AnnulationArriereState state, String executantName) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppColors.danger.withValues(alpha: 0.1),
            border: Border.all(color: AppColors.danger.withValues(alpha: 0.25)),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            _soldeRestant != null
                ? 'Solde restant dû pour ${widget.paiement.annee} : $_soldeRestant ${_devise ?? ''}'
                : 'Solde restant non déterminable automatiquement — utilisez un montant précis.',
            style: TextStyle(fontSize: 13, color: AppColors.textPrimary, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: 10),
        Container(
          constraints: const BoxConstraints(maxHeight: 220),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.appBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(10),
          ),
          child: SingleChildScrollView(
            child: Text.rich(
              TextSpan(
                style: TextStyle(fontSize: 12, height: 1.5, color: AppColors.textMuted),
                children: [
                  const TextSpan(
                    text: "ATTESTATION D'ANNULATION D'ARRIÉRÉ DE PAIEMENT\n\n",
                    style: TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(
                    text: 'Je soussigné(e) $executantName, certifie procéder à l\'annulation du solde impayé '
                        "de l'année académique ${widget.paiement.annee} pour l'étudiant "
                        '${widget.paiement.nom} ${widget.paiement.prenom}, sur instruction expresse de '
                        "${_ordonneParController.text.trim().isEmpty ? '…' : _ordonneParController.text.trim()}, "
                        'en sa qualité de '
                        "${_ordonneParFonction ?? '…'}.\n\n"
                        'Je reconnais que cette action :\n'
                        "• permet à l'étudiant de régler ses paiements de l'année en cours sans que le solde "
                        "de l'année précédente ne soit exigé au préalable ;\n"
                        "• n'efface pas la dette dans les registres : elle est enregistrée comme une dérogation, "
                        'horodatée et nominative ;\n'
                        '• reste réversible à tout moment par une personne autorisée, ce qui rétablira '
                        "l'obligation de règlement ;\n"
                        '• sera intégrée au rapport financier (personne ayant ordonné, personne ayant exécuté, '
                        'montant, motif).\n\n'
                        'En cochant la case ci-dessous, je confirme avoir pris connaissance de ces termes et '
                        "j'atteste de l'exactitude des informations saisies.",
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 10),
        CheckboxListTile(
          value: _accepteContrat,
          onChanged: (v) => setState(() => _accepteContrat = v ?? false),
          contentPadding: EdgeInsets.zero,
          controlAffinity: ListTileControlAffinity.leading,
          title: Text("J'ai lu et j'accepte les termes de cette attestation.",
              style: TextStyle(fontSize: 13, color: AppColors.textPrimary)),
        ),
        IgnorePointer(
          ignoring: !_accepteContrat,
          child: Opacity(
            opacity: _accepteContrat ? 1 : 0.4,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _ordonneParController,
                        onChanged: (_) => setState(() {}),
                        decoration: const InputDecoration(labelText: 'Ordonné par'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _ordonneParFonction,
                        decoration: const InputDecoration(labelText: 'Fonction'),
                        items: context
                            .watch<RolePermissionState>()
                            .roles
                            .map((r) => DropdownMenuItem(value: r.name, child: Text(r.name)))
                            .toList(),
                        onChanged: (v) => setState(() => _ordonneParFonction = v),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text('Montant à annuler', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                const SizedBox(height: 6),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'total', label: Text('Tout le reste')),
                    ButtonSegment(value: 'partiel', label: Text('Montant précis')),
                  ],
                  selected: {_typeAnnulation},
                  onSelectionChanged: (v) => setState(() => _typeAnnulation = v.first),
                ),
                const SizedBox(height: 8),
                if (_typeAnnulation == 'partiel')
                  TextField(
                    controller: _montantController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(labelText: 'Montant en GDES'),
                  ),
                const SizedBox(height: 12),
                TextField(
                  controller: _raisonController,
                  onChanged: (_) => setState(() {}),
                  maxLines: 3,
                  maxLength: 150,
                  decoration: const InputDecoration(
                    labelText: 'Raison (20 à 150 caractères)',
                    alignLabelWithHint: true,
                  ),
                ),
              ],
            ),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 4),
          Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
        ],
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Annuler'),
            ),
            const SizedBox(width: 8),
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
              onPressed: (!_accepteContrat || state.isSubmitting) ? null : _submit,
              child: state.isSubmitting
                  ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Accorder la dérogation'),
            ),
          ],
        ),
      ],
    );
  }
}
