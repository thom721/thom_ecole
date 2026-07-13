import 'package:flutter/material.dart';

import '../../../models/badge_layout.dart';
import '../../../theme/app_theme.dart';

/// Liste fermée/curatée, cohérente avec le style déjà établi dans ce code
/// (`_moisNoms`/`_salles` dans badge_screen.dart) — pas de sélecteur
/// Google Fonts ouvert, jamais utilisé pour du contenu ailleurs dans
/// l'app (seulement pour le chrome, via `theme/app_theme.dart`). Élargie
/// sur demande explicite — polices courantes sur Windows ET macOS (les
/// deux plateformes cibles de cette app), pas un choix arbitraire.
const _fontFamilies = [
  'Roboto',
  'Arial',
  'Helvetica',
  'Georgia',
  'Times New Roman',
  'Courier New',
  'Consolas',
  'Verdana',
  'Tahoma',
  'Trebuchet MS',
  'Segoe UI',
  'Calibri',
  'Cambria',
  'Garamond',
  'Palatino Linotype',
  'Century Gothic',
  'Franklin Gothic Medium',
  'Impact',
  'Comic Sans MS',
];

/// Grille de nuances élargie — pas de package sélecteur de couleur, pour
/// limiter les nouvelles dépendances (voir le plan de cette
/// fonctionnalité) ; le champ hexadécimal juste en dessous couvre le
/// reste (n'importe quelle couleur, pas seulement celles listées ici).
const _colorSwatches = [
  0xFF000000,
  0xFF404040,
  0xFF7C83A0,
  0xFFD1D5DB,
  0xFFFFFFFF,
  0xFF003366,
  0xFF1A73E8,
  0xFF0EA5E9,
  0xFF06B6D4,
  0xFF10B981,
  0xFF34A853,
  0xFF84CC16,
  0xFFFCBC05,
  0xFFF59E0B,
  0xFFEA580C,
  0xFFE74C3C,
  0xFFDC2626,
  0xFFF43F5E,
  0xFFEC4899,
  0xFF9B59B6,
  0xFF8B5CF6,
  0xFF6366F1,
  0xFFC9A84C,
];

/// Panneau contextuel de l'éditeur de badge — champs affichés selon le
/// type de [element] sélectionné. [element] est mutable (voir
/// `models/badge_layout.dart`) : chaque champ modifie directement ses
/// propriétés puis appelle [onChanged] pour que l'appelant déclenche un
/// `setState`.
class BadgeBuilderPropertyPanel extends StatelessWidget {
  const BadgeBuilderPropertyPanel({
    super.key,
    required this.element,
    required this.onChanged,
    this.onCaptureTestPhoto,
    this.onLoadTestPhoto,
    this.onPickElementImage,
    this.editingPoints = false,
    this.onToggleEditPoints,
  });

  final BadgeElement? element;
  final ValueChanged<BadgeElement> onChanged;

  /// `true` quand [element] (un tracé, `shapeKind == path`) est ACTUELLEMENT
  /// la cible du mode "Modifier les points" (voir badge_builder_canvas.dart::
  /// insertPathPoint et badge_builder_screen.dart::_editingPathElementId) —
  /// pilote le libellé du bouton (bascule Activer/Terminer).
  final bool editingPoints;

  /// Bascule le mode "Modifier les points" pour [element] — géré par
  /// l'écran (qui seul connaît quel élément est actuellement édité, pour
  /// pouvoir en sortir si la sélection change).
  final VoidCallback? onToggleEditPoints;

  /// Ouvre le dialogue de capture caméra (badge_test_photo_capture_dialog.dart)
  /// pour calibrer visuellement les réglages ci-dessous — géré par l'écran
  /// (badge_builder_screen.dart), pas par ce panneau, qui reste un simple
  /// éditeur de propriétés.
  final VoidCallback? onCaptureTestPhoto;

  /// Ouvre le sélecteur de fichier pour la photo test — même raison que
  /// [onCaptureTestPhoto].
  final VoidCallback? onLoadTestPhoto;

