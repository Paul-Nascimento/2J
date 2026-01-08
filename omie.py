import time
import json
import requests
from typing import List, Dict, Tuple, Optional,Any


class OmieContaReceberAPI:
    BASE_URL = "https://app.omie.com.br/api/v1/financas/contareceber/"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _post(self, call: str, param: dict):
        body = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [param],
        }
        resp = self.session.post(self.BASE_URL, data=json.dumps(body))
        resp.raise_for_status()
        return resp.json()

    def listar_contas_receber(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 20,
        apenas_importado_api: str = "N",
    ):
        param = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
        }
        return self._post("ListarContasReceber", param)

    def incluir_conta_receber(
        self,
        *,
        codigo_lancamento_integracao: str,
        codigo_cliente_fornecedor: int,
        data_vencimento: str,
        valor_documento: float,
        codigo_categoria: str,
        id_conta_corrente: int,
        data_previsao: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Cria um lançamento de Conta a Receber no Omie via método IncluirContaReceber.

        Datas devem estar no formato "DD/MM/AAAA".
        Campos mínimos comuns (exemplo oficial): codigo_lancamento_integracao, codigo_cliente_fornecedor,
        data_vencimento, valor_documento, codigo_categoria, data_previsao, id_conta_corrente.
        :contentReference[oaicite:1]{index=1}

        Retorno esperado (quando sucesso) inclui "codigo_lancamento_omie" e "descricao_status".
        :contentReference[oaicite:2]{index=2}
        """
        if not data_previsao:
            data_previsao = data_vencimento

        if not codigo_lancamento_integracao:
            raise ValueError("codigo_lancamento_integracao é obrigatório (string).")
        if not isinstance(codigo_cliente_fornecedor, int):
            raise TypeError("codigo_cliente_fornecedor deve ser int.")
        if not isinstance(id_conta_corrente, int):
            raise TypeError("id_conta_corrente deve ser int.")
        if valor_documento is None or float(valor_documento) <= 0:
            raise ValueError("valor_documento deve ser maior que zero.")

        param: Dict[str, Any] = {
            "codigo_lancamento_integracao": str(codigo_lancamento_integracao),
            "codigo_cliente_fornecedor": codigo_cliente_fornecedor,
            "data_vencimento": data_vencimento,
            "valor_documento": float(valor_documento),
            "codigo_categoria": codigo_categoria,
            "data_previsao": data_previsao,
            "id_conta_corrente": id_conta_corrente,
        }

        if extras:
            # permite enviar outros campos aceitos pela Omie sem precisar mudar assinatura
            param.update(extras)

        return self._post("IncluirContaReceber", param)

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

import json
import requests
import json
import requests

def consultar_clientes(app_key, app_secret):
    url = 'https://app.omie.com.br/api/v1/geral/clientes/'
    headers = {"Content-Type": "application/json"}

    pagina = 1
    registros_por_pagina = 500
    clientes_dict = {}

    while True:
        payload = {
            "call": "ListarClientes",
            "app_key": app_key,
            "app_secret": app_secret,
            "param": [{
                "pagina": pagina,
                "registros_por_pagina": registros_por_pagina
            }]
        }

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

        for cliente in result.get("clientes_cadastro", []):
            cpfcnpj = str(cliente.get('cnpj_cpf', ''))
            cpfcnpj = cpfcnpj.replace('.', '').replace('/', '').replace('-', '')
            codigo_omie = cliente.get('codigo_cliente_omie')

            if cpfcnpj and codigo_omie:
                clientes_dict[cpfcnpj] = codigo_omie

        total_paginas = int(result.get("total_de_paginas", 1))
        if pagina >= total_paginas:
            break

        pagina += 1

    return clientes_dict



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

def criar_cliente_pf_omie(
    app_key: str,
    app_secret: str,
    nome: str,
    cpf: str,
    email: str = None
):
    """
    Cria um cliente Pessoa Física no Omie apenas para fins financeiros
    (sem emissão de nota fiscal).

    Campos mínimos:
    - Nome
    - CPF
    """

    url = "https://app.omie.com.br/api/v1/geral/clientes/"

    payload = {
        "call": "IncluirCliente",
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [
            {
                "codigo_cliente_integracao": cpf,
                "razao_social": nome,
                "nome_fantasia": nome,
                "cnpj_cpf": cpf,
                "pessoa_fisica": "S",
                "email": email,
                "bloquear_faturamento": "N",
                "inativo": "N"
            }
        ]
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    response.raise_for_status()
    return response.json()



if __name__ == "__main__":
    APP_KEY = '6327079006248'
    APP_SECRET = '6d3cfc23d7eafa0b63a2878e8e5f01d8'

    
    #pATINHO FEIO
    #APP_KEY = '5521527811800'
    #APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    import pandas as pd
    #APP_KEY = '4123090876905' #YUSER
    #APP_SECRET = 'fec203d2b600db8491d1b3ed793e2e83'
    #categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=400)
    
    #df = pd.DataFrame(categorias['categoria_cadastro'])
    #df.to_excel("saida_categorias_omie.xlsx", index=False)
    
    
    #cc = listar_contas_correntes(APP_KEY,APP_SECRET,pagina=1,registros_por_pagina=100)
    #df_contas = pd.DataFrame(cc)
    #df_contas.to_excel("saida_contas_correntes_omie.xlsx", index=False)
    
    


    
    #df_clientes = pd.DataFrame(clientes)
    #df_clientes.to_excel("saida_clientes_omie.xlsx", index=False)
    exit()
    
    
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    print(lp)
    
    import pandas as pd
    df = pd.DataFrame(lp.get('produto_servico_cadastro', []))
    df.to_excel("saida_produtos_omie2.xlsx", index=False)

    
    
