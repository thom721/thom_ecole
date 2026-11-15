from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool 
from alembic import context

import sys
import os

# Ajoute le dossier parent (ecole_nginx) au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Ajoute aussi le dossier app
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.database import get_engine_dynamically,Base
from app.Models.MFinancials import PaiementStatut
# from database import  get_engine_dynamically,Base

from alembic.operations import Operations
from sqlalchemy.exc import DBAPIError


# --- Migrations tolérantes au schéma déjà présent ------------------------
# Une base locale peut recevoir des tables/colonnes AVANT ses migrations :
# synchronisation depuis le serveur distant lors d'une installation, ou
# exécution précédente interrompue. Sans tolérance, la première « colonne
# déjà existante » arrête Alembic et TOUTES les migrations suivantes restent
# non appliquées (vu en pratique : cours_inscriptions.note_globale manquante
# → fiche étudiant en erreur 500 "Unknown column").
#
# Ici, une opération de schéma dont l'objet existe déjà (ou, pour un drop,
# n'existe plus) est ignorée avec un message, et la migration continue.
# Codes d'erreur MySQL — la base est toujours MySQL (local et web).
_DEJA_PRESENT = {
    1050: "table déjà existante",
    1060: "colonne déjà existante",
    1061: "index déjà existant",
    1022: "clé déjà existante",
    1826: "clé étrangère déjà existante",
}
_DEJA_ABSENT = {
    1051: "table déjà absente",
    1091: "colonne ou clé déjà absente",
}
_OPS_SCHEMA = (
    "add_column", "create_table", "create_index", "create_foreign_key",
    "create_unique_constraint", "drop_column", "drop_table", "drop_index",
    "drop_constraint",
)
# Opérations de données (backfills). Si la migration en cours a trouvé son
# schéma déjà en place, ses données ont été synchronisées avec : les
# rejouer écraserait des valeurs réelles (ex. 7e23faa1c08d remet
# payrolls.montant_du = montant sur toutes les lignes). On les saute alors.
_OPS_DONNEES = ("execute", "bulk_insert")

# Réinitialisé après chaque migration (voir _apres_migration).
_migration_en_cours = {"schema_deja_present": False}


def _code_mysql(exc):
    args = getattr(getattr(exc, "orig", None), "args", ())
    return args[0] if args and isinstance(args[0], int) else None


def _rendre_tolerante(nom):
    originale = getattr(Operations, nom)

    def tolerante(self, *args, **kwargs):
        try:
            return originale(self, *args, **kwargs)
        except DBAPIError as exc:
            code = _code_mysql(exc)
            raison = _DEJA_PRESENT.get(code) or _DEJA_ABSENT.get(code)
            if raison is None:
                raise
            _migration_en_cours["schema_deja_present"] = True
            cible = ", ".join(str(a) for a in args[:2] if isinstance(a, str))
            print(f"   ↷ Migration : {nom}({cible}) ignoré — {raison}.")
            return None

    setattr(Operations, nom, tolerante)


def _sauter_si_schema_present(nom):
    originale = getattr(Operations, nom)

    def gardee(self, *args, **kwargs):
        if _migration_en_cours["schema_deja_present"]:
            print(f"   ↷ Migration : {nom} de données ignoré — schéma déjà présent, "
                  "données supposées déjà synchronisées.")
            return None
        return originale(self, *args, **kwargs)

    setattr(Operations, nom, gardee)


def _apres_migration(**_kwargs):
    _migration_en_cours["schema_deja_present"] = False


# Garde : env.py peut être rechargé dans le même processus (stamp puis
# upgrade…) — ne pas envelopper deux fois.
if not getattr(Operations, "_lekol360_tolerant", False):
    for _nom in _OPS_SCHEMA:
        _rendre_tolerante(_nom)
    for _nom in _OPS_DONNEES:
        _sauter_si_schema_present(_nom)
    Operations._lekol360_tolerant = True

def include_object(object, name, type_, reflected, compare_to): 
    if type_ == "table" and reflected and compare_to is None:
        return False
    return True

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    try:
        engine = get_engine_dynamically()
        # On extrait l'URL sous forme de chaîne de caractères
        url = str(engine.url)
    except Exception as e:
        print(f"Erreur lors de la récupération de l'URL : {e}")
        return
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = get_engine_dynamically()

    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    #     compare_type=True
    # )

    with connectable.connect() as connection:
        context.configure(
            include_object=include_object,
            connection=connection, target_metadata=target_metadata,
            on_version_apply=_apres_migration,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
