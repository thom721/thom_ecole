import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/student.dart';
import '../../state/auth_state.dart';
import '../../state/reference_data_state.dart';
import '../../state/students_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/data_table_card.dart';
import '../../widgets/pill_button.dart';
import '../../widgets/section_header.dart';
import 'badge_screen.dart';
import 'etudiant_detail_screen.dart';

/// Équivalent de etudiant_page (Resources/main_school1.ui) et
/// set_table_refresh_data_student()/go_to_student_page() (Controllers/Main.py,
/// school_client) pour les DONNÉES/actions de base — étendu, sur demande
/// explicite ("comme le web"), avec les vraies fonctionnalités du frontend
/// web (Etudiants.vue, ecole_nginx/frontend) : bascule actif/inactif
/// (toggleStatus), actions "voir"/"modifier" distinctes, et restriction des
/// boutons d'écriture aux rôles admin/Responsable des admissions/Responsable
/// pédagogique (`canWrite`).
///
/// Volontairement omis — re-vérifié en profondeur (recherche exhaustive
/// dans Controllers/Main.py + Resources/main_school1.ui, au-delà de la
/// première lecture) :
/// - "Importer" (Import Excel) : btn_importer_exel() (Main.py:8097) ouvre
///   un QFileDialog dont le chemin choisi n'est jamais lu nulle part — ni
///   assigné à self, ni traité. Aucune autre logique d'import Excel
///   n'existe dans tout le projet. Bouton mort, confirmé.
/// - "Diplôme" / "Certificat" : diplome_page()/certificat_page() (Main.py)
///   ouvrent une simple table de recherche d'élève — `diplome_page` et
///   `certificat_page` dans Resources/main_school1.ui ne contiennent QUE le
///   champ de recherche et la table, aucun bouton "Générer"/"Imprimer".
///   Aucune fonction de génération de diplôme/certificat n'existe nulle
///   part (recherche exhaustive de QPainter/QPrinter/toPdf combinés à
///   "diplome"/"certificat" : zéro résultat). Boutons morts, confirmés.
///
/// "Badge" EST réellement implémenté côté bureau (make_an_identity_card() →
/// generate_badge()/generate_badge_and_save(), Main.py:5594 et 6114-6267) :
/// compose un badge 1013×638 (photo + nom + classe + identifiant + salle +
/// QR du contact responsable) via QPainter, l'enregistre en PNG local, et
/// synchronise la photo vers le serveur (PATCH v1/save-badge-image) sur
/// "Enregistrer". Repris ici via BadgeScreen (lib/screens/etudiant/
/// badge_screen.dart), webcam comprise (camera_macos).
///
/// "Importer"/"Diplôme"/"Certificat" sont repris ici aussi — sur demande
/// explicite de parité visuelle avec school_client — mais restent fidèles
/// à leur nature réellement morte côté bureau (cf. ci-dessus) : "Importer"
/// ouvre un sélecteur de fichier dont le résultat n'est lu nulle part
/// (btn_importer_exel(), Main.py:8097) ; "Diplôme"/"Certificat" ouvrent une
/// page avec seulement un champ de recherche + table, sans aucun bouton de
/// génération (diplome_page()/certificat_page(), .ui).
class EtudiantScreen extends StatefulWidget {
  const EtudiantScreen({super.key});

  @override
  State<EtudiantScreen> createState() => _EtudiantScreenState();
}

enum _Mode { list, add, edit, badge, diplome, certificat }

class _EtudiantScreenState extends State<EtudiantScreen> {
  final _searchController = TextEditingController();
  _Mode _mode = _Mode.list;
  Student? _selectedStudent;

  /// Statut actif/inactif observé après bascule manuelle dans cette session
  /// — la liste (GET v1/etudiant, EtudiantResponseRead) ne renvoie pas la
  /// relation `user`, donc le statut réel est inconnu tant qu'on n'a pas
  /// basculé au moins une fois (même limitation que toggleStatus() côté web,
  /// qui lit `row?.user?.status`, toujours undefined depuis cette liste).
  final Map<String, bool> _statusOverrides = {};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ReferenceDataState>().loadOnce();
      context.read<StudentsState>().load();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  bool _canWrite(List<String> roles) =>
      roles.contains('admin') ||
      roles.contains('Responsable des admissions') ||
      roles.contains('Responsable pédagogique');

