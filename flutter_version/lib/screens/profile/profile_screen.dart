import 'dart:convert';
import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/template_store.dart';
import '../../state/account_state.dart';
import '../../state/auth_state.dart';
import '../../state/profile_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/section_header.dart';
import 'tabs/permission_assignment_tab.dart';
import 'tabs/role_assignment_tab.dart';
import 'tabs/tab_config_tab.dart';

/// Équivalent de profile()/save_profile()/choisir_image_profile()
/// (school_client, Controllers/Main.py:6285-6346, 6799-6846), plus
/// role_page()/permission_page() (Controllers/Main.py:6348-6393) — les
/// boutons "Role"/"Permission" du bureau vivent dans la même zone d'écran
/// que le profil de l'école (Resources/main_school1.ui:18743-18785,
/// frame_90), d'où le sélecteur École/Rôles/Permissions ci-dessous plutôt
/// qu'une page séparée.
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

enum _ProfileSection { ecole, compte, roles, permissions, vues }

class _ProfileScreenState extends State<ProfileScreen> {
  _ProfileSection _section = _ProfileSection.ecole;
  final _nomController = TextEditingController();
  final _emailController = TextEditingController();
  final _ligne1Controller = TextEditingController();
  final _ligne2Controller = TextEditingController();
  final _adresseController = TextEditingController();

  String? _newLogoDataUri;
  String? _existingLogoBase64;
  String? _error;
  bool _loadedOnce = false;

  // Équivalent de "Mon profil" (adProfile.vue) — Prénom/Nom/Email/Username.
  final _compteNomController = TextEditingController();
  final _comptePrenomController = TextEditingController();
  final _compteEmailController = TextEditingController();
  final _compteUsernameController = TextEditingController();
  bool _compteLoadedOnce = false;

  final _pwCurrentController = TextEditingController();
  final _pwNewController = TextEditingController();
  final _pwConfirmController = TextEditingController();
  bool _obscurePwCurrent = true;
  bool _obscurePwNew = true;
  bool _obscurePwConfirm = true;

  // PIN d'autorisation (admin/Comptable uniquement) — utilisé par les autres
  // rôles pour faire approuver un retour de paiement ou une suppression de
  // vente/dépense/transaction sans avoir eux-mêmes la permission requise.
  final _pinController = TextEditingController();
  final _pinConfirmController = TextEditingController();

  // Équivalent de template_badge_1()/template_badge_2()/template_certificat()/
  // template_diplome() (Main.py:6817-6989) — uploads locaux, cf. TemplateStore.
  final Map<String, Uint8List?> _templates = {
    'template_badge_1': null,
    'template_badge_2': null,
    'template_certificat': null,
    'template_diplome': null,
  };
  String? _templateError;

  @override
  void initState() {
    super.initState();
    // Équivalent de isBaseUser (adProfile.vue) : un rôle "user" nu n'a accès
    // qu'à "Mon compte" — pas la peine de charger le profil de l'école ni
    // les templates, qui lui resteront invisibles.
    if (context.read<AuthState>().isBaseUser) {
      _section = _ProfileSection.compte;
      WidgetsBinding.instance.addPostFrameCallback((_) => _loadCompte());
    } else {
      WidgetsBinding.instance.addPostFrameCallback((_) => _load());
      _loadTemplates();
    }
  }

  Future<void> _loadTemplates() async {
    for (final key in _templates.keys.toList()) {
      final bytes = await TemplateStore.instance.read(key);
      if (mounted) setState(() => _templates[key] = bytes);
    }
  }

  Future<void> _pickTemplate(String key) async {
    final error = await TemplateStore.instance.pickAndSave(key);
    if (!mounted) return;
    if (error != null) {
      setState(() => _templateError = error);
      return;
    }
    final bytes = await TemplateStore.instance.read(key);
    if (!mounted) return;
    setState(() {
      _templateError = null;
      _templates[key] = bytes;
    });
  }

