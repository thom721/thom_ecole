export const STATS = [
  { n: '1 200+', l: 'Élèves inscrits' },
  { n: '85',     l: 'Enseignants qualifiés' },
  { n: '27 ans', l: "D'expérience" },
  { n: '98%',    l: 'Taux de réussite au bac' }
];

export const FEATURES = [
  {
    i: '👨‍🏫', t: 'Enseignants certifiés',
    d: "Tous nos professeurs sont diplômés d'État et suivent des formations pédagogiques continues.",
  },
  {
    i: '📚', t: 'Bibliothèque & ressources',
    d: 'Fonds documentaire riche, accès numérique et espace de travail supervisé pour les élèves.',
  },
  {
    i: '👨‍👩‍👧', t: 'Suivi parental',
    d: 'Réunions trimestrielles, bulletins détaillés et communication directe avec les enseignants.',
  },
  {
    i: '🏟️', t: 'Infrastructures modernes',
    d: 'Salles équipées, laboratoires scientifiques, complexe sportif et espaces verts sécurisés.',
  },
  // {
  //   i: '🍽️', t: 'Cantine & restauration',
  //   d: 'Repas équilibrés préparés sur place, menus adaptés et surveillance durant la pause déjeuner.',
  //   featured: true
  // },
  {
    i: '🔒', t: 'Sécurité & encadrement',
    d: 'Accès sécurisé, surveillance permanente et protocole de sécurité certifié pour tous les élèves.',
  }
];

export const TESTIMONIALS = [
  {
    t: "Mes enfants s'épanouissent vraiment ici. Les enseignants sont attentifs et les résultats sont au rendez-vous.",
    n: 'Marie-Claire Fortuné',
    r: 'Parent d\'élève — Cycle secondaire'
  },
  {
    t: "L'encadrement est sérieux et bienveillant. Mon fils a gagné en confiance et ses notes se sont nettement améliorées.",
    n: 'Jean-Pierre Alexis',
    r: 'Parent d\'élève — Cycle fondamental'
  },
  {
    t: "Une école qui tient ses promesses. La communication avec l'administration est claire et les professeurs sont disponibles.",
    n: 'Nadège Saint-Hilaire',
    r: 'Parent d\'élève — Préscolaire & Primaire'
  }
];

export const FORMATIONS = [
  {
    id: 1, lv: 'Préscolaire', t: 'Maternelle & Éveil', dur: '3 ans', col: '#10b981',
    img: 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=700&q=75',
    d: "Éveil sensoriel, motricité, socialisation et langage oral dans un environnement sécurisant et stimulant.",
    pills: ['Éveil', 'Motricité', 'Langage', 'Arts', 'Socialisation'],
    sn: '15', sr: '100%', sd: '5+',
    deb: ['Entrée en cycle fondamental', 'Bases solides en lecture et écriture', 'Épanouissement personnel']
  },
  {
    id: 2, lv: 'Primaire', t: 'Cycle Fondamental', dur: '6 ans', col: '#3b82f6',
    img: 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=700&q=75',
    d: "Acquisition des savoirs fondamentaux : lecture, écriture, calcul, sciences et éducation civique.",
    pills: ['Français', 'Mathématiques', 'Sciences', 'Histoire-Géo', 'Anglais', 'EPS'],
    sn: '22', sr: '98%', sd: '15+',
    deb: ['Entrée en 6ème avec les meilleures bases', 'Maîtrise du français et des maths', 'Esprit critique développé']
  },
  {
    id: 3, lv: 'Collège', t: 'Cycle Secondaire 1er cycle', dur: '4 ans', col: '#8b5cf6',
    img: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=700&q=75',
    d: "Approfondissement des disciplines, initiation aux sciences expérimentales et préparation au brevet.",
    pills: ['Maths', 'Physique-Chimie', 'SVT', 'Français', 'Anglais', 'Histoire-Géo'],
    sn: '25', sr: '97%', sd: '20+',
    deb: ['Brevet des collèges toutes mentions', 'Orientation lycée général ou pro', 'Projets d\'orientation accompagnés']
  },
  {
    id: 4, lv: 'Lycée', t: 'Baccalauréat Général', dur: '3 ans', col: '#f59e0b',
    img: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=700&q=75',
    d: "Spécialités au choix, tutorat personnalisé et préparation rigoureuse aux examens du baccalauréat.",
    pills: ['Philosophie', 'Maths', 'Sciences', 'Lettres', 'Langues', 'SES'],
    sn: '28', sr: '99%', sd: '25+',
    deb: ['Baccalauréat général', 'Accès universités et grandes écoles', 'Préparation aux concours']
  },
];

