from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.Config import settings
from app.Routes import (
    RAuth, RUsers, RCategories, RCourses, RSections, REnrollments, RResources, RAssignments, RSubmissions,
    RQuestionCategories, RQuestions, RQuizzes, RQuizAttempts,
    RGradeCategories, RGradeItems, RGrades,
    RForums, RChoices, RGlossaries, RWikis, RGroups, RCohorts, REnrollmentMethods, RCalendar, RNotifications,
    RCompletion, RCourseExport, RAccessLogReport, RAccessConditions, RScales, RGradeLetters,
    RIntegration, RLessons, RLessonAttempts,
    RWorkshops, RWorkshopSubmissions, RWorkshopAllocations, RWorkshopAssessments,
    RMessaging, RBadges,
    RCompetencies, RCompetencyPlans, RBlocks,
    RLiveSessions, RInteractiveVideos, RWebhooks,
    RPermissions, RStaffMeetings,
)
from app.database import SessionLocal
from app.Helper.permissions import ensure_permissions_seeded
from app.Helper.bootstrap_admin import ensure_bootstrap_admin

app = FastAPI(title="IUSTH e-learning", version="0.1.0")

API_PREFIX = "/api/v1"

app.include_router(RAuth.router, prefix=API_PREFIX)
app.include_router(RUsers.router, prefix=API_PREFIX)
app.include_router(RUsers.admin_router, prefix=API_PREFIX)
app.include_router(RCategories.router, prefix=API_PREFIX)
app.include_router(RCourses.router, prefix=API_PREFIX)
app.include_router(RSections.router, prefix=API_PREFIX)
app.include_router(REnrollments.router, prefix=API_PREFIX)
app.include_router(RResources.router, prefix=API_PREFIX)
app.include_router(RAssignments.router, prefix=API_PREFIX)
app.include_router(RSubmissions.router, prefix=API_PREFIX)
app.include_router(RQuestionCategories.router, prefix=API_PREFIX)
app.include_router(RQuestions.router, prefix=API_PREFIX)
app.include_router(RQuizzes.router, prefix=API_PREFIX)
app.include_router(RQuizAttempts.router, prefix=API_PREFIX)
app.include_router(RGradeCategories.router, prefix=API_PREFIX)
app.include_router(RGradeItems.router, prefix=API_PREFIX)
app.include_router(RGrades.router, prefix=API_PREFIX)
app.include_router(RForums.router, prefix=API_PREFIX)
app.include_router(RChoices.router, prefix=API_PREFIX)
app.include_router(RGlossaries.router, prefix=API_PREFIX)
app.include_router(RWikis.router, prefix=API_PREFIX)
app.include_router(RGroups.router, prefix=API_PREFIX)
app.include_router(RCohorts.router, prefix=API_PREFIX)
app.include_router(REnrollmentMethods.router, prefix=API_PREFIX)
app.include_router(RCalendar.router, prefix=API_PREFIX)
app.include_router(RNotifications.router, prefix=API_PREFIX)
app.include_router(RCompletion.router, prefix=API_PREFIX)
app.include_router(RCourseExport.router, prefix=API_PREFIX)
app.include_router(RAccessLogReport.router, prefix=API_PREFIX)
app.include_router(RAccessConditions.router, prefix=API_PREFIX)
app.include_router(RScales.router, prefix=API_PREFIX)
app.include_router(RGradeLetters.router, prefix=API_PREFIX)
app.include_router(RIntegration.router, prefix=API_PREFIX)
app.include_router(RLessons.router, prefix=API_PREFIX)
app.include_router(RLessonAttempts.router, prefix=API_PREFIX)
app.include_router(RWorkshops.router, prefix=API_PREFIX)
app.include_router(RWorkshopSubmissions.router, prefix=API_PREFIX)
app.include_router(RWorkshopAllocations.router, prefix=API_PREFIX)
app.include_router(RWorkshopAssessments.router, prefix=API_PREFIX)
app.include_router(RMessaging.router, prefix=API_PREFIX)
app.include_router(RBadges.router, prefix=API_PREFIX)
app.include_router(RCompetencies.router, prefix=API_PREFIX)
app.include_router(RCompetencyPlans.router, prefix=API_PREFIX)
app.include_router(RBlocks.router, prefix=API_PREFIX)
app.include_router(RLiveSessions.router, prefix=API_PREFIX)
app.include_router(RInteractiveVideos.router, prefix=API_PREFIX)
app.include_router(RWebhooks.router, prefix=API_PREFIX)
app.include_router(RPermissions.router, prefix=API_PREFIX)
app.include_router(RStaffMeetings.router, prefix=API_PREFIX)

# CORS enregistré en dernier (couche la plus externe du stack de
# middleware Starlette) — même règle que ecole_nginx/app/main.py:96-116.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _seed_permissions() -> None:
    """Voir plan Épic 21 — upsert idempotent du catalogue de permissions,
    aucune donnée seedée en migration (fragile avec des UUID générés en
    SQL brut), refait à chaque démarrage sans risque de doublon."""
    db = SessionLocal()
    try:
        ensure_permissions_seeded(db)
        ensure_bootstrap_admin(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": "IUSTH e-learning", "status": "ok"}
