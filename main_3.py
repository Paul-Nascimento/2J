from omie import *
from zig import *
import pprint
from decimal import Decimal, ROUND_HALF_UP

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
    if categoria in cervejas_e_chopps:
        cfop = 5405
        icms = 500
        ncm = '22030000'
        piscofins = 4
    elif categoria in alimentos:
        cfop = 5102
        icms = 102
        piscofins = 99
        ncm = '21069090'
    
    elif categoria in drinks:
        cfop = 5405
        icms = 500
        piscofins = 99
        ncm = '22089000'

    else:
        #return {"status": "erro", "mensagem": f"Categoria '{categoria}' não mapeada."}
        cfop = 5405
        icms = 500
        piscofins = 99
        ncm = '22089000'
    
    return {"cfop": cfop, "icms": icms, "piscofins": piscofins, "ncm":ncm, "status": "ok"}

def adicionando_produtos_omie(delay=1):
    'Recupera os produtos do Zig e adiciona na Omie se não existirem'
    
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=delay)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=delay)).strftime("%Y-%m-%d")

    #Listando produtos da Omie
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    produtos_existentes = [str(produto['descricao']).upper() for produto in lp['produto_servico_cadastro']]
    
    produtos_a_cadastrar = []
    erros_ao_cadastrar = []
        

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)

        for produto in consulta_zig:
            #descricao = produto.get("descricao", "").strip()
            if str(produto['productName']).upper() in produtos_existentes:
                print(f"Produto já existe: {produto}")
            else:
                produtos_a_cadastrar.append(produto)
                print(f"Produto a cadastrar: {produto}")
                print(f"O valor unitário é {produto['unitValue']} / 100")
                
                print(f'A categoria do produto é {produto["productCategory"]}')
                print(f'O nome do produto é {produto["productName"]}')
                tributacao = identifica_tributacao(produto['productCategory'])

                if tributacao['status'] == 'erro':
                    print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                    continue

                print(tributacao)

                produto = {
                    "codigo_produto_integracao": produto['productSku'],
                    "codigo": f'PROD{produto["productSku"]}',
                    "descricao": produto['productName'][:119],
                    "unidade": "UN",
                    "ncm": tributacao['ncm'],
                    "valor_unitario": produto['unitValue'] / 100,   
                    'cst_pis': tributacao['piscofins'],
                    'cst_cofins': tributacao['piscofins'],
                    'cfop': tributacao['cfop'],
                    'csosn_icms': tributacao['icms'],
                }


                try:
                    incluir_produto(APP_KEY, APP_SECRET, produto)
               
                    time.sleep(1)  # Para evitar problemas de limite de requisições
                    print(f"Produto cadastrado: {produto['descricao']}")
                except Exception as e:
                    print(f"Erro ao cadastrar produto {produto['descricao']}: {e}")
                    erros_ao_cadastrar.append((produto, str(e)))

        return produtos_a_cadastrar, erros_ao_cadastrar
    
def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

from decimal import Decimal, ROUND_HALF_UP

