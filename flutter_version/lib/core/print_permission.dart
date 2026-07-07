import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/auth_state.dart';
import '../theme/app_theme.dart';

/// Vérifie la permission RBAC (Role/Permission, `Imprimer ...`) requise pour
/// une action d'impression — distinct et indépendant de `print_gate.dart`
/// (canPrintNonReceipt), qui vérifie la licence/activation, pas les droits
/// de l'utilisateur. Les deux gardes s'appliquent : un reçu contourne la
/// licence (voir print_gate.dart) mais reste soumis à sa permission RBAC
/// (`Imprimer paiement`/`Imprimer vente`/`Imprimer enregistrement`).
///
/// Retourne true si l'impression est autorisée.
bool canPrintPermission(BuildContext context, String permissionName) {
  final auth = context.read<AuthState>();
  if (auth.permissions.contains(permissionName)) return true;

  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
    content: Text(
      'Vous n\'avez pas la permission d\'imprimer ce document '
      '("$permissionName" requise).',
    ),
    backgroundColor: AppColors.danger,
    duration: const Duration(seconds: 4),
  ));
  return false;
}
