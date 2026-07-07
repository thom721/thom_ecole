import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

/// Écran "À Propos" — contenu éditorial statique (présentation d'Infini
/// Software, l'éditeur du logiciel), pas une simple boîte de dialogue.
/// Remplace l'ancien `showAboutDialog` (nom + version seulement) déclenché
/// depuis app_shell.dart:292 — la version reste visible dans le pied de
/// page persistant de l'application (AppShell), pas besoin de la répéter
/// ici.
class AProposScreen extends StatelessWidget {
  const AProposScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _HeroSection(),
          const SizedBox(height: 32),
          _ValuesSection(),
        ],
      ),
    );
  }
}

const _missionCards = [
  (
    icon: '🎯',
    title: 'Notre mission',
    body: 'Rendre la technologie accessible à toutes les entreprises en '
        'livrant des logiciels fiables, performants et abordables qui '
        'résolvent de vrais problèmes métier.',
  ),
  (
    icon: '🔭',
    title: 'Notre vision',
    body: 'Devenir la référence caribéenne et francophone en développement '
        "logiciel sur mesure, reconnue pour la qualité et l'innovation de "
        'ses solutions.',
  ),
  (
    icon: '💎',
    title: 'Nos valeurs',
    body: 'Excellence, transparence, engagement client et amélioration '
        'continue. Nous livrons ce que nous promettons, quand nous le '
        'promettons.',
  ),
];

const _guidingValues = [
  (
    icon: '💡',
    title: 'Innovation',
    body: 'Toujours à la pointe des technologies pour livrer ce qu\'il y a '
        'de mieux.',
  ),
  (
    icon: '🤝',
    title: 'Engagement',
    body: 'Nous traitons chaque projet comme si c\'était le nôtre.',
  ),
  (
    icon: '🎯',
    title: 'Précision',
    body: 'Chaque détail compte. Nous livrons du code propre et '
        'maintenable.',
  ),
  (
    icon: '🌱',
    title: 'Croissance',
    body: 'Nous grandissons avec nos clients sur le long terme.',
  ),
];

class _Eyebrow extends StatelessWidget {
  const _Eyebrow(this.label, {this.alignment = Alignment.centerLeft});

  final String label;
  final Alignment alignment;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Text(
        label.toUpperCase(),
        style: TextStyle(
          fontSize: 12,
          letterSpacing: 3,
          fontWeight: FontWeight.w700,
          color: AppColors.accentLight,
        ),
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final emerald = AppColors.cardPalette['emerald']!.bar;
    final amber = AppColors.cardPalette['amber']!.bar;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _Eyebrow('Notre histoire'),
        const SizedBox(height: 10),
        Text.rich(
          TextSpan(
            children: [
              TextSpan(
                text: 'Nous construisons le\n',
                style: TextStyle(
                  fontSize: 34,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                  height: 1.2,
                ),
              ),
              TextSpan(
                text: 'futur digital',
                style: TextStyle(
                  fontSize: 34,
                  fontWeight: FontWeight.w800,
                  height: 1.2,
                  foreground: Paint()
                    ..shader = LinearGradient(colors: [emerald, amber]).createShader(
                      const Rect.fromLTWH(0, 0, 260, 40),
                    ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Text(
            "Infini Software est née d'une conviction : chaque entreprise "
            'mérite des outils technologiques à la hauteur de ses '
            'ambitions. Fondée par des passionnés du logiciel, nous '
            'combinons créativité et rigueur technique pour livrer des '
            'solutions qui durent.',
            style: TextStyle(fontSize: 14.5, height: 1.5, color: AppColors.textMuted),
          ),
        ),
        const SizedBox(height: 24),
        LayoutBuilder(
          builder: (context, constraints) {
            const spacing = 16.0;
            final cards = _missionCards
                .map((c) => _InfoCard(icon: c.icon, title: c.title, body: c.body))
                .toList();
            // En dessous de 760px, un Row à largeur fixe déborderait — on
            // empile plutôt les cartes (la hauteur égale entre elles perd
            // alors son sens, chacune prend la largeur disponible).
            if (constraints.maxWidth < 760) {
              return Column(
                children: [
                  for (final card in cards) ...[card, const SizedBox(height: spacing)],
                ],
              );
            }
            // IntrinsicHeight + stretch : les 3 cartes de cette ligne
            // partagent la hauteur de la plus grande d'entre elles, plutôt
            // que chacune sa propre hauteur intrinsèque (Wrap ne fait pas
            // ça — chaque enfant d'un run garde sa hauteur naturelle).
            return IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (var i = 0; i < cards.length; i++) ...[
                    Expanded(child: cards[i]),
                    if (i != cards.length - 1) const SizedBox(width: spacing),
                  ],
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.icon,
    required this.title,
    required this.body,
    this.centered = false,
  });

  final String icon;
  final String title;
  final String body;
  final bool centered;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        border: Border.all(color: AppColors.borderSubtle),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: centered ? CrossAxisAlignment.center : CrossAxisAlignment.start,
        children: [
          Text(icon, style: const TextStyle(fontSize: 28)),
          const SizedBox(height: 14),
          Text(
            title,
            textAlign: centered ? TextAlign.center : TextAlign.start,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.accentLight),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            textAlign: centered ? TextAlign.center : TextAlign.start,
            style: TextStyle(fontSize: 13, height: 1.5, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}

class _ValuesSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _Eyebrow('Ce qui nous guide', alignment: Alignment.center),
        const SizedBox(height: 8),
        Text(
          'Nos valeurs',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
        ),
        const SizedBox(height: 24),
        LayoutBuilder(
          builder: (context, constraints) {
            const spacing = 16.0;
            const columns = 4;
            final isNarrow = constraints.maxWidth < 900;
            final perRow = isNarrow ? 2 : columns;
            final cardWidth = (constraints.maxWidth - spacing * (perRow - 1)) / perRow;
            return Wrap(
              alignment: WrapAlignment.center,
              spacing: spacing,
              runSpacing: spacing,
              children: _guidingValues.map((v) {
                return SizedBox(
                  width: cardWidth,
                  child: _InfoCard(icon: v.icon, title: v.title, body: v.body, centered: true),
                );
              }).toList(),
            );
          },
        ),
      ],
    );
  }
}
