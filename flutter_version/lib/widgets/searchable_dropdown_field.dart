import 'package:flutter/material.dart';

/// Dropdown de sélection avec recherche par saisie de texte, pour les
/// listes trop longues pour un DropdownButtonFormField classique (ex.
/// liste de professeurs/cours/matières). Reprend le pattern Autocomplete
/// déjà utilisé pour la recherche d'étudiants (classe_students_dialog.dart)
/// plutôt que d'introduire un package externe.
///
/// [selectedId] pilote uniquement le texte affiché à la création du
/// widget (comme `initialValue` d'un DropdownButtonFormField) — s'il
/// change après coup (ex. valeur chargée en asynchrone), le rebuild seul
/// ne suffit pas : donner à ce widget une `Key` qui change une fois la
/// bonne valeur disponible pour forcer un remount (même limitation que
/// DropdownButtonFormField.initialValue).
class SearchableDropdownField<T extends Object> extends StatelessWidget {
  const SearchableDropdownField({
    super.key,
    required this.options,
    required this.displayStringForOption,
    required this.idOf,
    required this.labelText,
    required this.onSelected,
    this.selectedId,
    this.isDense = false,
    this.enabled = true,
  });

  final List<T> options;
  final String Function(T) displayStringForOption;
  final String Function(T) idOf;
  final String labelText;
  final ValueChanged<T> onSelected;
  final String? selectedId;
  final bool isDense;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    T? selected;
    if (selectedId != null) {
      for (final o in options) {
        if (idOf(o) == selectedId) {
          selected = o;
          break;
        }
      }
    }
    final initialText = selected != null ? displayStringForOption(selected) : '';

    return Autocomplete<T>(
      initialValue: TextEditingValue(text: initialText),
      displayStringForOption: displayStringForOption,
      optionsBuilder: (value) {
        if (value.text.isEmpty) return options;
        final q = value.text.toLowerCase();
        return options.where((o) => displayStringForOption(o).toLowerCase().contains(q));
      },
      onSelected: onSelected,
      fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) => TextField(
        controller: controller,
        focusNode: focusNode,
        enabled: enabled,
        decoration: InputDecoration(labelText: labelText, isDense: isDense),
      ),
    );
  }
}
