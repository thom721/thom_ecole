from app.Models.MUser import SystemRole

# Catalogue en code, jamais deviné à l'exécution (voir plan Épic 23) — noms
# de rôles réels ecole_nginx (Routes/Initialisation.py::ROLES côté
# ecole_nginx) qui donnent des pouvoirs elearning-iusth élevés.
_ADMIN_ROLE_NAMES = {"admin", "Directeur"}
_TEACHER_ROLE_NAMES = {"teacher", "Enseignant", "Formateur", "professeur"}


def resolve_system_role(source_type: str, role_names: list[str]) -> SystemRole:
    """Un compte Professeur reste enseignant par construction, quel que
    soit son rôle RBAC exact côté ecole_nginx (déjà un vrai enseignant,
    confirmé par source_type, pas seulement par nom de rôle). Pour un
    Personnel, le vrai rôle RBAC tranche : direction → admin, enseignement
    → teacher, tout le reste → staff (jamais teacher/admin par défaut,
    voir décision de périmètre du plan)."""
    if any(name in _ADMIN_ROLE_NAMES for name in role_names):
        return SystemRole.admin
    if source_type == "professeur" or any(name in _TEACHER_ROLE_NAMES for name in role_names):
        return SystemRole.teacher
    return SystemRole.staff
