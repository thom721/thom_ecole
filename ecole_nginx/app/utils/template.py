import base64
from sqlalchemy.orm import Session
from app.Models.MSystems import Profile
from app.database import get_db

def get_profile():
    """Récupère le profil depuis la base de données"""
    db = next(get_db())
    try:
        return db.query(Profile).first()
    finally:
        db.close()

def get_logo_base641(logo_data) -> str:
    """
    Accepte soit :
    - un chemin de fichier (str) ex: "app/static/logo.png"
    - des bytes directement depuis la DB
    - une string base64 déjà encodée
    """
    # Déjà en base64 string
    if isinstance(logo_data, str) and logo_data.startswith("data:image"):
        return logo_data

    # Bytes depuis la DB (champ LargeBinary/BLOB)
    if isinstance(logo_data, bytes):
        encoded = base64.b64encode(logo_data).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    # Chemin de fichier
    if isinstance(logo_data, str) and not logo_data.startswith("data:"):
        with open(logo_data, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext  = logo_data.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        return f"data:{mime};base64,{encoded}"

    return ""


def build_email_template(
    title: str,
    intro: str,
    body_html: str,
    footer_note: str = "Cet email a été envoyé automatiquement, merci de ne pas y répondre.",
    cta_text: str = None,
    cta_url: str = None,
) -> str:

    # Récupération dynamique du profil
    profile  = get_profile()
    app_name = profile.nom if profile else "Lekol 360"

    # Logo depuis la DB
    try:
        logo_src = get_logo_base64(profile.logo_image_base64) if profile and profile.logo_image_base64 else ""
    except Exception as e:
        print(f"⚠️ Logo non chargé : {e}")
        logo_src = ""

    logo_tag = f"""
    <img
      src="{logo_src}"
      alt="{app_name}"
      width="100"
      style="display:block; margin:0 auto 16px; border-radius:50%; object-fit:contain;"
    />
    """ if logo_src else ""

    cta_block = f"""
    <tr>
      <td align="center" style="padding: 8px 0 32px;">
        <a href="{cta_url}" style="
          display:inline-block;
          background:#4f8ef7;
          color:#ffffff;
          text-decoration:none;
          font-size:14px;
          font-weight:600;
          padding:14px 40px;
          border-radius:8px;
          letter-spacing:0.5px;
        ">{cta_text}</a>
      </td>
    </tr>
    """ if cta_text and cta_url else ""

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0; padding:0; background-color:#0f1117; font-family:'Segoe UI', Arial, sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117; padding:48px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="
          background:#1a1d27;
          border-radius:16px;
          overflow:hidden;
          border:1px solid #2a2d3a;
        ">

          <!-- Header -->
          <tr>
            <td style="padding:36px 48px 28px; text-align:center; border-bottom:1px solid #2a2d3a;">
              {logo_tag}
              <p style="margin:0; color:#6b7280; font-size:11px; font-weight:600; letter-spacing:3px; text-transform:uppercase;">
                {app_name}
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 48px 32px;">
              <h1 style="margin:0 0 14px; color:#f1f1f3; font-size:21px; font-weight:700; line-height:1.4;">
                {title}
              </h1>
              <p style="margin:0 0 32px; color:#9ca3af; font-size:14px; line-height:1.9;">
                {intro}
              </p>

              {body_html}

              <table width="100%" cellpadding="0" cellspacing="0">
                {cta_block}
              </table>

              <p style="margin:32px 0 0; color:#4b5563; font-size:13px; line-height:1.7; border-top:1px solid #2a2d3a; padding-top:24px;">
                Cordialement,<br>
                <strong style="color:#6b7280;">L'équipe {app_name}</strong>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#13151f; padding:20px 48px; text-align:center; border-top:1px solid #2a2d3a;">
              <p style="margin:0 0 4px; color:#374151; font-size:11px;">
                © 2025 {app_name} — Tous droits réservés
              </p>
              <p style="margin:0; color:#374151; font-size:11px;">
                {footer_note}
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
"""




# import base64
# import os

# def get_logo_base64(logo_path: str) -> str:
#     """Convertit le logo en base64 pour l'intégrer directement dans l'email"""
#     with open(logo_path, "rb") as f:
#         encoded = base64.b64encode(f.read()).decode("utf-8")
#     ext = logo_path.split(".")[-1].lower()
#     mime = "image/png" if ext == "png" else "image/jpeg"
#     return f"data:{mime};base64,{encoded}"


import base64
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.Models.MSystems import Profile
from app.database import get_db
from app.config.Config import settings


# ─────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────

def get_profile1():
    db = next(get_db())
    try:
        return db.query(Profile).first()
    finally:
        db.close()


def get_logo_base64(logo_data) -> str:
    if isinstance(logo_data, str) and logo_data.startswith("data:image"):
        return logo_data
    if isinstance(logo_data, bytes):
        encoded = base64.b64encode(logo_data).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    if isinstance(logo_data, str) and not logo_data.startswith("data:"):
        with open(logo_data, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext  = logo_data.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        return f"data:{mime};base64,{encoded}"
    return ""


def generate_temp_password() -> str:
    """Génère un mot de passe lisible ex: Etoile@392"""
    words  = ["Soleil", "Lekol", "Ecole", "Avenir", "Etoile",
              "Futur", "Espoir", "Savoir", "Lumiere", "Force"]
    word    = secrets.choice(words)
    numbers = ''.join(secrets.choice(string.digits) for _ in range(3))
    symbol  = secrets.choice("#@!$%")
    return f"{word}{symbol}{numbers}"


def send_email(to_email: str, subject: str, html: str):
    """Fonction d'envoi générique"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email envoyé à {to_email}")
    except Exception as e:
        raise Exception(f"Erreur envoi email : {e}")


# ─────────────────────────────────────────
# TEMPLATE DE BASE
# ─────────────────────────────────────────

def build_email_template1(
    title: str,
    intro: str,
    body_html: str,
    footer_note: str = "Cet email a été envoyé automatiquement, merci de ne pas y répondre.",
    cta_text: str = None,
    cta_url: str = None,
) -> str:

    profile  = get_profile()
    app_name = profile.nom if profile else "Lekol 360"

    try:
        logo_src = get_logo_base64(profile.logo_image_base64) if profile and profile.logo_image_base64 else ""
    except Exception as e:
        print(f"⚠️ Logo non chargé : {e}")
        logo_src = ""

    logo_tag = f"""
    <img src="{logo_src}" alt="{app_name}" width="100"
      style="display:block; margin:0 auto 16px; border-radius:50%; object-fit:contain;"/>
    """ if logo_src else ""

    cta_block = f"""
    <tr>
      <td align="center" style="padding:8px 0 32px;">
        <a href="{cta_url}" style="
          display:inline-block; background:#4f8ef7; color:#ffffff;
          text-decoration:none; font-size:14px; font-weight:600;
          padding:14px 40px; border-radius:8px; letter-spacing:0.5px;
        ">{cta_text}</a>
      </td>
    </tr>
    """ if cta_text and cta_url else ""

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0; padding:0; background-color:#0f1117; font-family:'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f1117; padding:48px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="
          background:#1a1d27; border-radius:16px;
          overflow:hidden; border:1px solid #2a2d3a;">

          <!-- Header -->
          <tr>
            <td style="padding:36px 48px 28px; text-align:center; border-bottom:1px solid #2a2d3a;">
              {logo_tag}
              <p style="margin:0; color:#6b7280; font-size:11px; font-weight:600; letter-spacing:3px; text-transform:uppercase;">
                {app_name}
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 48px 32px;">
              <h1 style="margin:0 0 14px; color:#f1f1f3; font-size:21px; font-weight:700; line-height:1.4;">
                {title}
              </h1>
              <p style="margin:0 0 32px; color:#9ca3af; font-size:14px; line-height:1.9;">
                {intro}
              </p>
              {body_html}
              <table width="100%" cellpadding="0" cellspacing="0">{cta_block}</table>
              <p style="margin:32px 0 0; color:#4b5563; font-size:13px; line-height:1.7; border-top:1px solid #2a2d3a; padding-top:24px;">
                Cordialement,<br>
                <strong style="color:#6b7280;">L'équipe {app_name}</strong>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#13151f; padding:20px 48px; text-align:center; border-top:1px solid #2a2d3a;">
              <p style="margin:0 0 4px; color:#374151; font-size:11px;">© 2025 {app_name} — Tous droits réservés</p>
              <p style="margin:0; color:#374151; font-size:11px;">{footer_note}</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# ─────────────────────────────────────────
# EMAILS SPÉCIFIQUES
# ─────────────────────────────────────────

def send_reset_code_email1(to_email: str, code: str):
    body = f"""
    <div style="text-align:center; background:#12151f; border:1px solid #2a2d3a; border-radius:12px; padding:28px 48px; margin-bottom:24px;">
      <p style="margin:0 0 8px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:3px;">
        Code de vérification
      </p>
      <p style="margin:0; color:#4f8ef7; font-size:44px; font-weight:800; letter-spacing:12px;">
        {code}
      </p>
      <p style="margin:10px 0 0; color:#4b5563; font-size:12px;">Expire dans 15 minutes</p>
    </div>
    <div style="background:#1a1400; border-left:3px solid #ca8a04; border-radius:8px; padding:16px 20px;">
      <p style="margin:0; color:#92740a; font-size:13px; line-height:1.6;">
        ⚠️ Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
      </p>
    </div>
    """
    html = build_email_template(
        title     = "Réinitialisation de mot de passe",
        intro     = "Bonjour, nous avons reçu une demande de réinitialisation de votre mot de passe. Utilisez le code ci-dessous.",
        body_html = body,
    )
    send_email(to_email, "🔐 Code de réinitialisation", html)


def send_activation_email1(to_email: str, prenom: str, nom: str, password: str, login_url: str = "https://lekol360.com/login"):
    body = f"""
    <!-- Bannière activation -->
    <div style="background:#0d1f17; border-left:3px solid #16a34a; border-radius:8px; padding:16px 20px; margin-bottom:28px;">
      <p style="margin:0; color:#16a34a; font-size:14px; font-weight:600;">
        🎉 Votre compte a été activé par l'administration
      </p>
    </div>

    <!-- Identifiants -->
    <p style="margin:0 0 14px; color:#9ca3af; font-size:12px; text-transform:uppercase; letter-spacing:2px; font-weight:600;">
      Vos identifiants de connexion
    </p>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <tr>
        <td style="padding:0 0 10px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#12151f; border:1px solid #2a2d3a; border-radius:10px;">
            <tr>
              <td style="padding:16px 20px;">
                <p style="margin:0 0 4px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:1px;">📧 Adresse email</p>
                <p style="margin:0; color:#f1f1f3; font-size:16px; font-weight:600;">{to_email}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#12151f; border:1px solid #2a2d3a; border-radius:10px;">
            <tr>
              <td style="padding:16px 20px;">
                <p style="margin:0 0 4px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:1px;">🔑 Mot de passe temporaire</p>
                <p style="margin:0; color:#4f8ef7; font-size:22px; font-weight:800; letter-spacing:4px;">{password}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <!-- Avertissement première connexion -->
    <div style="background:#1a1400; border-left:3px solid #ca8a04; border-radius:8px; padding:16px 20px; margin-bottom:24px;">
      <p style="margin:0 0 4px; color:#ca8a04; font-size:13px; font-weight:600;">⚠️ Première connexion</p>
      <p style="margin:0; color:#92740a; font-size:13px; line-height:1.7;">
        Lors de votre première connexion, vous serez automatiquement invité à changer votre mot de passe.
        Choisissez un mot de passe fort que vous n'utilisez nulle part ailleurs.
      </p>
    </div>

    <!-- Conseils sécurité -->
    <div style="background:#12151f; border:1px solid #2a2d3a; border-radius:8px; padding:16px 20px;">
      <p style="margin:0 0 10px; color:#4b5563; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">🔒 Conseils de sécurité</p>
      <p style="margin:0 0 4px; color:#6b7280; font-size:13px;">• Ne partagez jamais vos identifiants</p>
      <p style="margin:0 0 4px; color:#6b7280; font-size:13px;">• L'administration ne vous demandera jamais votre mot de passe</p>
      <p style="margin:0; color:#6b7280; font-size:13px;">• Déconnectez-vous après chaque session sur un appareil partagé</p>
    </div>
    """

    html = build_email_template(
        title     = f"Bienvenue, {prenom} {nom} !",
        intro     = f"Bonjour {prenom}, votre compte étudiant a été activé par l'administration. Voici vos informations de première connexion.",
        body_html = body,
        cta_text  = "Se connecter maintenant",
        cta_url   = login_url,
    )
    send_email(to_email, "🎓 Activation de votre compte", html)