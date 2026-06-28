import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'api_client.dart';
import '../theme/app_theme.dart';

/// Sentinelle renvoyée par les méthodes d'état gérées par DualAuthChecker
/// (backend) quand l'appel reçoit un HTTP 202 — "l'utilisateur courant n'a
/// pas la permission, une approbation admin/Comptable est requise". Garde
/// la convention existante "retourne une String? d'erreur" plutôt que de
/// faire remonter une exception à travers les State.
const kApprovalRequiredError = '__approval_required__';

/// Équivalent du flux "demander un compte admin pour autoriser" qu'avait
/// commencé le backend (DualAuthChecker, POST /auth/autorisation-access)
/// sans jamais le terminer côté client : si l'action renvoie
/// [kApprovalRequiredError], on demande un PIN (admin ou Comptable),
/// l'échange contre un approval_token via POST /auth/autorisation-access-pin,
/// puis on retente l'action une seule fois avec ce token.
Future<String?> runWithPinApproval({
  required BuildContext context,
  required String permission,
  required Future<String?> Function({String? approvalToken}) action,
}) async {
  final error = await action();
  if (error != kApprovalRequiredError) return error;
  if (!context.mounted) return error;

  final token = await _promptForPin(context, permission);
  if (token == null) return "Action annulée : autorisation requise.";
  if (!context.mounted) return null;
  return action(approvalToken: token);
}

Future<String?> _promptForPin(BuildContext context, String permission) {
  return showDialog<String>(
    context: context,
    builder: (_) => _PinApprovalDialog(permission: permission),
  );
}

class _PinApprovalDialog extends StatefulWidget {
  const _PinApprovalDialog({required this.permission});

  final String permission;

  @override
  State<_PinApprovalDialog> createState() => _PinApprovalDialogState();
}

class _PinApprovalDialogState extends State<_PinApprovalDialog> {
  final _pinController = TextEditingController();
  bool _isSubmitting = false;
  String? _error;

  @override
  void dispose() {
    _pinController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!RegExp(r'^\d{6}$').hasMatch(_pinController.text)) {
      setState(() => _error = 'Le PIN doit contenir exactement 6 chiffres.');
      return;
    }
    setState(() {
      _isSubmitting = true;
      _error = null;
    });
    try {
      final apiClient = context.read<ApiClient>();
      final response = await apiClient.post(
        'auth/autorisation-access-pin',
        data: {'pin': _pinController.text, 'permission': widget.permission},
      );
      final token = (response.data as Map<String, dynamic>)['approval_token']
          ?.toString();
      if (!mounted) return;
      Navigator.of(context).pop(token);
    } catch (e) {
      final detail = e is DioException && e.response?.data is Map
          ? (e.response?.data as Map)['detail']?.toString()
          : null;
      if (!mounted) return;
      setState(() => _error = detail ?? 'PIN invalide ou non autorisé.');
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.panelBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(
        'Autorisation requise',
        style: TextStyle(color: AppColors.textPrimary),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Vous n'avez pas la permission requise. Entrez le PIN d'un administrateur ou d'un comptable pour continuer.",
            style: TextStyle(color: AppColors.textMuted, fontSize: 13),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _pinController,
            obscureText: true,
            autofocus: true,
            keyboardType: TextInputType.number,
            maxLength: 6,
            decoration: const InputDecoration(
              labelText: 'PIN (6 chiffres)',
              counterText: '',
            ),
            onSubmitted: (_) => _submit(),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(
              _error!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(null),
          child: const Text('Annuler'),
        ),
        FilledButton(
          onPressed: _isSubmitting ? null : _submit,
          child: _isSubmitting
              ? const SizedBox(
                  height: 16,
                  width: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Valider'),
        ),
      ],
    );
  }
}

/// Dialogue de confirmation avec un champ "raison" obligatoire (20 à 150
/// caractères) — partagé par le retour de paiement et les suppressions de
/// vente/dépense/transaction.
Future<String?> showReasonDialog({
  required BuildContext context,
  required String title,
  required String message,
  String confirmLabel = 'Confirmer',
}) {
  return showDialog<String>(
    context: context,
    builder: (_) => _ReasonDialog(
      title: title,
      message: message,
      confirmLabel: confirmLabel,
    ),
  );
}

class _ReasonDialog extends StatefulWidget {
  const _ReasonDialog({
    required this.title,
    required this.message,
    required this.confirmLabel,
  });

  final String title;
  final String message;
  final String confirmLabel;

  @override
  State<_ReasonDialog> createState() => _ReasonDialogState();
}

class _ReasonDialogState extends State<_ReasonDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  bool get _isValid =>
      _controller.text.trim().length >= 20 &&
      _controller.text.trim().length <= 150;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.panelBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(widget.title, style: TextStyle(color: AppColors.textPrimary)),
      content: SizedBox(
        width: 420,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.message, style: TextStyle(color: AppColors.textMuted)),
            const SizedBox(height: 16),
            TextField(
              controller: _controller,
              maxLines: 3,
              maxLength: 150,
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Raison (20 à 150 caractères)',
                alignLabelWithHint: true,
              ),
              onChanged: (_) => setState(() {}),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, null),
          child: const Text('Annuler'),
        ),
        FilledButton(
          style: FilledButton.styleFrom(backgroundColor: AppColors.danger),
          onPressed: _isValid
              ? () => Navigator.pop(context, _controller.text.trim())
              : null,
          child: Text(widget.confirmLabel),
        ),
      ],
    );
  }
}
