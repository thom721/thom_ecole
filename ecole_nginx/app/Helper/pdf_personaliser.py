import os
import platform
import sys
import subprocess
import tempfile
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
import io
from app.Helper.APP_ROOT import get_app_root
# from datetime import datetime
from datetime import date, datetime
import base64 
# mkdir -p /tmp/weasyprint_lemignon
# chown www-data:www-data /tmp/weasyprint_lemignon
# chmod 755 /tmp/weasyprint_lemignon

class PDFGenerator:
    def __init__(self):
        self.user_profile = os.path.expanduser("~")
        self.system = platform.system()
        # self.weasyprint_exe = os.path.join(
        #     self.user_profile, "AppData", "Local", ".ecole_360", "weasyprint.exe"
        # )
        
            # Chemin des templates
        self.template_path = os.path.join(
                self.user_profile, "AppData", "Local", ".ecole_360", "templates"
            )
            
        if self.system == "Windows":
            if not os.path.exists(self.template_path):
                os.makedirs(self.template_path, exist_ok=True)

    def get_real_path(self, relative_path): 

        # PyInstaller (onefile)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS

        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable) 
 
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def format_versement(self,key, index):
        parts = key.split('_')
        if len(parts) < 3:
            return key

        versement_type = parts[0]
        suffix = "er" if index == 1 else "eme"
        return f"{index}{suffix} {versement_type}"
    
    def date_formated(self, value) -> str:
        if not value:
            return "N/A"
        try:
            # Si c'est du texte (ISO format)
            if isinstance(value, str):
                dt = datetime.fromisoformat(value)
            # Si c'est déjà un objet date ou datetime
            else:
                dt = value
            return dt.strftime("%d %b %Y")
        except Exception:
            return str(value)
        
    

    def statut_echeance1(self,value):
        if not value:
            return "N/A"
        
        try:
            # Conversion si c'est une chaîne
            if isinstance(value, str): 
                dt_value = datetime.fromisoformat(value).date()
            elif isinstance(value, datetime):
                dt_value = value.date()
            else:
                dt_value = value
                
            aujourdhui = date.today()
            
            # Logique : Si la date est passée (inférieure à aujourd'hui)
            if dt_value < aujourdhui:
                return "Terminé"
            else:
                return "En cours"
                
        except Exception:
            return "Date invalide"

    def statut_echeance(self, value, date_debut=None):
        if not value:
            return "N/A"
        
        try:
            if isinstance(value, str): 
                dt_value = datetime.fromisoformat(value).date()
            elif isinstance(value, datetime):
                dt_value = value.date()
            else:
                dt_value = value
                
            aujourdhui = date.today()

            # ✅ Année pas encore commencée
            if date_debut:
                if isinstance(date_debut, str):
                    debut = datetime.fromisoformat(date_debut).date()
                elif isinstance(date_debut, datetime):
                    debut = date_debut.date()
                else:
                    debut = date_debut

                if aujourdhui < debut:
                    return "En attente"

            # Année commencée
            if dt_value < aujourdhui:
                return "Terminé"
            else:
                return "En cours"
                    
        except Exception:
            return "Date invalide"


    def generate_pdf_for_api(self, template_file: str, data: dict, 
                           output_filename: str = None) -> io.BytesIO:
        """
        Génère un PDF et retourne un BytesIO pour FastAPI
        """
        from weasyprint import HTML, CSS
        try:
            template_path = self.get_real_path("app/templates")
            
            if not os.path.exists(template_path):
                template_path = os.path.join(
                    self.user_profile, "AppData", "Local", ".ecole_360", "templates"
                )
            # 1. Setup Jinja2
            env = Environment(
                loader=FileSystemLoader(template_path),
                auto_reload=True,
                # enable_async=True,
                extensions=['jinja2.ext.loopcontrols','jinja2.ext.do']
            )
            import json
            env.filters['from_json'] = json.loads
            env.filters["format_versement"] = self.format_versement
            # templates.env.add_extension('jinja2.ext.do')
            template = env.get_template(template_file)
            
            # 2. Rendre le template
            html_content = template.render(**data)
            
            # 3. Créer un répertoire temporaire unique
            with tempfile.TemporaryDirectory() as temp_dir:
                # Chemins temporaires
                temp_html = os.path.join(temp_dir, "document.html")
                temp_css = os.path.join(temp_dir, "style.css")
                temp_pdf = os.path.join(temp_dir, "document.pdf")
                
                # 4. Écrire le HTML
                with open(temp_html, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                # 5. Écrire le CSS
                css_content = """
                @page {
                    size: A4;
                    margin: 15mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }
                .header {
                    text-align: left;
                    margin-bottom: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                """
                
                with open(temp_css, "w", encoding="utf-8") as f:
                    f.write(css_content)
                
                # 6. Exécuter WeasyPrint
                subprocess.run([
                    self.weasyprint_exe,
                    temp_html,
                    temp_pdf,
                    "-s", temp_css
                ], check=True, capture_output=True, text=True)
                
                # 7. Lire le PDF généré
                with open(temp_pdf, "rb") as f:
                    pdf_content = f.read()
                
                # 8. Retourner BytesIO
                return io.BytesIO(pdf_content)
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erreur WeasyPrint: {e.stderr}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Erreur génération PDF: {str(e)}")
        



    def generate_pdf_for_api_html1(self, template_file: str, data: dict, 
                           output_filename: str = None) -> io.BytesIO:
        """
        Charge un template Jinja2, injecte les données, 
        et génère un buffer PDF en mémoire.
        """
        css_content = """
                @page {
                    size: A4;
                    margin: 15mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }
                .header {
                    text-align: left;
                    margin-bottom: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                """
        from weasyprint import HTML, CSS

        if self.system == "Windows":
            user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
            server_path = os.path.join(
            user_profile, "AppData", "Local", ".ecole_360","templates"
                    )
            APP_ROOT = get_app_root()
            template_dir = os.path.join(APP_ROOT, "app", "templates")
            if not os.path.exists(template_dir):
                template_dir = server_path
        else:
            template_dir = "/var/www/admin.institutionlemignon.com/public_html/app/templates"

        env = Environment(
            loader=FileSystemLoader(template_dir),
            auto_reload=True,
            # enable_async=True,
            extensions=['jinja2.ext.loopcontrols','jinja2.ext.do']
            )
          
        import json
        env.filters['from_json'] = json.loads
        env.filters["format_versement"] = self.format_versement
        env.filters["date_formated"] = self.date_formated
        env.filters["statut_echeance"] = self.statut_echeance
        
        try:
            print(template_file)
            template = env.get_template(template_file)
            
            html_out = template.render(data)
            
            pdf_buffer = io.BytesIO()

            stylesheets = []
            if css_content:
                stylesheets.append(CSS(string=css_content))

            HTML(string=html_out, base_url=template_dir).write_pdf(pdf_buffer)
        
            pdf_buffer.seek(0)
            
            return pdf_buffer

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Erreur lors de la génération du PDF: {e}")
            return None
        



    def get_base64_logo():
        from app.Helper.persistent_storage import LOGO_DIR
        logo_path = str(LOGO_DIR / "school_logo.png")

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                # Encodage en base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                # On ajoute le préfixe pour le HTML
                return f"data:image/png;base64,{encoded_string}"
        return ""
    


    def generate_pdf_for_api_html(self, template_file: str, data: dict, 
                           output_filename: str = None) -> io.BytesIO:

        import os
        import io
        import tempfile
        from weasyprint import HTML, CSS
        from jinja2 import Environment, FileSystemLoader
        import json
        import traceback
        
        # Configuration du dossier temporaire pour WeasyPrint
        # tempfile.gettempdir() retourne le bon dossier selon l'OS
        # (/tmp sur Linux/Mac, %TEMP% sur Windows) au lieu d'un chemin Unix fixe.
        BASE_DIR = Path(__file__).resolve().parent
        temp_dir = os.path.join(tempfile.gettempdir(), 'weasyprint_lemignon')
        os.makedirs(temp_dir, exist_ok=True)
        os.environ['TMPDIR'] = temp_dir
        os.environ['TEMP'] = temp_dir
        os.environ['TMP'] = temp_dir
        tempfile.tempdir = temp_dir
        print(f"📁 Dossier temporaire WeasyPrint: {temp_dir}")

        css_content = """
                @page {
                    size: A4;
                    margin: 15mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }
                .header {
                    text-align: left;
                    margin-bottom: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                """

        # Déterminer le répertoire des templates
        BASE_DIR = Path(__file__).resolve().parent
        if self.system == "Windows":
            user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
            server_path = os.path.join(
                user_profile, "AppData", "Local", ".ecole_360", "templates"
            )
            APP_ROOT = get_app_root()
            template_dir = os.path.join(APP_ROOT, "app", "templates")
            if not os.path.exists(template_dir):
                template_dir = server_path
        else:
            # BASE_DIR = .../app/Helper -> .../app/templates (le vrai dossier des templates)
            template_dir = BASE_DIR.parent / "templates"
            # template_dir = "/var/www/admin.institutionlemignon.com/public_html/app/templates"
        
        # Vérifier que le dossier templates existe
        if not os.path.exists(template_dir):
            print(f"⚠️ Dossier templates introuvable: {template_dir}")
            template_dir = os.path.join(os.path.dirname(__file__), "../templates")
            os.makedirs(template_dir, exist_ok=True)
            print(f"📁 Utilisation du dossier: {template_dir}")

        # Configuration de Jinja2
        env = Environment(
            loader=FileSystemLoader(template_dir),
            auto_reload=True,
            extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.do']
        )
        
        # Ajout des filtres personnalisés
        env.filters['from_json'] = json.loads
        env.filters["format_versement"] = self.format_versement
        env.filters["date_formated"] = self.date_formated
        env.filters["statut_echeance"] = self.statut_echeance
        
        try:
            print(f"📄 Chargement du template: {template_file}")
            template = env.get_template(template_file)
            
            html_out = template.render(data)

            # Création du buffer PDF
            pdf_buffer = io.BytesIO()

            # Configuration des stylesheets
            stylesheets = []
            if css_content:
                stylesheets.append(CSS(string=css_content))

            # Génération du PDF avec gestion d'erreur améliorée
            # try:
            #     html = HTML(string=html_out, base_url=template_dir)
            #     html.write_pdf(pdf_buffer)
                
            # except Exception as pdf_error:
            #     print(f"❌ Erreur WeasyPrint: {pdf_error}")
            #     # Tentative avec configuration alternative
            #     html = HTML(string=html_out)
            #     html.write_pdf(pdf_buffer, stylesheets=stylesheets)
            # Remplacer le bloc try/except de génération PDF par :
            try:
                from weasyprint.text.fonts import FontConfiguration
                font_config = FontConfiguration()
                html = HTML(string=html_out, base_url=str(template_dir))
                html.write_pdf(pdf_buffer, font_config=font_config)

            except Exception as pdf_error:
                print(f"❌ Erreur WeasyPrint: {pdf_error}")
                html = HTML(string=html_out)
                html.write_pdf(pdf_buffer, stylesheets=stylesheets)
        
            pdf_buffer.seek(0)
            print("✅ PDF généré avec succès")
            return pdf_buffer

        except Exception as e:
            print(f"❌ Erreur lors de la génération du PDF: {e}")
            traceback.print_exc()
            raise RuntimeError(f"Échec génération PDF: {e}") from e


 