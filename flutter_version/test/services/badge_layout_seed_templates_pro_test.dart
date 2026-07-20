import 'package:flutter_test/flutter_test.dart';
import 'package:school_client_flutter/models/badge_layout.dart';
import 'package:school_client_flutter/services/badge_layout_seed_templates_pro.dart';

/// Vérification structurelle des 22 gabarits "pro" (11 modèles × portrait/
/// paysage, voir badge_layout_seed_templates_pro.dart) — étant donné le
/// volume de coordonnées écrites à la main, ce test attrape les erreurs
/// mécaniques (id dupliqué, NaN, gradient mal formé, tracé sans point)
/// qu'une relecture visuelle seule pourrait manquer, sans dépendre d'un
/// rendu réel (`dart:ui`, qui ne se termine jamais dans cet environnement
/// de test — voir badge_layout_renderer_test.dart).
void main() {
  final templates = buildProSeedBadgeTemplates();

  test('exactement 22 gabarits (11 modèles × portrait/paysage)', () {
    expect(templates, hasLength(22));
  });

  test('tous les identifiants de gabarit sont uniques', () {
    final ids = templates.map((t) => t.id).toSet();
    expect(ids, hasLength(templates.length));
  });

  test('chaque gabarit survit à un aller-retour JSON identique', () {
    for (final t in templates) {
      final decoded = BadgeLayoutTemplate.fromJsonString(t.toJsonString());
      expect(
        decoded.toJsonString(),
        t.toJsonString(),
        reason: 'gabarit ${t.id}',
      );
    }
  });

  void checkSide(
    String templateId,
    String sideLabel,
    BadgeSide side,
    bool isLandscape,
  ) {
    final canvasW = isLandscape ? kBadgeLandscapeWidth : kBadgeLandscapeHeight;
    final canvasH = isLandscape ? kBadgeLandscapeHeight : kBadgeLandscapeWidth;

    expect(
      side.elements,
      isNotEmpty,
      reason: '$templateId/$sideLabel : aucun élément',
    );

    final ids = side.elements.map((e) => e.id).toSet();
    expect(
      ids,
      hasLength(side.elements.length),
      reason: '$templateId/$sideLabel : id d\'élément dupliqué',
    );

    for (final el in side.elements) {
      for (final v in [el.x, el.y, el.width, el.height, el.rotationDegrees]) {
        expect(
          v.isFinite,
          isTrue,
          reason: '$templateId/$sideLabel/${el.id} : valeur non finie',
        );
      }
      expect(
        el.width,
        greaterThan(0),
        reason: '$templateId/$sideLabel/${el.id} : largeur non positive',
      );
      expect(
        el.height,
        greaterThan(0),
        reason: '$templateId/$sideLabel/${el.id} : hauteur non positive',
      );

      // Un élément raisonnablement dans les limites du canevas (une marge
      // généreuse est tolérée : les bandes décoratives débordent parfois
      // volontairement du bord pour un effet plein cadre).
      expect(
        el.x,
        greaterThan(-canvasW),
        reason: '$templateId/$sideLabel/${el.id} : x très hors canevas',
      );
      expect(
        el.x,
        lessThan(canvasW * 2),
        reason: '$templateId/$sideLabel/${el.id} : x très hors canevas',
      );
      expect(
        el.y,
        greaterThan(-canvasH),
        reason: '$templateId/$sideLabel/${el.id} : y très hors canevas',
      );
      expect(
        el.y,
        lessThan(canvasH * 2),
        reason: '$templateId/$sideLabel/${el.id} : y très hors canevas',
      );

      if (el.shapeKind == BadgeShapeKind.path) {
        expect(
          el.pathPoints,
          isNotEmpty,
          reason: '$templateId/$sideLabel/${el.id} : tracé sans point',
        );
        for (final p in el.pathPoints) {
          expect(p.x.isFinite, isTrue);
          expect(p.y.isFinite, isTrue);
        }
      }

      if (el.fillGradient != null) {
        expect(
          el.fillGradient!.stops.length,
          greaterThanOrEqualTo(2),
          reason:
              '$templateId/$sideLabel/${el.id} : dégradé à moins de 2 arrêts',
        );
      }

      if (el.type == BadgeElementType.text) {
        expect(
          el.text,
          isNotNull,
          reason: '$templateId/$sideLabel/${el.id} : texte sans contenu',
        );
        expect(
          el.text!.isNotEmpty,
          isTrue,
          reason: '$templateId/$sideLabel/${el.id} : texte vide',
        );
      }
    }
  }

  test('chaque face (recto/verso) a des éléments structurellement valides', () {
    for (final t in templates) {
      checkSide(t.id, 'recto', t.recto, t.isLandscape);
      if (t.hasVerso) checkSide(t.id, 'verso', t.verso!, t.isLandscape);
    }
  });

  test(
    'l\'orientation du nom correspond à BadgeLayoutTemplate.isLandscape',
    () {
      for (final t in templates) {
        final labelSaysLandscape = t.name.contains('paysage');
        expect(t.isLandscape, labelSaysLandscape, reason: t.id);
      }
    },
  );

  test('chaque modèle a bien une version portrait ET une version paysage', () {
    final baseIds = templates
        .map((t) => t.id.replaceAll(RegExp(r'_l$'), ''))
        .toSet();
    for (final base in baseIds) {
      expect(
        templates.any((t) => t.id == base),
        isTrue,
        reason: 'portrait manquant pour $base',
      );
      expect(
        templates.any((t) => t.id == '${base}_l'),
        isTrue,
        reason: 'paysage manquant pour $base',
      );
    }
  });

  test(
    'le bandeau en vague du modèle 1 (portrait) a un VRAI creux, pas la ligne plate du bug initial '
    '(4 points de contrôle à la même hauteur ⇒ segment de Bézier parfaitement rectiligne)',
    () {
      final t = templates.firstWhere((t) => t.id == 'seed_pro_idcard_wave');
      final band = t.recto.elements.firstWhere((e) => e.id == 'bg');
      expect(band.shapeKind, BadgeShapeKind.path);

      // Évalue le point de la courbe cubique à t=0.5 entre les deux
      // ancres du bas (celles qui portent les poignées de courbure) —
      // même formule que badge_builder_canvas.dart::_cubicPointAt.
      final p0 = band.pathPoints[1]; // ancre gauche du creux
      final p1 = band.pathPoints[2]; // ancre droite du creux
      final cp1 = (x: p0.x + (p0.outX ?? 0), y: p0.y + (p0.outY ?? 0));
      final cp2 = (x: p1.x + (p1.inX ?? 0), y: p1.y + (p1.inY ?? 0));
      const mt = 0.5, tt = 0.5;
      final midY =
          mt * mt * mt * p0.y +
          3 * mt * mt * tt * cp1.y +
          3 * mt * tt * tt * cp2.y +
          tt * tt * tt * p1.y;

      // Les ancres elles-mêmes sont à une hauteur "haute" (bord) — le
      // milieu de la courbe doit tomber NETTEMENT plus bas (creux),
      // pas rester à la même hauteur (l'ancien bug). Seuil RELATIF à
      // l'amplitude réelle du creux (p1.y - p0.y) plutôt qu'une valeur
      // absolue fixe : cette amplitude a changé (creux rendu plus subtil
      // après retour visuel) sans que la propriété testée — le milieu de
      // la courbe descend bien à mi-chemin, pas une ligne plate — change.
      final dipAmplitude = p1.y - p0.y;
      expect(
        midY,
        greaterThan(p0.y + dipAmplitude * 0.3),
        reason:
            'le creux doit descendre nettement sous le niveau des bords, pas rester une ligne plate',
      );

      // Second bug corrigé après retour visuel : des poignées de courbure
      // alignées sur la CORDE (même angle que la pente moyenne) évitent
      // un coin vif à CHAQUE point pris isolément, mais donnent une pente
      // quasi CONSTANTE sur tout le segment — donc un "V" à coins
      // arrondis, pas une vraie vallée. Un simple test "la courbe dévie
      // de la ligne droite en son MILIEU (t=0.5)" ne suffit PAS à
      // détecter ça : avec des poignées horizontales symétriques aux deux
      // bouts, la courbe et la ligne droite ont exactement LA MÊME
      // hauteur en leur milieu respectif (démontré : la moyenne des 4
      // hauteurs de contrôle (p0,p0,p1,p1) vaut toujours (p0+p1)/2). La
      // vraie signature d'une vallée lisse (par opposition à un "V") est
      // la PLATITUDE près des bords : à t=0.25 (proche de l'ancre), la
      // courbe doit rester BIEN PLUS PROCHE de la hauteur de bord que ne
      // le serait une ligne droite au même t.
      const mt25 = 0.75, tt25 = 0.25;
      final y25 =
          mt25 * mt25 * mt25 * p0.y +
          3 * mt25 * mt25 * tt25 * cp1.y +
          3 * mt25 * tt25 * tt25 * cp2.y +
          tt25 * tt25 * tt25 * p1.y;
      final curveDeviation = (y25 - p0.y).abs();
      final straightDeviation = (0.25 * (p1.y - p0.y)).abs();
      // Une vraie courbe "ease" à tangentes horizontales aux deux bouts a
      // un ratio FIXE de 0.625 à t=0.25 (propriété mathématique des
      // poids de Bernstein à ce paramètre, indépendante de la magnitude
      // des poignées — vérifié par le calcul) : le seuil ci-dessous
      // (0.75) laisse une marge confortable au-dessus de cette valeur
      // attendue, tout en détectant sans ambiguïté une ligne droite/un
      // "V" (ratio ≈ 1.0).
      expect(
        curveDeviation,
        lessThan(straightDeviation * 0.75),
        reason:
            'près du bord (t=0.25), la courbe doit rester BEAUCOUP plus plate que la ligne droite équivalente — sinon c\'est un "V" à coins arrondis, pas une vraie vallée lisse',
      );
    },
  );

  test(
    'la photo du modèle 1 (portrait) reste tangente/sous la vague à son point le plus large '
    '(pas de croisement franc de plusieurs pixels avec le bord du bandeau) — le motif "deux '
    'bosses" du modèle de référence vient de la ligne d\'écho ([_scallopedEcho]), pas d\'un '
    'défaut de superposition photo/bandeau',
    () {
      final t = templates.firstWhere((t) => t.id == 'seed_pro_idcard_wave');
      final band = t.recto.elements.firstWhere((e) => e.id == 'bg');
      final photo = t.recto.elements.firstWhere((e) => e.id == 'photo');

      final p0 = band.pathPoints[1];
      final p1 = band.pathPoints[2];
      final cp1 = (x: p0.x + (p0.outX ?? 0), y: p0.y + (p0.outY ?? 0));
      final cp2 = (x: p1.x + (p1.inX ?? 0), y: p1.y + (p1.inY ?? 0));

      // Hauteur (normalisée) du bandeau à une abscisse normalisée donnée
      // — recherche binaire sur `t`, la courbe étant monotone en x sur ce
      // demi-segment (ancre gauche → creux central).
      double bandYAt(double targetX) {
        var lo = 0.0, hi = 1.0;
        for (var i = 0; i < 40; i++) {
          final mid = (lo + hi) / 2;
          final mt = 1 - mid;
          final x =
              mt * mt * mt * p0.x +
              3 * mt * mt * mid * cp1.x +
              3 * mt * mid * mid * cp2.x +
              mid * mid * mid * p1.x;
          if (x < targetX) {
            lo = mid;
          } else {
            hi = mid;
          }
        }
        final t = (lo + hi) / 2;
        final mt = 1 - t;
        return mt * mt * mt * p0.y +
            3 * mt * mt * t * cp1.y +
            3 * mt * t * t * cp2.y +
            t * t * t * p1.y;
      }

      final photoCenterX = photo.x + photo.width / 2;
      final photoCenterY = photo.y + photo.height / 2;
      final radius = photo.width / 2;

      // Au point le plus LARGE de la photo (gauche/droite, à la hauteur
      // de son centre), elle doit être dans le BLANC (sous la limite du
      // bandeau), à une petite tolérance (5px) près — un contact
      // pratiquement TANGENT à ce point précis est sans effet visuel
      // (vérifié par un rendu réel de la géométrie, voir la doc de
      // [_scallopedBand]) ; c'est un décalage FRANC qui produit
      // l'illusion de deux bosses, pas un frôlement de quelques pixels.
      const tolerance = 5.0;
      for (final dx in [-radius, radius]) {
        final xAbs = photoCenterX + dx;
        final xNorm = (xAbs / band.width).clamp(0.0, 1.0);
        final effectiveXNorm = xNorm <= 0.5 ? xNorm : 1 - xNorm;
        final boundaryY = bandYAt(effectiveXNorm) * band.height + band.y;
        expect(
          photoCenterY,
          greaterThan(boundaryY - tolerance),
          reason:
              'au point le plus large de la photo (dx=$dx), elle doit rester sous la vague (dans le blanc), à une petite tolérance de contact près',
        );
      }
    },
  );
}
