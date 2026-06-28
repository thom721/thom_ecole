import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/presence.dart';
import '../../state/presence_state.dart';
import '../../state/reference_data_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/pill_button.dart';

const _moisFr = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'octobre',
  'novembre',
  'décembre',
];
const _joursFr = [
  'lundi',
  'mardi',
  'mercredi',
  'jeudi',
  'vendredi',
  'samedi',
  'dimanche',
];

String _formatDateLong(DateTime d) =>
    '${_joursFr[d.weekday - 1]} ${d.day} ${_moisFr[d.month - 1]} ${d.year}';

/// Équivalent de l'onglet "Appel du jour" de Presences.vue.
class AppelTab extends StatefulWidget {
  const AppelTab({super.key});

  @override
  State<AppelTab> createState() => _AppelTabState();
}

class _AppelTabState extends State<AppelTab> {
  String? _niveauId;
  String? _classeId;
  String? _anneeId;
  late DateTime _date = DateTime.now();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await context.read<ReferenceDataState>().loadOnce();
      _maybeLoad();
    });
  }

  void _maybeLoad() {
    if (_classeId != null && _anneeId != null) {
      context.read<PresenceState>().loadAppel(
        classeId: _classeId!,
        anneeId: _anneeId!,
        date: _todayIsoFor(_date),
      );
    }
  }

  String _todayIsoFor(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _date,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => _date = picked);
      _maybeLoad();
    }
  }

  Future<void> _save() async {
    if (_classeId == null || _anneeId == null) return;
    await context.read<PresenceState>().saveAppel(
      classeId: _classeId!,
      anneeId: _anneeId!,
      date: _todayIsoFor(_date),
    );
  }

  @override
  Widget build(BuildContext context) {
    final refData = context.watch<ReferenceDataState>();
    final state = context.watch<PresenceState>();
    final classesForNiveau = refData.classesForNiveau(_niveauId);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _niveauId,
                decoration: const InputDecoration(labelText: 'Niveau'),
                items: refData.niveaux
                    .map(
                      (n) => DropdownMenuItem(value: n.id, child: Text(n.name)),
                    )
                    .toList(),
                onChanged: (v) => setState(() {
                  _niveauId = v;
                  _classeId = null;
                }),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _classeId,
                decoration: const InputDecoration(labelText: 'Classe'),
                items: classesForNiveau
                    .map(
                      (c) => DropdownMenuItem(
                        value: c.id,
                        child: Text(c.nomClasse),
                      ),
                    )
                    .toList(),
                onChanged: _niveauId == null
                    ? null
                    : (v) {
                        setState(() => _classeId = v);
                        _maybeLoad();
                      },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _anneeId,
                decoration: const InputDecoration(
                  labelText: 'Année académique',
                ),
                items: refData.annees
                    .map(
                      (a) => DropdownMenuItem(value: a.id, child: Text(a.nom)),
                    )
                    .toList(),
                onChanged: (v) {
                  setState(() => _anneeId = v);
                  _maybeLoad();
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: InkWell(
                onTap: _pickDate,
                child: InputDecorator(
                  decoration: const InputDecoration(labelText: 'Date'),
                  child: Text(_todayIsoFor(_date)),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (_classeId == null || _anneeId == null)
          Expanded(
            child: Center(
              child: Text(
                'Sélectionnez une classe et une année académique.',
                style: TextStyle(color: AppColors.textMuted),
              ),
            ),
          )
        else if (state.isLoadingAppel)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (state.appelError != null)
          Expanded(
            child: Center(
              child: Text(
                state.appelError!,
                style: TextStyle(color: AppColors.textPrimary),
              ),
            ),
          )
        else
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.sidebarBg,
                border: Border.all(color: AppColors.borderSubtle),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          _formatDateLong(_date),
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ),
                      if (state.dejaEnregistre)
                        Container(
                          margin: const EdgeInsets.only(right: 8),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 3,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.accent.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'Déjà enregistré',
                            style: TextStyle(
                              fontSize: 11,
                              color: AppColors.accentLight,
                            ),
                          ),
                        ),
                      _CountBadge(
                        label: '${state.presentsCount} présents',
                        color: const Color(0xFF34D399),
                      ),
                      const SizedBox(width: 8),
                      _CountBadge(
                        label: '${state.absentsCount} absents',
                        color: AppColors.danger,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      PillButton(
                        label: 'Tous présents',
                        colorKey: 'emerald',
                        icon: Icons.check_circle_outline,
                        onPressed: () => state.markAll(true),
                      ),
                      const SizedBox(width: 8),
                      PillButton(
                        label: 'Tous absents',
                        colorKey: 'rose',
                        icon: Icons.cancel_outlined,
                        onPressed: () => state.markAll(false),
                      ),
                      const Spacer(),
                      FilledButton.icon(
                        onPressed: state.isSavingAppel ? null : _save,
                        icon: state.isSavingAppel
                            ? const SizedBox(
                                height: 14,
                                width: 14,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.save_outlined, size: 16),
                        label: const Text("Enregistrer l'appel"),
                      ),
                    ],
                  ),
                  if (state.appelSuccess != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      state.appelSuccess!,
                      style: const TextStyle(
                        color: Color(0xFF34D399),
                        fontSize: 12.5,
                      ),
                    ),
                  ],
                  const SizedBox(height: 12),
                  Divider(color: AppColors.borderSubtle),
                  Expanded(
                    child: state.appelStudents.isEmpty
                        ? Center(
                            child: Text(
                              'Aucun élève dans cette classe.',
                              style: TextStyle(color: AppColors.textMuted),
                            ),
                          )
                        : ListView.separated(
                            itemCount: state.appelStudents.length,
                            separatorBuilder: (_, _) => Divider(
                              height: 1,
                              color: AppColors.borderSubtle,
                            ),
                            itemBuilder: (context, index) => _StudentRow(
                              index: index + 1,
                              student: state.appelStudents[index],
                            ),
                          ),
                  ),
                  Divider(color: AppColors.borderSubtle),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _RecapStat(
                        label: 'Total',
                        value: '${state.appelStudents.length}',
                      ),
                      _RecapStat(
                        label: 'Présents',
                        value: '${state.presentsCount}',
                      ),
                      _RecapStat(
                        label: 'Absents',
                        value: '${state.absentsCount}',
                      ),
                      _RecapStat(
                        label: 'Non marqués',
                        value: '${state.nonMarquesCount}',
                        color: const Color(0xFFFBBF24),
                      ),
                      _RecapStat(
                        label: 'Taux de présence',
                        value: '${state.tauxAppel.toStringAsFixed(0)}%',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _CountBadge extends StatelessWidget {
  const _CountBadge({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11.5,
          fontWeight: FontWeight.w500,
          color: color,
        ),
      ),
    );
  }
}