  void _openAdd() => setState(() {
        _selectedStudent = null;
        _mode = _Mode.add;
      });

  void _openEdit(Student s) => setState(() {
        _selectedStudent = s;
        _mode = _Mode.edit;
      });

  void _openBadge([Student? s]) => setState(() {
        _selectedStudent = s;
        _mode = _Mode.badge;
      });

  void _openDiplome() => setState(() => _mode = _Mode.diplome);

  void _openCertificat() => setState(() => _mode = _Mode.certificat);

  /// Équivalent de btn_importer_exel() (Main.py:8097) : ouvre un sélecteur
  /// de fichier dont le résultat n'est lu nulle part dans la source
  /// d'origine — reproduit ici à l'identique (mort, mais présent).
  Future<void> _onImporter() async {
    await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['xlsx', 'xls', 'csv'],
    );
  }

  void _backToList() {
    setState(() => _mode = _Mode.list);
    context.read<StudentsState>().clearDetail();
  }

  Future<void> _toggleActive(Student s) async {
    final result = await context.read<StudentsState>().toggleActive(s.id);
    if (!mounted) return;
    if (result.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.error!)));
    } else if (result.status != null) {
      setState(() => _statusOverrides[s.id] = result.status!);
    }
  }

  Future<void> _confirmDelete(Student student) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer'),
        content: Text('Supprimer ${student.prenom} ${student.nom} ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<StudentsState>().delete(student.id);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_mode != _Mode.list) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
            child: TextButton.icon(
              onPressed: _backToList,
              icon: const Icon(Icons.arrow_back, size: 16),
              label: const Text('Retour à la liste'),
            ),
          ),
          Expanded(
            child: switch (_mode) {
              _Mode.badge => BadgeScreen(initialStudent: _selectedStudent),
              _Mode.diplome => const _DeadSearchTablePage(title: 'Diplôme'),
              _Mode.certificat => const _DeadSearchTablePage(title: 'Certificat'),
              _ => EtudiantDetailScreen(
                  key: ValueKey(_selectedStudent?.id ?? 'new'),
                  student: _selectedStudent,
                ),
            },
          ),
        ],
      );
    }

    final state = context.watch<StudentsState>();
    final auth = context.watch<AuthState>();
    final roles = auth.roles;
    final canWrite = _canWrite(roles);
    // Sous-onglet "etudiant.badge" : configurable dans Vues par rôle.
    // null = pas de restriction → bouton badge visible pour tous.
    final etudiantSubs = auth.visibleSubItems('etudiant');
    final canSeeBadgeButton = etudiantSubs == null || etudiantSubs.contains('badge');

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SectionHeader(
            title: 'Étudiants',
            subtitle: 'Inscriptions, dossiers et scolarité',
            icon: Icons.groups_outlined,
            colorKey: 'blue',
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    if (canWrite)
                      PillButton(
                        label: 'Ajouter étudiant',
                        colorKey: 'blue',
                        icon: Icons.add,
                        onPressed: _openAdd,
                      ),
                    if (canWrite)
                      PillButton(
                        label: 'Importer',
                        colorKey: 'amber',
                        icon: Icons.upload_file_outlined,
                        onPressed: _onImporter,
                      ),
                    PillButton(
                      label: 'Diplôme',
                      colorKey: 'violet',
                      icon: Icons.workspace_premium_outlined,
                      onPressed: _openDiplome,
                    ),
                    PillButton(
                      label: 'Certificat',
                      colorKey: 'cyan',
                      icon: Icons.description_outlined,
                      onPressed: _openCertificat,
                    ),
                    PillButton(
                      label: 'Badge',
                      colorKey: 'rose',
                      icon: Icons.badge_outlined,
                      onPressed: _openBadge,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 300,
                child: TextField(
                  controller: _searchController,
                  style: TextStyle(color: AppColors.textPrimary, fontSize: 13),
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.search, color: AppColors.textMuted, size: 18),
                    hintText: 'Rechercher un étudiant...',
                    isDense: true,
                  ),
                  onSubmitted: (v) => context.read<StudentsState>().load(page: 1, search: v),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.errorMessage != null)
            Expanded(
              child: Center(
                child: Text(state.errorMessage!, style: TextStyle(color: AppColors.textPrimary)),
              ),
            )
          else
            Expanded(
              child: SingleChildScrollView(
                child: DataTableCard(
                  currentPage: state.currentPage,
                  lastPage: state.lastPage,
                  onPageChange: (page) => context.read<StudentsState>().load(page: page),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('IDENTIFIANT')),
                      DataColumn(label: Text('NOM')),
                      DataColumn(label: Text('PRÉNOM')),
                      DataColumn(label: Text('SEXE')),
                      DataColumn(label: Text('TÉLÉPHONE')),
                      DataColumn(label: Text('EMAIL')),
                      DataColumn(label: Text('')),
                    ],
                    rows: state.students.map((s) {
                      final isToggling = state.activatingId == s.id;
                      final override = _statusOverrides[s.id];
                      final badgeColor = override == null
                          ? AppColors.danger
                          : (override ? const Color(0xFF3FB950) : const Color(0xFFF59E0B));
                      return DataRow(cells: [
                        DataCell(
                          isToggling
                              ? const SizedBox(
                                  height: 14,
                                  width: 14,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : InkWell(
                                  onTap: canWrite ? () => _toggleActive(s) : null,
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: badgeColor.withValues(alpha: 0.1),
                                      border: Border.all(color: badgeColor.withValues(alpha: 0.3)),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: Text(
                                      s.identifiant,
                                      style: TextStyle(fontSize: 12, fontFamily: 'monospace', color: badgeColor),
                                    ),
                                  ),
                                ),
                        ),
                        DataCell(Text(s.nom)),
                        DataCell(Text(s.prenom)),
                        DataCell(Text(s.sexe)),
                        DataCell(Text(s.telephone ?? '-')),
                        DataCell(Text(s.email ?? '-')),
                        DataCell(Row(
                          children: [
                            IconButton(
                              tooltip: 'Détails',
                              icon: const Icon(Icons.visibility_outlined, size: 17, color: Color(0xFF34D399)),
                              onPressed: () => _openEdit(s),
                            ),
                            if (canWrite)
                              IconButton(
                                tooltip: 'Modifier',
                                icon: Icon(Icons.edit_outlined, size: 17, color: AppColors.accentLight),
                                onPressed: () => _openEdit(s),
                              ),
                            if (canSeeBadgeButton)
                              IconButton(
                                tooltip: 'Badge',
                                icon: const Icon(Icons.badge_outlined, size: 17, color: Color(0xFFF472B6)),
                                onPressed: () => _openBadge(s),
                              ),
                            if (canWrite)
                              IconButton(
                                tooltip: 'Supprimer',
                                icon: const Icon(Icons.delete_outline, size: 17, color: AppColors.danger),
                                onPressed: () => _confirmDelete(s),
                              ),
                          ],
                        )),
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

/// Équivalent de diplome_page()/certificat_page() (Resources/main_school1.ui)
/// : un simple champ de recherche + table, sans aucun bouton de génération
/// — fidèlement repris à l'identique (page réellement morte côté bureau).
class _DeadSearchTablePage extends StatefulWidget {
  const _DeadSearchTablePage({required this.title});

  final String title;

  @override
  State<_DeadSearchTablePage> createState() => _DeadSearchTablePageState();
}

class _DeadSearchTablePageState extends State<_DeadSearchTablePage> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StudentsState>();

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SectionHeader(
            title: widget.title,
            subtitle: 'Recherche d’un étudiant',
            icon: Icons.search,
            colorKey: 'violet',
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _searchController,
            decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search, size: 18),
              hintText: 'Rechercher un étudiant...',
              isDense: true,
            ),
            onChanged: (v) => context.read<StudentsState>().searchLive(v),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: state.isSearchingLive
                ? const Center(child: CircularProgressIndicator())
                : SingleChildScrollView(
                    child: DataTable(
                      columns: const [
                        DataColumn(label: Text('IDENTIFIANT')),
                        DataColumn(label: Text('NOM')),
                        DataColumn(label: Text('PRÉNOM')),
                      ],
                      rows: state.liveSearchResults
                          .map((s) => DataRow(cells: [
                                DataCell(Text(s.identifiant)),
                                DataCell(Text(s.nom)),
                                DataCell(Text(s.prenom)),
                              ]))
                          .toList(),
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
