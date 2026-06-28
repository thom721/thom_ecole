from fastapi import APIRouter, Depends, Query,status,HTTPException,Header
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_,String,func, extract
from app.database import get_db
from app.Models.MModels import Etudiant, User,Professeur
from app.Models.MFinancials import Vente,Depense,Loan, OrderItem,LoanRepayment,Produit
from app.Models.MSystems import Personnel
from app.Schemas.SVente import * 
import random 
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe,DualAuthChecker,verify_dual_auth
from app.Helper.context import UserContext,ActionContext,ReasonContext,AdminAuthorization
 
from datetime import date, datetime
from decimal import Decimal

router = APIRouter(prefix="/api/v1", tags=["Vente"])

@router.get("/vente", response_model=PaginatedResponse)
def index_ventes(
    search: str | None = None,
    page: int = 1,
    per_page: int = 16,
    db: Session = Depends(get_db),
):
    skip = (page - 1) * per_page

    query = (
        db.query(Vente)
        .options(
            joinedload(Vente.user),
            joinedload(Vente.etudiant),
            joinedload(Vente.order_items),
        )
    )

    if search:
        query = query.filter(
            or_(
                Vente.etudiant.has(
                    or_(
                        Etudiant.nom.ilike(f"%{search}%"),
                        Etudiant.prenom.ilike(f"%{search}%"),
                        Etudiant.identifiant.ilike(f"%{search}%"),
                    )
                ),
                Vente.user.has(User.name.ilike(f"%{search}%")),
                Vente.order_itemId.ilike(f"%{search}%"),
            )
        )

    total = query.count()

    ventes = (
        query
        .order_by(Vente.updated_at.desc())
        .offset(skip)
        .limit(per_page)
        .all()
    )

    return {
        "data": [VenteSchema.from_model(v) for v in ventes],
        "meta": {
            "current_page": page,
            "last_page": (total + per_page - 1) // per_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if ventes else 0,
            "to": skip + len(ventes) if ventes else 0,
        }
    }

