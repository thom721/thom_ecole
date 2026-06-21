def appliquer_erreurs(erreurs, *champs):
    """
    Applique un style d'erreur aux champs ayant une erreur et enlève l'erreur pour les autres.
    
    :param erreurs: Dictionnaire des erreurs retourné par la réponse.
    :param champs: Liste de tuples (nom_du_champ, champ_ui).
    """
    for nom_champ, champ_ui in champs:
        if nom_champ in erreurs and erreurs[nom_champ]:  
            champ_ui.setStyleSheet("border: 1px solid red;")
        else:
            champ_ui.setStyleSheet("border: 1px solid #ccc;") 