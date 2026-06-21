"""Seed les sections de la page d'accueil si elles n'existent pas encore."""
from sqlalchemy.orm import Session
from app.services.page_section_service import get_by_key, upsert
from app.Schemas.SPageSection import PageSectionCreate

DEFAULT_SECTIONS = [
    {
        "section_key": "stats", "ordre": 1,
        "titre": "Chiffres clés", "sous_titre": None,
        "items": [
            {"n": "1 200+", "l": "Élèves inscrits"},
            {"n": "85",     "l": "Enseignants qualifiés"},
            {"n": "27 ans", "l": "D'expérience"},
            {"n": "98%",    "l": "Taux de réussite au bac"},
        ]
    },
    {
        "section_key": "cycles", "ordre": 2,
        "titre": "Nos cycles", "sous_titre": "De la maternelle au baccalauréat",
        "items": [
            {"i": "🌱", "age": "3 – 5 ans", "t": "Préscolaire", "color": "#F59E0B",
             "d": "L'éveil par le jeu et la découverte dans un cadre sécurisant.",
             "items": ["Motricité fine & globale", "Langage oral", "Socialisation", "Activités créatives"]},
            {"i": "📖", "age": "6 – 11 ans", "t": "Fondamental", "color": "#10B981",
             "d": "Les bases solides en lecture, écriture, mathématiques et sciences.",
             "items": ["Français & Créole", "Mathématiques", "Sciences naturelles", "Histoire-Géographie"]},
            {"i": "🎓", "age": "12 – 18 ans", "t": "Secondaire", "color": "#3B82F6",
             "d": "Préparation rigoureuse au baccalauréat et à l'université.",
             "items": ["Séries scientifique & littéraire", "Langues vivantes", "Informatique", "Orientation universitaire"]},
        ]
    },
    {
        "section_key": "features", "ordre": 3,
        "titre": "Nos atouts", "sous_titre": "Pourquoi choisir Le Mignon ?",
        "items": [
            {"i": "👨‍🏫", "t": "Enseignants certifiés",   "d": "Tous nos professeurs sont diplômés d'État."},
            {"i": "📚",  "t": "Bibliothèque & ressources", "d": "Fonds documentaire riche et accès numérique."},
            {"i": "👨‍👩‍👧", "t": "Suivi parental",          "d": "Réunions trimestrielles et bulletins détaillés."},
            {"i": "🏟️", "t": "Infrastructures modernes",  "d": "Salles équipées, labos, complexe sportif."},
            {"i": "🔒",  "t": "Sécurité & encadrement",   "d": "Accès sécurisé et surveillance permanente."},
        ]
    },
    {
        "section_key": "activities", "ordre": 4,
        "titre": "Vie scolaire", "sous_titre": "L'école, au-delà des cours",
        "items": [
            {"t": "Sport & EPS",       "tag": "Parascolaire", "img": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80", "desc": ""},
            {"t": "Arts plastiques",   "tag": "Créativité",   "img": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&q=80", "desc": ""},
            {"t": "Club de lecture",   "tag": "Culture",      "img": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600&q=80", "desc": ""},
            {"t": "Concours scolaires","tag": "Excellence",   "img": "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=600&q=80", "desc": ""},
        ]
    },
    {
        "section_key": "testimonials", "ordre": 5,
        "titre": "Témoignages", "sous_titre": "Ce que disent les familles",
        "items": [
            {"t": "Mes enfants s'épanouissent vraiment ici.", "n": "Marie-Claire Fortuné",   "r": "Parent d'élève — Cycle secondaire"},
            {"t": "L'encadrement est sérieux et bienveillant.", "n": "Jean-Pierre Alexis",    "r": "Parent d'élève — Cycle fondamental"},
            {"t": "Une école qui tient ses promesses.",        "n": "Nadège Saint-Hilaire",  "r": "Parent d'élève — Préscolaire & Primaire"},
        ]
    },
    {
        "section_key": "values", "ordre": 6,
        "titre": "Nos valeurs", "sous_titre": None,
        "items": [
            {"i": "🎯", "t": "Excellence"},
            {"i": "🤝", "t": "Bienveillance"},
            {"i": "💡", "t": "Innovation"},
            {"i": "🌍", "t": "Citoyenneté"},
        ]
    },
]

FORMATION_SECTIONS = [
    {
        "section_key": "formation_atouts", "ordre": 1,
        "titre": "Nos atouts", "sous_titre": None,
        "items": [
            {"i": "👨‍🏫", "t": "Enseignants certifiés",  "d": "100% titulaires d'un Master ou d'une agrégation."},
            {"i": "🏫",  "t": "Petits groupes",          "d": "25 élèves max pour un suivi individualisé."},
            {"i": "💻",  "t": "Équipements modernes",    "d": "Salles numériques, labos, bibliothèque, coworking."},
            {"i": "🤝",  "t": "Réseau alumni",           "d": "3 500+ anciens dans les meilleures entreprises."},
        ]
    },
]

def seed_home(db: Session):
    for s in DEFAULT_SECTIONS:
        if not get_by_key(db, "home", s["section_key"]):
            upsert(db, PageSectionCreate(page="home", **s))

def seed_formations(db: Session):
    for s in FORMATION_SECTIONS:
        if not get_by_key(db, "formations", s["section_key"]):
            upsert(db, PageSectionCreate(page="formations", **s))
