import requests
import pandas as pd
from omie import *


#token = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlcGxheVNlc3Npb25zIjp7ImVTTEhPZHVJZjFWdWVUb2FUajJiMkIwZkFSUDIiOjExfSwicm9sZXBsYXlVc2VySWQiOiJlU0xIT2R1SWYxVnVlVG9hVGoyYjJCMGZBUlAyIiwicm9sZXBsYXlSZXNvdXJjZXMiOlsic2FsZXMiLCJwcm9kdWN0cyIsInJlcG9ydHMiLCJtZW1iZXJzIiwiY2xpZW50cyIsImFmZmlsaWF0ZXMiLCJjb3Vwb25zIiwicmVmdW5kcyIsIndhbGxldCIsImludGVncmF0aW9ucyIsImhvbWUiLCJzdWJzY3JpcHRpb25zIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnMiLCJtZW1iZXJzX2FyZWFfbm90aWZpY2F0aW9uc19jb21tZW50X2FwcHJvdmFsIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfY29tbWVudF9tZW50aW9uIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfY29udGVudF9ldmFsdWF0aW9uIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfdGFza19hcHByb3ZhbCIsInJvbGVwbGF5Il0sImhhc0NvbXBsZXRlZE1GQSI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2NoYXRwYXktY2QxMjAiLCJhdWQiOiJjaGF0cGF5LWNkMTIwIiwiYXV0aF90aW1lIjoxNzY1MTEwMzQ5LCJ1c2VyX2lkIjoiQU1RRERiZ3huZ2dRYUVTbXRONHRHakYzNHNQMiIsInN1YiI6IkFNUUREYmd4bmdnUWFFU210TjR0R2pGMzRzUDIiLCJpYXQiOjE3NjUxMTAzNDksImV4cCI6MTc2NTExMzk0OSwiZW1haWwiOiJmaW5hbmNlaXJvQGpvdmVtZG92aW5oby5jb20uYnIiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInBob25lX251bWJlciI6Iis1NTYxOTkzMjY1NzY3IiwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJmaW5hbmNlaXJvQGpvdmVtZG92aW5oby5jb20uYnIiXSwicGhvbmUiOlsiKzU1NjE5OTMyNjU3NjciXX0sInNpZ25faW5fcHJvdmlkZXIiOiJjdXN0b20ifX0.nFdc86V_iAu0i86D7-bRyAMTBztC1Iz7StczndSsgugK9sMRnqOG1vwTkWZ5ZjDXwaw3DkKGrM1XO3wdcli50lZXKB3YMgif61ReqjkWobs3O-BGaCWwj32a3CLU6YaHA8ZVS8tTs-nRvsIn3fMbg4kkAv6tN4Wtz6UitmYcMLfSuLYuxE1s_tjrUZthUpWrFXkDB5CyqgiKAI91xAVr5HRevuen1SMzXR0Z7hqLmBQfYbL1i1s94qB0YeiMS8NRDdjVNiw0JR1PT9bprOtqeWL4xag82H7hHg2IyM7gh9JTq8hs3AkUVe-64_Z91fujjz8YQLqFie5TsiSUlI34_Q'

def get_products(token):
    url = 'https://backend-bff-product.platform.hub.la/api/v1/products/list'

    payload = {"page": 1, "pageSize": 25, "orderBy": "createdAt", "orderDir": "DESC", "filters": {"search": ""}}

    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response)
    if response.status_code == 201:
        print(response.json())
        return response.json().get("products", [])
 
def login():

    key = 'AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'
    payload = {"returnSecureToken": True, "email": "financeiro@jovemdovinho.com.br", "password": "2jFinanceiro", "clientType":"CLIENT_TYPE_WEB"}

    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'

    headers = {
        "Content-Type":"application/json"
    }
    response = requests.post(url,json=payload,headers=headers)

    #print(response.json())
    
    return response.json().get("idToken", None),response.json().get("refreshToken", None)

def get_secure_token(id_token):
    url = 'https://securetoken.googleapis.com/v1/token?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'

    headers = {
        "Content-Type":"application/json",

    }
    payload = {
        "grant_type":"refresh_token",
        "refresh_token":id_token
    }

    response = requests.post(url,headers=headers,json=payload)

    #print(response.json())
    return response.json().get("access_token", None),response.json().get("refresh_token", None),response.json().get("user_id", None)

def get_sign_in(sign_in_token,user_id): #Bearer
    url ='https://backend-bff-web.platform.hub.la/api/v1/user/roleplay/sign-in'

    headers = {
        "Content-Type": "application/json",
        "Authorization": sign_in_token,
        "Accept": "application/json, text/plain, */*",
    }

    payload = {
        "roleplayUserId":"eSLHOduIf1VueToaTj2b2B0fARP2"
    }
    
    response = requests.post(url, headers=headers,json=payload)
    

    return response.text
    #return response.json().get("acess_token", None)

