import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/professeur.dart';
import '../../state/professeur_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';

/// Équivalent de professeur_page()/set_table_refresh_data_teacher()/
/// add_professeur()/active_teacher() (school_client, Controllers/Main.py:
/// 9388-9627) pour la STRUCTURE (champs, actions, contrat API) — voir
/// ProfesseurState. Le STYLE (violet, cards, badges, modal) reprend
/// Professeur.vue (ecole_nginx/frontend/src/views/admin).
///
/// Volontairement omis : la "Modifier" du web utilise en réalité un autre
/// chemin (slot d'action `editProf()`, bien réel) — repris ici. Le bouton
/// "Supprimer" du web n'est qu'un `console.log` jamais relié à une requête
/// (et il n'existe d'ailleurs aucune route DELETE /professeur côté
/// serveur) — omis, fidèle à cette absence réelle de fonctionnalité.
class ProfesseurScreen extends StatefulWidget {
  const ProfesseurScreen({super.key});

  @override
  State<ProfesseurScreen> createState() => _ProfesseurScreenState();
}

class _ProfesseurScreenState extends State<ProfesseurScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => context.read<ProfesseurState>().load());
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _toggleActive(Professeur p) async {
    final state = context.read<ProfesseurState>();
    final result = await state.toggleActive(p.id);
    if (!mounted) return;
    if (result.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.error!)));
    } else {
      await state.load(page: state.currentPage);
    }
  }

  Future<void> _openForm({Professeur? professeur}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _ProfesseurFormDialog(professeur: professeur),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(professeur == null ? 'Professeur ajouté.' : 'Professeur modifié.')),
      );
    }
  }

  Color _statusColor(Professeur p) {
    if (p.userStatus == 1) return const Color(0xFF34D399);
    if (p.userStatus == 0) return const Color(0xFFF59E0B);
    return AppColors.danger;
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ProfesseurState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Professeurs',
            subtitle: 'Gestion du corps enseignant',
            icon: Icons.school_outlined,
            colorKey: 'violet',
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              PillButton(
                label: 'Ajouter Professeur',
                colorKey: 'violet',
                icon: Icons.add,
                onPressed: () => _openForm(),
              ),
              const Spacer(),
              SizedBox(
                width: 280,
                child: TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search, size: 18),
                    hintText: 'Rechercher un professeur..',
                    isDense: true,
                  ),
                  onSubmitted: (v) => context.read<ProfesseurState>().load(page: 1, search: v),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.errorMessage != null)
            Expanded(child: Center(child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary))))
          else
            Expanded(
              child: SingleChildScrollView(
                child: DataTableCard(
                  currentPage: state.currentPage,
                  lastPage: state.lastPage,
                  onPageChange: (page) => context.read<ProfesseurState>().load(page: page),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('NOM')),
                      DataColumn(label: Text('PRÉNOM')),
                      DataColumn(label: Text('TÉLÉPHONE')),
                      DataColumn(label: Text('SEXE')),
                      DataColumn(label: Text('ADRESSE')),
                      DataColumn(label: Text('COURRIEL')),
                      DataColumn(label: Text('STATUS')),
                      DataColumn(label: Text('')),
                    ],
                    rows: state.items.map((p) {
                      final isToggling = state.activatingId == p.id;
                      final color = _statusColor(p);
                      return DataRow(cells: [
                        DataCell(
                          isToggling
                              ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                              : InkWell(
                                  onTap: () => _toggleActive(p),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: color.withValues(alpha: 0.1),
                                      border: Border.all(color: color.withValues(alpha: 0.3)),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: Text(p.nom, style: TextStyle(fontSize: 12.5, color: color)),
                                  ),
                                ),
                        ),
                        DataCell(Text(p.prenom)),
                        DataCell(Text(p.telephone)),
                        DataCell(Text(p.sexe)),
                        DataCell(Text(p.adresse)),
                        DataCell(Text(p.email)),
                        DataCell(Text(p.statusLabel, style: TextStyle(color: AppColors.textMuted, fontSize: 12.5))),
                        DataCell(
                          IconButton(
                            tooltip: 'Modifier',
                            icon: Icon(Icons.edit_outlined, size: 17, color: AppColors.accentLight),
                            onPressed: () => _openForm(professeur: p),
                          ),
                        ),
                      ]);
                    }).toList(),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

