from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import admin, install, licence

Base.metadata.create_all(bind=engine)

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
