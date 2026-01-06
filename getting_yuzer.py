import requests


login = 'financeiroverrieverri@gmail.com'
senha = 'Bpo@123'

def authenticate_user(username, password):
    """
    Authenticates a user based on provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

        """
    
    url = "https://login.eagle.yuzer.com.br/api/auth/login"

    payload = {
        "username": username, 
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }   
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception("Authentication failed with status code: {}".format(response.status_code))
    
def get_products(token):
    """
    Retrieves products using the provided authentication token.

    Args:
        token (str): The authentication token.

    Returns:
        list: A list of products.
    """
    url = "https://api.eagle.yuzer.com.br/api/products/search"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }  

    payload = {"status": "ALL", "page": 1, "perPage": 500, "q": "", "sort": "desc", "sortColumn": "id"}

    response = requests.post(url, headers=headers,json=payload)
    if response.status_code == 200:
        print(response.json())
        #Contar a quantidade de produtos retornados e paginas; Se for mais de 500 produtos, fazer paginação
        #total_products = response.json().get("total", 0)    


        return response.json().get("products", [])
    else:
        raise Exception("Failed to retrieve products with status code: {}".format(response.status_code))

def get_events(token):

    """
    Retrieves events using the provided authentication token.

    Args:
        token (str): The authentication token.

    Returns:
        list: A list of events.
    """
    url = "https://api.eagle.yuzer.com.br/api/salesPanels/search"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }  

    payload = {"page": 1, "perPage": 500, "q": "", "sort": "desc", "sortColumn": "id", "status":"ALL"}

    response = requests.post(url, headers=headers,json=payload)
    if response.status_code == 200:
        print(response.json())
        #return response.json().get("events", [])
    else:
        raise Exception("Failed to retrieve events with status code: {}".format(response.status_code))

def get_sales(token,event_id):
    url = f'https://api.eagle.yuzer.com.br/api/salesPanels/{event_id}/products/search'

    payload = {
        "status": "ALL",
        "page": 1,
        "perPage": 10,
        "from": "2025-05-01T17:00:00.000Z",
        "to": "2025-05-02T00:00:00.000Z",
        "currency": "BRL",
        "expandCombo": False,
        "q": "",
        "sort": "desc",
        "sortColumn": "count"
        }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(response.json())
        #return response.json().get("products", [])

    

#token = authenticate_user(login, senha)
token = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmaW5hbmNlaXJvdmVycmlldmVycmlAZ21haWwuY29tIiwiaWQiOjI0MjYsIm5hbWUiOiJBcnRodXIgTMO0Ym8iLCJ0eXBlIjoiQURNSU5JU1RSQVRJT04iLCJtYXN0ZXJDb21wYW55SWQiOjU1NywiaWF0IjoxNzY1MTA5MjYxLCJleHAiOjE3NjUxOTU2NjF9.VAv5sKPUW3DDIGmoojmO3k44CqVom5TZtUKsi_C4K_8'
print("Authentication token:", token)

#products = get_products(token)
#print("Retrieved products:", products)

#events = get_events(token)
#print("Retrieved events:", events)

sales = get_sales(token, 9902)