const _sexeOptions = {'M': 'Homme', 'F': 'Femme'};

class _ProfesseurFormDialog extends StatefulWidget {
  const _ProfesseurFormDialog({this.professeur});

  final Professeur? professeur;

  @override
  State<_ProfesseurFormDialog> createState() => _ProfesseurFormDialogState();
}

class _ProfesseurFormDialogState extends State<_ProfesseurFormDialog> {
  late final _nom = TextEditingController(text: widget.professeur?.nom);
  late final _prenom = TextEditingController(text: widget.professeur?.prenom);
  late final _telephone = TextEditingController(text: widget.professeur?.telephone);
  late final _email = TextEditingController(text: widget.professeur?.email);
  late final _adresse = TextEditingController(text: widget.professeur?.adresse);
  late final _matiere = TextEditingController(text: widget.professeur?.matiereEnseignee);
  String _sexe = 'M';
  bool _notification = false;
  String? _error;

  // Section "activer/désactiver" — équivalent de prof_status/
  // status_prof_change (Resources/main_school1.ui:12941,12948), visible
  // seulement en modification (frame_302/frame_313 cachés en création,
  // Main.py:9403-9412).
  late int? _userStatus = widget.professeur?.userStatus;
  bool _togglingStatus = false;

  final _newPassword = TextEditingController();
  final _confirmPassword = TextEditingController();
  String? _passwordError;
  String? _passwordSuccess;

  @override
  void initState() {
    super.initState();
    final sexe = widget.professeur?.sexe.toUpperCase();
    if (sexe == 'F' || sexe == 'FEMININ' || sexe == 'FEMME') _sexe = 'F';
  }

  @override
  void dispose() {
    _nom.dispose();
    _prenom.dispose();
    _telephone.dispose();
    _email.dispose();
    _adresse.dispose();
    _matiere.dispose();
    _newPassword.dispose();
    _confirmPassword.dispose();
    super.dispose();
  }

