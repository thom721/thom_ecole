"""
Mixin pour rendre un modèle observable
"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect



# class ObservableMixin:
#     def notify(self, action):
#         from app.Observers.global_observer import GlobalModelObserver
#         GlobalModelObserver.handle(self, action)


class ObservableMixin:
    """
    Mixin à ajouter aux modèles SQLAlchemy qui doivent être observés
    
    Usage:
        class User(Base, ObservableMixin):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            nom = Column(String(100))
    """
    
    @declared_attr
    def __mapper_args__(cls):
        """Configuration automatique des événements SQLAlchemy"""
        return {
            'eager_defaults': True
        }
    
    @classmethod
    def register_observers(cls, db: Session, request_ip: str = None):
        """
        Enregistrer les observateurs SQLAlchemy pour ce modèle
        À appeler au démarrage de l'application
        """
        from app.Observers.global_observer import GlobalModelObserver
        observer = GlobalModelObserver(db, request_ip)
        
        @event.listens_for(cls, 'after_insert')
        def after_insert(mapper, connection, target):
            """Événement déclenché après insertion"""
            observer.created(target)
        
        @event.listens_for(cls, 'after_update')
        def after_update(mapper, connection, target):
            """Événement déclenché après mise à jour"""
            # Récupérer les anciennes valeurs
            old_values = {}
            state = inspect(target)
            for attr in state.attrs:
                hist = attr.load_history()
                if hist.has_changes() and hist.deleted:
                    old_values[attr.key] = hist.deleted[0]
            
            observer.updated(target, old_values)
        
        @event.listens_for(cls, 'after_delete')
        def after_delete(mapper, connection, target):
            """Événement déclenché après suppression"""
            observer.deleted(target)