def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def consolidar_itens(itens, produtos_existentes_dict):
    """
    itens: lista de dicts no formato do exemplo.
    identifica_tributacao_func: função(categoria:str) -> {cfop, icms, piscofins, ncm, status}
    produtos_existentes_dict: dict {descricao_upper: codigo_produto} vindo do Omie.
      Ex.: { str(p['descricao']).upper(): p['codigo_produto'] for p in lp['produto_servico_cadastro'] }

    Retorna: lista consolidada com campos em português + tributação + codigo_produto.
    """
    consolidados_por_chave = {}

    for it in itens:
        # Normalizações e conversões
        descricao = (it.get('productName') or '').strip()[:119]
        descricao_upper = descricao.upper()
        sku = (it.get('productSku') or '').strip()

        valor_unitario = _to_money_cents(it.get('unitValue'))
        valor_desconto = _to_money_cents(it.get('discountValue'))
        quantidade = int(it.get('count') or 0)

        # Chave de agregação (mesmos produto+sku+preço+desconto)
        chave = (descricao, sku, valor_unitario, valor_desconto)

        if chave not in consolidados_por_chave:
            # Tributação pela categoria do item
            categoria = it.get('productCategory') or ''
            trib = identifica_tributacao(categoria)

            # Código do produto no Omie (por descrição)
            codigo_produto = produtos_existentes_dict.get(descricao_upper)

            consolidados_por_chave[chave] = {
                'descricao': descricao,
                'codigo_item_integracao': sku,
                'valor_unitario': float(valor_unitario),   # use Decimal se preferir
                'valor_desconto': float(valor_desconto),
                'quantidade': quantidade,
                'tipo_desconto': 'v',  # valor

                # Tributação
                'cfop': trib.get('cfop'),
                'icms': trib.get('icms'),
                'piscofins': trib.get('piscofins'),
                'ncm': trib.get('ncm'),
                'status_tributacao': trib.get('status'),

                # Código Omie
                'codigo_produto': codigo_produto
            }
        else:
            # soma quantidades
            consolidados_por_chave[chave]['quantidade'] += quantidade

    return list(consolidados_por_chave.values())



def cria_corpo_do_pedido_de_venda():
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    #lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    produtos_existentes = {
    str(produto['descricao']).upper(): produto['codigo_produto']
    for produto in lp['produto_servico_cadastro']
}
    pprint.pprint(produtos_existentes)

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]
    
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)
        
        d = consolidar_itens(consulta_zig,produtos_existentes)
        pprint.pprint(d)
        
        exit()
        for produto in consulta_zig:

            """com o --"descricao": produto['productName'][:119]-- buscar o produto na lista de produtos da Omie"""
            pprint.pprint(produto)
            
            tributacao = identifica_tributacao(produto['productCategory'])
            if tributacao['status'] == 'erro':
                print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                continue

            item = {
                "ide": {
                    "codigo_item_integracao": produto['productSku'] #Informar 1,2,3... para cada item do pedido
                },
                "inf_adic": {
                    "peso_bruto": 1,
                    "peso_liquido": 1
                },
                "produto": {
                    "cfop": tributacao['cfop'],
                    "codigo_produto": f'PROD{produto["productSku"]}',
                    "descricao": produto['productName'][:119],
                    "ncm": tributacao['ncm'],
                    "quantidade": produto['quantity'],
                    "unidade": "UN",
                    "tipo_desconto":"V",
                    "valor_desconto": 0,
                    "valor_unitario": produto['unitValue'] / 100
                }
            }
            #det.append(item)   

cria_corpo_do_pedido_de_venda()

