import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../screens/shell/app_shell.dart';
import '../../../state/role_permission_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/section_header.dart';

/// Configure quels onglets de navigation sont visibles pour chaque rôle.
/// Un rôle avec accessible_tabs=null voit tous les onglets (accès total).
/// Les onglets non cochés sont masqués pour les utilisateurs ayant ce rôle.
class TabConfigTab extends StatefulWidget {
  const TabConfigTab({super.key});

  @override
  State<TabConfigTab> createState() => _TabConfigTabState();
}

class _TabConfigTabState extends State<TabConfigTab> {
  String? _selectedRoleId;
  /// null signifie "accès total" (tous les onglets cochés sans restriction)
  Set<String>? _checkedTabIds;
  bool _allTabs = true;
  String? _error;

  static const _allNavItems = kAllNavItems;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback(
      (_) => context.read<RolePermissionState>().loadLists(),
    );
  }

  void _onRoleChanged(String? roleId) {
    if (roleId == null) return;
    final roles = context.read<RolePermissionState>().roles;
    final role = roles.firstWhere((r) => r.id == roleId);
    setState(() {
      _selectedRoleId = roleId;
      _error = null;
      if (role.accessibleTabs == null) {
        _allTabs = true;
        _checkedTabIds = null;
      } else {
        _allTabs = false;
        _checkedTabIds = role.accessibleTabs!.toSet();
      }
    });
  }

  void _toggleAll(bool value) {
    setState(() {
      _allTabs = value;
      _checkedTabIds = value ? null : {};
    });
  }

  Future<void> _submit() async {
    if (_selectedRoleId == null) {
      setState(() => _error = 'Sélectionnez un rôle.');
      return;
    }
    setState(() => _error = null);
    final tabs = _allTabs ? null : _checkedTabIds!.toList();
    final error = await context.read<RolePermissionState>().updateRoleTabs(
      _selectedRoleId!,
      tabs,
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vues du rôle mises à jour.')),
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
          title: 'Vues par rôle',
          subtitle: 'Choisissez quels onglets chaque rôle peut voir',
          icon: Icons.visibility_outlined,
          colorKey: 'sky',
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
              if (state.isLoadingLists)
                const Center(child: CircularProgressIndicator())
              else
                DropdownButtonFormField<String>(
                  initialValue: _selectedRoleId,
                  decoration: const InputDecoration(labelText: 'Rôle'),
                  items: state.roles
                      .map((r) => DropdownMenuItem(
                            value: r.id,
                            child: Text(r.name),
                          ))
                      .toList(),
                  onChanged: _onRoleChanged,
                ),
              const SizedBox(height: 16),
              if (_selectedRoleId != null) ...[
                Material(
                  color: Colors.transparent,
                  child: CheckboxListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                    value: _allTabs,
                    title: Text(
                      'Accès total (tous les onglets)',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                    activeColor: AppColors.accent,
                    onChanged: (v) => _toggleAll(v ?? false),
                  ),
                ),
                if (!_allTabs) ...[
                  const Divider(height: 20),
                  Text(
                    'ONGLETS AUTORISÉS',
                    style: TextStyle(
                      fontSize: 11,
                      letterSpacing: 1,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 12,
                    runSpacing: 4,
                    children: _allNavItems
                        .where((item) => item.id != 'actualiser' && item.id != 'a_propos')
                        .map((item) {
                      final checked = _checkedTabIds!.contains(item.id);
                      return SizedBox(
                        width: 200,
                        child: Material(
                          color: Colors.transparent,
                          child: CheckboxListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            controlAffinity: ListTileControlAffinity.leading,
                            value: checked,
                            activeColor: AppColors.accent,
                            title: Row(
                              children: [
                                Icon(item.icon, size: 15, color: AppColors.textMuted),
                                const SizedBox(width: 6),
                                Text(
                                  item.label,
                                  style: TextStyle(
                                    color: AppColors.textPrimary,
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                            ),
                            onChanged: (v) => setState(() {
                              if (v == true) {
                                _checkedTabIds!.add(item.id);
                              } else {
                                _checkedTabIds!.remove(item.id);
                              }
                            }),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ],
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
                  onPressed: (_selectedRoleId == null || state.isUpdatingTabs)
                      ? null
                      : _submit,
                  child: state.isUpdatingTabs
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
