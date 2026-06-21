import requests
from Config import BASE_URL


# def connect(email, password):
#     url = f"{BASE_URL}login" 

#     payload = {
#         "email": email,
#         "password": password
#     }
#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json'
#       }
#     # print(url)
#     try:
#         response = requests.post(url, json=payload, headers=headers) 

#         response_data = response.json()   
    
#         if response.status_code == 200:
#             # print(response_data)
           
#             return response_data  
#         else:
#             print(response_data)
#             return response_data

#     except requests.exceptions.RequestException as e:
#         return print(f"{e}")

# Exemple d'utilisation
# result = connect("test@example.com", "password123")
# print(result)
