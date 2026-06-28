import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/role_permission.dart';
import '../../../state/role_permission_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/section_header.dart';

/// Les permissions n'ont pas de champ "module" en base (SPermission) mais
/// suivent toutes la convention "Verbe Ressource" (cf. seed
/// Initialisation.py : Ajouter/Modifier/Supprimer/Voir/Imprimer) — on colore
/// donc par verbe d'action, qui correspond au type d'opération autorisée.
String _permissionColorKey(String name) {
  final n = name.trim().toLowerCase();
  if (n.startsWith('ajouter')) return 'emerald';
  if (n.startsWith('modifier')) return 'amber';
  if (n.startsWith('supprimer')) return 'rose';
  if (n.startsWith('voir')) return 'sky';
  if (n.startsWith('imprimer')) return 'violet';
  return 'purple';
}

/// Équivalent de permission_page() (school_client, Controllers/Main.py:
/// 6369-6393) : assigne des permissions soit à un RÔLE, soit à un
/// UTILISATEUR — jamais les deux à la fois (AssignPermissionRequest.
/// validate_role_or_user, RRolePermission.py:282-296). Le bureau affiche
/// les deux champs (combo rôle + recherche utilisateur) simultanément sans
/// les exclure visuellement ; on rend ici le choix explicite via un
/// sélecteur Rôle/Utilisateur, plus sûr et tout aussi fidèle au backend.
class PermissionAssignmentTab extends StatefulWidget {
  const PermissionAssignmentTab({super.key});

  @override
  State<PermissionAssignmentTab> createState() =>
      _PermissionAssignmentTabState();
}

enum _Target { role, user }

