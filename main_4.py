import requests

def listar_meios_pagamento(app_key: str, app_secret: str):
    url = "https://app.omie.com.br/api/v1/geral/meiospagamento/"
    payload = {
        "call": "ListarMeiosPagamento",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "codigo": ""  # vazio lista todos
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if "fault" in data:
        raise Exception(f"Erro da API: {data['fault']}")
    # Espera-se data["MeiosPagamentoLista"]
    return data.get("MeiosPagamentoLista", [])

# Exemplo de uso
if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9' 
    try:
        meios = listar_meios_pagamento(APP_KEY,APP_SECRET)
        print("Meios de pagamento:", meios)
    except Exception as e:
        print("Erro:", e)


