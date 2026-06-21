from fastapi import APIRouter, HTTPException, Depends
import logging
from datetime import datetime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from typing import Optional, List, Dict, Any
import json

def _naissance(date_de_naissance) -> str:
    if date_de_naissance:
        if isinstance(date_de_naissance, str):
            dt = datetime.fromisoformat(date_de_naissance)
        else:
            dt = date_de_naissance
        return dt.strftime("%d %b %Y")
    return ""
def calculer_moyenne_generale(
    data_etudiant: Any, 
    identifiant: str, 
    mois: str
) -> tuple[float, List[float], List[float]]: 
    # Parser les données 
    if isinstance(data_etudiant, str):
        parse_data = json.loads(data_etudiant)
    else:
        parse_data = data_etudiant
    
    if identifiant not in parse_data:
        return (0.0, [], [])
    
    data = parse_data[identifiant]
    notes = []
    coefficient = []
    print(f"details,mois {mois}")
    def traiter_section(section: Dict) -> None:
        """Traite une section (base ou orale)"""
        for matiere, details in section.items():
            coef = float(details['coefficients'])
          #   print(details['notes'],mois)
            if mois == 'all':
                for key,note_mois in details['notes'].items(): 
                    print(f"key  {key} note_mois note_mois {note_mois}")
                    notes.append(note_mois)
                    coefficient.append(coef)
            elif mois in details['notes']:
                notes.append(details['notes'][mois])
                coefficient.append(coef)
    
    # Traiter les sections base et orale
    if 'base' in data:
        traiter_section(data['base'])
    if 'orale' in data:
        traiter_section(data['orale'])
     
    notes = [to_float(n) for n in notes]
    coefficient = [to_float(c) for c in coefficient] 
    total_coef = sum(coefficient)

     # moyenne = (sum(notes) / total_coef) * 10 if total_coef > 0 else 0
    print('notes')
    print(notes)

    print('coefficient')
    print(coefficient)
    # Calculer la moyenne
    if len(coefficient) > 0 and sum(coefficient) > 0:
        moyenne = (sum(notes) / sum(coefficient)) * 10
    else:
        moyenne = 1.0
    
    return (round(moyenne, 2), notes, coefficient)


def moyenne_and_place(
    classes_id: int, 
    mois: str, 
    student_list: List[Any],full_info=False
) -> Dict[str, Any]:
    """
    Calcule les moyennes et le classement des étudiants
    
    Args:
        classes_id: ID de la classe
        mois: Mois concerné
        student_list: Liste des étudiants
    
    Returns:
        Dictionnaire avec les résultats et la moyenne de classe
    """
    print(f"mois: str   {mois}")
    try:
        data_promus = []
        moyennes_classe = []
        for value in student_list: 
            if value.data_etudiant != '"[]"':
                
                results = calculer_moyenne_generale(
                    value.data_etudiant, 
                    value.identifiant, 
                    mois
                )
                
                moyenne = results[0]
                moyennes_classe.append(moyenne)
                
                data_promus.append({
                    'etudiant_id': value.etudiant_id,
                    'identifiant': value.identifiant,
                    'nom': value.fname,
                    'prenom': value.lname,
                    
                    'moyenne': moyenne
                })
            else:
                logger.info(f"Étudiant sans notes: {value.fname} {value.lname}")
        
        # Calculer la moyenne de classe
        if len(moyennes_classe) > 0:
            moyenne_classe = sum(moyennes_classe) / len(moyennes_classe)
        else:
            moyenne_classe = 0.0
        
        # Trier par moyenne décroissante
        data_promus.sort(key=lambda x: x['moyenne'], reverse=True)
        
        # Attribuer les rangs
        rang = 0
        derniere_moyenne = None
        
        for student in data_promus:
            if derniere_moyenne is None or student['moyenne'] != derniere_moyenne:
                rang += 1
                derniere_moyenne = student['moyenne']
            
            student['rang'] = rang
        
        return {
            'result': data_promus,
            'moyenne_classe': round(moyenne_classe, 2)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Erreur dans moyenne_and_place: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))


def to_float(value, default=0.0):
    try:
        if value in ("", None, "[]"):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default