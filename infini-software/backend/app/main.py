from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.database import Base, engine
from app.routes import admin, install, licence

Base.metadata.create_all(bind=engine)

# Migration SQLite : ajoute les colonnes manquantes sur les tables existantes.
def _run_migrations():
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(pricing_config)"))}
        if "auto_release" not in existing:
            conn.execute(text("ALTER TABLE pricing_config ADD COLUMN auto_release BOOLEAN NOT NULL DEFAULT 0"))
            conn.commit()

_run_migrations()

app = FastAPI(title="Infini Software API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(install.router)
app.include_router(licence.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
