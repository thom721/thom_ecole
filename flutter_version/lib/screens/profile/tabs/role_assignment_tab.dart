import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../models/role_permission.dart';
import '../../../state/role_permission_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/badge_pill.dart';
import '../../../widgets/section_header.dart';

/// Aucune catégorisation par rôle n'existe côté backend (RolesPermissions
/// n'a qu'un nom) — on attribue donc une couleur stable par position dans la
/// liste, pour distinguer visuellement les rôles entre eux.
const _kRoleColorKeys = [
  'blue',
  'emerald',
  'violet',
  'amber',
  'sky',
  'rose',
  'purple',
  'cyan',
];
String _roleColorKey(int index) =>
    _kRoleColorKeys[index % _kRoleColorKeys.length];

/// Équivalent de role_page() (school_client, Controllers/Main.py:6348-6368) :
/// recherche un professeur/personnel, puis coche les rôles à lui assigner.
class RoleAssignmentTab extends StatefulWidget {
  const RoleAssignmentTab({super.key});

  @override
  State<RoleAssignmentTab> createState() => _RoleAssignmentTabState();
}

class _RoleAssignmentTabState extends State<RoleAssignmentTab> {
  final _searchController = TextEditingController();
  RoleSearchUser? _selectedUser;
  final Set<String> _checkedRoleIds = {};
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

  void _selectUser(RoleSearchUser user) {
    setState(() {
      _selectedUser = user;
      _checkedRoleIds
        ..clear()
        ..addAll(user.roleIds);
      _searchController.text = '${user.nom} ${user.prenom}';
    });
    context.read<RolePermissionState>().searchUsersForRole('');
  }

  Future<void> _submit() async {
    final user = _selectedUser;
    if (user == null || _checkedRoleIds.isEmpty) {
      setState(
        () => _error = 'Sélectionnez un utilisateur et au moins un rôle.',
      );
      return;
    }
    setState(() => _error = null);
    final error = await context.read<RolePermissionState>().assignRolesToUser(
      userId: user.id,
      roleIds: _checkedRoleIds,
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rôles assignés avec succès.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<RolePermissionState>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SectionHeader(
          title: 'Attribution des rôles',
          subtitle: 'Recherchez un professeur ou un membre du personnel',
          icon: Icons.badge_outlined,
          colorKey: 'violet',
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
              TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  labelText: 'Rechercher un utilisateur',
                  prefixIcon: Icon(Icons.search, size: 18),
                ),
                onChanged: (v) {
                  if (_selectedUser != null)
                    setState(() => _selectedUser = null);
                  context.read<RolePermissionState>().searchUsersForRole(v);
                },
              ),
              if (state.isSearchingForRole)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_selectedUser == null &&
                  state.roleSearchResults.isNotEmpty)
                Container(
                  margin: const EdgeInsets.only(top: 10),
                  decoration: BoxDecoration(
                    color: AppColors.appBg,
                    border: Border.all(color: AppColors.borderSubtle),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: state.roleSearchResults.length,
                    separatorBuilder: (_, _) =>
                        Divider(height: 1, color: AppColors.borderSubtle),
                    itemBuilder: (context, index) {
                      final u = state.roleSearchResults[index];
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
              const SizedBox(height: 18),
              Text(
                'RÔLES',
                style: TextStyle(
                  fontSize: 11,
                  letterSpacing: 1,
                  color: AppColors.textMuted,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              if (state.isLoadingLists)
                const Center(child: CircularProgressIndicator())
              else
                Wrap(
                  spacing: 16,
                  runSpacing: 8,
                  children: state.roles.asMap().entries.map((entry) {
                    final r = entry.value;
                    final checked = _checkedRoleIds.contains(r.id);
                    final color =
                        AppColors.cardPalette[_roleColorKey(entry.key)]!.text;
                    return SizedBox(
                      width: 220,
                      // Voir permission_assignment_tab.dart : sans ce
                      // Material transparent, le Container décoré englobant
                      // masque le fond/ink splash du CheckboxListTile
                      // (assertion debug "background color or ink splashes
                      // may be invisible").
                      child: Material(
                        color: Colors.transparent,
                        child: CheckboxListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          controlAffinity: ListTileControlAffinity.leading,
                          value: checked,
                          enabled: _selectedUser != null,
                          activeColor: color,
                          checkColor: AppColors.cardBg,
                          side: BorderSide(color: color.withValues(alpha: 0.5)),
                          title: Opacity(
                            opacity: checked ? 1 : 0.55,
                            child: BadgePill(
                              label: r.name,
                              colorKey: _roleColorKey(entry.key),
                              showBorder: false,
                            ),
                          ),
                          onChanged: (v) => setState(() {
                            if (v == true) {
                              _checkedRoleIds.add(r.id);
                            } else {
                              _checkedRoleIds.remove(r.id);
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
                  onPressed: state.isAssigningRoles ? null : _submit,
                  child: state.isAssigningRoles
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
