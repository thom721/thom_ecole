import time
import os
from Controllers.Main_run import Main_run
from Helper.generate_key_1 import generate_and_send

# def check_connection():
#     try:
#          requests.get('https://www.google.com')
#          return True
#     except Exception as e:
#         print(f"error {e}")





if __name__ == "__main__":
    # print("=========open app++++++++++++++++11")
    # try:
    # masked_input()
    # runner = Main_run()
    # print("=========open app++++++++++++++222222222")
    # runner.install_and_config()
    # print("=========open app++++++++++++++33333333333")
    # except KeyboardInterrupt  as e:
    #   print(f'An KeyboardInterrupt occurred {e}')

    # except Exception  as e:
    #   print(f'An exception occurred {e}')

    # try:


    start_time = time.time()

      # Vérifier les fichiers recherchés
    # for folder in ["Helpers", "Controllers", "api"]:
    #     path = os.path.join(os.getcwd(), folder)
    #     print(f" Vérification du dossier : {path} - Existe ? {os.path.exists(path)}")

    print(f" Temps de démarrage : {time.time() - start_time:.2f} secondes") 
    runner = Main_run()
    runner.install_and_config()
    # except Exception as e:
    #   print(f"Erreur : {e}")
    input("Appuyez sur Entrée pour... quitter...")