def decrement_produit_stock(db: Session, produit_id: str | None, quantite: float):
    """Décrémente le stock du produit vendu. Lève une 422 si le stock est
    insuffisant, pour éviter de survendre un produit enregistré."""
    if not produit_id:
        return
    produit = db.query(Produit).filter(Produit.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    # quantite_stock est Numeric (Decimal côté Python) : on convertit via
    # str() plutôt que de mélanger Decimal et float (lève TypeError sinon),
    # même convention que repay_loan() plus bas dans ce fichier.
    quantite_dec = Decimal(str(quantite))
    if produit.quantite_stock < quantite_dec:
        raise HTTPException(
            status_code=422,
            detail=f"Stock insuffisant pour {produit.nom} (disponible: {produit.quantite_stock})",
        )
    produit.quantite_stock -= quantite_dec
    db.add(produit)


# fonction pour générer un order_itemId unique
def generate_unique_order_item_id(db: Session):
    while True:
        order_item_id = random.randint(100000, 999999)
        exists = db.query(Vente).filter(Vente.order_itemId == order_item_id).first()
        if not exists:
            return order_item_id


@router.get("/order-vente/{vente}")
def show_order_items(vente: str, db: Session = Depends(get_db), current_user:User= Depends(get_current_user)):
    items = db.query(OrderItem).filter(OrderItem.vente_id == vente).all()
    return {"data": [
        {
            "id": item.id,
            "nom": item.nom,
            "category": item.category,
            "prix": item.prix,
            "quantite": item.quantite,
            "total": item.total,
            "status": item.status,
            "vente_id": item.vente_id,
            "user_id": item.user_id,
            "produit_id": item.produit_id
        }
        for item in items
    ]}
    # 'id','order_itemId','nom','quantite','total','utilisateur','date'

@router.post("/vente")
def store_vente(
    data: VenteSchemaPost,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_approval_token: str | None = Header(None),
):
    UserContext.set_user_id(current_user.id)
    try:
        user = db.query(User).filter(User.id == str(data.user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        Gtotal = 0
        quantite = 0

        if data.id:
            # 🔹 Update
            ActionContext.set_action("update")
            # vérifier autorisation admin si nécessaire
            vente = db.query(Vente).filter(Vente.id == data.id).first()
            if not vente:
                raise HTTPException(status_code=404, detail="Vente not found")
            # ActionPersonalisation.setPersoAction('update')
            auth_data = verify_dual_auth("Modifier paiement", x_approval_token, db, current_user)
            AdminAuthorization.set_admin_id(auth_data["admin_id"])

            for item_data in data.items:
                status_value = item_data.status or 1
                if item_data.id:
                    order_item = db.query(OrderItem).filter(OrderItem.id == item_data.id).first()
                    if order_item:
                        order_item.nom = item_data.nom
                        order_item.category = item_data.category
                        order_item.prix = item_data.prix
                        order_item.quantite = item_data.quantite
                        order_item.total = item_data.total
                        order_item.status = status_value
                        db.add(order_item)
                        Gtotal += item_data.total
                        quantite += item_data.quantite
                else:
                    # nouvel item
                    decrement_produit_stock(db, item_data.produit_id, item_data.quantite)
                    order_item = OrderItem(
                        nom=item_data.nom,
                        category=item_data.category,
                        prix=item_data.prix,
                        status=status_value,
                        quantite=item_data.quantite,
                        total=item_data.total,
                        vente_id=vente.id,
                        user_id=current_user.id,
                        produit_id=item_data.produit_id
                    )
                    db.add(order_item)
                    Gtotal += item_data.total
                    quantite += item_data.quantite

            # mettre à jour total et quantite de la vente
            # vente.total = sum([oi.total for oi in vente.order_items if oi.status == 1])
            # if vente.etudiant_id != data.etudiant_id:
            #     vente.etudiant_id = data.etudiant_id
            # db.add(vente)
            db.commit()
            db.refresh(vente)
            return {"success": "success", "id": vente.id}

        else:
            # 🔹 Create
            ActionContext.set_action("create")
            # ActionPersonalisation.setPersoAction('create')
            if not user_has_permission(current_user, "Ajouter paiement",db):
                raise HTTPException(status_code=403, detail="Unauthorized to update payment")

            vente = Vente(
                user_id=current_user.id,
                order_itemId=generate_unique_order_item_id(db),
                etudiant_id=data.etudiant_id
            )
            db.add(vente)
            db.commit()
            db.refresh(vente)

            for item_data in data.items:
                decrement_produit_stock(db, item_data.produit_id, item_data.quantite)
                order_item = OrderItem(
                    nom=item_data.nom,
                    category=item_data.category,
                    prix=item_data.prix,
                    status=item_data.status or 1,
                    quantite=item_data.quantite,
                    total=item_data.total,
                    vente_id=vente.id,
                    user_id=current_user.id,
                    produit_id=item_data.produit_id
                )
                db.add(order_item)
                Gtotal += item_data.total
                quantite += item_data.quantite

            vente.total = Gtotal
            vente.quantite = quantite
            db.add(vente)
            db.commit()
            db.refresh(vente)
            return {"success": "success", "id": vente.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))



@router.delete("/order_item")
def destroy_order_item(
    order_item_id: str = Query(..., alias="vente"),
    vente_id: str = Query(...),
    raison: str = Query(..., min_length=20, max_length=150),
    db: Session = Depends(get_db),
    # current_user:User= Depends(get_current_user)
    auth_data: dict = Depends(DualAuthChecker("Supprimer paiement")),

):
    current_user = auth_data["user_id"]
    current_admin = auth_data["admin_id"]
    # if not user_has_permission(current_user, "Supprimer paiement",db):
    #     raise HTTPException(status_code=403, detail="Unauthorized to delete payment")

    UserContext.set_user_id(current_user)
    AdminAuthorization.set_admin_id(current_admin)
    ReasonContext.set_reason(raison)
    try:
        order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
        if not order_item:
            raise HTTPException(status_code=404, detail="OrderItem not found")
        ActionContext.set_action("delete")
        db.delete(order_item)
        db.commit()

        vente = db.query(Vente).filter(Vente.id == vente_id).first()
        if not vente:
            raise HTTPException(status_code=404, detail="Vente not found")

        total_vente = sum([oi.total for oi in vente.order_items])
        if total_vente == 0:
            db.delete(vente)
            db.commit()

        return {"success": "Opération réussie", "total_vente": total_vente}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/get-loans")
def index_loans(
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    get_current: User = Depends(get_current_user),
):
    query = db.query(Loan).options(
        joinedload(Loan.repayments),
        joinedload(Loan.user),
    ).order_by(Loan.created_at.desc())
 
    if user_has_role(get_current, ["admin"],db):
        total = query.count()

        loans = (
            query.offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "data": [LoanSchema.from_model(l) for l in loans],
            "meta": {
                "current_page": page,
                "last_page": (total + per_page - 1) // per_page,
                "per_page": per_page,
                "total": total,
                "from": (page - 1) * per_page + 1 if total else 0,
                "to": (page - 1) * per_page + len(loans) if total else 0,
            }
        }
 
    loans = (
        query.filter(Loan.user_id == get_current.id)
        .all()
    )

    return {
        "data": [LoanSchema.from_model(l) for l in loans]
    }

@router.get("/get-data-user-for-loans")
def get_data_user_for_loans(db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    # 🔹 récupérer tous les users Professeur ou Personnel
    users = db.query(User).filter(
        User.userable_id.in_([Professeur.id, Personnel.id])
        
    ).all()
    from sqlalchemy.orm import aliased

    # Aliases pour les tables
    Prof = aliased(Professeur)
    Pers = aliased(Personnel)

    users = db.query(User, Prof.nom.label("prof_nom"), Prof.prenom.label("prof_prenom"),
                    Pers.nom.label("pers_nom"), Pers.prenom.label("pers_prenom")) \
        .outerjoin(Prof,  (User.userable_id == Prof.id)) \
        .outerjoin(Pers,  (User.userable_id == Pers.id)) \
        .filter(User.userable_id.in_([Pers.id, Prof.id])) \
        .all()


    result = []
    for u, prof_nom, prof_prenom, pers_nom, pers_prenom in users:
        if u.userable_type == "App\\Models\\Professeur":
            nom = prof_nom or ""
            prenom = prof_prenom or ""
        else:
            nom = pers_nom or ""
            prenom = pers_prenom or ""

        result.append({
            "id": u.id,
            "nom": nom,
            "prenom": prenom,
            "type": u.userable_type
        })
    # users = db.query(User).filter(User.userable_type.in_(["App\\Models\\Professeur",App\\Model\\Personnel"])).all()

    # result = []
    # for u in users:
    #     userable_obj = u.userable(db)
    #     result.append({
    #         "id": u.id,
    #         "nom": getattr(userable_obj, "nom", "") if userable_obj else "",
    #         "prenom": getattr(userable_obj, "prenom", "") if userable_obj else "",
    #         "type": u.userable_type
    #     })

    return {"data": result}

@router.post("/post-loans")
def store_loan(data: LoanCreateSchema, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    # Vérifier que l'user existe
    UserContext.set_user_id(current_user.id)
    user = db.query(User).filter(User.id == str(data.user_id)).first()
    if not user:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    ActionContext.set_action("Create")
    try:
        loan = Loan(
            user_id=str(data.user_id),
            amount=data.amount,
            term_months=data.term_months,
            interest_rate=data.interest_rate,
            monthly_payment=data.monthly_payment,
            remaining_balance=data.amount,
            status=data.status or "pending"
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)

        return {"success": "success"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/loans/repay")
def repay_loan(
    data: LoanRepaySchema,
    db: Session = Depends(get_db),
    current_user:User= Depends(get_current_user)  # équivalent $req->user()
):
    UserContext.set_user_id(current_user.id)
    # 🔹 Vérifier que le prêt existe
    loan = db.query(Loan).filter(Loan.id == str(data.loans_id)).first()
    if not loan:
        raise HTTPException(status=404, detail="Loan not found")
    ActionContext.set_action("Create")
    # 🔹 Créer le remboursement
    repayment = LoanRepayment(
        loans_id=str(data.loans_id),
        paid_amount=data.paid_amount,
        payment_date=datetime.utcnow(),
        payment_method=data.payment_method,
        collected_by=current_user.id
    )
    db.add(repayment)

    # 🔹 Mettre à jour le prêt
    # loan.remaining_balance = (loan.remaining_balance or loan.amount) - data.paid_amount
    # if loan.remaining_balance <= 0:
    #     loan.remaining_balance = 0
    #     loan.status = "paid"
    from decimal import Decimal
 
    loan.remaining_balance = Decimal(str(loan.remaining_balance or loan.amount)) - Decimal(str(data.paid_amount))

    if loan.remaining_balance <= 0:
        loan.remaining_balance = 0
        loan.status = "paid"

    db.commit()
    db.refresh(repayment)
    db.refresh(loan)

    # 🔹 Retourner le remboursement
    return {
        "id": repayment.id,
        "loans_id": repayment.loans_id,
        "paid_amount": repayment.paid_amount,
        "payment_date": repayment.payment_date.strftime("%Y-%m-%d %H:%M:%S"),
        "payment_method": repayment.payment_method,
        "collected_by": repayment.collected_by
    }
 


@router.get("/depense")
def index_depense(
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(16, le=100),
    db: Session = Depends(get_db),
    current_user:User= Depends(get_current_user)
):
    query = db.query(Depense).options(joinedload(Depense.user))

    # if search:
    #     query = query.filter(
    #         or_(
    #             Depense.description.ilike(f"%{search}%"),
    #             Depense.updated_at.cast(String).ilike(f"%{search}%"),
    #             Depense.user.has(User.name.ilike(f"%{search}%")),
    #         )
    #     )

    if search:
        query = query.filter(
            or_(
                Depense.description.ilike(f"%{search}%"),
                Depense.updated_at.cast(String).ilike(f"%{search}%"),
                Depense.user.has(User.name.ilike(f"%{search}%")),
            )
        )

    total = query.count()

    depenses = (
        query.order_by(Depense.updated_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
#  [VenteSchema.model_validate(v) for v in ventes]
    return {
        "data": [DepenseSchema.from_model(d) for d in depenses],
        "meta": {
            "current_page": page,
            "last_page": (total + per_page - 1) // per_page,
            "per_page": per_page,
            "total": total,
            "from": (page - 1) * per_page + 1 if total else 0,
            "to": (page - 1) * per_page + len(depenses) if total else 0,
        },
    }


@router.post("/depense")
def store_depense(
    data: DepenseSchemaPost,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_approval_token: str | None = Header(None),
):
    user_id = current_user.id
    UserContext.set_user_id(user_id)
    # 🔹 Si update, vérifier autorisation admin (PIN si le rôle courant n'a pas la permission)
    if data.id:
        auth_data = verify_dual_auth("Modifier paiement", x_approval_token, db, current_user)
        AdminAuthorization.set_admin_id(auth_data["admin_id"])

    try:
        if data.id:
            # 🔹 Update existant
            ActionContext.set_action("update")
            depense = db.query(Depense).filter(Depense.id == data.id).first()
            if not depense:
                raise HTTPException(status_code=404, detail="Depense not found")
            
            depense.description = data.description
            depense.prix = data.prix
            db.commit()
            db.refresh(depense)


            return {"success": "success"}

        else:
            if not user_has_permission(current_user,"Ajouter paiement",db):
                raise HTTPException(status_code=403, detail="Unauthorized to update payment")
            # 🔹 Création
            ActionContext.set_action("Create")
            depense = Depense(
                user_id=user_id,
                description=data.description,
                prix=data.prix
            )
            db.add(depense)
            db.commit()
            db.refresh(depense)

            # 🔹 Action personnalisation
            # ActionPersonalisation.setPersoAction('create')  # à implémenter si nécessaire

            return {"success": "success"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delete-depense")
def delete_depense(
    id_depense: str = Query(...),
    raison: str = Query(..., min_length=20, max_length=150),
    db: Session = Depends(get_db),
    # current_user:User= Depends(get_current_user)
    auth_data: dict = Depends(DualAuthChecker("Supprimer paiement")),

):
    current_user = auth_data["user_id"]
    current_admin = auth_data["admin_id"]
    UserContext.set_user_id(current_user)
    AdminAuthorization.set_admin_id(current_admin)
    ReasonContext.set_reason(raison)

    # Le contrôle d'autorisation réel est déjà fait par DualAuthChecker
    # ci-dessus (qui exige le bon admin via X-Approval-Token si le rôle
    # courant n'a pas la permission). Le re-contrôle qui suivait ici passait
    # current_user (une string id, pas un objet User) à user_has_permission,
    # qui fait toujours `user.id` en interne — ça levait systématiquement une
    # AttributeError et faisait 500 sur CHAQUE appel, même autorisé.

    # 🔹 Action personnalisation
    # ActionPersonalisation.setPersoAction('delete')  # à implémenter si nécessaire
    ActionContext.set_action("delete")
    try:
        depense = db.query(Depense).filter(Depense.id == id_depense).first()
        if not depense:
            raise HTTPException(status_code=404, detail="Depense not found")

        db.delete(depense)
        db.commit()

        return {"success": "Opération réussie"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/stats-ventes")
def stats_ventes(db: Session = Depends(get_db)):
    today = date.today()
    year = today.year
    month = today.month

    # Recettes ce mois
    recettes_ce_mois = db.query(func.sum(Vente.total)).filter(
        extract('year', Vente.created_at) == year,
        extract('month', Vente.created_at) == month
    ).scalar() or 0

    # Recettes mois dernier
    if month == 1:
        last_month_year = year - 1
        last_month = 12
    else:
        last_month_year = year
        last_month = month - 1

    recettes_mois_dernier = db.query(func.sum(Vente.total)).filter(
        extract('year', Vente.created_at) == last_month_year,
        extract('month', Vente.created_at) == last_month
    ).scalar() or 0

    # Calcul évolution %
    if recettes_mois_dernier:
        evolution = round((recettes_ce_mois - recettes_mois_dernier) / recettes_mois_dernier * 100, 2)
    else:
        evolution = 100.0 if recettes_ce_mois else 0.0

    # Frais scolarité perçus
    frais_scolaires_total = db.query(func.sum(Vente.total)).filter(
        Vente.category == "Frais scolarité",
        extract('year', Vente.created_at) == year,
        extract('month', Vente.created_at) == month
    ).scalar() or 0

    total_frais = db.query(func.count(Vente.id)).filter(Vente.category == "Frais scolarité").scalar() or 0
    payes = db.query(func.count(Vente.id)).filter(
        Vente.category == "Frais scolarité",
        Vente.status == "Payé"
    ).scalar() or 0

    # En attente
    en_attente = db.query(func.count(Vente.id)).filter(Vente.status == "En attente").scalar() or 0

    return {
        "ventesCards": [
            {
                "label": "Recettes ce mois",
                "value": f"{recettes_ce_mois:,.0f}",
                "unit": "HTG",
                "color": "text-[#e8eaf0]",
                "sub": f"↑ {evolution}% vs mois dernier" if evolution >= 0 else f"↓ {abs(evolution)}% vs mois dernier",
                "subColor": "text-emerald-400" if evolution >= 0 else "text-red-400"
            },
            {
                "label": "Frais scolarité perçus",
                "value": f"{frais_scolaires_total:,.0f}",
                "unit": "HTG",
                "color": "text-[#e8eaf0]",
                "sub": f"{payes} / {total_frais} élèves"
            },
            {
                "label": "En attente",
                "value": str(en_attente),
                "unit": "",
                "color": "text-amber-400",
                "sub": "élèves non payés"
            }
        ]
    }


 

@router.get("/stats-depenses")
def stats_depenses(db: Session = Depends(get_db)):
    today = date.today()
    year = today.year
    month = today.month

    # --- Dépenses totales ce mois ---
    depenses_ce_mois = db.query(func.sum(Depense.prix)).filter(
        extract('year', Depense.created_at) == year,
        extract('month', Depense.created_at) == month
    ).scalar() or 0

    # --- Salaires ---
    salaires = db.query(func.sum(Depense.prix)).filter(
        extract('year', Depense.created_at) == year,
        extract('month', Depense.created_at) == month,
        Depense.description.ilike('%salaire%')
    ).scalar() or 0

    # --- Opérationnel ---
    operationnel = depenses_ce_mois - salaires

    # --- Répartition par catégorie ---
    repartition_query = (
        db.query(
            Depense.description.label("cat"),
            func.sum(Depense.prix).label("total")
        )
        .filter(
            extract('year', Depense.created_at) == year,
            extract('month', Depense.created_at) == month
        )
        .group_by(Depense.description)
        .order_by(func.sum(Depense.prix).desc())
    )

    repartition_raw = repartition_query.all()

    # Calcul du pourcentage pour chaque catégorie
    repartition = [
        {
            "cat": r.cat,
            "val": round((r.total / depenses_ce_mois) * 100, 2) if depenses_ce_mois else 0
        }
        for r in repartition_raw
    ]

    return {
        "depenseCards": [
            {
                "label": "Dépenses ce mois",
                "value": f"{depenses_ce_mois:,.0f}",
                "color": "text-red-400"
            },
            {
                "label": "Salaires",
                "value": f"{salaires:,.0f}",
                "color": "text-[#e8eaf0]"
            },
            {
                "label": "Opérationnel",
                "value": f"{operationnel:,.0f}",
                "color": "text-[#e8eaf0]"
            }
        ],
        "repartition": repartition
    }

@router.get("/stats-depenses1")
def stats_depenses(db: Session = Depends(get_db)):
    today = date.today()
    year = today.year
    month = today.month

    # Dépenses totales ce mois
    depenses_ce_mois = db.query(func.sum(Depense.prix)).filter(
        extract('year', Depense.created_at) == year,
        extract('month', Depense.created_at) == month
    ).scalar() or 0

    # Salaires
    salaires = db.query(func.sum(Depense.prix)).filter(
        extract('year', Depense.created_at) == year,
        extract('month', Depense.created_at) == month,
        Depense.description.ilike('%salaire%')
    ).scalar() or 0

    # Opérationnel = total - salaires
    operationnel = depenses_ce_mois - salaires

    return {
        "depenseCards": [
            {
                "label": "Dépenses ce mois",
                "value": f"{depenses_ce_mois:,.0f}",
                "color": "text-red-400"
            },
            {
                "label": "Salaires",
                "value": f"{salaires:,.0f}",
                "color": "text-[#e8eaf0]"
            },
            {
                "label": "Opérationnel",
                "value": f"{operationnel:,.0f}",
                "color": "text-[#e8eaf0]"
            }
        ]
    }