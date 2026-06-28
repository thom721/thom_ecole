
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, desc, func, String
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date,timedelta
from enum import Enum
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
from app.Models.MSystems import Log
from app.Schemas.SLog import *
import math
import logging
from app.Models.MModels import User
import json
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Logs"])

@router.get("/logs-graphic", response_model=Union[PaginatedLogsResponse, LogsResponse])
async def index(
    search: Optional[str] = Query(None, description="Recherche dans date, user, action, model"),
    page: Optional[int] = Query(None, ge=1, description="Numéro de page pour la pagination"),
    action: Optional[ActionType] = Query(None, description="Filtrer par action"),
    model: Optional[str] = Query(None, description="Filtrer par model_type"),
    user: Optional[str] = Query(None, description="Filtrer par utilisateur"),
    date_from: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    per_page: int = Query(16, ge=1, le=100, description="Nombre d'éléments par page"),
    sort_by: str = Query("updated_at", description="Champ de tri"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Ordre de tri"),
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """
    Liste tous les logs avec filtres optionnels
    
    Filtres disponibles:
    - **search**: Recherche globale dans date, user, action, model
    - **action**: Filtre par type d'action (create, update, delete, etc.)
    - **model**: Filtre par type de modèle
    - **user**: Filtre par nom d'utilisateur
    - **date_from**: Logs à partir de cette date
    - **date_to**: Logs jusqu'à cette date
    
    Pagination:
    - **page**: Numéro de page (si null, retourne tous les résultats)
    - **per_page**: Nombre d'éléments par page (défaut: 16, max: 100)
    
    Tri:
    - **sort_by**: Champ de tri (défaut: updated_at)
    - **sort_order**: Ordre de tri (asc/desc, défaut: desc)
    """
    
    try:
        # Construire la requête de base
        query = select(Log)
        
        # Appliquer les filtres
        filters = []
        
        # Filtre de recherche globale
        if search:
            search_filter = or_(
                Log.date.cast(String).like(f"%{search}%"),
                Log.user.like(f"%{search}%"),
                Log.action.like(f"%{search}%"),
                Log.model.like(f"%{search}%")
            )
            filters.append(search_filter)
        
        # Filtrer par action
        if action:
            filters.append(Log.action == action.value)
        
        # Filtrer par model_type
        if model:
            filters.append(Log.model_type == model)
        
        # Filtrer par utilisateur
        if user:
            filters.append(Log.user.like(f"%{user}%"))
        
        # Filtrer par plage de dates
        if date_from:
            filters.append(Log.date >= datetime.combine(date_from, datetime.min.time()))
        
        if date_to:
            filters.append(Log.date <= datetime.combine(date_to, datetime.max.time()))
        
        # Appliquer tous les filtres
        if filters:
            query = query.where(and_(*filters))
        
        # Si pas de pagination demandée, retourner tous les résultats
        if page is None:
            # Appliquer le tri
            sort_column = getattr(Log, sort_by, Log.updated_at)
            if sort_order == SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
            
            results = db.execute(query).scalars().all()

            data = [
                LogResource.model_validate({
                    **log.__dict__,
                    "user": log.user.name if log.user else None,
                    "admin": log.admin.name if log.admin else None,
                })
                for log in results
            ]
                        
            return LogsResponse(
                data=data#[LogResource.model_validate(log) for log in results]
            )
        
        # Pagination
        # Compter le total
        count_query = select(func.count()).select_from(Log)
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total = db.execute(count_query).scalar()
        
        # Calculer les métadonnées de pagination
        last_page = math.ceil(total / per_page) if total > 0 else 1
        offset = (page - 1) * per_page
        
        # Appliquer la pagination et l'ordre
        sort_column = getattr(Log, sort_by, Log.updated_at)
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        query = query.offset(offset).limit(per_page)
        
        results = db.execute(query).scalars().all()
        
        # Calculer from et to
        from_ = offset + 1 if total > 0 else 0
        to = min(offset + per_page, total)
        
        # Construire les liens de pagination
        base_url = "/logs"
        links = PaginationLinks(
            first=f"{base_url}?page=1&per_page={per_page}",
            last=f"{base_url}?page={last_page}&per_page={per_page}",
            prev=f"{base_url}?page={page-1}&per_page={per_page}" if page > 1 else None,
            next=f"{base_url}?page={page+1}&per_page={per_page}" if page < last_page else None
        )
        
        # Construire la réponse paginée
        return PaginatedLogsResponse(
            # data=[LogResource.model_validate(log) for log in results],
            data = [
                    LogResource.model_validate({
                        "id": log.id,
                        "action": log.action,
                        "user": log.user.name if log.user else None,
                        'authorization_id' : log.admin.name if log.user else None,
                        'model_type' : log.model_type,
                        'model_id'   : log.model_id,
                        "reason": log.reason,
                        "updated_at": log.updated_at,
                    })
                    for log in results
                ],
            meta=PaginationMeta(
                current_page=page,
                per_page=per_page,
                total=total,
                last_page=last_page,
                from_=from_,
                to=to,
                path=base_url
            ),
            links=links
        )
        
    except Exception as e:
        logger.error(f"Erreur dans index logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.get("/stats", response_model=LogStatsResponse)
async def log_stats(
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques des logs
    
    Retourne:
    - Nombre total de logs
    - Répartition par action
    - Répartition par modèle
    - Nombre de logs des dernières 24h
    """
    
    try:
        # Total de logs
        total_logs = db.execute(select(func.count()).select_from(Log)).scalar()
        
        # Répartition par action
        actions_query = select(
            Log.action,
            func.count(Log.id).label('count')
        ).group_by(Log.action)
        
        actions_results = db.execute(actions_query).all()
        actions_count = {row.action: row.count for row in actions_results if row.action}
        
        # Répartition par modèle
        models_query = select(
            Log.model,
            func.count(Log.id).label('count')
        ).group_by(Log.model)
        
        models_results = db.execute(models_query).all()
        models_count = {row.model: row.count for row in models_results if row.model}
        
        # Activité récente (dernières 24h)
        yesterday = datetime.now() - timedelta(days=1)
        recent_query = select(func.count()).select_from(Log).where(
            Log.created_at >= yesterday
        )
        recent_activity = db.execute(recent_query).scalar()
        
        return LogStatsResponse(
            total_logs=total_logs,
            actions_count=actions_count,
            models_count=models_count,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Erreur dans log_stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.get("/logs-graphic-show/{item}", response_model=LogShowResponse)
async def log_show(
    item: str = Path(..., description="ID du log à récupérer"),
    db: Session = Depends(get_db)
):
    """
    Récupère un log spécifique par son ID
    
    - **item**: ID unique du log
    
    Retourne les détails complets du log incluant old_values et new_values
    """
    
    try:
        # Récupérer le log
        log = db.query(Log).filter(Log.id == item).first()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail={"errors": f"Log avec ID {item} non trouvé"}
            )
        
        return LogShowResponse(
            data=LogBase.model_validate({
                **log.__dict__,
                # old_values/new_values sont des colonnes JSON (dict côté
                # SQLAlchemy) mais LogBase les déclare en str — sérialiser
                # explicitement pour éviter l'échec de validation Pydantic.
                "old_values": json.dumps(log.old_values, ensure_ascii=False) if log.old_values is not None else None,
                "new_values": json.dumps(log.new_values, ensure_ascii=False) if log.new_values is not None else None,
                "date": log.updated_at,
            })
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans log_show: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.delete("/logs-graphic/{item_id}")
async def log_delete(
    item_id: str = Path(..., description="ID du log à supprimer"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),current_user:User= Depends(get_current_user)
):
    """
    Supprime un log spécifique (requiert des permissions admin)
    """
    
    try:
        # Vérifier les permissions
        user_has_permission(user, "Supprimer log", db)
        
        # Récupérer le log
        log = db.query(Log).filter(Log.id == item_id).first()
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail={"errors": f"Log avec ID {item_id} non trouvé"}
            )
        
        # Supprimer
        db.delete(log)
        db.commit()
        
        return {"message": "Log supprimé avec succès"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans log_delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})

  