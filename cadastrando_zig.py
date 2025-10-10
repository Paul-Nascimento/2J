import pandas as pd
from omie import *
from main_final import identifica_tributacao


filepath = r'D:\Projetos\2J\Produtos_ZIG_2025.xlsx'
df = pd.read_excel(filepath)

APP_KEY = '5521527811800'
APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

#ZIG    

REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"

lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")

produtos_existentes = [str(prod['codigo']) for prod in lp['produto_servico_cadastro']]

for index, p in df.iterrows():
    print(f"Processando produto {index + 1}/{len(df)}: {p['productName']} (ID: {p['productId']})")
    
    if f'PRODTESTE{p["productId"]}' not in produtos_existentes:
        print(f"Produto {p['productName']} (ID: {p['productId']}) não cadastrado. Pulando...")
        
        tributacao = identifica_tributacao(p['productCategory'])
        if tributacao.get('status') == 'erro':
            #print(f"Erro ao identificar tributação: {tributacao.get('mensagem')}")
            continue

        payload = {
            "codigo_produto_integracao": f'PRODTESTE{p["productId"]}',
            "codigo": f'PRODTESTE{p["productId"]}',
            "descricao": f"{p['productName'][:105]}-",
            "unidade": "UN",
            "ncm": tributacao['ncm'],
            "valor_unitario": (p.get('unitValue') or 0) / 100,
            "cst_pis": tributacao['piscofins'],
            "cst_cofins": tributacao['piscofins'],
            "cfop": tributacao['cfop'],
            "csosn_icms": tributacao['icms'],
        }

        try:
            print(f'Cadastrando produto {payload}')
            print(p["productId"])
            
            cd = incluir_produto(APP_KEY, APP_SECRET, payload)
            print(cd)
            #time.sleep(1)  # Para evitar problemas de limite de requisições
            #print(f"Produto cadastrado: {payload['descricao']}")

            # opcional: atualiza o conjunto local para evitar reprocesso em execuções contínuas
            #_existentes_norm.add(payload["codigo"])

            # se quiser, pode postergar um refresh completo da lista do Omie para após o loop
            # lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=800,
            #                      apenas_importado_api="N", filtrar_apenas_omiepdv="N")
            # produtos_existentes = [str(prod['codigo']) for prod in lp['produto_servico_cadastro']]

        except Exception as e:
            print(f"Erro ao cadastrar produto {payload['descricao']}: {e}")

            payload['descricao'][-1] = "_"   # Trunca para evitar erros de tamanho
            try:
                cd = incluir_produto(APP_KEY, APP_SECRET, payload)
            #erros_ao_cadastrar.append((payload, str(e)))   
            except Exception as e2:
                print(f"Erro ao cadastrar produto {payload['descricao']} na 2a tentativa: {e2}")
                #erros_ao_cadastrar.append((payload, str(e2)))
