import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/personnel.dart';
import '../../state/personnel_state.dart';
import '../../state/role_permission_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';

/// Équivalent de admin_page()/set_table_refresh_data_admin()/
/// add_personnel()/active_personnel() (school_client, Controllers/Main.py:
/// 7691-7970) pour la STRUCTURE (gestion du personnel administratif, avec
/// attribution de rôle) — voir PersonnelState. Le STYLE (ambre, cards,
/// badges, modal) reprend Administration.vue (ecole_nginx/frontend/src/
/// views/admin).
///
/// Volontairement omis : le bouton "Supprimer" du web (Administration.vue)
/// a un onClick vide (jamais relié à une requête), et il n'existe aucune
/// route DELETE /personnel côté serveur — omis, fidèle à cette absence
/// réelle de fonctionnalité. "Modifier" est en revanche bien réel
/// (editPerso()) — repris ici.
class AdministrationScreen extends StatefulWidget {
  const AdministrationScreen({super.key});

  @override
  State<AdministrationScreen> createState() => _AdministrationScreenState();
}

class _AdministrationScreenState extends State<AdministrationScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PersonnelState>().load();
      context.read<RolePermissionState>().loadLists();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _toggleActive(Personnel p) async {
    final state = context.read<PersonnelState>();
    final result = await state.toggleActive(p.id);
    if (!mounted) return;
    if (result.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.error!)));
    } else {
      await state.load(page: state.currentPage);
    }
  }

  Future<void> _openForm({Personnel? personnel}) async {
    final saved = await showDialog<bool>(
      context: context,
      builder: (_) => _PersonnelFormDialog(personnel: personnel),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(personnel == null ? 'Personnel ajouté.' : 'Personnel modifié.')),
      );
    }
  }

  Color _statusColor(Personnel p) {
    if (p.userStatus == 1) return const Color(0xFF34D399);
    if (p.userStatus == 0) return const Color(0xFFF59E0B);
    return AppColors.danger;
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<PersonnelState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Administration',
            subtitle: 'Gestion du personnel administratif',
            icon: Icons.admin_panel_settings_outlined,
            colorKey: 'amber',
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              PillButton(
                label: 'Ajouter Personnel',
                colorKey: 'amber',
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
                    hintText: 'Rechercher un Personnel...',
                    isDense: true,
                  ),
                  onSubmitted: (v) => context.read<PersonnelState>().load(page: 1, search: v),
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
                  onPageChange: (page) => context.read<PersonnelState>().load(page: page),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('NOM')),
                      DataColumn(label: Text('PRÉNOM')),
                      DataColumn(label: Text('SEXE')),
                      DataColumn(label: Text('TÉLÉPHONE')),
                      DataColumn(label: Text('COURRIEL')),
                      DataColumn(label: Text('STATUT')),
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
                        DataCell(Text(p.sexe)),
                        DataCell(Text(p.telephone)),
                        DataCell(Text(p.email)),
                        DataCell(Text(p.statusLabel, style: TextStyle(color: AppColors.textMuted, fontSize: 12.5))),
                        DataCell(
                          IconButton(
                            tooltip: 'Modifier',
                            icon: Icon(Icons.edit_outlined, size: 17, color: AppColors.accentLight),
                            onPressed: () => _openForm(personnel: p),
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

class _PersonnelFormDialog extends StatefulWidget {
  const _PersonnelFormDialog({this.personnel});

  final Personnel? personnel;

  @override
  State<_PersonnelFormDialog> createState() => _PersonnelFormDialogState();
}

class _PersonnelFormDialogState extends State<_PersonnelFormDialog> {
  late final _nom = TextEditingController(text: widget.personnel?.nom);
  late final _prenom = TextEditingController(text: widget.personnel?.prenom);
  late final _telephone = TextEditingController(text: widget.personnel?.telephone);
  late final _email = TextEditingController(text: widget.personnel?.email);
  late final _adresse = TextEditingController(text: widget.personnel?.adresse);
  String _sexe = 'M';
  String? _roleId;
  String? _error;

  // Section "activer/désactiver" — équivalent de admin_status/
  // admin_change_status (Resources/main_school1.ui:7157,7164), visible
  // seulement en modification (frame_305 caché en création, Main.py:
  // 7762-7774).
  late int? _userStatus = widget.personnel?.userStatus;
  bool _togglingStatus = false;

  final _newPassword = TextEditingController();
  final _confirmPassword = TextEditingController();
  String? _passwordError;
  String? _passwordSuccess;

  @override
  void initState() {
    super.initState();
    final sexe = widget.personnel?.sexe.toUpperCase();
    if (sexe == 'F' || sexe == 'FEMININ' || sexe == 'FEMME') _sexe = 'F';
    _roleId = widget.personnel?.roleId;
  }

  @override
  void dispose() {
    _nom.dispose();
    _prenom.dispose();
    _telephone.dispose();
    _email.dispose();
    _adresse.dispose();
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
    final error = await context.read<PersonnelState>().resetPassword(
          personnelId: widget.personnel!.id,
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

  /// Équivalent de active_personnel() déclenché par admin_change_status
  /// (Main.py:7707-7711, 1072) — même endpoint que le clic sur le badge
  /// "Nom" de la liste (PATCH v1/active-personnel), action dupliquée ici
  /// fidèlement à l'emplacement réel du bureau (dans le formulaire).
  Future<void> _toggleStatus() async {
    setState(() => _togglingStatus = true);
    final personnelState = context.read<PersonnelState>();
    final result = await personnelState.toggleActive(widget.personnel!.id);
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
      await personnelState.load(page: personnelState.currentPage);
    }
  }

  Future<void> _submit() async {
    if (_nom.text.trim().length < 3 || _prenom.text.trim().length < 3) {
      setState(() => _error = 'Nom et prénom requis (3 caractères minimum).');
      return;
    }
    if (_roleId == null) {
      setState(() => _error = 'Le rôle est requis.');
      return;
    }
    final error = await context.read<PersonnelState>().save({
      if (widget.personnel != null) 'id': widget.personnel!.id,
      'nom': _nom.text.trim(),
      'prenom': _prenom.text.trim(),
      'sexe': _sexe,
      'email': _email.text.trim(),
      'telephone': _telephone.text.trim(),
      'adresse': _adresse.text.trim(),
      'role': _roleId,
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
    final state = context.watch<PersonnelState>();
    final roles = context.watch<RolePermissionState>().roles;
    final isEdit = widget.personnel != null;

    return Dialog(
      backgroundColor: AppColors.cardBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(isEdit ? 'Modifier un Personnel' : 'Ajouter un Personnel',
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
                DropdownButtonFormField<String>(
                  initialValue: _roleId,
                  decoration: const InputDecoration(labelText: 'Rôle'),
                  items: roles.map((r) => DropdownMenuItem(value: r.id, child: Text(r.name))).toList(),
                  onChanged: (v) => setState(() => _roleId = v),
                ),
                const SizedBox(height: 12),
                TextField(controller: _adresse, decoration: const InputDecoration(labelText: 'Adresse')),
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
