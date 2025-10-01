import time
import json
import requests
from typing import List, Dict, Tuple, Optional


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
            "registros_por_pagina": 386
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

def listar_categorias(app_key: str, app_secret: str, pagina: int = 1, registros_por_pagina: int = 50) -> dict:
    """
    Lista categorias de lançamento no Omie.
    Retorna dict com chaves: pagina, total_de_paginas, registros, total_de_registros e lista_categorias.
    """
    url = "https://app.omie.com.br/api/v1/geral/categorias/"
    payload = {
        "call": "ListarCategorias",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
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
        raise Exception(f"Erro da API Omie: {result['faultstring']}")
    return result

def listar_produtos(app_key: str, app_secret: str,
                    pagina: int = 1, registros_por_pagina: int = 50,
                    apenas_importado_api: str = "N", filtrar_apenas_omiepdv: str = "N") -> dict:
    """
    Lista produtos cadastrados no Omie.
    Retorna dict com chaves: pagina, total_de_paginas, registros, total_de_registros e lista_produtos.
    """
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    payload = {
        "call": "ListarProdutos",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
            "filtrar_apenas_omiepdv": filtrar_apenas_omiepdv
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
        raise Exception(f"Erro da API Omie: {result['faultstring']}")
    return result

def listar_cfop(app_key: str, app_secret: str, pagina: int = 1, registros_por_pagina: int = 50) -> dict:
    """
    Lista CFOP (Código Fiscal de Operações e Prestações) no Omie.
    Retorna dict com chaves: pagina, total_de_paginas, registros, total_de_registros e lista_cfop.
    """
    url = "https://app.omie.com.br/api/v1/produtos/cfop/"
    payload = {
        "call": "ListarCFOP",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP ao listar CFOP:", e)
        print("Status:", resp.status_code)
        print("Retorno API:", resp.text)
        raise
    result = resp.json()
    if result.get("faultstring"):
        raise Exception(f"Erro da API Omie (CFOP): {result['faultstring']}")
    return result

def listar_ncm(app_key: str, app_secret: str, pagina: int = 1, registros_por_pagina: int = 50) -> dict:
    """
    Lista NCM (Nomenclatura Comum do Mercosul) no Omie.
    Retorna dict com chaves: pagina, total_de_paginas, registros, total_de_registros e lista_ncm.
    """
    url = "https://app.omie.com.br/api/v1/produtos/ncm/"
    payload = {
        "call": "ListarNCM",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [{
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP ao listar NCM:", e)
        print("Status:", resp.status_code)
        print("Retorno API:", resp.text)
        raise
    result = resp.json()
    if result.get("faultstring"):
        raise Exception(f"Erro da API Omie (NCM): {result['faultstring']}")
    return result
# Uso:
def incluir_produto(app_key: str, app_secret: str, produto: dict, session: Optional[requests.Session] = None) -> dict:
    """
    Inclui UM produto na Omie.
    `produto` deve seguir o schema do endpoint /geral/produtos - call: IncluirProduto.
    Exemplo mínimo:
    {
        "codigo_produto_integracao": "SKU-123",
        "descricao": "Produto Exemplo",
        "unidade": "UN",
        "ncm": "12345678",            # opcional, mas recomendado
        "ean": "7891234567890",       # opcional
        "peso_liq": 0,                # opcional
        "peso_bruto": 0,              # opcional
        "origem": "0"                 # opcional (0 = nacional, conforme Tabela de Origem)
        ...
    }
    """
    url = "https://app.omie.com.br/api/v1/geral/produtos/"
    payload = {
        "call": "IncluirProduto",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [produto]
    }
    sess = session or requests.Session()
    resp = sess.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Log detalhado
        raise RuntimeError(f"HTTP error ao incluir produto: {e}\nStatus={resp.status_code}\nRetorno={resp.text}") from e

    data = resp.json()
    if data.get("faultstring"):
        # Erro semântico/regra de negócio na Omie
        raise RuntimeError(f"Erro Omie ao incluir produto: {data['faultstring']}")
    return data

def criar_produtos_em_lote(
    app_key: str,
    app_secret: str,
    produtos: List[Dict],
    stop_on_error: bool = False,
    max_retries: int = 3,
    backoff_base_seconds: float = 1.5
) -> Tuple[List[Dict], List[Dict]]:
    """
    Cria produtos em lote na Omie.
    - `produtos`: lista de dicionários no schema aceito por IncluirProduto.
    - `stop_on_error`: se True, para no primeiro erro e lança exceção; se False, continua e acumula falhas.
    - `max_retries`: tentativas extras para erros 429/5xx (backoff exponencial).
    - Retorna (sucessos, falhas) onde:
        sucessos = lista de dicts {"input": produto, "result": resposta_omie}
        falhas   = lista de dicts {"input": produto, "error": "mensagem do erro"}

    Observação: utilize `codigo_produto_integracao` para idempotência no cadastro.
    """
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    sucessos = []
    falhas = []

    for idx, prod in enumerate(produtos, start=1):
        # Retry simples para erros transitórios
        attempt = 0
        while True:
            attempt += 1
            try:
                result = incluir_produto(app_key, app_secret, prod, session=session)
                sucessos.append({"input": prod, "result": result})
                break  # saiu do loop de retry deste item
            except RuntimeError as err:
                err_msg = str(err)
                # Tenta identificar status code 429/5xx no texto (pois já foi englobado na RuntimeError)
                transient = any(code in err_msg for code in [" 429", " 500", " 502", " 503", " 504"])

                if transient and attempt <= max_retries:
                    # backoff exponencial
                    sleep_for = (backoff_base_seconds ** attempt)
                    time.sleep(sleep_for)
                    continue  # tenta de novo
                else:
                    falhas.append({"input": prod, "error": err_msg})
                    if stop_on_error:
                        raise RuntimeError(f"Falha ao criar produto no item {idx}: {err_msg}") from None
                    break  # segue para o próximo produto

    return sucessos, falhas





if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #cc = listar_contas_correntes(APP_KEY,APP_SECRET,pagina=1,registros_por_pagina=100)
    #clientes = consultar_clientes(APP_KEY, APP_SECRET)
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    print(lp)
    
    import pandas as pd
    df = pd.DataFrame(lp.get('produto_servico_cadastro', []))
    df.to_excel("saida_produtos_omie2.xlsx", index=False)

    """
    nomes_dos_produtos = [produto['descricao'] for produto in lp.get('produto_servico_cadastro', [])]
    print(nomes_dos_produtos)
    #cfop = listar_cfop(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #ncm =listar_ncm(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)

    pedido = {
        "cabecalho": {
            "codigo_cliente": 2483785544, # 'codigo_cliente_omie' na API ListarClientes
            "codigo_pedido_integracao": "19000000", #Esse valor vem do zig
            "data_previsao": "15/08/2025",
            "etapa": "10",
            "numero_pedido": "27447",
            "codigo_parcela": "999",
            "qtde_parcelas": 1,
            "origem_pedido": "API"
        },
        "det": [
            {
            "ide": {
                "codigo_item_integracao": "1"
            },
            "inf_adic": {
                "peso_bruto": 1,
                "peso_liquido": 1
            },
            "produto": {
                "cfop": "5102",
                "codigo_produto": "2514568647",
                "descricao": "Produto Teste",
                "ncm": "94033000",
                "quantidade": 1,
                "unidade": "UN",
                "valor_desconto": 0,
                "valor_unitario": 200
                    }
                }
            ],
        "informacoes_adicionais": {
            "codigo_categoria": "2.11.01",
            "codigo_conta_corrente": 2461399601, #nCodCC na api ListarContasCorrentes
            "consumidor_final": "S",
            "enviar_email": "N"
        },
            
        "lista_parcelas": {
            "parcela": [
            {
                    "data_vencimento": "15/08/2025",
                    "numero_parcela": 1,
                    "percentual": 50,
                    "valor": 100
                },
                {
                    "data_vencimento": "19/01/2026",
                    "numero_parcela": 2,
                    "percentual": 50,
                    "valor": 100
                }
            ]
        }
        }

    #clientes = consultar_clientes(APP_KEY,APP_SECRET)
    #resposta = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)
    #print("Resposta da API:", resposta)
    resp = listar_contas_correntes(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #print(resp)
    

#Criar pedido
#Verificar se o pedido existe
#Criar itens
#Inserir itens no pedido



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