def get_identity_toolkit_token(token):
    url ="https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8"


    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://app.hub.la",
        "referer": "https://app.hub.la/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        
        # Esses headers "X-browser" não são validados pelo Firebase, mas manter não atrapalha:
        "x-browser-channel": "stable",
        "x-browser-copyright": "Copyright 2025 Google LLC. All Rights reserved.",
        "x-browser-validation": "Aj9fzfu+SaGLBY9Oqr3S7RokOtM=",
        "x-browser-year": "2025",
        
        # Firebase exige esse em alguns cenários (não obrigatório sempre)
        "x-client-version": "Chrome/JsCore/11.4.0/FirebaseCore-web",
        "x-firebase-gmpid": "1:223497474066:web:7732a1419a7052e60108cb"
    }

    payload = {
        "returnSecureToken":True,
        "token":token
    }
    
    response = requests.post(url, headers=headers,json=payload)

    #print(response.json())
    return response.json().get("idToken", None)

def get_auth(id_token):
    url ='https://hub.la/api/auth/get'

    headers = {
        "Content-Type":"application/json",
        "Authorization":id_token
        

    }

    paylaod = {}

    response = requests.post(url,headers=headers,json=paylaod)

    #print(response.json())

def get_offers(token):
    url = 'https://backend-bff-product.platform.hub.la/api/v1/filters/offers'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {token}',
    }

    req = requests.get(url,headers=headers)

    data = req.json()['owner']

    ids = []

    for item in data:
        ids.append(item['id'])
    
    return ids

def get_sales(token,offers):
    url = 'https://backend-bff-web.platform.hub.la/api/v1/invoices/list'
                #Offers são os próprios produtos 
    payload = {"offerIds":offers,
               "hasSelectedAll":True,
               "filters":{"startDate":"2025-12-20T00:00:00-03:00","endDate":"2025-12-20T23:59:59-03:00",
                          "status":["paid"],
                          "type":[],
                          "paymentMethod":[],
                          "search":"",
                          "utmSource":"",
                          "utmMedium":"",
                          "utmCampaign":"",
                          "utmContent":"",
                          "utmTerm":"",
                          "dateRangeBy":"createdAt"},
                          "page":1,
                          "pageSize":25,
                          "orderBy":"createdAt",
                          "orderDirection":"DESC"}


    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    response = requests.post(url, headers=headers, json=payload)
    
    #df = pd.DataFrame(response.json().get("items"))

    #df.to_excel(r'D:\Projetos\2J\hublasalex.xlsx', index=False)

    #print(response.json())
    if response.status_code == 201:
        #print(response.json())
        return response.json().get("items", [])



    response = requests.get(url, headers=headers)
    #print(response.json())

    return response.json()['items']

"""
Login > Token

Get-Secure-Token

Get-Sign-in-Token

Get-Identity-Toolkit-token


"""
APP_KEY = '6327079006248'
APP_SECRET = '6d3cfc23d7eafa0b63a2878e8e5f01d8'



cr = OmieContaReceberAPI(APP_KEY, APP_SECRET)
clientes = consultar_clientes(APP_KEY, APP_SECRET)
clientes_dict = {}
for categoria in clientes['clientes_cadastro']:
    cpfcnpj = str(categoria['cnpj_cpf']).replace('.',"").replace("/","").replace("-","")
    codigo_omie = categoria['codigo_cliente_omie']
    clientes_dict[cpfcnpj] = codigo_omie

categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=400)
categorias_dict = {}
for categoria in categorias['categoria_cadastro']:
    codigo = categoria['codigo']
    descricao = categoria['descricao']
    categorias_dict[descricao] = codigo


#Processo de autenticação
login_token,refresh_login_token = login()
secure_token,refresh_secure_token,user_id = get_secure_token(refresh_login_token)
sigin_token = get_sign_in(f'Bearer {secure_token}',user_id)
toolkit_token = get_identity_toolkit_token(sigin_token)



import pprint
offers =get_offers(toolkit_token)
sales = get_sales(toolkit_token,offers)

for sale in sales:
    produtos = sale['amountDetail']['products']
    taxa_da_hubla = sale['amountDetail']['installmentFeeCents']

    payer_email = sale['payer']['identity']['email']
    payer_name = sale['payer']['identity']['fullName']
    payer_cpf = sale['payer']['identity']['document']

    for product in produtos:
        nome_do_produto = product['productName'] #Categoria no OMIE
        valor_do_produtos = product['priceCents'] / 100 
        #print(product)
        print(nome_do_produto)
        print(valor_do_produtos)
        print(taxa_da_hubla)
        print(payer_name,payer_cpf)
        print(categorias_dict[nome_do_produto])

        if payer_cpf in clientes_dict.keys():
            codigo_cliente = clientes_dict[payer_cpf]
        else:
            codigo_cliente = criar_cliente_pf_omie(APP_KEY,APP_SECRET,payer_name,payer_cpf,payer_email)['codigo_cliente_omie']


        #Outra validacao para categoria
        if nome_do_produto in categorias_dict.keys():
            codigo_categoria = categorias_dict[nome_do_produto]

        else:
            codigo_categoria = 'Errooo'

        lancamento_conta_a_receber = cr.incluir_conta_receber(
            codigo_lancamento_integracao="1691776455",
            codigo_cliente_fornecedor=codigo_cliente,
            data_vencimento="11/01/2026",
            valor_documento=valor_do_produtos,
            codigo_categoria=codigo_categoria, #1.01.88 
            id_conta_corrente=8657749943,
        )

        print(lancamento_conta_a_receber)



        #req = criar_cliente_pf_omie(APP_KEY,APP_SECRET,'Paulo Nascimento','99738961149','paulonascimento0910@gmail.com')
    
    exit()