exit()
if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")

    #categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #cc = listar_contas_correntes(APP_KEY,APP_SECRET,pagina=1,registros_por_pagina=100)
    #clientes = consultar_clientes(APP_KEY, APP_SECRET)

    #Listando produtos da Omie
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    produtos_existentes = [str(produto['descricao']).upper() for produto in lp['produto_servico_cadastro']]
    

    print(f'Café expresso está na lista? {"Café expresso" in produtos_existentes}')
    print(produtos_existentes)
    produtos_a_cadastrar = []
    erros_ao_cadastrar = []
        

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)
        #produtos_zig = list(set([produto['productName'] for produto in consulta_zig]))
        #produtos_zig = {p['productSku']: p['productName']:p['unitValue'] for p in consulta_zig}
        #print(produtos_zig)

        for produto in consulta_zig:
            #descricao = produto.get("descricao", "").strip()
            if str(produto['productName']).upper() in produtos_existentes:
                print(f"Produto já existe: {produto}")
            else:
                produtos_a_cadastrar.append(produto)
                print(f"Produto a cadastrar: {produto}")
                print(f"O valor unitário é {produto['unitValue']} / 100")
                
                print(f'A categoria do produto é {produto["productCategory"]}')
                print(f'O nome do produto é {produto["productName"]}')
                tributacao = identifica_tributacao(produto['productCategory'])

                if tributacao['status'] == 'erro':
                    print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                    continue

                print(tributacao)

                produto = {
                    "codigo_produto_integracao": produto['productSku'],
                    "codigo": f'PROD{produto["productSku"]}',
                    "descricao": produto['productName'][:119],
                    "unidade": "UN",
                    "ncm": tributacao['ncm'],
                    "valor_unitario": produto['unitValue'] / 100,   
                    'cst_pis': tributacao['piscofins'],
                    'cst_cofins': tributacao['piscofins'],
                    'cfop': tributacao['cfop'],
                    'csosn_icms': tributacao['icms'],
                }


                try:
                    incluir_produto(APP_KEY, APP_SECRET, produto)
               
                    time.sleep(1)  # Para evitar problemas de limite de requisições
                    print(f"Produto cadastrado: {produto['descricao']}")
                except Exception as e:
                    print(f"Erro ao cadastrar produto {produto['descricao']}: {e}")
                    erros_ao_cadastrar.append((produto, str(e)))

        import pandas as pd 

        df = pd.DataFrame(produtos_a_cadastrar)
        df.to_excel('produtos_a_cadastrar.xlsx')

        df_erros = pd.DataFrame(erros_ao_cadastrar, columns=['produto', 'erro'])
        df_erros.to_excel('erros_ao_cadastrar.xlsx')
                
        #lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")

        faturamento = api.get_faturamento(dtinicio, dtfim, loja_id)

        """det = [{
            
                "ide": {
                    "codigo_item_integracao": "1" #Informar 1,2,3... para cada item do pedido
                },
                "inf_adic": {
                    "peso_bruto": 1,
                    "peso_liquido": 1
                },
                
                }
        ]"""
        
        det = []
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)

        for produto in consulta_zig:
            tributacao = identifica_tributacao(produto['productCategory'])
            if tributacao['status'] == 'erro':
                print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                continue

            item = {
                "ide": {
                    "codigo_item_integracao": produto['productSku'] #Informar 1,2,3... para cada item do pedido
                },
                "inf_adic": {
                    "peso_bruto": 1,
                    "peso_liquido": 1
                },
                "produto": {
                    "cfop": tributacao['cfop'],
                    "codigo_produto": f'PROD{produto["productSku"]}',
                    "descricao": produto['productName'][:119],
                    "ncm": tributacao['ncm'],
                    "quantidade": produto['quantity'],
                    "unidade": "UN",
                    "tipo_desconto":"V",
                    "valor_desconto": 0,
                    "valor_unitario": produto['unitValue'] / 100
                }
            }
            det.append(item)        

        print(det)

        exit()
        
        pedido = {
            "cabecalho": {
                "codigo_cliente": 2483785544, # 'codigo_cliente_omie' na API ListarClientes
                "codigo_pedido_integracao": "19000003", #Esse valor vem do zig
                "data_previsao": "15/09/2025",
                "etapa": "10",
                "numero_pedido": "27450",
                "codigo_parcela": "999",
                "qtde_parcelas": 2,
                "origem_pedido": "API"
            },
            "det": [
                {
                "ide": {
                    "codigo_item_integracao": "1" #Informar 1,2,3... para cada item do pedido
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
                "tipo_desconto":"V",
                "valor_desconto": 0,
                "valor_unitario": 9381.09
                    }
                },

                    
                    
                ],
            "informacoes_adicionais": {
                "codigo_categoria": "1.01.01",
                "codigo_conta_corrente": 2483743038, #nCodCC na api ListarContasCorrentes
                "consumidor_final": "S",
                "enviar_email": "N"
            },
                
            "lista_parcelas": {
                "parcela": [
                {
                        "data_vencimento": "15/09/2025",
                        "numero_parcela": 1,
                        "percentual": 97.08,
                        "valor": 9107.49
                    },
                    {
                        "data_vencimento": "19/01/2026",
                        "numero_parcela": 2,
                        "percentual": 2.92,
                        "valor": 273.60
                    }
                ]
            }
            }

        #clientes = consultar_clientes(APP_KEY,APP_SECRET)
        #resposta = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)
