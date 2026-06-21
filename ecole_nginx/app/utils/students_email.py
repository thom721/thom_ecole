import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.Config import settings, BASE_URL
from .template import build_email_template
from app.config.Config import logo_url,url
   

# ── Config SMTP ────────────────────────────────────────────────
SMTP_HOST     = "smtp.hostinger.com"
SMTP_PORT     = 465
SMTP_USER     = "noreply@infini-software.cloud"
SMTP_PASSWORD = "@Janvier1991"
MAIL_FROM     = "noreply@infini-software.cloud"
MAIL_FROM_NAME = "Lekol 360"

# ── Mapping type → libellés ────────────────────────────────────
ROLE_CONFIG = {
    "etudiant": {
        "label":       "étudiant",
        "subject":     "🎓 Bienvenue sur Lekol 360 — Vos accès étudiant",
        "platform":    "plateforme étudiante",
        "banner_icon": "🎓",
        "banner_text": "Votre compte étudiant a été activé par l'administration",
        "banner_bg":   "#0d1f17",
        "banner_color":"#16a34a",
        "login_url":   f"{url}/login",
    },
    "personnel": {
        "label":       "personnel",
        "subject":     "👔 Bienvenue sur Lekol 360 — Vos accès personnel",
        "platform":    "plateforme de gestion",
        "banner_icon": "👔",
        "banner_text": "Votre compte personnel a été activé par l'administration",
        "banner_bg":   "#0d1525",
        "banner_color":"#3b82f6",
        "login_url":   f"{url}/login",
    },
    "professeur": {
        "label":       "professeur",
        "subject":     "📚 Bienvenue sur Lekol 360 — Vos accès professeur",
        "platform":    "plateforme enseignante",
        "banner_icon": "📚",
        "banner_text": "Votre compte professeur a été activé par l'administration",
        "banner_bg":   "#1a0d25",
        "banner_color":"#a855f7",
        "login_url":   f"{url}/login",
    },
}


def build_email_template(title, intro, body_html, cta_text, cta_url):
    """Template HTML d'email universel."""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/></head>