  /// Ouvre le sélecteur de fichier pour choisir/remplacer l'image d'un
  /// élément `BadgeElementType.staticImage` — géré par l'écran
  /// (`BadgeLayoutStore.pickElementImage`), même raison que
  /// [onCaptureTestPhoto].
  final VoidCallback? onPickElementImage;

  @override
  Widget build(BuildContext context) {
    final el = element;
    return Container(
      width: 280,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(12),
      ),
      child: el == null
          ? Center(
              child: Text(
                'Sélectionnez un élément pour modifier ses propriétés.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textMuted, fontSize: 12.5),
              ),
            )
          : SingleChildScrollView(
              key: ValueKey(el.id),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _typeLabel(el.type),
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _geometryFields(el),
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 14),
                    child: Divider(height: 1),
                  ),
                  if (el.type == BadgeElementType.text) _textFields(el),
                  if (el.type == BadgeElementType.shape) _shapeFields(el),
                  if (el.type == BadgeElementType.photoPlaceholder)
                    _photoFields(el),
                  if (el.type == BadgeElementType.qrPlaceholder) _qrFields(el),
                  if (el.type == BadgeElementType.staticImage)
                    _staticImageFields(el),
                ],
              ),
            ),
    );
  }

  String _typeLabel(BadgeElementType type) => switch (type) {
    BadgeElementType.text => 'Texte',
    BadgeElementType.shape => 'Forme / trait',
    BadgeElementType.photoPlaceholder => 'Emplacement photo',
    BadgeElementType.qrPlaceholder => 'Emplacement QR code',
    BadgeElementType.staticImage => 'Image (logo, signature...)',
  };

  void _emit(BadgeElement el) => onChanged(el);

  Widget _label(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Text(
      text,
      style: TextStyle(fontSize: 11.5, color: AppColors.textMuted),
    ),
  );

  /// Valide sur Entrée ET sur perte de focus (`_CommitOnBlurField`) —
  /// cliquer ailleurs (ex. sur le canevas) après avoir tapé une valeur
  /// l'applique désormais, alors qu'un simple `onFieldSubmitted` (Entrée
  /// uniquement) perdait silencieusement la saisie si on ne pensait pas à
  /// appuyer sur Entrée. [decimals] contrôle le format affiché/attendu
  /// (0 pour les coordonnées/tailles en pixels, 2 pour un décalage 0..1).
  Widget _numberField(
    String label,
    double value,
    ValueChanged<double> onSet, {
    int decimals = 0,
    double width = 118,
  }) {
    return _CommitOnBlurField(
      width: width,
      label: label,
      displayValue: value.toStringAsFixed(decimals),
      keyboardType: TextInputType.numberWithOptions(
        signed: true,
        decimal: decimals > 0,
      ),
      onCommit: (v) {
        final parsed = double.tryParse(v);
        if (parsed != null) onSet(parsed);
      },
    );
  }

  Widget _geometryFields(BadgeElement el) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _numberField('X', el.x, (v) {
          el.x = v;
          _emit(el);
        }),
        _numberField('Y', el.y, (v) {
          el.y = v;
          _emit(el);
        }),
        _numberField('Largeur', el.width, (v) {
          el.width = v;
          _emit(el);
        }),
        _numberField('Hauteur', el.height, (v) {
          el.height = v;
          _emit(el);
        }),
        _numberField('Rotation °', el.rotationDegrees, (v) {
          el.rotationDegrees = v;
          _emit(el);
        }),
      ],
    );
  }

  Widget _textFields(BadgeElement el) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          // La clé ne doit PAS dépendre de `el.text` : ce champ suit la
          // frappe en direct via `onChanged`, donc `el.text` change à
          // chaque caractère — l'inclure dans la clé forcerait un
          // remontage (et donc une perte de focus) après chaque touche.
          // Seul un changement d'élément sélectionné (`el.id`) doit
          // remonter le champ pour rafraîchir `initialValue`.
          key: ValueKey('text-${el.id}'),
          initialValue: el.text ?? '',
          decoration: const InputDecoration(labelText: 'Texte', isDense: true),
          maxLines: 2,
          onChanged: (v) {
            el.text = v;
            _emit(el);
          },
        ),
        const SizedBox(height: 8),
        _label('Jetons de substitution'),
        Wrap(
          spacing: 4,
          runSpacing: 4,
          children: kBadgePlaceholderTokens
              .map(
                (token) => ActionChip(
                  visualDensity: VisualDensity.compact,
                  label: Text(token, style: const TextStyle(fontSize: 10.5)),
                  onPressed: () {
                    el.text = '${el.text ?? ''}$token';
                    _emit(el);
                  },
                ),
              )
              .toList(),
        ),
        const SizedBox(height: 14),
        DropdownButtonFormField<String>(
          key: ValueKey('font-${el.id}'),
          initialValue: el.fontFamily ?? _fontFamilies.first,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Police', isDense: true),
          items: _fontFamilies
              .map(
                (f) => DropdownMenuItem(
                  value: f,
                  child: Text(f, style: TextStyle(fontFamily: f)),
                ),
              )
              .toList(),
          onChanged: (v) {
            if (v == null) return;
            el.fontFamily = v;
            _emit(el);
          },
        ),
        const SizedBox(height: 10),
        _numberField('Taille', el.fontSize ?? 16, (v) {
          el.fontSize = v;
          _emit(el);
        }),
        const SizedBox(height: 10),
        Wrap(
          spacing: 6,
          children: [
            FilterChip(
              label: const Text('Gras'),
              visualDensity: VisualDensity.compact,
              selected: el.bold,
              onSelected: (v) {
                el.bold = v;
                _emit(el);
              },
            ),
            FilterChip(
              label: const Text('Italique'),
              visualDensity: VisualDensity.compact,
              selected: el.italic,
              onSelected: (v) {
                el.italic = v;
                _emit(el);
              },
            ),
          ],
        ),
        const SizedBox(height: 10),
        SegmentedButton<BadgeTextAlign>(
          segments: const [
            ButtonSegment(
              value: BadgeTextAlign.left,
              icon: Icon(Icons.format_align_left, size: 16),
            ),
            ButtonSegment(
              value: BadgeTextAlign.center,
              icon: Icon(Icons.format_align_center, size: 16),
            ),
            ButtonSegment(
              value: BadgeTextAlign.right,
              icon: Icon(Icons.format_align_right, size: 16),
            ),
          ],
          selected: {el.textAlign},
          onSelectionChanged: (s) {
            el.textAlign = s.first;
            _emit(el);
          },
        ),
        const SizedBox(height: 14),
        _label('Couleur du texte'),
        _colorSwatchGrid(el.color, (c) {
          el.color = c;
          _emit(el);
        }, allowNone: false),
      ],
    );
  }

  Widget _shapeFields(BadgeElement el) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<BadgeShapeKind>(
          key: ValueKey('shape-${el.id}'),
          initialValue: el.shapeKind ?? BadgeShapeKind.rectangle,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Forme', isDense: true),
          items: const [
            DropdownMenuItem(
              value: BadgeShapeKind.rectangle,
              child: Text('Rectangle'),
            ),
            DropdownMenuItem(
              value: BadgeShapeKind.roundedRectangle,
              child: Text('Rectangle arrondi'),
            ),
            DropdownMenuItem(value: BadgeShapeKind.oval, child: Text('Ovale')),
            DropdownMenuItem(value: BadgeShapeKind.line, child: Text('Trait')),
            DropdownMenuItem(
              value: BadgeShapeKind.curve,
              child: Text('Courbe'),
            ),
            DropdownMenuItem(
              value: BadgeShapeKind.path,
              child: Text('Tracé libre (plume)'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            el.shapeKind = v;
            _emit(el);
          },
        ),
        if (el.shapeKind == BadgeShapeKind.roundedRectangle) ...[
          const SizedBox(height: 10),
          _numberField('Rayon des coins', el.cornerRadius ?? 8, (v) {
            el.cornerRadius = v;
            _emit(el);
          }),
        ],
        if (el.shapeKind == BadgeShapeKind.curve) ...[
          const SizedBox(height: 10),
          _numberField(
            'Hauteur de la courbe',
            el.cornerRadius ?? (el.height / 2),
            (v) {
              el.cornerRadius = v;
              _emit(el);
            },
          ),
        ],
        if (el.shapeKind == BadgeShapeKind.path) ...[
          const SizedBox(height: 10),
          // Un tracé plume terminé "ouvert" (bouton "Terminer (ouvert)" ou
          // annulé avant de rejoindre le premier point) n'accepte aucun
          // remplissage — voir badge_layout_renderer.dart::_drawShape et
          // badge_builder_canvas.dart::_ShapePreviewPainter, qui sautent
          // volontairement le remplissage d'un tracé ouvert (une forme non
          // refermée n'a pas d'intérieur bien défini). Ce bouton permet de
          // refermer un tracé déjà posé sans avoir à le redessiner.
          InkWell(
            key: ValueKey('path-closed-${el.id}'),
            onTap: () {
              el.pathClosed = !el.pathClosed;
              _emit(el);
            },
            child: Row(
              children: [
                Checkbox(
                  value: el.pathClosed,
                  onChanged: (v) {
                    el.pathClosed = v ?? el.pathClosed;
                    _emit(el);
                  },
                ),
                const Expanded(
                  child: Text(
                    'Forme fermée (autorise le remplissage)',
                    style: TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          // Mode "Modifier les points" — voir badge_builder_canvas.dart
          // (insertPathPoint, poignées d'ancrage) : cliquer sur le tracé
          // (pas sur une ancre existante) ajoute un point ; glisser une
          // ancre existante la déplace. Contrairement à l'outil plume
          // (barre d'outils, dessine un NOUVEAU tracé), ce bouton retouche
          // le tracé DÉJÀ posé et sélectionné.
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              key: ValueKey('edit-points-${el.id}'),
              onPressed: onToggleEditPoints,
              icon: Icon(
                editingPoints ? Icons.check : Icons.timeline,
                size: 16,
              ),
              label: Text(
                editingPoints
                    ? 'Terminer l\'édition des points'
                    : 'Modifier les points',
                style: const TextStyle(fontSize: 12),
              ),
              style: editingPoints
                  ? OutlinedButton.styleFrom(
                      backgroundColor: AppColors.accentLight.withValues(
                        alpha: 0.18,
                      ),
                      side: BorderSide(color: AppColors.accent),
                    )
                  : null,
            ),
          ),
        ],
        const SizedBox(height: 14),
        _label('Couleur du trait'),
        _colorSwatchGrid(el.strokeColor, (c) {
          el.strokeColor = c;
          _emit(el);
        }, allowNone: true),
        const SizedBox(height: 10),
        _numberField('Épaisseur', el.strokeWidth ?? 2, (v) {
          el.strokeWidth = v;
          _emit(el);
        }),
        const SizedBox(height: 10),
        DropdownButtonFormField<BadgeStrokeStyle>(
          key: ValueKey('stroke-style-${el.id}'),
          initialValue: el.strokeStyle,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Style du trait',
            isDense: true,
          ),
          items: const [
            DropdownMenuItem(
              value: BadgeStrokeStyle.solid,
              child: Text('Plein'),
            ),
            DropdownMenuItem(
              value: BadgeStrokeStyle.dashed,
              child: Text('Tirets'),
            ),
            DropdownMenuItem(
              value: BadgeStrokeStyle.dotted,
              child: Text('Pointillés'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            el.strokeStyle = v;
            _emit(el);
          },
        ),
        const SizedBox(height: 10),
        // Action PONCTUELLE (pas un état persistant) : grave IMMÉDIATEMENT
        // un trou PERMANENT dans chaque élément en dessous de cette forme,
        // réellement chevauché par elle — voir
        // `BadgeElement.subtractBackground`/`cutoutPaths`
        // (models/badge_layout.dart) et badge_builder_screen.dart::
        // _onElementChanged (qui effectue la découpe puis réinitialise ce
        // déclencheur). Volontairement un BOUTON plutôt qu'une case à
        // cocher persistante : un premier essai (case à cocher = état
        // durable, trou recalculé à chaque frame selon la position
        // COURANTE de cette forme) donnait l'impression que "rien n'était
        // fait" dès qu'on déplaçait la forme après coup pour vérifier —
        // l'utilisateur attendait une découpe qui reste en place.
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            key: ValueKey('subtract-bg-${el.id}'),
            onPressed: () {
              el.subtractBackground = true;
              _emit(el);
            },
            icon: const Icon(Icons.content_cut, size: 16),
            label: const Text(
              'Soustraire du fond (découper maintenant)',
              style: TextStyle(fontSize: 12),
            ),
          ),
        ),
        if (el.shapeKind != BadgeShapeKind.line &&
            el.shapeKind != BadgeShapeKind.curve) ...[
          const SizedBox(height: 14),
          _fillSection(el),
        ],
      ],
    );
  }

  /// Bascule entre couleur unie (`el.fillColor`) et dégradé (`el.fillGradient`,
  /// prioritaire sur `fillColor` au rendu — voir badge_layout_renderer.dart).
  Widget _fillSection(BadgeElement el) {
    final hasGradient = el.fillGradient != null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _label('Remplissage'),
        SegmentedButton<bool>(
          segments: const [
            ButtonSegment(value: false, label: Text('Couleur unie')),
            ButtonSegment(value: true, label: Text('Dégradé')),
          ],
          selected: {hasGradient},
          onSelectionChanged: (s) {
            final wantsGradient = s.first;
            if (wantsGradient && el.fillGradient == null) {
              el.fillGradient = BadgeGradient(
                type: BadgeGradientType.linear,
                stops: [
                  BadgeGradientStop(
                    color: el.fillColor ?? 0xFF1A73E8,
                    offset: 0,
                  ),
                  BadgeGradientStop(color: 0xFFFFFFFF, offset: 1),
                ],
              );
            } else if (!wantsGradient) {
              el.fillGradient = null;
            }
            _emit(el);
          },
        ),
        const SizedBox(height: 10),
        if (hasGradient)
          _gradientEditor(el)
        else
          _colorSwatchGrid(el.fillColor, (c) {
            el.fillColor = c;
            _emit(el);
          }, allowNone: true),
      ],
    );
  }

  Widget _gradientEditor(BadgeElement el) {
    final gradient = el.fillGradient!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<BadgeGradientType>(
          key: ValueKey('gradient-type-${el.id}'),
          initialValue: gradient.type,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Type de dégradé',
            isDense: true,
          ),
          items: const [
            DropdownMenuItem(
              value: BadgeGradientType.linear,
              child: Text('Linéaire'),
            ),
            DropdownMenuItem(
              value: BadgeGradientType.radial,
              child: Text('Radial'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            gradient.type = v;
            _emit(el);
          },
        ),
        if (gradient.type == BadgeGradientType.linear) ...[
          const SizedBox(height: 10),
          _numberField('Angle °', gradient.angleDegrees, (v) {
            gradient.angleDegrees = v;
            _emit(el);
          }),
        ],
        const SizedBox(height: 10),
        _label('Arrêts de couleur'),
        for (var i = 0; i < gradient.stops.length; i++)
          _gradientStopRow(el, gradient, i),
        TextButton.icon(
          onPressed: () {
            gradient.stops.add(BadgeGradientStop(color: 0xFF000000, offset: 1));
            _emit(el);
          },
          icon: const Icon(Icons.add, size: 16),
          label: const Text('Ajouter un arrêt', style: TextStyle(fontSize: 12)),
        ),
      ],
    );
  }

  Widget _gradientStopRow(BadgeElement el, BadgeGradient gradient, int index) {
    final stop = gradient.stops[index];
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            width: 20,
            height: 20,
            margin: const EdgeInsets.only(right: 6),
            decoration: BoxDecoration(
              color: Color(stop.color),
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.borderSubtle),
            ),
          ),
          _hexField(
            stop.color,
            (c) {
              stop.color = c;
              _emit(el);
            },
            label: null,
            width: 82,
          ),
          const SizedBox(width: 6),
          _numberField(
            '0-1',
            stop.offset,
            (v) {
              stop.offset = v.clamp(0, 1);
              _emit(el);
            },
            decimals: 2,
            width: 56,
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 16),
            tooltip: 'Retirer cet arrêt',
            onPressed: gradient.stops.length > 2
                ? () {
                    gradient.stops.removeAt(index);
                    _emit(el);
                  }
                : null,
          ),
        ],
      ),
    );
  }

  Widget _photoFields(BadgeElement el) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<BadgePhotoFit>(
          key: ValueKey('fit-${el.id}'),
          initialValue: el.fit,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Ajustement de la photo',
            isDense: true,
          ),
          items: const [
            DropdownMenuItem(
              value: BadgePhotoFit.centerCrop,
              child: Text('Recadrer (remplir)'),
            ),
            DropdownMenuItem(
              value: BadgePhotoFit.contain,
              child: Text('Contenir (sans recadrer)'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            el.fit = v;
            _emit(el);
          },
        ),
        const SizedBox(height: 14),
        DropdownButtonFormField<BadgeShapeKind>(
          key: ValueKey('photo-shape-${el.id}'),
          initialValue: el.shapeKind ?? BadgeShapeKind.rectangle,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Forme du cadre',
            isDense: true,
          ),
          items: const [
            DropdownMenuItem(
              value: BadgeShapeKind.rectangle,
              child: Text('Rectangle'),
            ),
            DropdownMenuItem(
              value: BadgeShapeKind.roundedRectangle,
              child: Text('Rectangle arrondi'),
            ),
            DropdownMenuItem(
              value: BadgeShapeKind.oval,
              child: Text('Cercle / ovale'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            el.shapeKind = v;
            _emit(el);
          },
        ),
        if (el.shapeKind == BadgeShapeKind.roundedRectangle) ...[
          const SizedBox(height: 10),
          _numberField('Rayon des coins', el.cornerRadius ?? 8, (v) {
            el.cornerRadius = v;
            _emit(el);
          }),
        ],
        const SizedBox(height: 14),
        _label('Couleur de la bordure'),
        _colorSwatchGrid(el.strokeColor, (c) {
          el.strokeColor = c;
          _emit(el);
        }, allowNone: true),
        const SizedBox(height: 10),
        _numberField('Épaisseur de la bordure', el.strokeWidth ?? 0, (v) {
          el.strokeWidth = v;
          _emit(el);
        }),
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 14),
          child: Divider(height: 1),
        ),
        Text(
          'Réglages de la photo (appliqués à chaque étudiant)',
          style: TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 12.5,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Prenez ou chargez une photo test pour voir l\'effet en direct — '
          'jamais sauvegardée dans le gabarit (seuls les réglages ci-dessous '
          'le sont), mais peut être enregistrée sur la fiche d\'un étudiant '
          'prévisualisé via "Enregistrer la photo" dans la barre du haut.',
          style: TextStyle(fontSize: 11, color: AppColors.textMuted),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: onCaptureTestPhoto,
                icon: const Icon(Icons.camera_alt_outlined, size: 16),
                label: const Text('Prendre une photo'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: onLoadTestPhoto,
                icon: const Icon(Icons.upload_file_outlined, size: 16),
                label: const Text('Charger une photo'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        _sliderField('Luminosité', el.photoBrightness, -1, 1, (v) {
          el.photoBrightness = v;
          _emit(el);
        }),
        _sliderField('Contraste', el.photoContrast, 0, 2, (v) {
          el.photoContrast = v;
          _emit(el);
        }),
        _sliderField('Saturation', el.photoSaturation, 0, 2, (v) {
          el.photoSaturation = v;
          _emit(el);
        }),
        if (el.fit == BadgePhotoFit.centerCrop) ...[
          _sliderField('Centrage horizontal', el.photoOffsetX, 0, 1, (v) {
            el.photoOffsetX = v;
            _emit(el);
          }),
          _sliderField('Centrage vertical', el.photoOffsetY, 0, 1, (v) {
            el.photoOffsetY = v;
            _emit(el);
          }),
          _sliderField('Zoom', el.photoZoom, 1, 3, (v) {
            el.photoZoom = v;
            _emit(el);
          }, format: (v) => '${(v * 100).round()}%'),
        ],
      ],
    );
  }

  /// Curseur avec libellé + valeur affichée — pas de souci de perte de
  /// focus (contrairement aux champs texte, `Slider.onChanged` s'applique
  /// en direct pendant le glisser).
  Widget _sliderField(
    String label,
    double value,
    double min,
    double max,
    ValueChanged<double> onSet, {
    String Function(double)? format,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 104,
            child: Text(
              label,
              style: TextStyle(fontSize: 11, color: AppColors.textMuted),
            ),
          ),
          Expanded(
            child: Slider(
              value: value.clamp(min, max),
              min: min,
              max: max,
              onChanged: onSet,
            ),
          ),
          SizedBox(
            width: 38,
            child: Text(
              format != null ? format(value) : value.toStringAsFixed(2),
              style: const TextStyle(fontSize: 10.5),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  /// Sans donnée personnalisée, le QR est rempli automatiquement (contact
  /// du responsable de l'étudiant, comme le flux existant de
  /// badge_screen.dart) — la case à cocher n'est là que pour les cas où
  /// cette information manque ou n'est pas pertinente pour ce gabarit.
  Widget _qrFields(BadgeElement el) {
    final hasCustom = el.qrCustomData != null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Par défaut, rempli automatiquement avec le contact du '
          'responsable de l\'étudiant au moment de générer le badge.',
          style: TextStyle(fontSize: 11, color: AppColors.textMuted),
        ),
        const SizedBox(height: 10),
        FilterChip(
          label: const Text('Donnée personnalisée'),
          visualDensity: VisualDensity.compact,
          selected: hasCustom,
          onSelected: (v) {
            el.qrCustomData = v ? '' : null;
            _emit(el);
          },
        ),
        if (hasCustom) ...[
          const SizedBox(height: 10),
          TextFormField(
            key: ValueKey('qr-custom-${el.id}'),
            initialValue: el.qrCustomData,
            decoration: const InputDecoration(
              labelText: 'Texte encodé dans le QR',
              isDense: true,
            ),
            maxLines: 2,
            onChanged: (v) {
              el.qrCustomData = v;
              _emit(el);
            },
          ),
        ],
      ],
    );
  }

  /// Contrairement à `_photoFields` (une photo DIFFÉRENTE par étudiant,
  /// jamais persistée dans le gabarit), le fichier choisi ici EST
  /// persisté (`el.imagePath`, copié par `BadgeLayoutStore.pickElementImage`)
  /// et identique sur chaque badge généré — un logo ou une signature
  /// scannée, pas une donnée liée à l'étudiant.
  Widget _staticImageFields(BadgeElement el) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: onPickElementImage,
            icon: const Icon(Icons.upload_file_outlined, size: 16),
            label: Text(
              el.imagePath == null ? 'Choisir une image' : 'Remplacer l\'image',
            ),
          ),
        ),
        const SizedBox(height: 14),
        DropdownButtonFormField<BadgePhotoFit>(
          key: ValueKey('image-fit-${el.id}'),
          initialValue: el.fit,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Ajustement',
            isDense: true,
          ),
          items: const [
            DropdownMenuItem(
              value: BadgePhotoFit.contain,
              child: Text('Contenir (sans recadrer)'),
            ),
            DropdownMenuItem(
              value: BadgePhotoFit.centerCrop,
              child: Text('Recadrer (remplir)'),
            ),
          ],
          onChanged: (v) {
            if (v == null) return;
            el.fit = v;
            _emit(el);
          },
        ),
      ],
    );
  }

  Widget _colorSwatchGrid(
    int? selected,
    ValueChanged<int?> onPick, {
    required bool allowNone,
  }) {
    Widget swatch(int? color, {bool isNone = false}) {
      final isSelected = selected == color;
      return GestureDetector(
        onTap: () => onPick(color),
        child: Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: isNone ? null : Color(color!),
            shape: BoxShape.circle,
            border: Border.all(
              color: isSelected ? AppColors.accent : AppColors.borderSubtle,
              width: isSelected ? 2.5 : 1,
            ),
          ),
          child: isNone
              ? const Icon(Icons.close, size: 14, color: Colors.grey)
              : null,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: [
            if (allowNone) swatch(null, isNone: true),
            ..._colorSwatches.map((c) => swatch(c)),
          ],
        ),
        const SizedBox(height: 6),
        _hexField(selected, (c) => onPick(c)),
      ],
    );
  }

  /// Couleur libre au format hexadécimal — au-delà de la grille de nuances
  /// fixes, sans ajouter de package sélecteur de couleur (voir le plan de
  /// cette fonctionnalité : dépendances minimales pour l'éditeur).
  Widget _hexField(
    int? current,
    ValueChanged<int> onSubmit, {
    String? label = 'Couleur (hex)',
    double width = 130,
  }) {
    final hex = current == null
        ? ''
        : '#${(current & 0xFFFFFF).toRadixString(16).padLeft(6, '0').toUpperCase()}';
    return _CommitOnBlurField(
      width: width,
      label: label,
      hintText: '#RRGGBB',
      displayValue: hex,
      style: const TextStyle(fontSize: 12),
      onCommit: (v) {
        final parsed = _parseHexColor(v);
        if (parsed != null) onSubmit(parsed);
      },
    );
  }

  int? _parseHexColor(String input) {
    var s = input.trim();
    if (s.startsWith('#')) s = s.substring(1);
    if (s.length == 3) s = s.split('').map((c) => '$c$c').join();
    if (s.length != 6) return null;
    final value = int.tryParse(s, radix: 16);
    if (value == null) return null;
    return 0xFF000000 | value;
  }
}

