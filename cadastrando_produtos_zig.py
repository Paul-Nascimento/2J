import pandas as pd
from omie import *
from zig import *
from new_produts import *


drinks =  ['VINHOS ROSE',
            'ESPUMANTES',
            'SOFT DRINKS',
            'DRINKS',
            'COQUETÉIS CLASSICOS',
            'DOSE',
            'CAIPI',
            'HAPPY HOUR (11:00 ÀS 21:00)',
            'GARRAFAS',
            'VINHOS TINTOS',
            'VINHOS BRANCOS','COQUETÉIS LOW','CACHAÇA','SHOTS']

cervejas_e_chopps = ['CERVEJAS','CHOPP']

alimentos = ['ACOMPANHAMENTOS',
          'CORTES DA CASA',
          'JUNINO',
          'BELISCOS DE BOTECO',
          'ESTUFA',
          'EXECUTIVO, (SEG A SEX, ALMOÇO) (ENTRADA, PRATO PRINCIPAL E SOBREMESA)',
          'COMIDA POPULAR BRASILEIRA',
          'KIDS','SOBREMESA','SALADA, O PATO QUER SER FIT','PARA COMPARTILHAR']



def identifica_tributacao(categoria):
    # Observações de formato exigidas pela API Omie:
    # - PIS/COFINS (cod_sit_trib_*): string de 2 dígitos, p.ex. "01", "04", "99"
    # - CFOP: string com ponto (ex.: "5.102", "5.405")
    # - CSOSN (ICMS do Simples): inteiro (ex.: 101, 102, 500)

    if categoria in cervejas_e_chopps:
        cfop = "5.405"     # 5405 -> "5.405"
        icms = 500         # CSOSN 500 (Substituição tributária / outros – ajuste se necessário)
        ncm = "22030000"
        piscofins = "04"   # era 4 -> usar "04" (duas casas)
    elif categoria in alimentos:
        cfop = "5.102"     # 5102 -> "5.102"
        icms = 102         # CSOSN 102
        piscofins = "99"   # Outras operações; ajuste conforme sua regra real
        ncm = "21069090"
    elif categoria in drinks:
        cfop = "5.405"     # 5405 -> "5.405"
        icms = 500
        piscofins = "99"
        ncm = "22089000"
    else:
        # fallback padronizado
        cfop = "5.405"
        icms = 500
        piscofins = "99"
        ncm = "22089000"

    return {
        "cfop": cfop,            # string com ponto, p.ex. "5.102"
        "icms": icms,            # CSOSN (int), p.ex. 101/102/500
        "piscofins": piscofins,  # CST PIS/COFINS como string "01"/"04"/"99"
        "ncm": ncm,
        "status": "ok",
    }


def rotina_produtos_zig(APP_KEY,APP_SECRET,REDE,TOKEN,email,senha,prefixo_empresa='PTF-',dias_retroativos=3):
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    lp_p2 = listar_produtos(APP_KEY, APP_SECRET, pagina=2, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")


    print(len(lp), len(lp_p2))
    produtos_cadastrados = []

    produtos_existentes = [str(prod['codigo']) for prod in lp['produto_servico_cadastro']]
    produtos_existentes_p2 = [str(prod['codigo']) for prod in lp_p2['produto_servico_cadastro']]

    print(produtos_existentes)

    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=dias_retroativos)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=dias_retroativos)).strftime("%Y-%m-%d")
    
    print(f"Consultando produtos do ZIG de {dtinicio} até {dtfim}")
    #produtos_totais = lp + lp_p2
    #print(produtos_existentes)
    contagem = 0
    #Fazer uma consulta dos produtos do ZIG no DIA

    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]

        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)
        
        for index, p in enumerate(consulta_zig):
            #print(f"Processando produto  {p}")
            
            codigo_produto = f'{prefixo_empresa}{p["productId"]}'
            if codigo_produto not in produtos_existentes and codigo_produto not in produtos_existentes_p2:
                print(f"Produto {p['productName']} (ID: {p['productId']}) não cadastrado. Pulando...")
                
                tributacao = identifica_tributacao(p['productCategory'])
                if tributacao.get('status') == 'erro':
                    #print(f"Erro ao identificar tributação: {tributacao.get('mensagem')}")
                    continue

                payload = {
                    "codigo_produto_integracao": codigo_produto,
                    "codigo": codigo_produto,
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
                    

                    contagem+=1 
                    #payload['productCategory'] = p['productCategory']
                    cd = incluir_produto(APP_KEY, APP_SECRET, payload)
                    produtos_cadastrados.append(payload)
                    time.sleep(2)  # Para evitar problemas de limite de requisições
                    print(f"Produto cadastrado: {payload['descricao']}")

                except Exception as e:
                    print(f"Erro ao cadastrar produto {payload['descricao']}: {e}")


        if len(produtos_cadastrados) > 0:
            import os
            DESTS = ["financeiropatinhofeio@gmail.com","lucca@2jbpo.com.br","samara@2jbpo.com.br"]
            DESTS = ['paulonascimento0910@gmail.com']
            #CC = ["gerente@empresa.com.br"]
            #SMTP_PASS = os.getenv("SMTP_PASS_PATINHO", "")

            
            print(email,senha)
            """
            send_product_creation_alert(
                destinatarios=DESTS,
                registros=produtos_cadastrados,
                smtp_user=email,
                smtp_password=senha,  # não exponha a senha no código
                remetente=f"Alertas Patinho Feio <{email}>",
                numero_pedido=None,
                previsao_faturamento=None,
                usar_starttls=True,
            )
            """
        print(f'Total cadastrado: {contagem}')

if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    #REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    #TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    #api = ZigAPI(REDE, TOKEN)

    #rotina_produtos_zig(APP_KEY,APP_SECRET,REDE,TOKEN,dias_retroativos=26)