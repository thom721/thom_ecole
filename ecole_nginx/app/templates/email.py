email_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Notification de compte</title>
</head>
<body>
    <h2>Bonjour {{ prenom }},</h2>
    <p>Votre compte {{ type_compte }} a été créé avec succès pour {{ school_name }}.</p>
    <p><strong>Vos identifiants de connexion :</strong></p>
    <ul>
        <li>Email: {{ email }}</li>
        <li>Mot de passe: {{ password }}</li>
    </ul>
    <p>Vous pouvez vous connecter à l'adresse suivante: <a href="{{ url }}">{{ url }}</a></p>
    <p>Cordialement,<br>L'équipe de {{ school_name }}</p>
</body>
</html>
"""