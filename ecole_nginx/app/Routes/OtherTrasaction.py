from sqlalchemy import select, func
from app.Models.MFinancials import OtherTransaction

class TransactionService:
    def __init__(self):
        self.session = SessionLocal()

    # --- READ avec PAGINATION ---
    def get_all(self, page=1, per_page=10):
        try:
            offset = (page - 1) * per_page
            
            # Requête pour les données
            stmt = select(OtherTransaction).offset(offset).limit(per_page)
            results = self.session.execute(stmt).scalars().all()
            
            # Requête pour le total (utile pour l'interface)
            total = self.session.query(func.count(OtherTransaction.id)).scalar()
            
            return {
                "data": results,
                "total": total,
                "page": page,
                "last_page": (total + per_page - 1) // per_page
            }
        finally:
            self.session.close()

    # --- CREATE ---
    def create(self, description, montant, user_id):
        new_trans = OtherTransaction(
            description=description,
            montant=montant,
            user_id=user_id
        )
        try:
            self.session.add(new_trans)
            self.session.commit()
            self.session.refresh(new_trans)
            return new_trans
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    # --- UPDATE ---
    def update(self, trans_id, **kwargs):
        try:
            trans = self.session.get(OtherTransaction, trans_id)
            if trans:
                for key, value in kwargs.items():
                    setattr(trans, key, value)
                self.session.commit()
            return trans
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    # --- DELETE ---
    def delete(self, trans_id):
        try:
            trans = self.session.get(OtherTransaction, trans_id)
            if trans:
                self.session.delete(trans)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()