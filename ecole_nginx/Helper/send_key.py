import smtplib
from email.message import EmailMessage

def send_email(activation_key, recipient_email):
    """Envoie la clé d'activation par email"""
    sender_email = "tonemail@gmail.com"
    sender_password = "ton_mdp_app"

    msg = EmailMessage()
    msg.set_content(f"Votre clé d'activation : {activation_key}")
    msg["Subject"] = "Clé d'activation de votre application"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email envoyé avec succès")
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email : {e}")

# Exemple d'envoi
send_email(activation_key, "client@example.com")
