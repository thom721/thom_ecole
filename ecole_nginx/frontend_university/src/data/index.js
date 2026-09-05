// Vide intentionnellement : aucun événement réel IUSTH connu (l'audit ne
// donne aucune date vérifiable). Mieux vaut une page "Aucun événement pour
// le moment" honnête que des événements fictifs datés dans le passé — voir
// Audit_site_IUSTH_2026-08-27.pdf, point 2.5 sur le contenu de démonstration.
// À remplir via l'admin une fois de vrais événements programmés.
export const EVENTS = [];
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

// Documents adaptés à une admission universitaire (candidats majeurs) :
// pas de pièce d'identité de tuteur, diplôme/relevés du secondaire plutôt
// que des bulletins trimestriels. Le reste (équivalence ou concours, droit
// d'inscription) est décrit dans AdmissionView.vue — voir la page Génie
// Civil de iusth.edu.ht, seule source réelle disponible sur le processus.
export const DOCS_BASE = [
  { type_de_document: 'Acte de naissance',           i: '📄', h: 'Original ou copie certifiée conforme (PDF/JPG)', document_image: null,document_date_dexpiration: '' },
  { type_de_document: "Photo d'identité récente",    i: '🖼️', h: 'Portrait fond blanc, format JPG ou PNG',         document_image: null,document_date_dexpiration: '' },
  { type_de_document: "Pièce d'identité du candidat", i: '🪪', h: 'CNI ou passeport en cours de validité',          document_image: null,document_date_dexpiration: '' },
  { type_de_document: 'Diplôme du secondaire ou équivalent', i: '📊', h: 'Original ou copie certifiée conforme, requis pour le concours ou l\'équivalence', document_image: null,document_date_dexpiration: '' },
  { type_de_document: 'Justificatif de domicile',    i: '🏠', h: 'Facture ou document officiel de moins de 3 mois', document_image: null,document_date_dexpiration: '' }
];

// Jalons réels et vérifiés (voir /presentation/ sur iusth.edu.ht) — pas de
// dates inventées pour compléter une frise ; seulement ce qui est confirmé.
export const MILESTONES = [
  { y: '2021', t: "Création de l'IUSTH", d: "Institution privée d'enseignement supérieur et de recherche, reconnue d'utilité publique par l'État haïtien." },
  { y: '2024', t: 'Plan stratégique 2024-2030', d: "Priorité à la technologie, à l'excellence académique et à l'extension de l'institution dans les régions du pays." }
];

// Valeurs réelles de l'IUSTH (voir /presentation/)
export const VALS = [
  { i: '🎯', t: 'Qualité',              d: 'Exiger le meilleur de chaque étudiant, en respectant les critères académiques et légaux.' },
  { i: '🤝', t: 'Inclusion sociale',    d: 'Un environnement accessible et bienveillant, ouvert à toute la communauté.' },
  { i: '⚖️', t: 'Équité de genres',     d: "L'égalité des chances entre étudiantes et étudiants dans tous les programmes." },
  { i: '🌍', t: 'Éducation à la citoyenneté', d: 'Former des étudiants responsables, engagés et respectueux des droits humains.' }
];