<body style="margin:0;padding:0;background:#0a0d14;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0d14;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#0f1724,#0d1f2a);border-radius:16px 16px 0 0;padding:36px 40px;text-align:center;border:1px solid #1e2a38;border-bottom:none;">
          <p style="margin:0 0 8px;color:#06b6d4;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:3px;">Lekol 360</p>
          <h1 style="margin:0;color:#f1f5f9;font-size:26px;font-weight:800;line-height:1.3;">{title}</h1>
        </td></tr>

        <!-- Body -->
        <tr><td style="background:#0f1724;padding:36px 40px;border:1px solid #1e2a38;border-top:none;border-bottom:none;">
          <p style="margin:0 0 28px;color:#94a3b8;font-size:15px;line-height:1.7;">{intro}</p>
          {body_html}
        </td></tr>

        <!-- CTA -->
        <tr><td style="background:#0f1724;padding:0 40px 36px;border:1px solid #1e2a38;border-top:none;border-bottom:none;text-align:center;">
          <a href="{cta_url}" style="display:inline-block;background:#06b6d4;color:#080c10;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:99px;letter-spacing:.5px;">
            {cta_text}
          </a>
        </td></tr>

        <!-- Footer -->
        <tr><td style="background:#0a0d14;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border:1px solid #1e2a38;border-top:1px solid #1e2a38;">
          <p style="margin:0 0 4px;color:#374151;font-size:12px;">© 2026 Lekol 360 — Infini Software</p>
          <p style="margin:0;color:#374151;font-size:11px;">Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_activation_email(
    to_email:  str,
    prenom:    str,
    nom:       str,
    email:     str,
    password:  str,
    platform:  str="Institution le mignon",
    role:      str = "etudiant",   # "etudiant" | "personnel" | "professeur"
    login_url: str = None,
):
    """
    Envoie un email d'activation dynamique selon le rôle de l'utilisateur.

    Args:
        to_email  : adresse email du destinataire
        prenom    : prénom
        nom       : nom de famille
        email     : email de connexion (peut différer de to_email)
        password  : mot de passe temporaire
        role      : "etudiant", "personnel" ou "professeur"
        login_url : URL de connexion (surcharge la valeur par défaut du rôle)
    """
    cfg = ROLE_CONFIG.get(role, ROLE_CONFIG["etudiant"])

    # Surcharge de l'URL si fournie
    url = login_url or cfg["login_url"]

    body = f"""
    <!-- Bannière rôle -->
    <div style="background:{cfg['banner_bg']};border-left:3px solid {cfg['banner_color']};border-radius:8px;padding:16px 20px;margin-bottom:28px;">
      <p style="margin:0;color:{cfg['banner_color']};font-size:14px;font-weight:600;">
        {cfg['banner_icon']} {cfg['banner_text']}
      </p>
    </div>

    <!-- Badge rôle -->
    <p style="margin:0 0 16px;color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:2px;font-weight:600;">
      Vos identifiants de connexion
    </p>

    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
      <!-- Email -->
      <tr><td style="padding:0 0 10px;">
        <table width="100%" cellpadding="0" cellspacing="0"
          style="background:#12151f;border:1px solid #2a2d3a;border-radius:10px;padding:16px 20px;">
          <tr><td>
            <p style="margin:0 0 4px;color:#4b5563;font-size:11px;text-transform:uppercase;letter-spacing:1px;">📧 Adresse email</p>
            <p style="margin:0;color:#f1f1f3;font-size:16px;font-weight:600;">{email}</p>
          </td></tr>
        </table>
      </td></tr>

      <!-- Mot de passe -->
      <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0"
          style="background:#12151f;border:1px solid #2a2d3a;border-radius:10px;padding:16px 20px;">
          <tr><td>
            <p style="margin:0 0 4px;color:#4b5563;font-size:11px;text-transform:uppercase;letter-spacing:1px;">🔑 Mot de passe temporaire</p>
            <p style="margin:0;color:#4f8ef7;font-size:20px;font-weight:800;letter-spacing:4px;">{password}</p>
          </td></tr>
        </table>
      </td></tr>
    </table>

    <!-- Avertissement -->
    <div style="background:#1a1400;border-left:3px solid #ca8a04;border-radius:8px;padding:16px 20px;margin-bottom:28px;">
      <p style="margin:0 0 4px;color:#ca8a04;font-size:13px;font-weight:600;">⚠️ Première connexion</p>
      <p style="margin:0;color:#92740a;font-size:13px;line-height:1.7;">
        Lors de votre première connexion, vous serez automatiquement invité à changer votre mot de passe.
        Choisissez un mot de passe fort que vous n'utilisez pas ailleurs.
      </p>
    </div>

    <!-- Sécurité -->
    <div style="background:#12151f;border:1px solid #2a2d3a;border-radius:8px;padding:16px 20px;">
      <p style="margin:0 0 8px;color:#4b5563;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">🔒 Conseils de sécurité</p>
      <p style="margin:0 0 4px;color:#6b7280;font-size:13px;">• Ne partagez jamais vos identifiants avec quelqu'un d'autre</p>
      <p style="margin:0 0 4px;color:#6b7280;font-size:13px;">• L'administration ne vous demandera jamais votre mot de passe</p>
      <p style="margin:0;color:#6b7280;font-size:13px;">• Déconnectez-vous après chaque session sur un appareil partagé</p>
    </div>
    """

    html = build_email_template(
        title    = f"Bienvenue, {prenom} {nom} !",
        intro    = f"Bonjour {prenom}, votre compte {cfg['label']} sur la {platform} a été activé par l'administration. Voici vos informations de connexion.",
        body_html= body,
        cta_text = "Se connecter maintenant",
        cta_url  = url,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = cfg["subject"]
    msg["From"]    = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
            print(f"[OK] Email d'activation envoyé à {to_email} (rôle: {role})")
    except Exception as e:
        raise Exception(f"Erreur envoi email : {e}")


# ── Exemples d'utilisation ─────────────────────────────────────
#
# Étudiant
# send_activation_email("eleve@gmail.com", "Jean", "Pierre", "eleve@gmail.com", "Tmp@1234", role="etudiant")
#
# Personnel
# send_activation_email("staff@ecole.com", "Marie", "Dupont", "staff@ecole.com", "Tmp@5678", role="personnel")
#
# Professeur
# send_activation_email("prof@ecole.com", "Paul", "Martin", "prof@ecole.com", "Tmp@9012", role="professeur")
#
# Avec URL personnalisée
# send_activation_email("prof@ecole.com", "Paul", "Martin", "prof@ecole.com", "Tmp@9012", role="professeur", login_url="https://monapp.com/login")

# def send_activation_email(
#     to_email: str,
#     prenom: str,
#     nom: str,
#     email: str,
#     password: str,
#     login_url: str = "https://lekol360.com/login"
# ):
#     body = f"""
#     <!-- Bannière de bienvenue -->
#     <div style="background:#0d1f17; border-left:3px solid #16a34a; border-radius:8px; padding:16px 20px; margin-bottom:28px;">
#       <p style="margin:0; color:#16a34a; font-size:14px; font-weight:600;">
#         🎉 Votre compte a été activé par l'administration
#       </p>
#     </div>

#     <!-- Infos de connexion -->
#     <p style="margin:0 0 16px; color:#9ca3af; font-size:13px; text-transform:uppercase; letter-spacing:2px; font-weight:600;">
#       Vos identifiants de connexion
#     </p>

#     <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">

#       <!-- Email -->
#       <tr>
#         <td style="padding:0 0 10px;">
#           <table width="100%" cellpadding="0" cellspacing="0" style="
#             background:#12151f;
#             border:1px solid #2a2d3a;
#             border-radius:10px;
#             padding:16px 20px;
#           ">
#             <tr>
#               <td>
#                 <p style="margin:0 0 4px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:1px;">
#                   📧 Adresse email
#                 </p>
#                 <p style="margin:0; color:#f1f1f3; font-size:16px; font-weight:600;">
#                   {email}
#                 </p>
#               </td>
#             </tr>
#           </table>
#         </td>
#       </tr>

#       <!-- Mot de passe -->
#       <tr>
#         <td>
#           <table width="100%" cellpadding="0" cellspacing="0" style="
#             background:#12151f;
#             border:1px solid #2a2d3a;
#             border-radius:10px;
#             padding:16px 20px;
#           ">
#             <tr>
#               <td>
#                 <p style="margin:0 0 4px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:1px;">
#                   🔑 Mot de passe temporaire
#                 </p>
#                 <p style="margin:0; color:#4f8ef7; font-size:20px; font-weight:800; letter-spacing:4px;">
#                   {password}
#                 </p>
#               </td>
#             </tr>
#           </table>
#         </td>
#       </tr>

#     </table>

#     <!-- Avertissement changement mot de passe -->
#     <div style="background:#1a1400; border-left:3px solid #ca8a04; border-radius:8px; padding:16px 20px; margin-bottom:28px;">
#       <p style="margin:0 0 4px; color:#ca8a04; font-size:13px; font-weight:600;">
#         ⚠️ Première connexion
#       </p>
#       <p style="margin:0; color:#92740a; font-size:13px; line-height:1.7;">
#         Lors de votre première connexion, vous serez automatiquement invité à changer votre mot de passe.
#         Choisissez un mot de passe fort que vous n'utilisez pas ailleurs.
#       </p>
#     </div>

#     <!-- Sécurité -->
#     <div style="background:#12151f; border:1px solid #2a2d3a; border-radius:8px; padding:16px 20px;">
#       <p style="margin:0 0 8px; color:#4b5563; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">
#         🔒 Conseils de sécurité
#       </p>
#       <p style="margin:0 0 4px; color:#6b7280; font-size:13px;">• Ne partagez jamais vos identifiants avec quelqu'un d'autre</p>
#       <p style="margin:0 0 4px; color:#6b7280; font-size:13px;">• L'administration ne vous demandera jamais votre mot de passe</p>
#       <p style="margin:0; color:#6b7280; font-size:13px;">• Déconnectez-vous après chaque session sur un appareil partagé</p>
#     </div>
#     """

#     html = build_email_template(
#         title=f"Bienvenue, {prenom} {nom} !",
#         intro=f"Bonjour {prenom}, votre compte étudiant sur la plateforme a été activé par l'administration. Voici vos informations de connexion.",
#         body_html=body,
#         cta_text="Se connecter maintenant",
#         cta_url=login_url,
#     )

#     # Envoi
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = f"🎓 Bienvenue sur Lekol 360 — Vos accès"
#     msg["From"]    = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
#     msg["To"]      = to_email
#     msg.attach(MIMEText(html, "html"))


#     try:
#         SMTP_HOST = "smtp.hostinger.com"
#         SMTP_PORT = 465
#         SMTP_USER = "noreply@infini-software.cloud"
#         SMTP_PASSWORD = "@Janvier1991"
#         MAIL_FROM="noreply@infini-software.cloud"

#      #    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
#      #    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
#         with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
#              server.login(SMTP_USER, SMTP_PASSWORD)
#              server.sendmail(MAIL_FROM, to_email, msg.as_string())
#           #    server.ehlo()
#           #    server.starttls()
#           #    server.ehlo()
#           #    server.login(SMTP_USER, SMTP_PASSWORD)
#           #    server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
#           #    server.quit()
#              print("✅ Email d'activation envoyé")
#     except Exception as e:
#         raise Exception(f"Erreur envoi email : {e}")