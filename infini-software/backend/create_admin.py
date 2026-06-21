"""Crée le premier (ou un nouveau) compte administrateur pour la partie
/api/admin/*. Équivalent, côté infini-software, de
ecole_nginx/scripts/create-first-admin.sh.

Usage : python create_admin.py
"""
import getpass

from dotenv import load_dotenv

load_dotenv()

from app.database import Base, SessionLocal, engine
from app.models import AdminUser
from app.security import hash_password

Base.metadata.create_all(bind=engine)


def main():
    email = input("Email administrateur : ").strip()
    password = getpass.getpass("Mot de passe : ")

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            existing.password_hash = hash_password(password)
            db.commit()
            print(f"✅ Mot de passe mis à jour pour {email}.")
            return

        admin = AdminUser(email=email, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        print(f"✅ Administrateur {email} créé.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