/// Champ texte qui valide sur Entrée ET sur perte de focus — sans ça,
/// taper une valeur (ex. l'angle d'un dégradé) puis cliquer ailleurs
/// (le canevas, un autre champ) pour voir le résultat perdait
/// silencieusement la saisie, puisque `TextFormField.onFieldSubmitted`
/// seul ne réagit qu'à la touche Entrée. [displayValue] ne réinitialise
/// le texte affiché QUE si le champ n'a pas le focus, pour ne jamais
/// écraser une frappe en cours suite à une modification externe (ex.
/// glisser une poignée de redimensionnement pendant que ce champ est
/// affiché mais pas focus).
class _CommitOnBlurField extends StatefulWidget {
  const _CommitOnBlurField({
    required this.displayValue,
    required this.onCommit,
    this.label,
    this.hintText,
    this.width,
    this.keyboardType,
    this.style,
  });

  final String displayValue;
  final ValueChanged<String> onCommit;
  final String? label;
  final String? hintText;
  final double? width;
  final TextInputType? keyboardType;
  final TextStyle? style;

  @override
  State<_CommitOnBlurField> createState() => _CommitOnBlurFieldState();
}

class _CommitOnBlurFieldState extends State<_CommitOnBlurField> {
  late final TextEditingController _controller;
  late final FocusNode _focusNode;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.displayValue);
    _focusNode = FocusNode()..addListener(_onFocusChange);
  }

  @override
  void didUpdateWidget(covariant _CommitOnBlurField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!_focusNode.hasFocus && widget.displayValue != _controller.text) {
      _controller.text = widget.displayValue;
    }
  }

  void _onFocusChange() {
    if (!_focusNode.hasFocus) widget.onCommit(_controller.text);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_onFocusChange);
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final field = TextFormField(
      controller: _controller,
      focusNode: _focusNode,
      decoration: InputDecoration(
        labelText: widget.label,
        hintText: widget.hintText,
        isDense: true,
      ),
      style: widget.style,
      keyboardType: widget.keyboardType,
      onFieldSubmitted: widget.onCommit,
    );
    return widget.width != null
        ? SizedBox(width: widget.width, child: field)
        : field;
  }
}
