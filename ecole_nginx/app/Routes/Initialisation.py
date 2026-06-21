from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MModels import User,Niveau
from app.Models.MSystems import Role,Permission

router = APIRouter(prefix="/api/v1", tags=["First Check"])

ROLES = [
    "admin", "user", "student", "teacher", "Directeur",
    "Responsable financier", "Responsable pédagogique",
    "Enseignant", "Secrétaire général",
    "Responsable des admissions", "Conseiller pédagogique",
    "Responsable informatique", "Surveillant",
    "Psychologue scolaire", "Gestionnaire de la bibliothèque",
    "Responsable des transports", "Comptable",
    "Chargé de la communication",
    "Responsable des activités extrascolaires",
    "Responsable des ressources humaines",
    "Chef de département", "Formateur",
    "Technicien de laboratoire", "Coordinateur de projet"
]


@router.get("/first-check")
def first_check(db: Session = Depends(get_db)):
    try:
     #    user = db.query(User).first()
        user = (
          db.query(User)
          .order_by(User.created_at.asc())
          .first()
          )
        if user:
            # print(user.__dict__)
            return {"status": True}
        # return {"status": False},422
        raise HTTPException(status_code=422, detail=f"Erreur serveur {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur {e}")


@router.get("/first-account-fill")#, include_in_schema=False
def fill_roles_and_permissions(db: Session = Depends(get_db)):
    try:
        # ------------------
        # ------------------
        for name in ROLES:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                db.add(Role(name=name, guard_name="web"))

        # db.commit()

        # ------------------
        # ------------------
        permissions = [
            "Ajouter etudiant", "Modifier permission", "Supprimer etudiant", "Voir permission",
            "Ajouter paiement", "Modifier paiement", "Supprimer paiement", "Voir paiement",
            "Ajouter classe", "Modifier classe", "Supprimer classe", "Voir classe",
            "Ajouter cours", "Modifier cours", "Supprimer cours", "Voir cours",
            "Ajouter note", "Modifier note", "Supprimer note", "Voir note",
            "Ajouter personnel", "Modifier personnel", "Supprimer personnel", "Voir personnel",
            "Ajouter profile", "Modifier profile", "Supprimer profile", "Voir profile",
            "Ajouter professeur", "Modifier professeur", "Supprimer professeur", "Voir professeur",
            "Ajouter role", "Modifier role", "Supprimer role", "Voir role",
            "Ajouter parametre", "Modifier parametre", "Supprimer parametre", "Voir parametre", "Supprimer transaction","Modifier transaction", 
            "Imprimer vente", "Imprimer paiement", "Imprimer rapport",
            "Imprimer rapport pedagogique", "Imprimer bulletin", "Imprimer enregistrement"
        ]

        for name in permissions:
            if not db.query(Permission).filter(Permission.name == name).first():
                db.add(Permission(name=name, guard_name="web"))

        # db.commit()

        # ------------------
        # ------------------
     #    resources = [
     #        "etudiant", "paiement", "classe", "cours", "note",
     #        "personnel", "profile", "professeur", "role", "parametre",
     #        "recu vente", "recu paiement", "rapport",
     #        "rapport pedagogique", "bulletin", "liste enregistrement"
     #    ]

     #    actions = ["Ajouter", "Modifier", "Supprimer", "Voir"]

     #    for resource in resources:
     #        for action in actions:
     #            name = f"{action} {resource}"
     #            if not db.query(Permission).filter(Permission.name == name).first():
     #                db.add(Permission(name=name, guard_name="web"))

     #    db.commit()

        # ------------------
        # ------------------
        niveaux = ["Maternelle", "Primaire","Secondaire", "Technique", "Universitaire"]
        for niveau in niveaux:
            if not db.query(Niveau).filter(Niveau.name == niveau).first():
                db.add(Niveau(name=niveau))

        # db.commit()

        # ------------------
        # ------------------


        db.commit()
        return {"status": True, "message": "Initialisation terminée"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

     

