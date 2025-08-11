



import requests
import json

class OmieContaReceberAPI:
    BASE_URL = "https://app.omie.com.br/api/v1/financas/contareceber/"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def _post(self, call: str, param: dict):
        body = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param]
        }
        resp = self.session.post(self.BASE_URL, data=json.dumps(body))
        resp.raise_for_status()
        return resp.json()

    def listar_contas_receber(self, pagina: int = 1, registros_por_pagina: int = 20, apenas_importado_api: str = "N"):
        """
        Lista contas a receber com paginação.
        Retorna dict com chaves: pagina, total_de_paginas, registros, total_de_registros e conta_receber_cadastro (lista).
        """
        param = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api
        }
        return self._post("ListarContasReceber", param)

def incluir_pedido_venda(app_key, app_secret, pedido):
    url = "https://app.omie.com.br/api/v1/produtos/pedido/"
    payload = {
        "call": "IncluirPedido",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [pedido]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP:", e)
        print("Status:", resp.status_code)
        print("Retorno API:", resp.text)
        raise
    result = resp.json()
    if result.get("faultstring"):
        raise Exception(f"Erro Omie API: {result['faultstring']}")
    return result

def consultar_clientes(app_key,app_secret):
    url = 'https://app.omie.com.br/api/v1/geral/clientes/'
    payload = {
        "call": "ListarClientes",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": 1,
            "registros_por_pagina": 1
        }]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP:", e)
        print("Status:", resp.status_code)
        print("Retorno API:", resp.text)
        raise
    result = resp.json()
    if result.get("faultstring"):
        raise Exception(f"Erro Omie API: {result['faultstring']}")
    return result

def listar_contas_correntes(app_key: str, app_secret: str, pagina: int = 1, registros_por_pagina: int = 50, apenas_importado_api: str = "N") -> dict:
    url = "https://app.omie.com.br/api/v1/geral/contacorrente/"
    payload = {
        "call": "ListarContasCorrentes",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api
        }]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP:", e)
        print("Status:", resp.status_code)
        print("Retorno API:", resp.text)
        raise
    data = resp.json()
    if data.get("faultstring"):
        raise Exception(f"Erro da API Omie: {data['faultstring']}")
    return data

# Uso:
if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    pedido = {
        "cabecalho": {
            "codigo_cliente": 2483761878,
            "codigo_pedido_integracao": "1754477779",
            "data_previsao": "06/08/2025",
            "etapa": "10",
            "numero_pedido": "27447",
            "codigo_parcela": "999",
            "quantidade_itens": 1
        },
        "det": [
            {
            "ide": {
                "codigo_item_integracao": "4422421"
            },
            "inf_adic": {
                "peso_bruto": 150,
                "peso_liquido": 150
            },
            "produto": {
                "cfop": "5.102",
                "codigo_produto": "4422421",
                "descricao": "Telefone Celular X",
                "ncm": "9403.30.00",
                "quantidade": 1,
                "tipo_desconto": "V",
                "unidade": "UN",
                "valor_desconto": 0,
                "valor_unitario": 200
            }
            }
            ],
            "frete": {
                "modalidade": "9"
            },
            "informacoes_adicionais": {
                "codigo_categoria": "1.01.03",
                "codigo_conta_corrente": 2461399515,
                "consumidor_final": "S",
                "enviar_email": "N"
            },
            "agropecuario": {
                "cNumReceita": "",
                "cCpfResponsavel": "",
                "nTipoGuia": 1,
                "cUFGuia": "",
                "cSerieGuia": "",
                "nNumGuia": 1
            },
            "lista_parcelas": {
                "parcela": [
                {
                    "data_vencimento": "07/08/2025",
                    "numero_parcela": 1,
                    "percentual": 50,
                    "valor": 100
                },
                {
                    "data_vencimento": "09/01/2026",
                    "numero_parcela": 2,
                    "percentual": 50,
                    "valor": 100
                }
                ]
            }
            }

    #clientes = consultar_clientes(APP_KEY,APP_SECRET)
    resposta = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)
    print("Resposta da API:", resposta)
    #resp = listar_contas_correntes(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #print(resp)
    

#Criar pedido
#Verificar se o pedido existe
#Criar itens
#Inserir itens no pedido


"""
if __name__ == "__main__":
    app_key = '5521527811800'
    app_secret = '9cff454af6348882c175d91a11f0d5d9' 
    api = OmieContaReceberAPI(app_key=app_key, app_secret=app_secret)
    resp = api.listar_contas_receber(pagina=1, registros_por_pagina=50)
    print("Página:", resp["pagina"])
    print("Total de páginas:", resp["total_de_paginas"])
    print("Total de registros:", resp["total_de_registros"])
    for conta in resp.get("conta_receber_cadastro", []):
        print(conta["codigo_lancamento_omie"], conta["valor_documento"])
"""