export const EVENTS = [
  { id: 1, t: 'Tournoi de Football Inter-classes',   cat: 'Sportif',    date: '10 Avr 2025', lieu: 'Terrain sportif de l\'école',  col: '#ef4444', img: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=600&q=75' },
  { id: 2, t: 'Exposition Arts Plastiques des élèves', cat: 'Culturel',   date: '22 Avr 2025', lieu: 'Hall principal',               col: '#8b5cf6', img: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&q=75' },
  { id: 3, t: 'Concours d\'Éloquence',               cat: 'Académique',  date: '5 Mai 2025',  lieu: 'Amphithéâtre',                 col: '#3b82f6', img: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=75' },
  { id: 4, t: 'Journée Portes Ouvertes',             cat: 'Admission',   date: '14 Sep 2025', lieu: 'Campus complet',               col: '#10b981', img: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&q=75' },
  { id: 5, t: 'Réunion Parents-Professeurs',         cat: 'Pédagogie',   date: '15 Mar 2025', lieu: 'Salles de classe',             col: '#f59e0b', img: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=75' },
  { id: 6, t: 'Cérémonie de remise des diplômes',   cat: 'Cérémonie',   date: '28 Jun 2025', lieu: 'Grande salle de l\'école',     col: '#D4A853', img: 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=600&q=75' }
];
//   type_de_document: '', document_numero: '',
//   document_date_dexpiration: '', document_status: '',
//   document_image: ''
// export const DOCS_BASE = [
//   { n: 'Acte de naissance',          i: '📄', h: 'Original ou copie certifiée conforme (PDF/JPG)', f: null },
//   { n: "Photo d'identité récente",   i: '🖼️', h: 'Portrait fond blanc, format JPG ou PNG',         f: null },
//   { n: "Pièce d'identité de l'élève", i: '🪪', h: 'CNI ou passeport en cours de validité',          f: null },
//   { n: 'Derniers bulletins scolaires', i: '📊', h: '2 derniers trimestres de l\'année précédente',   f: null },
//   { n: "Pièce d'identité du tuteur", i: '🪪', h: 'CNI ou passeport du responsable légal',           f: null },
//   { n: 'Justificatif de domicile',   i: '🏠', h: 'Facture ou document officiel de moins de 3 mois', f: null }
// ];

export const DOCS_BASE = [
  { type_de_document: 'Acte de naissance',          i: '📄', h: 'Original ou copie certifiée conforme (PDF/JPG)', document_image: null,document_date_dexpiration: '' },
  { type_de_document: "Photo d'identité récente",   i: '🖼️', h: 'Portrait fond blanc, format JPG ou PNG',         document_image: null,document_date_dexpiration: '' },
  { type_de_document: "Pièce d'identité de l'élève", i: '🪪', h: 'CNI ou passeport en cours de validité',          document_image: null,document_date_dexpiration: '' },
  { type_de_document: 'Derniers bulletins scolaires', i: '📊', h: '2 derniers trimestres de l\'année précédente',  document_image: null,document_date_dexpiration: '' },
  { type_de_document: "Pièce d'identité du tuteur", i: '🪪', h: 'CNI ou passeport du responsable légal',           document_image: null,document_date_dexpiration: '' },
  { type_de_document: 'Justificatif de domicile',   i: '🏠', h: 'Facture ou document officiel de moins de 3 mois', document_image: null,document_date_dexpiration: '' }
];

export const MILESTONES = [
  { y: '1998', t: "Fondation de l'établissement",       d: 'Ouverture des portes avec 120 élèves et 8 enseignants fondateurs.' },
  { y: '2005', t: 'Agrandissement du campus',           d: 'Construction de l\'amphithéâtre, des laboratoires et du complexe sportif.' },
  { y: '2010', t: 'Ouverture du cycle secondaire',      d: 'Accueil des premières classes de lycée général et professionnel.' },
  { y: '2018', t: 'Certification qualité',              d: 'Reconnaissance officielle par le Ministère de l\'Éducation Nationale.' },
  { y: '2025', t: 'Modernisation pédagogique',          d: 'Déploiement des outils numériques et rénovation complète des salles.' }
];

export const VALS = [
  { i: '🎓', t: 'Excellence',     d: 'Exiger le meilleur de chaque élève, en respectant son rythme et ses capacités.' },
  { i: '🤝', t: 'Bienveillance',  d: 'Un climat scolaire sûr, respectueux et propice à l\'épanouissement de tous.' },
  { i: '💡', t: 'Curiosité',      d: 'Éveiller l\'esprit critique, la créativité et le goût pour le savoir.' },
  { i: '🌍', t: 'Citoyenneté',    d: 'Former des élèves responsables, engagés et ouverts sur le monde.' }
];