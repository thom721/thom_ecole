import smtplib
from email.message import EmailMessage

from app.config.Config import settings


def send_password_reset_email(to_email: str, first_name: str, reset_link: str) -> None:
    message = EmailMessage()
    message["Subject"] = "Réinitialisation de votre mot de passe — IUSTH e-learning"
    message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    message["To"] = to_email
    message.set_content(
        f"Bonjour {first_name},\n\n"
        "Une réinitialisation de mot de passe a été demandée pour votre compte IUSTH e-learning.\n"
        f"Cliquez sur le lien suivant pour choisir un nouveau mot de passe (valable 1 heure) :\n{reset_link}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email."
    )
    message.add_alternative(
        f"""\
<html><body style="font-family: sans-serif; color: #111827;">
<p>Bonjour {first_name},</p>
<p>Une réinitialisation de mot de passe a été demandée pour votre compte <strong>IUSTH e-learning</strong>.</p>
<p><a href="{reset_link}" style="background:#111827;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Choisir un nouveau mot de passe</a></p>
<p style="color:#6b7280;font-size:13px;">Ce lien est valable 1 heure. Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.</p>
</body></html>""",
        subtype="html",
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)


def send_staff_meeting_email(to_email: str, first_name: str, meeting_title: str, scheduled_start, link_url: str) -> None:
    message = EmailMessage()
    message["Subject"] = f"Réunion du personnel — {meeting_title}"
    message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    message["To"] = to_email
    when = scheduled_start.strftime("%d/%m/%Y à %H:%M") if scheduled_start else "à une date à confirmer"
    message.set_content(
        f"Bonjour {first_name},\n\n"
        f"Vous êtes invité(e) à la réunion du personnel « {meeting_title} », {when}.\n"
        f"Rejoindre : {link_url}\n"
    )
    message.add_alternative(
        f"""\
<html><body style="font-family: sans-serif; color: #111827;">
<p>Bonjour {first_name},</p>
<p>Vous êtes invité(e) à la réunion du personnel <strong>{meeting_title}</strong>, {when}.</p>
<p><a href="{link_url}" style="background:#111827;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Rejoindre la réunion</a></p>
</body></html>""",
        subtype="html",
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)


def send_live_session_email(to_email: str, first_name: str, course_name: str, session_title: str,
                             scheduled_start, link_url: str) -> None:
    message = EmailMessage()
    message["Subject"] = f"Nouvelle session en direct — {course_name}"
    message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    message["To"] = to_email
    when = scheduled_start.strftime("%d/%m/%Y à %H:%M") if scheduled_start else "à une date à confirmer"
    message.set_content(
        f"Bonjour {first_name},\n\n"
        f"Une nouvelle session en direct « {session_title} » a été programmée dans le cours « {course_name} », {when}.\n"
        f"Rejoindre : {link_url}\n"
    )
    message.add_alternative(
        f"""\
<html><body style="font-family: sans-serif; color: #111827;">
<p>Bonjour {first_name},</p>
<p>Une nouvelle session en direct <strong>{session_title}</strong> a été programmée dans le cours <strong>{course_name}</strong>, {when}.</p>
<p><a href="{link_url}" style="background:#111827;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Voir la session</a></p>
</body></html>""",
        subtype="html",
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(message)
