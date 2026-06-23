import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Surchargeable via env (Docker : pointe vers un volume monté, ex. /data/infini.db,
# pour que la base survive à la recréation du conteneur — voir docker-compose.yml).
DB_PATH = Path(os.getenv("INFINI_DB_PATH", str(Path(__file__).resolve().parent.parent / "infini.db")))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
