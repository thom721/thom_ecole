from app.Models.MSystems import Role,Permission,ModelHasPermission,ModelHasRole,RoleHasPermission
from sqlalchemy.dialects.mysql import insert

# stmt = insert(model_has_roles_table).values(votre_liste_de_roles)
# stmt = stmt.on_duplicate_key_update(role_id=stmt.inserted.role_id)
# session.execute(stmt)
def assign_role(db, user, role):
    exists = db.query(ModelHasRole).filter(
        ModelHasRole.role_id == role.id,
        ModelHasRole.model_id == user.id,
        ModelHasRole.model_type == "App\\Models\\User"
    ).first()

    if not exists:
        db.add(ModelHasRole(
            role_id=role.id,
            model_id=user.id,
            model_type="App\\Models\\User"
        ))
        db.commit()

# def sync_roles(db, user, roles):
#     db.query(ModelHasRole).filter(
#         ModelHasRole.model_id == user.id,
#         ModelHasRole.model_type == "App\\Models\\User"
#     ).delete()

#     for role in roles:
#         db.add(ModelHasRole(
#             role_id=role.id,
#             model_id=user.id,
#             model_type="App\\Models\\User"
#         ))

#     db.commit() 

def sync_roles(db, user, roles): 
    db.query(ModelHasRole).filter(
        ModelHasRole.model_id == user.id,
        ModelHasRole.model_type == "App\\Models\\User"
    ).delete()
 
    unique_role_ids = {role.id for role in roles}
 
    for r_id in unique_role_ids:
        db.add(ModelHasRole(
            role_id=r_id,
            model_id=user.id,
            model_type="App\\Models\\User"
        ))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# def sync_permissions(db, user, permissions):
#     db.query(ModelHasPermission).filter(
#         ModelHasPermission.model_id == user.id,
#         ModelHasPermission.model_type == "App\\Models\\User"
#     ).delete()

#     for perm in permissions:
#         db.add(ModelHasPermission(
#             permission_id=perm.id,
#             model_id=user.id,
#             model_type="App\\Models\\User"
#         ))

#     db.commit()

def sync_permissions(db, user, permissions): 
    db.query(ModelHasPermission).filter(
        ModelHasPermission.model_id == user.id,
        ModelHasPermission.model_type == "App\\Models\\User"
    ).delete()
 
    unique_perm_ids = {perm.id for perm in permissions if perm is not None}
 
    for p_id in unique_perm_ids:
        db.add(ModelHasPermission(
            permission_id=p_id,
            model_id=user.id,
            model_type="App\\Models\\User"
        ))

    # 4. Transaction sécurisée
    try:
        db.commit()
    except Exception as e:
        db.rollback() # Annule tout en cas d'erreur de doublon résiduelle
        print(f"Erreur sync_permissions: {e}")
        raise e

def give_permission(db, user, permission):
    exists = db.query(ModelHasPermission).filter(
        ModelHasPermission.permission_id == permission.id,
        ModelHasPermission.model_id == user.id,
        ModelHasPermission.model_type == "App\\Models\\User"
    ).first()

    if not exists:
        db.add(ModelHasPermission(
            permission_id=permission.id,
            model_id=user.id,
            model_type="App\\Models\\User"
        ))
        db.commit()

def give_all_permissions_to_role(db, role, permissions):
    db.query(RoleHasPermission).filter(
        RoleHasPermission.role_id == role.id
    ).delete()

    for perm in permissions:
        db.add(RoleHasPermission(
            role_id=role.id,
            permission_id=perm.id
        ))

    db.commit()

def user_has_permission(db, user, permission_name):
    # permission directe
    direct = db.query(ModelHasPermission).join(Permission).filter(
        ModelHasPermission.model_id == user.id,
        Permission.name == permission_name
    ).first()

    if direct:
        return True

    # permission via rôle
    return db.query(RoleHasPermission).join(Permission).join(ModelHasRole).filter(
        ModelHasRole.model_id == user.id,
        RoleHasPermission.permission_id == Permission.id,
        RoleHasPermission.role_id == ModelHasRole.role_id
    ).first() is not None

