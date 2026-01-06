import requests
import json

def listar_clientes(app_key: str, app_secret: str, pagina_inicial: int = 1, registros_por_pagina: int = 500):
    """
    Consome o endpoint ListarClientes da API do Omie.

    Args:
        app_key (str): Chave da aplicação Omie.
        app_secret (str): Segredo da aplicação Omie.
        pagina_inicial (int): Página inicial da consulta (default=1).
        registros_por_pagina (int): Quantidade de registros por página (máx. 500).

    Returns:
        list: Lista consolidada de todos os clientes retornados.
    """
    
    url = "https://app.omie.com.br/api/v1/geral/clientes/"
    metodo = "ListarClientes"
    
    todos_clientes = []
    pagina = pagina_inicial
    terminou = False

    while not terminou:
        payload = {
            "call": metodo,
            "app_key": app_key,
            "app_secret": app_secret,
            "param": [
                {
                    "pagina": pagina,
                    "registros_por_pagina": registros_por_pagina,
                    "apenas_importado_api": "N"
                }
            ]
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            print(response.text)
            break

        data = response.json()

        if "clientes_cadastro" in data and data["clientes_cadastro"]:
            todos_clientes.extend(data["clientes_cadastro"])
            total_paginas = data.get("nTotPaginas", 1)
            
            print(f"✅ Página {pagina}/{total_paginas} importada com sucesso. ({len(data['clientes_cadastro'])} registros)")
            
            if pagina >= total_paginas:
                terminou = True
            else:
                pagina += 1
        else:
            terminou = True

    print(f"\nTotal de clientes retornados: {len(todos_clientes)}")
    return todos_clientes


if __name__ == "__main__":
    #JOVEM DO VINHO
    APP_KEY = '6327079006248'
    APP_SECRET = '6d3cfc23d7eafa0b63a2878e8e5f01d8'

    
    #pATINHO FEIO
    #APP_KEY = '5521527811800'
    #APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    clientes = listar_clientes(APP_KEY, APP_SECRET)
    # Exemplo de uso: imprimir os primeiros 5 clientes  
    import pandas as pd
    df_clientes = pd.DataFrame(clientes)    
    print(df_clientes.head())
    df_clientes.to_excel(r'D:\Projetos\2J\Clientes_OMIE.xlsx', index=False)    