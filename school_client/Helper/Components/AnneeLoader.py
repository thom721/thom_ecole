from PySide6.QtCore import QThread, Signal
import requests

class AnneeLoader(QThread):
    finished_annee = Signal(list)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        # self.url = url

    def run(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url=self.url, headers=headers)
            
            response.raise_for_status()

            # response_data = response.json()

            # if response.status_code == 200:
                
            #     return response_data['data']
            # else:
            #     return response_data

            data = response.json()
            
            self.finished_annee.emit(data.get("data", []))
        except Exception as e:
            print("[Annee] Erreur :", e)
            self.error.emit(str(e))
