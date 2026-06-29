import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/auth_state.dart';
import '../theme/app_theme.dart';

/// Équivalent du garde de handle_pdf() (Controllers/Main.py:3739-3752) :
///
///   if self.access_key != '22' or self.access_key_info != self.access_key
///       and not endpoint.startswith('v1/print-recu'):
///
/// Repose sur la double vérification croisée entre heart_autos.descript et
/// users.client_infos — deux champs écrits exclusivement par infini-software
/// via POST /activate-state → get_all_user(). Manipuler log_actives seul
/// ne contourne pas ce test (AuthState.isLicenseAuthorized vérifie les deux
/// sources indépendamment).
///
/// Les reçus (printRecu paiement/vente/inscription) ne passent PAS par cette
/// fonction — équivalent de l'exception `v1/print-recu` dans school_client.
///
/// Retourne true si l'impression est autorisée.
bool canPrintNonReceipt(BuildContext context) {
  final auth = context.read<AuthState>();
  if (auth.isLicenseAuthorized) return true;

  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
    content: Text(
      'La clé d\'activation est invalide.\n'
      'Vous ne pouvez pas imprimer.\n'
      'Veuillez contacter l\'administrateur ou l\'équipe de développement.',
    ),
    backgroundColor: AppColors.danger,
    duration: Duration(seconds: 4),
  ));
  return false;
}