  Future<void> _resetPassword() async {
    setState(() {
      _passwordError = null;
      _passwordSuccess = null;
    });
    if (_newPassword.text.length < 8) {
      setState(() => _passwordError = 'Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    if (_newPassword.text != _confirmPassword.text) {
      setState(() => _passwordError = 'Les mots de passe ne correspondent pas.');
      return;
    }
    final error = await context.read<ProfesseurState>().resetPassword(
          professeurId: widget.professeur!.id,
          password: _newPassword.text,
          passwordConfirm: _confirmPassword.text,
        );
    if (!mounted) return;
    setState(() {
      if (error != null) {
        _passwordError = error;
      } else {
        _passwordSuccess = 'Mot de passe réinitialisé.';
        _newPassword.clear();
        _confirmPassword.clear();
      }
    });
  }

  /// Équivalent de active_teacher() déclenché par status_prof_change
  /// (Main.py:9506-9509, 1071) — même endpoint que le clic sur le badge
  /// "Nom" de la liste (PATCH v1/active-teacher), action dupliquée ici
  /// fidèlement à l'emplacement réel du bureau (dans le formulaire).
  Future<void> _toggleStatus() async {
    setState(() => _togglingStatus = true);
    final profState = context.read<ProfesseurState>();
    final result = await profState.toggleActive(widget.professeur!.id);
    if (!mounted) return;
    setState(() {
      _togglingStatus = false;
      if (result.error != null) {
        _error = result.error;
      } else {
        _userStatus = result.status;
      }
    });
    if (result.error == null) {
      await profState.load(page: profState.currentPage);
    }
  }

  Future<void> _submit() async {
    if (_nom.text.trim().length < 3 || _prenom.text.trim().length < 3) {
      setState(() => _error = 'Nom et prénom requis (3 caractères minimum).');
      return;
    }
    final error = await context.read<ProfesseurState>().save({
      if (widget.professeur != null) 'id': widget.professeur!.id,
      'nom': _nom.text.trim(),
      'prenom': _prenom.text.trim(),
      'sexe': _sexe,
      'email': _email.text.trim(),
      'telephone': _telephone.text.trim(),
      'adresse': _adresse.text.trim(),
      'matiere_enseignee': _matiere.text.trim().isEmpty ? null : _matiere.text.trim(),
      'notification': _notification,
    });
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<ProfesseurState>();
    final isEdit = widget.professeur != null;

    return Dialog(
      backgroundColor: AppColors.cardBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 640),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(isEdit ? 'Modifier un Professeur' : 'Ajouter un Professeur',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                if (isEdit) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: AppColors.appBg,
                      border: Border.all(color: AppColors.borderSubtle),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      children: [
                        Text(
                          _userStatus == 1 ? 'Active' : 'Inactive',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: _userStatus == 1 ? const Color(0xFF4CAF50) : const Color(0xFFF44336),
                          ),
                        ),
                        const Spacer(),
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: _userStatus == 1 ? const Color(0xFFF44336) : const Color(0xFF4CAF50),
                            side: BorderSide(color: _userStatus == 1 ? const Color(0xFFF44336) : const Color(0xFF4CAF50)),
                          ),
                          onPressed: _togglingStatus ? null : _toggleStatus,
                          child: _togglingStatus
                              ? const SizedBox(height: 14, width: 14, child: CircularProgressIndicator(strokeWidth: 2))
                              : Text(_userStatus == 1 ? 'Desactiver' : 'Activer'),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 20),
                Row(children: [
                  Expanded(child: TextField(controller: _nom, decoration: const InputDecoration(labelText: 'Nom'))),
                  const SizedBox(width: 12),
                  Expanded(child: TextField(controller: _prenom, decoration: const InputDecoration(labelText: 'Prénom'))),
                ]),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _sexe,
                      decoration: const InputDecoration(labelText: 'Sexe'),
                      items: _sexeOptions.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
                      onChanged: (v) => setState(() => _sexe = v ?? _sexe),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(child: TextField(controller: _telephone, decoration: const InputDecoration(labelText: 'Téléphone'))),
                ]),
                const SizedBox(height: 12),
                TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email'), keyboardType: TextInputType.emailAddress),
                const SizedBox(height: 12),
                TextField(controller: _adresse, decoration: const InputDecoration(labelText: 'Adresse')),
                const SizedBox(height: 12),
                TextField(controller: _matiere, decoration: const InputDecoration(labelText: 'Matière enseignée')),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Switch(value: _notification, onChanged: (v) => setState(() => _notification = v)),
                    const SizedBox(width: 6),
                    Text('Notifier le prof', style: TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
                  ],
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
                ],
                if (isEdit) ...[
                  const SizedBox(height: 20),
                  Divider(color: AppColors.borderSubtle),
                  const SizedBox(height: 12),
                  Text('RÉINITIALISER LE MOT DE PASSE',
                      style: TextStyle(fontSize: 10.5, letterSpacing: 0.8, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
                  const SizedBox(height: 10),
                  Row(children: [
                    Expanded(
                      child: TextField(
                        controller: _newPassword,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Nouveau mot de passe', isDense: true),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: _confirmPassword,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Confirmation', isDense: true),
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: state.isResettingPassword ? null : _resetPassword,
                      child: state.isResettingPassword
                          ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Text('Réinitialiser'),
                    ),
                  ]),
                  if (_passwordError != null) ...[
                    const SizedBox(height: 8),
                    Text(_passwordError!, style: const TextStyle(color: AppColors.danger, fontSize: 12)),
                  ],
                  if (_passwordSuccess != null) ...[
                    const SizedBox(height: 8),
                    Text(_passwordSuccess!, style: const TextStyle(color: Color(0xFF34D399), fontSize: 12)),
                  ],
                ],
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Annuler')),
                    const SizedBox(width: 8),
                    FilledButton(
                      onPressed: state.isSubmitting ? null : _submit,
                      child: state.isSubmitting
                          ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : Text(isEdit ? 'Modifier' : 'Enregistrer'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