class _PermissionAssignmentTabState extends State<PermissionAssignmentTab> {
  _Target _target = _Target.role;
  String? _selectedRoleId;
  final _searchController = TextEditingController();
  PermissionSearchUser? _selectedUser;
  final Set<String> _checkedPermissionIds = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback(
      (_) => context.read<RolePermissionState>().loadLists(),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _changeTarget(_Target t) {
    setState(() {
      _target = t;
      _selectedRoleId = null;
      _selectedUser = null;
      _checkedPermissionIds.clear();
      _searchController.clear();
      _error = null;
    });
    context.read<RolePermissionState>().searchUsersForPermission('');
  }

  Future<void> _onRoleChanged(String? roleId) async {
    setState(() {
      _selectedRoleId = roleId;
      _checkedPermissionIds.clear();
    });
    if (roleId == null) return;
    await context.read<RolePermissionState>().loadPermissionsForRole(roleId);
    if (!mounted) return;
    setState(
      () => _checkedPermissionIds.addAll(
        context.read<RolePermissionState>().permissionsForSelectedRole,
      ),
    );
  }

  void _selectUser(PermissionSearchUser user) {
    setState(() {
      _selectedUser = user;
      _checkedPermissionIds
        ..clear()
        ..addAll(user.permissionIds);
      _searchController.text = '${user.nom} ${user.prenom}';
    });
    context.read<RolePermissionState>().searchUsersForPermission('');
  }

  Future<void> _submit() async {
    if (_checkedPermissionIds.isEmpty) {
      setState(() => _error = 'Sélectionnez au moins une permission.');
      return;
    }
    final state = context.read<RolePermissionState>();
    String? error;
    if (_target == _Target.role) {
      if (_selectedRoleId == null) {
        setState(() => _error = 'Sélectionnez un rôle.');
        return;
      }
      error = await state.assignPermissionsToRole(
        roleId: _selectedRoleId!,
        permissionIds: _checkedPermissionIds,
      );
    } else {
      if (_selectedUser == null) {
        setState(() => _error = 'Sélectionnez un utilisateur.');
        return;
      }
      error = await state.assignPermissionsToUser(
        userId: _selectedUser!.id,
        permissionIds: _checkedPermissionIds,
      );
    }
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      setState(() => _error = null);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Permissions assignées avec succès.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<RolePermissionState>();
    final canEdit = _target == _Target.role
        ? _selectedRoleId != null
        : _selectedUser != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SectionHeader(
          title: 'Attribution des permissions',
          subtitle: "Permissions d'un rôle, ou directement d'un utilisateur",
          icon: Icons.lock_outline,
          colorKey: 'emerald',
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SegmentedButton<_Target>(
                segments: const [
                  ButtonSegment(
                    value: _Target.role,
                    label: Text('Par rôle'),
                    icon: Icon(Icons.shield_outlined, size: 14),
                  ),
                  ButtonSegment(
                    value: _Target.user,
                    label: Text('Par utilisateur'),
                    icon: Icon(Icons.person_outline, size: 14),
                  ),
                ],
                selected: {_target},
                onSelectionChanged: (s) => _changeTarget(s.first),
              ),
              const SizedBox(height: 14),
              if (_target == _Target.role)
                DropdownButtonFormField<String>(
                  initialValue: _selectedRoleId,
                  decoration: const InputDecoration(labelText: 'Rôle'),
                  items: state.roles
                      .map(
                        (r) =>
                            DropdownMenuItem(value: r.id, child: Text(r.name)),
                      )
                      .toList(),
                  onChanged: _onRoleChanged,
                )
              else ...[
                TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    labelText: 'Rechercher un utilisateur',
                    prefixIcon: Icon(Icons.search, size: 18),
                  ),
                  onChanged: (v) {
                    if (_selectedUser != null)
                      setState(() => _selectedUser = null);
                    context
                        .read<RolePermissionState>()
                        .searchUsersForPermission(v);
                  },
                ),
                if (state.isSearchingForPermission)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else if (_selectedUser == null &&
                    state.permissionSearchResults.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 10),
                    decoration: BoxDecoration(
                      color: AppColors.appBg,
                      border: Border.all(color: AppColors.borderSubtle),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: ListView.separated(
                      shrinkWrap: true,
                      itemCount: state.permissionSearchResults.length,
                      separatorBuilder: (_, _) =>
                          Divider(height: 1, color: AppColors.borderSubtle),
                      itemBuilder: (context, index) {
                        final u = state.permissionSearchResults[index];
                        return ListTile(
                          dense: true,
                          title: Text(
                            '${u.nom} ${u.prenom}',
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 13,
                            ),
                          ),
                          onTap: () => _selectUser(u),
                        );
                      },
                    ),
                  ),
              ],
              const SizedBox(height: 18),
              Text(
                'PERMISSIONS',
                style: TextStyle(
                  fontSize: 11,
                  letterSpacing: 1,
                  color: AppColors.textMuted,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              if (state.isLoadingLists || state.isLoadingRolePermissions)
                const Center(child: CircularProgressIndicator())
              else
                Wrap(
                  spacing: 16,
                  runSpacing: 8,
                  children: state.permissions.map((p) {
                    final checked = _checkedPermissionIds.contains(p.id);
                    final color = AppColors
                        .cardPalette[_permissionColorKey(p.name)]!
                        .text;
                    return SizedBox(
                      width: 220,
                      // CheckboxListTile peint son fond/ink splash sur le
                      // Material ancestor le plus proche — sans ce Material
                      // transparent, c'est le Container décoré englobant
                      // (ligne ~154) qui s'en charge à la place et masque
                      // l'effet (assertion "background color or ink
                      // splashes may be invisible" en mode debug).
                      child: Material(
                        color: Colors.transparent,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          value: checked,
                          enabled: canEdit,
                          activeColor: color,
                          checkColor: AppColors.cardBg,
                          side: BorderSide(color: color.withValues(alpha: 0.5)),
                          title: Opacity(
                            opacity: checked ? 1 : 0.55,
                            child: BadgePill(
                              label: p.name,
                              colorKey: _permissionColorKey(p.name),
                              showBorder: false,
                            ),
                          ),
                          onChanged: (v) => setState(() {
                            if (v == true) {
                              _checkedPermissionIds.add(p.id);
                            } else {
                              _checkedPermissionIds.remove(p.id);
                            }
                          }),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              if (_error != null) ...[
                const SizedBox(height: 10),
                Text(
                  _error!,
                  style: const TextStyle(color: AppColors.danger, fontSize: 12),
                ),
              ],
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerRight,
                child: FilledButton(
                  onPressed: state.isAssigningPermissions ? null : _submit,
                  child: state.isAssigningPermissions
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Enregistrer'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
