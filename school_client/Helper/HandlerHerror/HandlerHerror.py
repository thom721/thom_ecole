 
from PySide6.QtWidgets import QMessageBox,QWidget, QLineEdit, QComboBox, QDateEdit, QTextEdit # Ajoute les autres si nécessaire
class HandlerHerror(QWidget):
     def __init__(self, parent=None):
        super().__init__(parent)

     def highlight_errors(self, error_fields,mapping={}):
        for field_name, widget in mapping.items():
             if isinstance(widget, list):
                  for item in widget:
                       if isinstance(item, dict):
                            self.highlight_errors(error_fields, item)
                  continue
             if isinstance(widget, dict):
                  for sub_key, sub_widget in widget.items():
                       # On allume si la clé spécifique (ex: Versement_1...) est en erreur
                       # OU si le parent (montant_par) est marqué en erreur
                       print(f"\n\nsub_key {sub_key}, field_name  {field_name}\n\n\n\n  sub_widget {sub_widget}\n\n\n")
                       if sub_key in error_fields or field_name in error_fields:
                            self._apply_style(sub_widget, True)
                       else:
                            self._apply_style(sub_widget, False)
                  continue
             is_error = field_name in error_fields
             self._apply_style(widget, is_error)

          #    if field in error_locs:
          #         print(field) 
          #         widget.setStyleSheet("""border: 1px solid #e74c3c; background-color: #fdeaea;  """)
    
          #    else:
          #         widget.setStyleSheet("border: 1px solid #40caf1;")

     def show_erros(self,error_msg,response_data,mapping_field, overlay):
        """
        Extrait proprement les messages d'erreurs de validation (FastAPI / Laravel-like)
        Retourne une string prête à afficher.
        """
        messages = []
        overlay.finish_loading()
        if not response_data:
             return "Une erreur inconnue est survenue."

        if isinstance(response_data, dict) and "errors" in response_data:
             errors = response_data["errors"]
             error_fields = []
             
             if isinstance(errors, list):
                 for err in errors:
                      msg = err.get("msg", "Erreur inconnue")
                      # loc est une liste, ex: ['body', 'prix']. On prend le dernier élément.
                      field_name = err.get('loc', ['champ'])[-1]
                      error_fields.append(field_name)
                    
                      # Nettoyage Pydantic V2
                      # On retire "Input " au début pour un rendu plus pro
                      if msg.startswith("Input "):
                         msg = msg.replace("Input ", "", 1)
                    
                      # On retire le préfixe "Value error, " si présent (souvent ajouté par les   validateurs custom)
                      msg = msg.replace("Value error,", "").strip()
                    
                      # Construction du message final : "nom_du_champ : message"
                      clean_message = f"<b>{field_name}</b>: {msg}" 
                      messages.append(clean_message)
                 self.highlight_errors(error_fields,mapping_field)
                    
             elif isinstance(errors, dict):
                 for field, errs in errors.items():
                      if isinstance(errs, list) and errs:
                         messages.append(f"{field.capitalize()} : {errs[0]}")
                      else:
                         messages.append(f"{field.capitalize()} : {errs}")

          # 🔹 Message global
        elif isinstance(response_data, dict) and "message" in response_data:
               
             messages.append(response_data["message"])

        elif isinstance(response_data, dict) and "detail" in response_data:
               
             detail = response_data.get("detail")
               
             if isinstance(detail, dict) and "errors" in detail:
                  d=detail.get("errors","") 
                  if isinstance(d, dict) and "warning" in detail.get("errors",""):
                       m=detail.get("errors",{}).get("warning","")  
                       messages.append(m)
                  else:   
                       if "errors" in detail: 
                           x=detail.get("errors","") 
                           print(x)                                   
                           messages.append(x)
             else:
                  messages.append(str(detail))
          # 🔹 Fallback
        else: 
            messages.append(str(response_data))
        full_message = "\n".join(f"• {m}" for m in messages if m)
        if 'SQLSTATE' not in full_message:
            QMessageBox.critical(
               self,
               f"Échec",
               full_message
               )





     def _apply_style(self, widget, is_error):
        """Méthode utilitaire pour éviter la répétition"""
        if hasattr(widget, "setStyleSheet") and not isinstance(widget, dict):
             if is_error:
                  widget.setStyleSheet("border: 1px solid #e74c3c; background-color: #fdeaea;")
             else:
                  widget.setStyleSheet("border: 1px solid #40caf1;")

     
def highlight_errors(self, error_fields, mapping_field, messages):
    """
    messages: la liste des messages d'erreur (ex: ['Le montant pour Versement_1...'])
    """
    # On crée une grosse chaîne avec tous les messages pour chercher dedans
    full_error_text = " ".join(messages).lower()
    
    # On met aussi les noms de champs en minuscule pour comparer sans erreur
    error_fields_low = [f.lower() for f in error_fields]

    for field_name, value in mapping_field.items():
        
        # CAS : Ta liste de dictionnaires [{ 'Versement_1_UUID': QLineEdit }]
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for sub_key, sub_widget in item.items():
                        key_low = sub_key.lower()
                        
                        is_error = (key_low in error_fields_low or 
                                    field_name.lower() in error_fields_low or 
                                    key_low in full_error_text)
                        
                        self._apply_style(sub_widget, is_error)
            continue

        # CAS : Widget standard
        is_error = field_name.lower() in error_fields_low or field_name.lower() in full_error_text
        self._apply_style(value, is_error)

def _apply_style(self, widget, is_error):
    if hasattr(widget, "setStyleSheet"):
        if is_error:
            widget.setStyleSheet("border: 2px solid #e74c3c; background-color: #fdeaea;")
        else:
            widget.setStyleSheet("")