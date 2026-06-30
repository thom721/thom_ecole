import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../screens/shell/app_shell.dart';
import '../../../state/role_permission_state.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/section_header.dart';

/// Configure quels onglets (et sous-onglets) sont visibles pour chaque rôle.
/// Les IDs de sous-onglets utilisent le format "parentId.sousId"
/// (ex: "vente.depenses") et sont stockés dans accessible_tabs au même niveau
/// que les IDs d'onglets principaux.
class TabConfigTab extends StatefulWidget {
  const TabConfigTab({super.key});

  @override
  State<TabConfigTab> createState() => _TabConfigTabState();
}

class _TabConfigTabState extends State<TabConfigTab> {
  String? _selectedRoleId;
  Set<String>? _checkedTabIds;
  bool _allTabs = true;
  String? _error;

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

  /// true si tous les sous-onglets de [parentId] sont en mode "accès total"
  /// (aucun ID "parentId.*" stocké dans _checkedTabIds → pas de restriction).
  bool _subAllChecked(String parentId) {
    return !_checkedTabIds!.any((id) => id.startsWith('$parentId.'));
  }

  /// Marqueur local (jamais envoyé au backend, filtré dans _submit) qui
  /// distingue "aucun id stocké car pas de restriction" de "l'utilisateur a
  /// volontairement décoché tous les sous-onglets un par un" — sans lui, le
  /// second cas était indiscernable du premier et _subAllChecked revenait
  /// automatiquement à "Tous les sous-onglets" coché.
  String _noneMarker(String parentId) => '$parentId.__none__';

  void _toggleSubAll(String parentId, bool allVisible) {
    final subs = kSubNavItems[parentId] ?? [];
    setState(() {
      if (allVisible) {
        _checkedTabIds!.removeWhere((id) => id.startsWith('$parentId.'));
      } else {
        _checkedTabIds!.remove(_noneMarker(parentId));
        for (final sub in subs) {
          _checkedTabIds!.add(sub.id);
        }
      }
    });
  }

  Future<void> _submit() async {
    if (_selectedRoleId == null) {
      setState(() => _error = 'Sélectionnez un rôle.');
      return;
    }
    setState(() => _error = null);
    final tabs = _allTabs
        ? null
        : _checkedTabIds!.where((id) => !id.endsWith('.__none__')).toList();
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

  Widget _buildParentCheckbox(NavItem item) {
    final checked = _checkedTabIds!.contains(item.id);
    final hasSubs = kSubNavItems.containsKey(item.id);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Material(
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
                  style: TextStyle(color: AppColors.textPrimary, fontSize: 13),
                ),
              ],
            ),
            onChanged: (v) => setState(() {
              if (v == true) {
                _checkedTabIds!.add(item.id);
              } else {
                _checkedTabIds!.remove(item.id);
                // Retirer les sous-onglets quand le parent est caché
                _checkedTabIds!.removeWhere((id) => id.startsWith('${item.id}.'));
              }
            }),
          ),
        ),
        if (checked && hasSubs) _buildSubGroup(item.id),
      ],
    );
  }

  Widget _buildSubGroup(String parentId) {
    final subs = kSubNavItems[parentId]!;
    final allVisible = _subAllChecked(parentId);

    return Padding(
      padding: const EdgeInsets.only(left: 24, bottom: 4),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: AppColors.appBg,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Material(
              color: Colors.transparent,
              child: CheckboxListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
                value: allVisible,
                activeColor: AppColors.accent,
                title: Text(
                  'Tous les sous-onglets',
                  style: TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                onChanged: (v) => _toggleSubAll(parentId, v ?? true),
              ),
            ),
            if (!allVisible) ...[
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                runSpacing: 0,
                children: subs.map((sub) {
                  final subChecked = _checkedTabIds!.contains(sub.id);
                  final none = _noneMarker(parentId);
                  return SizedBox(
                    width: 210,
                    child: Material(
                      color: Colors.transparent,
                      child: CheckboxListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                        value: subChecked,
                        activeColor: AppColors.accentLight,
                        title: Row(
                          children: [
                            Icon(sub.icon, size: 13, color: AppColors.textMuted),
                            const SizedBox(width: 5),
                            Expanded(
                              child: Text(
                                sub.label,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: AppColors.textPrimary,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ],
                        ),
                        onChanged: (v) => setState(() {
                          if (v == true) {
                            _checkedTabIds!.remove(none);
                            _checkedTabIds!.add(sub.id);
                          } else {
                            _checkedTabIds!.remove(sub.id);
                            final stillHasReal = _checkedTabIds!.any(
                              (id) => id.startsWith('$parentId.') && id != none,
                            );
                            if (!stillHasReal) {
                              _checkedTabIds!.add(none);
                            }
                          }
                        }),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
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
                  ...kAllNavItems
                      .where(
                        (item) =>
                            item.id != 'actualiser' && item.id != 'a_propos',
                      )
                      .map(_buildParentCheckbox),
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
