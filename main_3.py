from datetime import datetime, timedelta
from omie import *
from zig import *
import pprint
from datetime import datetime
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

def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def consolidar_itens_(itens, produtos_existentes_dict):
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
        chave = (descricao)

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

def consolidar_itens_para_det(itens_zig, produtos_existentes_dict, unidade_padrao="UN"):
    """
    itens_zig: lista vinda do ZIG (productId, productName, productSku, unitValue, discountValue, count, productCategory)
    produtos_existentes_dict: dict { codigo(Omie) -> codigo_produto(Omie) }, ex. {"PRODTESTE123": 2487654321}

    Busca no Omie pelo codigo = 'PRODTESTE{productId}'.
    """
    consolidados_por_chave = {}

    for it in itens_zig or []:
        product_id = it.get('productId')
        if product_id is None:
            continue

        # descricao como você vinha cadastrando (mantive o hífen final para aderir ao seu padrão de cadastro)
        descricao = f"{(it.get('productName') or '')[:105]}-"
        sku = it.get('productSku') or ''

        # valores
        valor_unitario = _to_money_cents(it.get('unitValue'))
        valor_desconto = _to_money_cents(it.get('discountValue'))
        if valor_unitario <= 0:
            continue

        quantidade = int(it.get('count') or 0)
        categoria = it.get('productCategory') or ''
        trib = identifica_tributacao(categoria) or {}

        # chave de agregação pelo PRODTESTE{productId} (evita colisão por descrição)
        codigo_omie = f"PRODTESTE{product_id}"
        chave = (codigo_omie,)

        # lookup seguro {codigo -> codigo_produto}
        codigo_produto = produtos_existentes_dict.get(codigo_omie.upper()) \
                         or produtos_existentes_dict.get(codigo_omie) \
                         or ""

        if chave not in consolidados_por_chave:
            consolidados_por_chave[chave] = {
                # base
                'descricao': descricao,
                'sku': sku,
                'valor_unitario': float(valor_unitario),
                'valor_desconto': float(valor_desconto),
                'quantidade': quantidade,
                'unidade': unidade_padrao,

                # tributação
                'cfop': trib.get('cfop'),
                'icms': trib.get('icms'),
                'piscofins': trib.get('piscofins'),
                'ncm': trib.get('ncm'),
                'status_tributacao': trib.get('status'),

                # Omie
                'codigo_produto': codigo_produto,  # string vazia se não achar
            }
        else:
            consolidados_por_chave[chave]['quantidade'] += quantidade
            consolidados_por_chave[chave]['valor_desconto'] += float(valor_desconto)

    # monta 'det'
    det = []
    for idx, item in enumerate(consolidados_por_chave.values(), start=1):
        det.append({
            "ide": {"codigo_item_integracao": str(idx)},
            "inf_adic": {"peso_bruto": 1, "peso_liquido": 1},
            "produto": {
                "cfop": str(item.get("cfop") or ""),
                "codigo_produto": str(item.get("codigo_produto") or ""),  # evita None
                "descricao": item.get("descricao") or "",
                "ncm": str(item.get("ncm") or ""),
                "quantidade": int(item.get("quantidade") or 0),
                "unidade": item.get("unidade") or unidade_padrao,
                "tipo_desconto": "V",
                "valor_desconto": float(item.get("valor_desconto") or 0.0),
                "valor_unitario": float(item.get("valor_unitario") or 0.0),
            }
        })

    return det



import unicodedata
from typing import List, Dict, Any
from datetime import datetime

# --- helpers (mantenha apenas se não existirem no seu arquivo) ---
def _norm(texto: str) -> str:
    """Normaliza string: remove acentos, upper e trim."""
    if texto is None:
        return ""
    return unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("ASCII").upper().strip()

def _cents_to_real(v: int) -> float:
    return round((v or 0) / 100.0, 2)

def _fmt_br_date_from_iso(iso: str) -> str:
    """'2025-09-21T14:45:42.223Z' -> '21/09/2025'"""
    try:
        iso = (iso or "").replace("Z", "")
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return ""

# --- de-para ZIG -> OMIE (normalizado sem acentos) ---
_DEPARA_ZIG_OMIE = {
    "CREDITO": "03",
    "DEBITO": "04",
    "DINHEIRO": "01",
    "PIX": "17",
    "APP": "18",
    "AME": "18",
    "MBWAY": "18",
    "VOUCHER": "12",
    "VOUCHER INTEGRADO": "12",
    "ANTECIPADO": "16",
    "BONUS": "19",  # usado só para totais, NÃO gera parcela
    "NOTAS MANUAIS + SERVICO": "99",
    "RECARGAS DEVOLVIDAS": "99",
    "OUTROS": "99",
    "DELIVERY ONLINE": "99",
    "IFOOD": "99",
    "RAPPI": "99",
    "UBER": "99",
}

def _map_meio_pagamento(payment_name: str) -> str:
    """Mapeia paymentName da ZIG para código OMIE, com fallback para '99' (Outros)."""
    key = _norm(payment_name)
    return _DEPARA_ZIG_OMIE.get(key, "99")

