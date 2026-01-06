from omie import *
from zig import *
from datetime import datetime, timedelta
import time
import pandas as pd

# Categorias
drinks = [
    'VINHOS ROSE',
    'ESPUMANTES',
    'SOFT DRINKS',
    'DRINKS',
    'COQUETÉIS CLASSICOS',
    'DOSE',
    'CAIPI',
    'HAPPY HOUR (11:00 ÀS 21:00)',
    'GARRAFAS',
    'VINHOS TINTOS',
    'VINHOS BRANCOS','COQUETÉIS LOW','CACHAÇA','SHOTS'
]

cervejas_e_chopps = ['CERVEJAS','CHOPP']

alimentos = [
    'ACOMPANHAMENTOS',
    'CORTES DA CASA',
    'JUNINO',
    'BELISCOS DE BOTECO',
    'ESTUFA',
    'EXECUTIVO, (SEG A SEX, ALMOÇO) (ENTRADA, PRATO PRINCIPAL E SOBREMESA)',
    'COMIDA POPULAR BRASILEIRA',
    'KIDS','SOBREMESA','SALADA, O PATO QUER SER FIT','PARA COMPARTILHAR'
]

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
        return {"status": "erro", "mensagem": f"Categoria '{categoria}' não mapeada."}
    return {"cfop": cfop, "icms": icms, "piscofins": piscofins, "ncm": ncm, "status": "ok"}

