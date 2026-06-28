import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/dashboard_charts.dart';
import '../../models/student.dart' as student_models;
import '../../state/dashboard_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../etudiant/etudiant_detail_screen.dart';

/// Équivalent du dialogue "Liste des élèves de la classe" ouvert par
/// on_row_clicked_class_show() (Controllers/Main.py:7346) après réception
/// de GET v1/student-with-classe (handle_request_completion(), lignes
/// 2883-3077) — réellement présent dans school_client, contrairement à ce
/// que laissait penser le dialogue commenté plus bas dans le même fichier.
Future<void> showClasseStudentsDialog(
  BuildContext context, {
  required String classeId,
  required String anneeId,
  required String nomClasse,
}) {
  context.read<DashboardState>().loadClasseStudents(classeId: classeId, anneeId: anneeId);
  context.read<ReferenceDataState>().loadOnce();
  return showDialog(
    context: context,
    builder: (_) => _ClasseStudentsDialog(nomClasse: nomClasse),
  );
}

class _ClasseStudentsDialog extends StatefulWidget {
  const _ClasseStudentsDialog({required this.nomClasse});

  final String nomClasse;

  @override
  State<_ClasseStudentsDialog> createState() => _ClasseStudentsDialogState();
}

class _ClasseStudentsDialogState extends State<_ClasseStudentsDialog> {
  // Équivalent de student_change/level_change/classe_change/
  // annee_academique_change (QComboBox de la barre d'outils) — purement
  // locaux à ce dialogue, comme dans school_client. Ce combo "Étudiant" ne
  // filtre PAS le tableau ci-dessous (qui montre toujours tous les élèves
  // de la classe) : il ne sert qu'à choisir qui déplacer via "Modifier".
  ClasseStudentRow? _selectedStudent;
  String? _selectedNiveauId;
  String? _selectedClasseId;
  String? _selectedAnneeId;

  /// Équivalent de change_student_class() (Controllers/Main.py:3517) : dans
  /// le bureau réel, l'appel API est commenté — seule la validation des
  /// champs existe, le bouton "Modifier" ne fait donc rien de plus.
  void _onModifier() {
    if (_selectedStudent == null || _selectedClasseId == null) return;
  }