from typing import List, Dict, Any

def montar_lista_parcelas(
    faturamento: List[Dict[str, Any]],
    produtos: List[Dict[str, Any]],
    data_vencimento: str,
) -> Dict[str, Any]:
    """
    Gera as parcelas para o Omie e calcula internamente os totais/consolidações.

    Regras adicionais:
      • NÃO gerar parcelas para 'BÔNUS/BONUS'.
      • 'Valores em aberto' (se > 0) vira uma parcela com meio_pagamento='99' (Outros).
      • Nenhuma parcela pode ficar com percentual 0,00% (se ficar, não é listada).
      • Os percentuais das parcelas listadas devem fechar 100,00%.
    """

    # ----------------- consolidação de produtos -----------------
    total_bruto_produtos_cents = 0
    total_descontos_produtos_cents = 0
    gorjeta_total_cents = 0
    produtos_por_desc_cents: Dict[str, Dict[str, int]] = {}

    for it in produtos or []:
        desc = (it.get("productName") or "").strip()
        desc_norm = _norm(desc)
        unit_cents = int(it.get("unitValue") or 0)
        disc_cents = int(it.get("discountValue") or 0)
        qtd = int(it.get("count") or 0)

        bruto_cents = unit_cents * qtd
        liquido_cents = bruto_cents - disc_cents

        total_bruto_produtos_cents += bruto_cents
        total_descontos_produtos_cents += disc_cents

        if "GORJET" in desc_norm:
            gorjeta_total_cents += liquido_cents

        agg = produtos_por_desc_cents.setdefault(desc, {
            "quantidade": 0,
            "valor_bruto_cents": 0,
            "desconto_cents": 0,
            "valor_liquido_cents": 0,
        })
        agg["quantidade"] += qtd
        agg["valor_bruto_cents"] += bruto_cents
        agg["desconto_cents"] += disc_cents
        agg["valor_liquido_cents"] += liquido_cents

    total_liquido_produtos_cents = total_bruto_produtos_cents - total_descontos_produtos_cents

    # ----------------- consolidação de faturamento -----------------
    fat_por_payment_cents: Dict[str, int] = {}
    faturamento_das_maquinas_cents = 0
    bonus_total_cents = 0

    componentes = []
    pagamentos_validos = []  # para gerar parcelas (exclui BONUS)
    for p in faturamento or []:
        val = int(p.get("value") or 0)
        if val <= 0:
            continue

        pay_name = (p.get("paymentName") or "").strip()
        pay_norm = _norm(pay_name)

        # totais (todos os pagamentos > 0, inclusive BONUS)
        fat_por_payment_cents[pay_name] = fat_por_payment_cents.get(pay_name, 0) + val
        faturamento_das_maquinas_cents += val

        # BONUS não vira parcela
        if "BONUS" in pay_norm:
            bonus_total_cents += val

            componentes.append({
            "valor_cents": int(val),
            "meio_pagamento": '90',
            "dv": data_vencimento,
        })
        else:
            pagamentos_validos.append(p)

    # métricas
    faturamento_real_cents = faturamento_das_maquinas_cents - gorjeta_total_cents
    valores_em_aberto_cents = total_liquido_produtos_cents - gorjeta_total_cents - faturamento_real_cents
    # receita = faturamento_das_maquinas_cents - bonus_total_cents  # (disponível se precisar)

    # ----------------- componentes que viram parcelas -----------------
    
    for p in pagamentos_validos:
        componentes.append({
            "valor_cents": int(p.get("value") or 0),
            "meio_pagamento": _map_meio_pagamento(p.get("paymentName")),
            "dv": data_vencimento,
        })

    # 'Valores em aberto' também vira parcela e DEVE compor os 100%
    if valores_em_aberto_cents > 0:

        componentes.append({
            "valor_cents": int(valores_em_aberto_cents),
            "meio_pagamento": "99",  # Outros
            "dv": data_vencimento,
        })

    # Se nada para parcelar, retorna vazio
    if not componentes:
        return {"parcela": []}

    total_para_percent_cents = sum(c["valor_cents"] for c in componentes)
    if total_para_percent_cents <= 0:
        return {"parcela": []}

    # ----------------- calcular percentuais e montar retorno -----------------
    parcelas = []
    percentuais = []

    idx = 0
    for comp in componentes:
        val_cents = comp["valor_cents"]
        if val_cents <= 0:
            continue
        perc = round((val_cents / total_para_percent_cents) * 100.0, 2)

        # regra: se percentual ficar 0,00% após arredondamento, não lista
        if perc <= 0.0:
            continue

        idx += 1
        parcela = {
            "data_vencimento": comp["dv"],
            "numero_parcela": idx,
            "percentual": perc,  # ajuste final abaixo
            "valor": _cents_to_real(val_cents),
            "meio_pagamento": comp["meio_pagamento"],
        }
        parcelas.append(parcela)
        percentuais.append(perc)

    # garantir soma dos percentuais = 100,00%
    if parcelas:
        soma_perc = round(sum(percentuais), 2)
        diff = round(100.00 - soma_perc, 2)
        parcelas[-1]["percentual"] = round(parcelas[-1]["percentual"] + diff, 2)

    return {"parcela": parcelas}