class _RecapStat extends StatelessWidget {
  const _RecapStat({required this.label, required this.value, this.color});

  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: color ?? AppColors.textPrimary,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: AppColors.textMuted),
        ),
      ],
    );
  }
}

class _StudentRow extends StatelessWidget {
  const _StudentRow({required this.index, required this.student});

  final int index;
  final PresenceStudent student;

  @override
  Widget build(BuildContext context) {
    final state = context.read<PresenceState>();
    final Color avatarColor = student.valeur == null
        ? AppColors.textMuted
        : student.valeur == true
        ? const Color(0xFF34D399)
        : const Color(0xFF7F1D1D);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 28,
            child: Text(
              '$index',
              style: TextStyle(fontSize: 12, color: AppColors.textMuted),
            ),
          ),
          CircleAvatar(
            radius: 16,
            backgroundColor: avatarColor.withValues(alpha: 0.2),
            child: Text(
              student.initiales,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: avatarColor,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  student.fullName,
                  style: TextStyle(
                    fontSize: 13,
                    color: AppColors.textPrimary,
                  ),
                ),
                if (student.matricule != null)
                  Text(
                    student.matricule!,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textMuted,
                    ),
                  ),
              ],
            ),
          ),
          _ToggleButton(
            label: 'Présent',
            icon: Icons.check,
            active: student.valeur == true,
            activeColor: const Color(0xFF34D399),
            onTap: () => state.toggleValeur(student, true),
          ),
          const SizedBox(width: 6),
          _ToggleButton(
            label: 'Absent',
            icon: Icons.close,
            active: student.valeur == false,
            activeColor: AppColors.danger,
            onTap: () => state.toggleValeur(student, false),
          ),
        ],
      ),
    );
  }
}

class _ToggleButton extends StatelessWidget {
  const _ToggleButton({
    required this.label,
    required this.icon,
    required this.active,
    required this.activeColor,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool active;
  final Color activeColor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: active ? activeColor.withValues(alpha: 0.18) : AppColors.cardBg,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 14,
                color: active ? activeColor : AppColors.textMuted,
              ),
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11.5,
                  color: active ? activeColor : AppColors.textMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