  Future<void> _load() async {
    final state = context.read<ProfileState>();
    await state.load();
    final p = state.profile;
    if (p != null && mounted) {
      setState(() {
        _nomController.text = p.nom;
        _emailController.text = p.email;
        _ligne1Controller.text = p.ligne1;
        _ligne2Controller.text = p.ligne2;
        _adresseController.text = p.adresse;
        _existingLogoBase64 = p.logoImageBase64;
        _loadedOnce = true;
      });
    } else if (mounted) {
      setState(() => _loadedOnce = true);
    }
  }

  Future<void> _loadCompte() async {
    final auth = context.read<AuthState>();
    final user = auth.user;
    if (user == null || user.userableId.isEmpty) return;
    final state = context.read<AccountState>();
    await state.load(
      userableId: user.userableId,
      userableType: user.userableType,
    );
    if (auth.roles.contains('admin') || auth.roles.contains('Comptable')) {
      await state.loadPinStatus();
    }
    if (!mounted) return;
    setState(() {
      _compteNomController.text = state.nom;
      _comptePrenomController.text = state.prenom;
      _compteEmailController.text = state.email;
      _compteUsernameController.text = state.username;
      _compteLoadedOnce = true;
    });
  }

  Future<void> _submitPin() async {
    if (!RegExp(r'^\d{6}$').hasMatch(_pinController.text)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Le PIN doit contenir exactement 6 chiffres.'),
        ),
      );
      return;
    }
    if (_pinController.text != _pinConfirmController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Les deux PIN ne correspondent pas.')),
      );
      return;
    }
    final error = await context.read<AccountState>().setPin(
      _pinController.text,
    );
    if (!mounted) return;
    if (error == null) {
      _pinController.clear();
      _pinConfirmController.clear();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('PIN enregistré avec succès.')),
      );
    }
  }

  Future<void> _submitCompte() async {
    final auth = context.read<AuthState>();
    final user = auth.user;
    if (user == null || user.userableId.isEmpty) return;
    final error = await context.read<AccountState>().updateProfile(
      userableId: user.userableId,
      nom: _compteNomController.text.trim(),
      prenom: _comptePrenomController.text.trim(),
      email: _compteEmailController.text.trim(),
      username: _compteUsernameController.text.trim(),
    );
    if (!mounted) return;
    if (error == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profil mis à jour avec succès.')),
      );
    }
  }

  Future<void> _submitPassword() async {
    final state = context.read<AccountState>();
    if (_pwNewController.text != _pwConfirmController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Les mots de passe ne correspondent pas.'),
        ),
      );
      return;
    }
    final error = await state.changePassword(
      currentPassword: _pwCurrentController.text,
      newPassword: _pwNewController.text,
      confirmPassword: _pwConfirmController.text,
    );
    if (!mounted) return;
    if (error == null) {
      _pwCurrentController.clear();
      _pwNewController.clear();
      _pwConfirmController.clear();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Mot de passe changé avec succès.')),
      );
    }
  }

  @override
  void dispose() {
    _nomController.dispose();
    _emailController.dispose();
    _ligne1Controller.dispose();
    _ligne2Controller.dispose();
    _adresseController.dispose();
    _compteNomController.dispose();
    _comptePrenomController.dispose();
    _compteEmailController.dispose();
    _compteUsernameController.dispose();
    _pwCurrentController.dispose();
    _pwNewController.dispose();
    _pwConfirmController.dispose();
    _pinController.dispose();
    _pinConfirmController.dispose();
    super.dispose();
  }

  Future<void> _pickLogo() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp'],
      withData: true,
    );
    final file = result?.files.single;
    if (file?.bytes == null) return;
    final ext = (file!.extension ?? 'png').toLowerCase();
    final mime = ext == 'jpg' ? 'jpeg' : ext;
    setState(
      () => _newLogoDataUri =
          'data:image/$mime;base64,${base64Encode(file.bytes!)}',
    );
  }

  Future<void> _submit() async {
    if (_nomController.text.trim().isEmpty ||
        _emailController.text.trim().isEmpty) {
      setState(() => _error = "Le nom et l'email de l'école sont requis.");
      return;
    }
    setState(() => _error = null);
    final error = await context.read<ProfileState>().submit(
      nom: _nomController.text.trim(),
      email: _emailController.text.trim(),
      ligne1: _ligne1Controller.text.trim(),
      ligne2: _ligne2Controller.text.trim(),
      adresse: _adresseController.text.trim(),
      logoImageDataUri: _newLogoDataUri,
    );
    if (!mounted) return;
    if (error != null) {
      setState(() => _error = error);
    } else {
      setState(() => _newLogoDataUri = null);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profil de l’école enregistré.')),
      );
    }
  }

  ImageProvider? _logoPreviewProvider() {
    final dataUri = _newLogoDataUri ?? _existingLogoBase64;
    if (dataUri == null) return null;
    final comma = dataUri.indexOf(',');
    final b64 = comma == -1 ? dataUri : dataUri.substring(comma + 1);
    try {
      return MemoryImage(base64Decode(b64));
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Recalcule les sections visibles pour choisir un fallback si _section
    // a été masquée par un changement de configuration de rôle.
    final auth = context.watch<AuthState>();
    final sub = auth.visibleSubItems('profile');
    bool subOk(String id) => sub == null || sub.contains(id);
    final visibleSections = <_ProfileSection>[
      if (!auth.isBaseUser && subOk('ecole')) _ProfileSection.ecole,
      if (subOk('compte')) _ProfileSection.compte,
      if (!auth.isBaseUser && auth.permissions.contains('Voir role') && subOk('roles'))
        _ProfileSection.roles,
      if (!auth.isBaseUser && auth.permissions.contains('Voir permission') && subOk('permissions'))
        _ProfileSection.permissions,
      if (!auth.isBaseUser && auth.permissions.contains('Voir role') && subOk('vues'))
        _ProfileSection.vues,
    ];
    final effectiveSection = visibleSections.contains(_section)
        ? _section
        : (visibleSections.isNotEmpty ? visibleSections.first : _ProfileSection.compte);

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSwitcher(),
          const SizedBox(height: 16),
          Expanded(
            child: SingleChildScrollView(
              child: switch (effectiveSection) {
                _ProfileSection.ecole => _buildEcoleSection(),
                _ProfileSection.compte => _buildCompteSection(),
                _ProfileSection.roles => RoleAssignmentTab(),
                _ProfileSection.permissions => PermissionAssignmentTab(),
                _ProfileSection.vues => TabConfigTab(),
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwitcher() {
    Widget pill(_ProfileSection value, String label, IconData icon) {
      final selected = _section == value;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: Material(
          color: selected ? AppColors.hoverOverlay : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () {
              setState(() => _section = value);
              if (value == _ProfileSection.compte && !_compteLoadedOnce) {
                _loadCompte();
              }
            },
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    icon,
                    size: 15,
                    color: selected
                        ? AppColors.accentLight
                        : AppColors.textMuted,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: selected
                          ? AppColors.textPrimary
                          : AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    // Mêmes restrictions que shouldShowMenuItem()/adProfile.vue (web) :
    // un rôle "user" nu ("isBaseUser") n'a accès qu'à "Mon compte" ; les
    // sections Rôles/Permissions exigent en plus les permissions "Voir
    // role"/"Voir permission" (adProfile.vue:371,417).
    // En plus : visibleSubItems('profile') peut restreindre davantage selon
    // la configuration "Vues" du rôle (accessible_tabs "profile.xxx").
    final auth = context.watch<AuthState>();
    final sub = auth.visibleSubItems('profile');
    bool subOk(String id) => sub == null || sub.contains(id);
    final canSeeEcole = !auth.isBaseUser && subOk('ecole');
    final canSeeCom = subOk('compte');
    final canSeeRoles =
        !auth.isBaseUser && auth.permissions.contains('Voir role') && subOk('roles');
    final canSeePermissions =
        !auth.isBaseUser && auth.permissions.contains('Voir permission') && subOk('permissions');
    final canSeeVues = canSeeRoles && subOk('vues');

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (canSeeEcole)
            pill(
              _ProfileSection.ecole,
              "Profil de l'école",
              Icons.account_balance_outlined,
            ),
          if (canSeeCom)
            pill(_ProfileSection.compte, 'Mon compte', Icons.person_outline),
          if (canSeeRoles)
            pill(_ProfileSection.roles, 'Rôles', Icons.badge_outlined),
          if (canSeePermissions)
            pill(
              _ProfileSection.permissions,
              'Permissions',
              Icons.lock_outline,
            ),
          if (canSeeVues)
            pill(
              _ProfileSection.vues,
              'Vues',
              Icons.visibility_outlined,
            ),
        ],
      ),
    );
  }

  Widget _buildEcoleSection() {
    final state = context.watch<ProfileState>();

    if (!_loadedOnce && state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SectionHeader(
          title: "Profil de l'école",
          subtitle: 'Coordonnées et logo affichés sur les documents officiels',
          icon: Icons.account_balance_outlined,
          colorKey: 'blue',
        ),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final twoCols = constraints.maxWidth >= 560;
              Widget field(
                String label,
                TextEditingController c, {
                TextInputType? type,
              }) {
                return TextField(
                  controller: c,
                  keyboardType: type,
                  decoration: InputDecoration(labelText: label),
                );
              }

              Widget row(Widget a, Widget b) {
                if (!twoCols) {
                  return Column(children: [a, const SizedBox(height: 12), b]);
                }
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: a),
                    const SizedBox(width: 16),
                    Expanded(child: b),
                  ],
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  row(
                    field('Nom de l’école', _nomController),
                    field(
                      'Email',
                      _emailController,
                      type: TextInputType.emailAddress,
                    ),
                  ),
                  const SizedBox(height: 12),
                  row(
                    field('Téléphone 1', _ligne1Controller),
                    field('Téléphone 2', _ligne2Controller),
                  ),
                  const SizedBox(height: 12),
                  field('Adresse', _adresseController),
                  const SizedBox(height: 20),
                  Text(
                    'LOGO',
                    style: TextStyle(
                      fontSize: 11,
                      letterSpacing: 1,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: AppColors.appBg,
                          border: Border.all(color: AppColors.borderSubtle),
                          borderRadius: BorderRadius.circular(12),
                          image: _logoPreviewProvider() != null
                              ? DecorationImage(
                                  image: _logoPreviewProvider()!,
                                  fit: BoxFit.cover,
                                )
                              : null,
                        ),
                        child: _logoPreviewProvider() == null
                            ? Icon(
                                Icons.image_outlined,
                                color: AppColors.textMuted,
                              )
                            : null,
                      ),
                      const SizedBox(width: 14),
                      OutlinedButton.icon(
                        onPressed: _pickLogo,
                        icon: const Icon(Icons.upload_outlined, size: 16),
                        label: const Text('Choisir une image'),
                      ),
                    ],
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 14),
                    Text(
                      _error!,
                      style: const TextStyle(
                        color: AppColors.danger,
                        fontSize: 12,
                      ),
                    ),
                  ],
                  const SizedBox(height: 20),
                  Align(
                    alignment: Alignment.centerRight,
                    child: SizedBox(
                      height: 44,
                      child: FilledButton(
                        onPressed: state.isSubmitting ? null : _submit,
                        child: state.isSubmitting
                            ? const SizedBox(
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text('Enregistrer'),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 20),
        _buildTemplatesSection(),
      ],
    );
  }

  /// Équivalent de "Mon profil" + "Changer le mot de passe" (adProfile.vue,
  /// MON PROFIL UTILISATEUR) — formulaires séparés (PATCH v1/user/profile,
  /// PUT v1/password-change-user-global), tous deux absents du bureau.
  Widget _buildCompteSection() {
    final state = context.watch<AccountState>();

    if (!_compteLoadedOnce && state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    Widget field(String label, TextEditingController c, {TextInputType? type}) {
      return TextField(
        controller: c,
        keyboardType: type,
        decoration: InputDecoration(labelText: label),
      );
    }

    Widget pwField(
      String label,
      TextEditingController c,
      bool obscure,
      VoidCallback toggle,
    ) {
      return TextField(
        controller: c,
        obscureText: obscure,
        decoration: InputDecoration(
          labelText: label,
          suffixIcon: IconButton(
            icon: Icon(
              obscure
                  ? Icons.visibility_off_outlined
                  : Icons.visibility_outlined,
              size: 18,
            ),
            onPressed: toggle,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SectionHeader(
          title: 'Mon compte',
          subtitle: 'Vos informations personnelles',
          icon: Icons.person_outline,
          colorKey: 'amber',
        ),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final twoCols = constraints.maxWidth >= 560;
              Widget row(Widget a, Widget b) {
                if (!twoCols) {
                  return Column(children: [a, const SizedBox(height: 12), b]);
                }
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: a),
                    const SizedBox(width: 16),
                    Expanded(child: b),
                  ],
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  row(
                    field('Prénom', _comptePrenomController),
                    field('Nom', _compteNomController),
                  ),
                  const SizedBox(height: 12),
                  row(
                    field(
                      'Email',
                      _compteEmailController,
                      type: TextInputType.emailAddress,
                    ),
                    field("Nom d'utilisateur", _compteUsernameController),
                  ),
                  if (state.profileError != null) ...[
                    const SizedBox(height: 14),
                    Text(
                      state.profileError!,
                      style: const TextStyle(
                        color: AppColors.danger,
                        fontSize: 12,
                      ),
                    ),
                  ],
                  const SizedBox(height: 20),
                  Align(
                    alignment: Alignment.centerRight,
                    child: SizedBox(
                      height: 44,
                      child: FilledButton(
                        onPressed: state.isSubmittingProfile
                            ? null
                            : _submitCompte,
                        child: state.isSubmittingProfile
                            ? const SizedBox(
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text('Mettre à jour'),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            border: Border.all(color: AppColors.borderSubtle),
            borderRadius: BorderRadius.circular(16),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final threeCols = constraints.maxWidth >= 700;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'CHANGER LE MOT DE PASSE',
                    style: TextStyle(
                      fontSize: 11,
                      letterSpacing: 1,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 14),
                  threeCols
                      ? Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: pwField(
                                'Mot de passe actuel',
                                _pwCurrentController,
                                _obscurePwCurrent,
                                () => setState(
                                  () => _obscurePwCurrent = !_obscurePwCurrent,
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: pwField(
                                'Nouveau mot de passe',
                                _pwNewController,
                                _obscurePwNew,
                                () => setState(
                                  () => _obscurePwNew = !_obscurePwNew,
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: pwField(
                                'Confirmer',
                                _pwConfirmController,
                                _obscurePwConfirm,
                                () => setState(
                                  () => _obscurePwConfirm = !_obscurePwConfirm,
                                ),
                              ),
                            ),
                          ],
                        )
                      : Column(
                          children: [
                            pwField(
                              'Mot de passe actuel',
                              _pwCurrentController,
                              _obscurePwCurrent,
                              () => setState(
                                () => _obscurePwCurrent = !_obscurePwCurrent,
                              ),
                            ),
                            const SizedBox(height: 12),
                            pwField(
                              'Nouveau mot de passe',
                              _pwNewController,
                              _obscurePwNew,
                              () => setState(
                                () => _obscurePwNew = !_obscurePwNew,
                              ),
                            ),
                            const SizedBox(height: 12),
                            pwField(
                              'Confirmer',
                              _pwConfirmController,
                              _obscurePwConfirm,
                              () => setState(
                                () => _obscurePwConfirm = !_obscurePwConfirm,
                              ),
                            ),
                          ],
                        ),
                  if (state.passwordError != null) ...[
                    const SizedBox(height: 14),
                    Text(
                      state.passwordError!,
                      style: const TextStyle(
                        color: AppColors.danger,
                        fontSize: 12,
                      ),
                    ),
                  ],
                  const SizedBox(height: 20),
                  Align(
                    alignment: Alignment.centerRight,
                    child: SizedBox(
                      height: 44,
                      child: FilledButton(
                        onPressed: state.isSubmittingPassword
                            ? null
                            : _submitPassword,
                        child: state.isSubmittingPassword
                            ? const SizedBox(
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text('Changer le mot de passe'),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        if (context.watch<AuthState>().roles.any(
          (r) => ['admin', 'Comptable'].contains(r),
        )) ...[
          const SizedBox(height: 20),
          _buildPinCard(state),
        ],
      ],
    );
  }

  /// Carte "PIN d'autorisation" — uniquement admin/Comptable (cf.
  /// PATCH v1/user/pin, RAcademic.py). Ce PIN permet à un autre rôle de
  /// faire approuver un retour de paiement ou une suppression de vente/
  /// dépense/transaction sans avoir lui-même la permission requise (voir
  /// lib/core/dual_auth.dart).
  Widget _buildPinCard(AccountState state) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'PIN D\'AUTORISATION',
                style: TextStyle(
                  fontSize: 11,
                  letterSpacing: 1,
                  color: AppColors.textMuted,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 10),
              if (state.hasPin)
                Text(
                  'Déjà configuré',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.cardPalette['emerald']!.text,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            "Utilisé par un autre rôle (ex: Caissier) pour faire approuver un retour de paiement ou une suppression sans avoir la permission lui-même.",
            style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: TextField(
                  controller: _pinController,
                  obscureText: true,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  decoration: InputDecoration(
                    labelText: state.hasPin
                        ? 'Nouveau PIN (6 chiffres)'
                        : 'PIN (6 chiffres)',
                    counterText: '',
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextField(
                  controller: _pinConfirmController,
                  obscureText: true,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  decoration: const InputDecoration(
                    labelText: 'Confirmer',
                    counterText: '',
                  ),
                ),
              ),
            ],
          ),
          if (state.pinError != null) ...[
            const SizedBox(height: 14),
            Text(
              state.pinError!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerRight,
            child: SizedBox(
              height: 44,
              child: FilledButton(
                onPressed: state.isSubmittingPin ? null : _submitPin,
                child: state.isSubmittingPin
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(
                        state.hasPin ? 'Modifier le PIN' : 'Enregistrer le PIN',
                      ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Équivalent des 4 liens "Template badge 1/2"/"Template certificat"/
  /// "Template diplome" (Resources/main_school1.ui:19243-19523, frame_393/
  /// frame_394) — sous le formulaire de profil, en grille 2x2.
  Widget _buildTemplatesSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'TEMPLATES DE DOCUMENTS',
            style: TextStyle(
              fontSize: 11,
              letterSpacing: 1,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Utilisés pour la génération du badge (1013-1015×639px). "Certificat"/"Diplôme" sont importables ici, '
            'comme sur le bureau, mais ne sont actuellement utilisés par aucune génération.',
            style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
          ),
          const SizedBox(height: 16),
          LayoutBuilder(
            builder: (context, constraints) {
              final cols = constraints.maxWidth >= 560 ? 2 : 1;
              return GridView.count(
                crossAxisCount: cols,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 14,
                crossAxisSpacing: 14,
                childAspectRatio: 2.6,
                children: [
                  _templateTile('template_badge_1', 'Template badge 1'),
                  _templateTile('template_badge_2', 'Template badge 2'),
                  _templateTile('template_certificat', 'Template certificat'),
                  _templateTile('template_diplome', 'Template diplome'),
                ],
              );
            },
          ),
          if (_templateError != null) ...[
            const SizedBox(height: 12),
            Text(
              _templateError!,
              style: const TextStyle(color: AppColors.danger, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }

  Widget _templateTile(String key, String label) {
    final bytes = _templates[key];
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.appBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              border: Border.all(color: AppColors.borderSubtle),
              borderRadius: BorderRadius.circular(8),
              image: bytes != null
                  ? DecorationImage(
                      image: MemoryImage(bytes),
                      fit: BoxFit.cover,
                    )
                  : null,
            ),
            child: bytes == null
                ? Icon(
                    Icons.image_outlined,
                    color: AppColors.textMuted,
                    size: 20,
                  )
                : null,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: InkWell(
              onTap: () => _pickTemplate(key),
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: AppColors.accentLight,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