# PIPELINE DE TESTE

def cria_corpo_do_pedido_de_venda(days):
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=days)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=days)).strftime("%Y-%m-%d")

    dtvencimento = (hoje - timedelta(days=days - 1)).strftime("%d/%m/%Y")
    dtajustada = (hoje - timedelta(days=days)).strftime("%d/%m/%Y")
    #lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    
    
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")

    import pandas as pd
    df = pd.DataFrame(lp['produto_servico_cadastro'])

    df.to_excel('Listagem de produtos OMIE.xlsx')

    exit()
    
    produtos_existentes_por_codigo = {
    str(p['codigo']).strip().upper(): p['codigo_produto']
        for p in lp['produto_servico_cadastro']
    }
    pprint.pprint(produtos_existentes_por_codigo)
    
    

    
    import pandas as pd 

    df = pd.DataFrame(lp['produto_servico_cadastro'])
    #df.to_excel('produtosssss.xlsx')

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]
    
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)
        
        d = consolidar_itens_para_det(consulta_zig,produtos_existentes_por_codigo)
        
        faturamento = api.get_faturamento(dtinicio, dtfim, loja_id)
        
        print(faturamento)

        lista = montar_lista_parcelas(faturamento,produtos=consulta_zig,data_vencimento=dtajustada)
        parcelas = montar_lista_parcelas(faturamento,produtos=consulta_zig,data_vencimento=dtvencimento)


        print(parcelas)
    
  
    
        pedido = {
            "cabecalho": {
                "codigo_cliente": 2483785544, # 'codigo_cliente_omie' na API ListarClientes
                "codigo_pedido_integracao": "19000016", #Esse valor vem do zig
                "data_previsao": dtajustada, #Mesma data do faturamento
                "etapa": "10",
                "numero_pedido": "27467", #Campo dinâmico
                "codigo_parcela": "999",
                "qtde_parcelas": len(parcelas['parcela']),
                "origem_pedido": "API"
            },
            "det": d,
            "informacoes_adicionais": {
                "codigo_categoria": "1.01.01",
                "codigo_conta_corrente": 2514366910, #nCodCC na api ListarContasCorrentes
                "consumidor_final": "S",
                "enviar_email": "N"
            },
                
            "lista_parcelas": parcelas
            } 

        print(d)
        resposta = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)

        print(resposta)


if __name__ == "__main__":
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    #ZIG    

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    api = ZigAPI(REDE, TOKEN)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    days = 2
    dtfim = (hoje - timedelta(days=days)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=days)).strftime("%Y-%m-%d")
    dtvencimento = (hoje - timedelta(days=days - 1)).strftime("%Y-%m-%d")

    #categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
    #cc = listar_contas_correntes(APP_KEY,APP_SECRET,pagina=1,registros_por_pagina=100)
    #clientes = consultar_clientes(APP_KEY, APP_SECRET)

    #Listando produtos da Omie
    lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
    produtos_existentes = [str(produto['codigo']) for produto in lp['produto_servico_cadastro']] #Filtrar pelo codigo_produto e codigo_produto_integracao
    

    pprint.pprint(produtos_existentes)
    produtos_a_cadastrar = []
    erros_ao_cadastrar = []
        

    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
    else:
        #print(f"Lojas encontradas: {len(lojas)}")

        # Escolhe a primeira loja para os próximos testes
        loja_id = lojas[0]["id"]
        consulta_zig = api.get_saida_produtos(dtinicio, dtfim, loja_id)

        pprint.pprint(consulta_zig)
        
        #produtos_zig = list(set([produto['productName'] for produto in consulta_zig]))
        #produtos_zig = {p['productSku']: p['productName']:p['unitValue'] for p in consulta_zig}
        #print(produtos_zig)
        
        r"""
        for produto in consulta_zig: #Diminuir essa consulta aqui
            #descricao = produto.get("descricao", "").strip()
            if f"PRODTESTE{str(produto['productId'])}".upper() in produtos_existentes:
                print(f"Produto já existe: {produto}")
            else:
                produtos_a_cadastrar.append(produto)
                tributacao = identifica_tributacao(produto['productCategory'])

                if tributacao['status'] == 'erro':
                    print(f"Erro ao identificar tributação: {tributacao['mensagem']}")
                    continue

    

                produto = {
                    "codigo_produto_integracao": f'PRODTESTE{produto["productId"]}',
                    "codigo": f'PRODTESTE{produto["productId"]}',
                    "descricao": f"{produto['productName'][:105]}-",
                    "unidade": "UN",
                    "ncm": tributacao['ncm'],
                    "valor_unitario": produto['unitValue'] / 100,   
                    'cst_pis': tributacao['piscofins'],
                    'cst_cofins': tributacao['piscofins'],
                    'cfop': tributacao['cfop'],
                    'csosn_icms': tributacao['icms'],
                }


                try:
                    print(f'Cadastrando produto {produto}')
                    
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
        """    
        cria_corpo_do_pedido_de_venda(days=days)