if __name__ == "__main__":
    # Credenciais OMIE (mantidas como no arquivo original)
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    # ZIG
    REDE = "4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período de teste (mantido)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")

    # 1) Listar produtos existentes da Omie (base para checagem/mapeamento)
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    lista_cad = lp.get('produto_servico_cadastro', []) or []

    # Mapas para localizar produtos rapidamente
    map_desc_upper = {str(p.get('descricao', '')).upper(): p for p in lista_cad}
    map_integracao = {p.get('codigo_produto_integracao'): p for p in lista_cad if p.get('codigo_produto_integracao')}

    produtos_existentes = [str(p.get('descricao', '')).upper() for p in lista_cad]

    print(f'Café expresso está na lista? {"Café expresso".upper() in produtos_existentes}')
    print(produtos_existentes)

    produtos_a_cadastrar = []
    erros_ao_cadastrar = []

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Seleciona a primeira loja (mantido)
        loja_id = lojas[0]["id"]

        # 2) Buscar saídas (itens do ZIG)
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)

        # 3) Garantir que todos os produtos usados no ZIG existam na Omie
        for prod in consulta_zig:
            nome = str(prod.get('productName', '')).strip()
            nome_upper = nome.upper()
            sku = prod.get('productSku')
            categoria = prod.get('productCategory')

            # Se já existir por integração ou descrição, segue
            existe = False
            if sku and sku in map_integracao:
                existe = True
            elif nome_upper in map_desc_upper:
                existe = True

            if existe:
                print(f"Produto já existe na Omie: {sku} - {nome}")
                continue

            # Caso não exista, preparar inclusão
            print(f"Produto a cadastrar (ZIG): {sku} - {nome}")
            produtos_a_cadastrar.append(prod)

            print(f"O valor unitário é {prod.get('unitValue', 0)} / 100")
            print(f'A categoria do produto é {categoria}')
            print(f'O nome do produto é {nome}')

            tributacao = identifica_tributacao(categoria)
            if tributacao['status'] == 'erro':
                print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                continue

            print(tributacao)

            novo_produto = {
                "codigo_produto_integracao": sku,                       # chave de integração = SKU do ZIG
                "codigo": f'PROD{sku}',                                 # opcional/ilustrativo
                "descricao": nome[:119],
                "unidade": "UN",
                "ncm": tributacao['ncm'],
                "valor_unitario": (prod.get('unitValue', 0) or 0) / 100,
                "cst_pis": tributacao['piscofins'],
                "cst_cofins": tributacao['piscofins'],
                "cfop": tributacao['cfop'],
                "csosn_icms": tributacao['icms'],
            }

            try:
                incluir_produto(APP_KEY, APP_SECRET, novo_produto)
                time.sleep(1)  # evitar throttling
                print(f"Produto cadastrado na Omie: {novo_produto['descricao']}")
            except Exception as e:
                print(f"Erro ao cadastrar produto {novo_produto['descricao']}: {e}")
                erros_ao_cadastrar.append((novo_produto, str(e)))

        # 3.1) Export debug (mantido/adaptado)
        if produtos_a_cadastrar:
            pd.DataFrame(produtos_a_cadastrar).to_excel('produtos_a_cadastrar.xlsx', index=False)
        if erros_ao_cadastrar:
            pd.DataFrame(erros_ao_cadastrar, columns=['produto', 'erro']).to_excel('erros_ao_cadastrar.xlsx', index=False)

        # 4) Relistar produtos após possíveis inclusões, para termos códigos atualizados
        lp2 = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
        lista_cad2 = lp2.get('produto_servico_cadastro', []) or []
        map_desc_upper = {str(p.get('descricao', '')).upper(): p for p in lista_cad2}
        map_integracao = {p.get('codigo_produto_integracao'): p for p in lista_cad2 if p.get('codigo_produto_integracao')}

        # 5) (Opcional) Buscar dados de faturamento ZIG (mantido)
        faturamento = api.get_faturamento(dtinicio, dtfim, loja_id)

        # 6) Montagem dinâmica do pedido a partir dos itens do ZIG
        det = []
        codigo_item = 1

        for item in consulta_zig:
            nome = str(item.get('productName', '')).strip()
            nome_upper = nome.upper()
            sku = item.get('productSku')
            categoria = item.get('productCategory')
            qtd = item.get('quantity', 1) or 1
            unit_value = (item.get('unitValue', 0) or 0) / 100

            tributacao = identifica_tributacao(categoria)
            if tributacao['status'] == 'erro':
                print(f"Pulando item sem tributação mapeada: {nome}")
                continue

            # Tentar localizar o produto na Omie (preferência por integração -> descrição)
            prod_omie = None
            if sku and sku in map_integracao:
                prod_omie = map_integracao[sku]
            elif nome_upper in map_desc_upper:
                prod_omie = map_desc_upper[nome_upper]

            # Campos padrão do produto no pedido
            produto_pedido = {
                "cfop": str(tributacao['cfop']),
                "descricao": nome[:119],
                "ncm": tributacao['ncm'],
                "quantidade": qtd,
                "unidade": "UN",
                "tipo_desconto": "V",
                "valor_desconto": 0,
                "valor_unitario": unit_value
            }

            # Se soubermos o código do produto OMIE, incluímos
            if prod_omie:
                # Algumas contas usam 'codigo_produto'; outras aceitam 'codigo_produto_integracao'.
                # Priorizamos 'codigo_produto' quando disponível.
                if prod_omie.get('codigo_produto'):
                    produto_pedido["codigo_produto"] = prod_omie['codigo_produto']
                elif prod_omie.get('codigo_produto_integracao'):
                    produto_pedido["codigo_produto_integracao"] = prod_omie['codigo_produto_integracao']

            det.append({
                "ide": {
                    "codigo_item_integracao": str(codigo_item)  # 1,2,3...
                },
                "inf_adic": {
                    "peso_bruto": 1,
                    "peso_liquido": 1
                },
                "produto": produto_pedido
            })
            codigo_item += 1

        # 7) Cabeçalho e info adicionais do pedido (mantidos, com pequenos ajustes)
        pedido = {
            "cabecalho": {
                "codigo_cliente": 2483785544,                    # 'codigo_cliente_omie'
                "codigo_pedido_integracao": f"PZ-{hoje:%Y%m%d%H%M%S}",  # usa timestamp para evitar conflitos
                "data_previsao": (hoje.strftime("%d/%m/%Y")),
                "etapa": "10",
                "numero_pedido": "27450",                        # manter se necessário, ou omitir para auto
                "codigo_parcela": "999",
                "qtde_parcelas": 2,
                "origem_pedido": "API"
            },
            "det": det if det else [
                # Fallback: Se por algum motivo não houver det, mantém um item exemplo (igual ao original)
                {
                    "ide": {"codigo_item_integracao": "1"},
                    "inf_adic": {"peso_bruto": 1, "peso_liquido": 1},
                    "produto": {
                        "cfop": "5102",
                        "codigo_produto": "2514568647",
                        "descricao": "Produto Teste",
                        "ncm": "94033000",
                        "quantidade": 1,
                        "unidade": "UN",
                        "tipo_desconto": "V",
                        "valor_desconto": 0,
                        "valor_unitario": 9381.09
                    }
                }
            ],
            "informacoes_adicionais": {
                "codigo_categoria": "1.01.01",
                "codigo_conta_corrente": 2483743038,  # nCodCC - ListarContasCorrentes
                "consumidor_final": "S",
                "enviar_email": "N"
            },
            "lista_parcelas": {
                "parcela": [
                    {
                        "data_vencimento": hoje.strftime("%d/%m/%Y"),
                        "numero_parcela": 1,
                        "percentual": 97.08,
                        "valor": 9107.49
                    },
                    {
                        "data_vencimento": (hoje + timedelta(days=126)).strftime("%d/%m/%Y"),
                        "numero_parcela": 2,
                        "percentual": 2.92,
                        "valor": 273.60
                    }
                ]
            }
        }

        # 8) Envio do pedido (mantido como comentário, igual ao original)
        # resposta = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)
        # print(resposta)

