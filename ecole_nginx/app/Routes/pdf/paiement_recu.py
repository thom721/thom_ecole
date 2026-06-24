from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from typing import Optional
from app.database import get_db
from app.Models.MFinancials import Paiement
from app.Models.MSystems import Profile
from app.Helper.pdf_personaliser import PDFGenerator
import logging
import json
logger = logging.getLogger(__name__)


class GeneratePDFRecuRequest(BaseModel):
    """Requête pour générer un reçu PDF"""
    id: UUID4 = Field(..., description="ID du paiement (UUID)")
    key: int = Field(..., description="Clé/index du paiement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "key": 0
            }
        }

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

def sa_to_dict(obj):
    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
    }

@router.post("/print-recu")
def generate_pdf_recu(
    request: GeneratePDFRecuRequest,
    db: Session = Depends(get_db)
):
    """
    Génère un PDF de reçu de paiement
    
    **Paramètres:**
    - **id**: UUID du paiement
    - **key**: Index du paiement dans info_paiement
    
    **Retourne:** Un fichier PDF en stream
    """
    
    try:
        # Vérifier que le paiement existe
        paiement_exists = db.query(
            select(Paiement.id).where(Paiement.id == str(request.id)).exists()
        ).scalar()
        
        if not paiement_exists:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"id": ["Le paiement spécifié n'existe pas"]}}
            )
        
        # Récupérer le paiement avec les relations
        paiement = db.query(Paiement).options(
            joinedload(Paiement.etudiant),
            joinedload(Paiement.niveau_ref),
            joinedload(Paiement.classe_ref)
        ).filter(Paiement.id == str(request.id)).first()
        

        if not paiement:
            raise HTTPException(
                status_code=404,
                detail={"errors": "Paiement non trouvé"}
            )
        # data = paiement.model_dump()
        
        data = sa_to_dict(paiement)
        try:
            
            paiement_details = json.loads(data.get("paiement_details", "{}")) \
                if isinstance(data.get("paiement_details", {}), str) else data.get("paiement_details", {})
            
            paiement = paiement_details.get('paiement_details', {})
            etudiant = paiement.get('details_etudiant', {})
            mois = paiement.get('mois', {})
            echeance = list(paiement.get('check_echeance', {}).keys())
        except Exception as e:
            logger.error(f"Erreur génération PDF  122: {str(e)}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail={"errors": str(e)}
            )
            
        # info_paiement vient d'une colonne JSON MySQL : l'ordre des clés
        # n'est PAS garanti d'être l'ordre chronologique d'insertion. Le web
        # et le bureau trient tous deux par date avant d'afficher l'historique
        # et d'en déduire l'index ("key") envoyé ici — on doit donc trier de
        # la même façon ici pour indexer le bon paiement, sinon le reçu
        # imprimé ne correspond pas à celui affiché.
        def _sort_key(item):
            try:
                return datetime.strptime(item[0], '%d-%m-%Y %H:%M')
            except (ValueError, TypeError):
                return datetime.min

        info_items = sorted(paiement.get('info_paiement', {}).items(), key=_sort_key)

        if 0 <= request.key < len(info_items):
            date_clef, paiement = info_items[request.key]
            # print("Clé (date) à l'index", keys, ":", date_clef)
            # print("Infos du paiement:", paiement)
        else:
            print("Index hors limites")
                # Récupérer les informations du profil
        info = db.query(Profile).first()

        # logo_base64_brut = info['logo_image_base64'] 

        # # Vérification du préfixe pour que le HTML le reconnaisse
        # if not logo_base64_brut.startswith('data:image'):
        #     # On ajoute le préfixe (adapte png ou jpg selon ton format)
        #     logo_final = f"data:image/png;base64,{logo_base64_brut}"
        # else:
        #     logo_final = logo_base64_brut
        logger.error(f"Erreur génération PDF ooffffffffffooo: {paiement}")
        data = {
            "info": info, 
            "date": date_clef, 
            "payment": paiement,
            "mois" : mois,
            "echeance_keys":echeance,
            'etudiant':etudiant,
            'logo_path':''
            }       

        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "paiement_recu.html",  # Votre template Jinja2
        data,
        "paiement_recu.pdf"
    )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=paiement_recu.pdf"
               }
          )
    except HTTPException:
        import traceback
        traceback.print_exc()
        raise
    except Exception as e:
        logger.error(f"Erreur génération PDF  11: {str(e)}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={"errors": str(e)}
        )