"""
Écriture explicite de Log — contournement de GlobalModelObserver/
ObservableMixin (app/Observers/global_observer.py), dont la session dédiée
(créée une fois au démarrage, voir main.py::register_observers) n'est plus
jamais committée depuis que son propre self.db.commit() a été retiré (pour
stopper un ResourceClosedError sur commit imbriqué — voir commit 734a71c).
Tout modèle qui compte uniquement sur cet observateur pour son audit trail
n'a donc en réalité JAMAIS de ligne Log persistée, sans aucune erreur
visible — déjà découvert et contourné au cas par cas (AnnulationArriere,
Payroll/PayrollVersement, Paiement). `log_action()` centralise ce même
contournement pour les modèles qui ne l'avaient pas encore.

À appeler sur la session de la REQUÊTE (celle qui vient de commit() la
mutation réelle), jamais sur une session à part.
"""
import json
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.Models.MSystems import Log


def _json_safe(value: Any) -> Any:
    """Rend une valeur (dict de colonnes, dates incluses) sérialisable pour
    les colonnes JSON old_values/new_values de Log."""
    if value is None:
        return None
    return json.loads(json.dumps(value, default=str))


def log_action(
    db: Session,
    user_id: str,
    action: str,
    model_type: str,
    model_id: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    reason: Optional[str] = None,
    authorization_id: Optional[str] = None,
) -> None:
    db.add(Log(
        action=action,
        user_id=user_id,
        authorization_id=authorization_id,
        model_type=model_type,
        model_id=model_id,
        old_values=_json_safe(old_values),
        new_values=_json_safe(new_values),
        reason=reason,
    ))
    db.commit()
