import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.Config import settings, BASE_URL
from .template import build_email_template
logo_path = "app/static/logo/school_logo.png" #static/logo/school_logo.png

def send_reset_code_email(to_email: str, code: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Code de réinitialisation de mot de passe"
    msg["From"]    = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"]      = to_email

    body = f"""
<div style="text-align:center; background:#12151f; border:1px solid #2a2d3a; border-radius:12px; padding:28px 48px; margin-bottom:24px;">
  <p style="margin:0 0 8px; color:#4b5563; font-size:11px; text-transform:uppercase; letter-spacing:3px;">Code de vérification</p>
  <p style="margin:0; color:#4f8ef7; font-size:44px; font-weight:800; letter-spacing:12px;">{code}</p>
  <p style="margin:10px 0 0; color:#4b5563; font-size:12px;">Expire dans 15 minutes</p>
</div>
<div style="background:#1f1a0e; border-left:3px solid #ca8a04; border-radius:6px; padding:14px 18px;">
  <p style="margin:0; color:#92740a; font-size:13px; line-height:1.6;">
    ⚠️ Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
  </p>
</div>
""" 

    html = build_email_template(
    title="Réinitialisation de mot de passe",
    intro="Bonjour, nous avons reçu une demande de réinitialisation de votre mot de passe.",
    body_html=body
    )
    msg.attach(MIMEText(html, "html")) 
    try:
        host = "smtp.hostinger.com"
        user = "noreply@infini-software.cloud"
        password = "@Janvier1991"
        with smtplib.SMTP_SSL(host, 465, timeout=10) as server:
     #    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(user, password)
          #   server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to_email, msg.as_string())
        print("Email envoyé avec succès")
    except smtplib.SMTPAuthenticationError:
        raise Exception("Identifiants SMTP incorrects")
    except smtplib.SMTPConnectError:
        raise Exception(f"Impossible de se connecter à {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Erreur envoi email : {str(e)}")
    