  Future<void> _confirmAndToggleStatus(ClasseStudentRow row) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Confirmation'),
        content: const Text("Voulez-vous vraiment changer le statut de l'élève ?"),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Non')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Oui')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<DashboardState>().updateClasseStudentStatus(
          classeEtudiantId: row.idClsEtudiant,
          delete: false,
        );
    if (error != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  Future<void> _confirmAndDelete(ClasseStudentRow row) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Confirmation'),
        content: const Text('Voulez-vous vraiment supprimer l\'élève de la classe?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Non')),
          FilledButton(onPressed: () => Navigator.of(context).pop(true), child: const Text('Oui')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    final error = await context.read<DashboardState>().updateClasseStudentStatus(
          classeEtudiantId: row.idClsEtudiant,
          delete: true,
        );
    if (error != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  /// Équivalent de on_row_clicked_Show() (Controllers/Main.py:7495) : le
  /// clic sur une ligne (hors case/bouton) ouvre la fiche de l'élève.
  void _openStudent(ClasseStudentRow row) {
    // On capture le NavigatorState AVANT de fermer le dialogue : après
    // pop(), le BuildContext de ce widget est en cours de démontage, donc
    // un second Navigator.of(context) sur ce même context serait fragile.
    final navigator = Navigator.of(context);
    navigator.pop();
    navigator.push(
      MaterialPageRoute(
        // EtudiantDetailScreen n'a pas son propre Scaffold (elle est conçue
        // pour vivre dans la zone de contenu d'AppShell, déjà à l'intérieur
        // d'un Scaffold) — en la poussant directement depuis ce dialogue,
        // il lui faut un ancêtre Material explicite, sinon les
        // DropdownButton/TextField internes plantent ("No Material widget
        // found"). Un AppBar (avec sa flèche de retour automatique tant que
        // Navigator.canPop est vrai) est en plus indispensable ici : cette
        // route remplace TOUT l'écran (sidebar d'AppShell comprise), donc
        // sans elle l'utilisateur reste bloqué sans aucun moyen de revenir
        // en arrière — contrairement à l'usage normal d'EtudiantDetailScreen
        // (EtudiantScreen._Mode), qui fournit son propre bouton "Retour à la
        // liste" au-dessus, lui aussi absent ici.
        builder: (_) => Scaffold(
          backgroundColor: AppColors.appBg,
          appBar: AppBar(
            backgroundColor: AppColors.appBg,
            elevation: 0,
            title: Text("Fiche de l'élève — ${row.nom} ${row.prenom}"),
          ),
          body: EtudiantDetailScreen(
            student: student_models.Student(
              id: row.id,
              identifiant: row.identifiant,
              nom: row.nom,
              prenom: row.prenom,
              sexe: row.sexe,
              dateDeNaissance: '',
              adresse: '',
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardState>();
    final reference = context.watch<ReferenceDataState>();
    final classesForNiveau = reference.classesForNiveau(_selectedNiveauId);

    return Dialog(
      backgroundColor: AppColors.cardBg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 900, maxHeight: 640),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 18, 12, 14),
              child: Row(
                children: [
                  Expanded(
                    child: Text('Liste des élèves de la classe — ${widget.nomClasse}',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  ),
                  IconButton(icon: const Icon(Icons.close, size: 18), onPressed: () => Navigator.of(context).pop()),
                ],
              ),
            ),
            Divider(color: AppColors.borderSubtle, height: 1),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 6),
              child: Wrap(
                spacing: 10,
                runSpacing: 10,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  SizedBox(
                    width: 220,
                    child: Autocomplete<ClasseStudentRow>(
                      displayStringForOption: (s) => '${s.nom} ${s.prenom}',
                      optionsBuilder: (value) {
                        if (value.text.isEmpty) return dashboard.classeStudents;
                        final q = value.text.toLowerCase();
                        return dashboard.classeStudents
                            .where((s) => '${s.nom} ${s.prenom}'.toLowerCase().contains(q));
                      },
                      onSelected: (s) => setState(() => _selectedStudent = s),
                      fieldViewBuilder: (context, controller, focusNode, onSubmit) => TextField(
                        controller: controller,
                        focusNode: focusNode,
                        decoration: const InputDecoration(labelText: 'Étudiant', isDense: true),
                      ),
                    ),
                  ),
                  SizedBox(
                    width: 150,
                    child: DropdownButtonFormField<String>(
                      initialValue: _selectedNiveauId,
                      isDense: true,
                      decoration: const InputDecoration(labelText: 'Niveau/Cycle', isDense: true),
                      items: reference.niveaux
                          .map((n) => DropdownMenuItem(value: n.id, child: Text(n.name)))
                          .toList(),
                      onChanged: (v) => setState(() {
                        _selectedNiveauId = v;
                        _selectedClasseId = null;
                      }),
                    ),
                  ),
                  SizedBox(
                    width: 150,
                    child: DropdownButtonFormField<String>(
                      initialValue: _selectedClasseId,
                      isDense: true,
                      decoration: const InputDecoration(labelText: 'Classe', isDense: true),
                      items: classesForNiveau
                          .map((c) => DropdownMenuItem(value: c.id, child: Text(c.nomClasse)))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedClasseId = v),
                    ),
                  ),
                  SizedBox(
                    width: 150,
                    child: DropdownButtonFormField<String>(
                      initialValue: _selectedAnneeId,
                      isDense: true,
                      decoration: const InputDecoration(labelText: 'Année académique', isDense: true),
                      items: reference.annees
                          .map((a) => DropdownMenuItem(value: a.id, child: Text(a.nom)))
                          .toList(),
                      onChanged: (v) => setState(() => _selectedAnneeId = v),
                    ),
                  ),
                  OutlinedButton(onPressed: _onModifier, child: const Text('Modifier')),
                ],
              ),
            ),
            Divider(color: AppColors.borderSubtle, height: 1),
            Expanded(
              child: dashboard.isLoadingClasseStudents
                  ? const Center(child: CircularProgressIndicator())
                  : dashboard.classeStudentsError != null
                      ? Center(
                          child: Text(dashboard.classeStudentsError!, style: const TextStyle(color: AppColors.danger)))
                      : dashboard.classeStudents.isEmpty
                          ? Center(
                              child: Text('Aucun élève trouvé.', style: TextStyle(color: AppColors.textMuted)))
                          : SingleChildScrollView(
                              child: SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: DataTable(
                                  columns: const [
                                    DataColumn(label: Text('ID')),
                                    DataColumn(label: Text('IDENTIFIANT')),
                                    DataColumn(label: Text('NOM')),
                                    DataColumn(label: Text('PRÉNOM')),
                                    DataColumn(label: Text('SEXE')),
                                    DataColumn(label: Text('ACTIF')),
                                    DataColumn(label: Text('')),
                                  ],
                                  rows: dashboard.classeStudents.map((s) {
                                    return DataRow(
                                      onSelectChanged: (_) => _openStudent(s),
                                      cells: [
                                        DataCell(Text(s.id, style: const TextStyle(fontSize: 11, fontFamily: 'monospace'))),
                                        DataCell(Text(s.identifiant)),
                                        DataCell(Text(s.nom)),
                                        DataCell(Text(s.prenom)),
                                        DataCell(Text(s.sexe)),
                                        DataCell(
                                          Checkbox(
                                            value: s.statusClsEtudiant,
                                            onChanged: (_) => _confirmAndToggleStatus(s),
                                          ),
                                        ),
                                        DataCell(
                                          TextButton(
                                            onPressed: () => _confirmAndDelete(s),
                                            style: TextButton.styleFrom(foregroundColor: AppColors.danger),
                                            child: const Text('Supprimer'),
                                          ),
                                        ),
                                      ],
                                    );
                                  }).toList(),
                                ),
                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }
}
