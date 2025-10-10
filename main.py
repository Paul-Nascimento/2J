from datetime import datetime, timedelta
from omie import *
from zig import *
import pprint
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import unicodedata
from typing import List, Dict, Any
from datetime import datetime



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


def _to_money_cents(valor):
    """Converte inteiro/None para Decimal em reais (divide por 100) com 2 casas."""
    v = Decimal(int(valor or 0)) / Decimal(100)
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def consolidar_itens_para_det_(itens_zig, produtos_existentes_dict, unidade_padrao="UN"):
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


def consolidar_itens_para_det(itens_zig, produtos_existentes_dict, unidade_padrao="UN"):
    """
    itens_zig: lista vinda do ZIG (productId, productName, productSku, unitValue, discountValue, count, productCategory)
    produtos_existentes_dict: dict { codigo(Omie) -> codigo_produto(Omie) }, ex. {"PRODTESTE123": 2487654321}

    Busca no Omie pelo codigo = 'PRODTESTE{productId}'.
    """
    consolidados_por_chave = {}

    for it in (itens_zig or []):
        product_id = it.get('productId')
        if product_id is None:
            continue

        # descrição (mantém hífen ao final para aderir ao seu padrão)
        descricao = f"{(it.get('productName') or '')[:105]}-"
        sku = it.get('productSku') or ''

        # valores (em cents na origem -> manter em cents na consolidação, converter para reais no det)
        valor_unitario_cents = _to_money_cents(it.get('unitValue'))
        valor_desconto_cents = _to_money_cents(it.get('discountValue'))
        if (valor_unitario_cents or 0) <= 0:
            continue

        quantidade = int(it.get('count') or 0)
        if quantidade <= 0:
            continue

        categoria = it.get('productCategory') or ''
        trib = identifica_tributacao(categoria) or {}
        if trib.get('status') == 'erro':
            # Se não houver mapeamento tributário, pode optar por continuar/registrar log
            # print(f"[SKIP] Tributação não mapeada: {descricao} -> {trib.get('mensagem')}")
            continue

        # chave de agregação por PRODTESTE{productId}
        codigo_omie = f"PRODTESTE{product_id}"
        chave = (codigo_omie,)

        # lookup seguro {codigo -> codigo_produto} (aceita key normal e upper)
        codigo_produto = (
            produtos_existentes_dict.get(codigo_omie)
            or produtos_existentes_dict.get(str(codigo_omie).upper())
            or ""
        )

        if chave not in consolidados_por_chave:
            consolidados_por_chave[chave] = {
                # base
                'descricao': descricao,
                'sku': sku,
                'valor_unitario_cents': int(valor_unitario_cents or 0),
                'valor_desconto_cents': int(valor_desconto_cents or 0),
                'quantidade': quantidade,
                'unidade': unidade_padrao,

                # tributação
                'cfop': trib.get('cfop'),
                'icms': trib.get('icms'),           # CSOSN (p/ Simples). Se não for SN, ajuste no envio.
                'piscofins': trib.get('piscofins'), # usar mesmo código para PIS/COFINS conforme sua função
                'ncm': trib.get('ncm'),
                'status_tributacao': trib.get('status'),

                # Omie
                'codigo_produto': codigo_produto,   # string vazia se não achar
                'codigo_omie': codigo_omie,
            }
        else:
            item = consolidados_por_chave[chave]
            item['quantidade'] += quantidade
            item['valor_desconto_cents'] += int(valor_desconto_cents or 0)

    # monta 'det' (converter cents -> reais aqui)
    det = []
    for index,item in enumerate(consolidados_por_chave.values()):
        valor_unitario = (item.get("valor_unitario_cents") or 0)
        valor_desconto = (item.get("valor_desconto_cents") or 0)
        quantidade = int(item.get("quantidade") or 0)

        # preferir vincular pelo codigo_produto; se não existir, usar codigo_produto_integracao
        produto_block = {
            "descricao": item.get("descricao") or "",
            "unidade": item.get("unidade") or unidade_padrao,
            "quantidade": quantidade,
            "tipo_desconto": "V",
            "valor_desconto": float(valor_desconto),
            "valor_unitario": float(valor_unitario),
            "cfop": str(item.get("cfop") or ""),
            "ncm": str(item.get("ncm") or ""),
        }
        if item.get("codigo_produto"):
            produto_block["codigo_produto"] = str(item["codigo_produto"])
        else:
            produto_block["codigo_produto_integracao"] = str(item.get("codigo_omie") or "")

        det.append({
            "ide": {
                # use o código de integração do item = mesmo PRODTESTE{productId} para rastreabilidade
                "codigo_item_integracao": str(index),
                # se de fato for Simples Nacional, marque; caso contrário, remova este campo
                "simples_nacional": "S",
            },
            "inf_adic": {"peso_bruto": 1, "peso_liquido": 1},
            "produto": produto_block,
            "imposto": {
                # ICMS do Simples Nacional (CSOSN). Se não for SN, troque para bloco 'icms'.
                "icms_sn": {
                    "cod_sit_trib_icms_sn": int(item.get("icms") or 0),
                },
                "pis_padrao": {
                    "cod_sit_trib_pis": str(item.get("piscofins") or ""),
                },
                "cofins_padrao": {
                    "cod_sit_trib_cofins": str(item.get("piscofins") or ""),
                },
                # Se precisar IPI, acrescente aqui:
                # "ipi": { "cod_sit_trib_ipi": 51, ... }
            },
        })

    return det




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
    "BONUS": "99",  # usado só para totais, NÃO gera parcela
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

def montar_lista_parcelas_(
    faturamento: List[Dict[str, Any]],
    produtos: List[Dict[str, Any]],   # mantido na assinatura por compatibilidade, mas não é usado
    data_vencimento: str,
) -> Dict[str, Any]:
    """
    Simplificado:
      • Apenas converte os pagamentos de 'faturamento' em parcelas.
      • NÃO gera parcelas para 'BÔNUS/BONUS'.
      • Ignora completamente 'produtos', gorjeta e 'valores em aberto'.
      • Nenhuma parcela com percentual 0,00%.
      • Percentuais somam 100,00% (ajuste na última).
    """
    if not faturamento:
        return {"parcela": []}

    # Filtra pagamentos válidos (> 0) e exclui BONUS
    componentes = []
    for p in faturamento:
        val = int(p.get("value") or 0)
        if val <= 0:
            continue
        pay_name = (p.get("paymentName") or "").strip()
        pay_norm = (pay_name or "").upper().replace("Ç", "C")
        #if "BONUS" in pay_norm:   # não entra como parcela
        #    continue

        componentes.append({
            "valor_cents": val,
            "meio_pagamento": _map_meio_pagamento(pay_name),
            "dv": data_vencimento,
        })

    if not componentes:
        return {"parcela": []}

    total_cents = sum(c["valor_cents"] for c in componentes)
    if total_cents <= 0:
        return {"parcela": []}

    # Monta parcelas com percentuais proporcionais
    parcelas = []
    percentuais = []
    idx = 0
    for comp in componentes:
        val_cents = comp["valor_cents"]
        if val_cents <= 0:
            continue

        perc = round((val_cents / total_cents) * 100.0, 2)
        if perc <= 0.0:
            continue

        idx += 1
        parcela = {
            "data_vencimento": comp["dv"],
            "numero_parcela": idx,
            "percentual": perc,  # ajustado ao final
            "valor": _cents_to_real(val_cents),
            "meio_pagamento": comp["meio_pagamento"],
        }
        parcelas.append(parcela)
        percentuais.append(perc)

    # Ajuste para fechar exatamente 100,00%
    if parcelas:
        soma = round(sum(percentuais), 2)
        diff = round(100.00 - soma, 2)
        parcelas[-1]["percentual"] = round(parcelas[-1]["percentual"] + diff, 2)


    #Total dos produtos - desconto - total recebido



    return {"parcela": parcelas}
# PIPELINE DE TESTE

def montar_lista_parcelas_(
    faturamento: List[Dict[str, Any]],
    produtos: List[Dict[str, Any]],   # mantido na assinatura por compatibilidade
    data_vencimento: str,
) -> Dict[str, Any]:
    """
    Simplificado:
      • Converte os pagamentos de 'faturamento' em parcelas.
      • (Novo) Se houver saldo a receber = total_produtos_liquido - total_faturado,
        cria mais uma parcela com meio_pagamento='99'.
      • Nenhuma parcela com percentual 0,00%.
      • Percentuais somam 100,00% (ajuste na última).
    """
    if not faturamento:
        faturamento = []

    # 1) Filtra pagamentos válidos (>0)
    componentes = []
    for p in faturamento:
        val = int(p.get("value") or 0)
        if val <= 0:
            continue
        pay_name = (p.get("paymentName") or "").strip()
        # pay_norm = (pay_name or "").upper().replace("Ç", "C")
        # if "BONUS" in pay_norm:   # se quiser excluir bônus, reative
        #     continue

        componentes.append({
            "valor_cents": val,
            "meio_pagamento": _map_meio_pagamento(pay_name),
            "dv": data_vencimento,
        })

    # 2) Calcula total faturado
    total_faturado_cents = sum(c["valor_cents"] for c in componentes)

    # 3) Calcula total líquido dos produtos (unit * qtd - desconto), tudo em cents
    total_produtos_liquido_cents = 0
    for it in (produtos or []):
        unit_cents = int(it.get("unitValue") or 0)
        disc_cents = int(it.get("discountValue") or 0)
        qtd = int(it.get("count") or 0)
        bruto = unit_cents * qtd
        liquido = bruto - disc_cents
        total_produtos_liquido_cents += max(liquido, 0)

    # 4) Se houver saldo (produtos - faturado) > 0, cria componente '99'
    restante_cents = total_produtos_liquido_cents - total_faturado_cents
    if restante_cents > 0:
        componentes.append({
            "valor_cents": int(restante_cents),
            "meio_pagamento": "99",  # Outros
            "dv": data_vencimento,
        })

    if not componentes:
        return {"parcela": []}

    total_cents = sum(c["valor_cents"] for c in componentes)
    if total_cents <= 0:
        return {"parcela": []}

    # 5) Monta parcelas com percentuais proporcionais
    parcelas = []
    percentuais = []
    idx = 0
    for comp in componentes:
        val_cents = comp["valor_cents"]
        if val_cents <= 0:
            continue

        perc = round((val_cents / total_cents) * 100.0, 2)
        if perc <= 0.0:
            continue

        idx += 1
        parcela = {
            "dv": comp["dv"],
            "numero_parcela": idx,
            "percentual": perc,  # ajustado ao final
            "valor": _cents_to_real(val_cents),
            "meio_pagamento": comp["meio_pagamento"],
        }
        parcelas.append(parcela)
        percentuais.append(perc)

    # 6) Ajuste para fechar exatamente 100,00%
    if parcelas:
        soma = round(sum(percentuais), 2)
        diff = round(100.00 - soma, 2)
        parcelas[-1]["percentual"] = round(parcelas[-1]["percentual"] + diff, 2)


    print(parcelas)
    
    return {"parcela": parcelas}

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any

def montar_lista_parcelas(
    faturamento: List[Dict[str, Any]],
    produtos: List[Dict[str, Any]],   # mantido na assinatura por compatibilidade
    data_vencimento: str,
) -> Dict[str, Any]:
    """
    Gera parcelas com percentuais de até 6 casas decimais,
    mantendo o fechamento exato em 100.000000%.
    """

    parcelas = []
    for item in faturamento or []:
        valor = int(item.get("value", 0))
        if valor > 0:
            pay_name = (item.get("paymentName") or "").strip()
            parcelas.append({
                "valor": valor / 100,  # em reais
                "meio_pagamento": _map_meio_pagamento(pay_name),
                "data_vencimento": data_vencimento,
            })

    if not parcelas:
        return None

    # ---------- cálculo dos percentuais ----------
    total_geral = sum(p["valor"] for p in parcelas)
    total_decimal = Decimal(str(total_geral))

    # Percentuais com 6 casas decimais
    percentuais = []
    for p in parcelas:
        perc = (Decimal(str(p["valor"])) / total_decimal) * Decimal("100")
        perc = perc.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        percentuais.append(perc)

    soma_perc = sum(percentuais)
    delta = Decimal("100.000000") - soma_perc

    # Ajuste do delta para fechar 100.000000%
    if delta != 0:
        idx_maior = max(range(len(parcelas)), key=lambda i: parcelas[i]["valor"])
        percentuais[idx_maior] = (percentuais[idx_maior] + delta).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    # ---------- atribui valores finais ----------
    for i, (p, perc) in enumerate(zip(parcelas, percentuais), start=1):
        p["numero_parcela"] = i
        p["percentual"] = float(perc)  # mantém até 6 casas, ex: 33.333333

    return {"parcela": parcelas}



def cria_corpo_do_pedido_de_venda(days,codigo_pedido_integracao, numero_pedido):
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

    
    
    produtos_existentes_por_codigo = {
    str(p['codigo']).strip().upper(): p['codigo_produto']
        for p in lp['produto_servico_cadastro']
    }
    pprint.pprint(produtos_existentes_por_codigo)
    


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
        produtos = pd.DataFrame(consulta_zig)
        
        
        d = consolidar_itens_para_det(consulta_zig,produtos_existentes_por_codigo)
        
        faturamento = api.get_faturamento(dtinicio, dtfim, loja_id)
        df_faturamento = pd.DataFrame(faturamento)
        
        print(faturamento)

        lista = montar_lista_parcelas(faturamento,produtos=consulta_zig,data_vencimento=dtajustada)
        parcelas = montar_lista_parcelas(faturamento,produtos=consulta_zig,data_vencimento=dtvencimento)

        if parcelas is None:
            print("Nenhuma parcela gerada, pulando...")
            return None
        

        df_parcelas = pd.DataFrame(parcelas)
        df_faturamento.to_excel('faturamento.xlsx')
        produtos.to_excel('produtos.xlsx')
        df_parcelas.to_excel('parcelas.xlsx')
        
        pedido = {
            "cabecalho": {
                "codigo_cliente": 2483785544, # 'codigo_cliente_omie' na API ListarClientes
                "codigo_pedido_integracao": str(codigo_pedido_integracao), #Esse valor vem do zig
                "data_previsao": dtajustada, #Mesma data do faturamento
                "etapa": "10",
                "numero_pedido": str(numero_pedido), #Campo dinâmico
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

    codigo_pedido_integracao = 19000001
    pedido = 2740001

    for day in range(34,10,-1):
        dtfim = (hoje - timedelta(days=day)).strftime("%Y-%m-%d")
        dtinicio = (hoje - timedelta(days=day)).strftime("%Y-%m-%d")
        dtvencimento = (hoje - timedelta(days=day - 1)).strftime("%Y-%m-%d")

        #categorias = listar_categorias(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=100)
        #cc = listar_contas_correntes(APP_KEY,APP_SECRET,pagina=1,registros_por_pagina=100)
        #clientes = consultar_clientes(APP_KEY, APP_SECRET)

        #Listando produtos da Omie
        lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=800, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
        produtos_existentes = [produto['codigo'] for produto in lp['produto_servico_cadastro']] #Filtrar pelo codigo_produto e codigo_produto_integracao
        
        
        print(f'Quantidade de produtos listados {len(produtos_existentes)}')
        
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

    
            
            #produtos_zig = list(set([produto['productName'] for produto in consulta_zig]))
            #produtos_zig = {p['productSku']: p['productName']:p['unitValue'] for p in consulta_zig}
            #print(produtos_zig)
        
            # 1) Verificar todos e montar candidatos a registrar
            candidatos = []
            produtos_a_cadastrar = []  # mantém para compatibilidade/inspeção
            

            # normaliza o conjunto de existentes para comparação estável

            
            r"""
            for p in (consulta_zig):  # Diminuir essa consulta aqui
                codigo = f"PRODTESTE{p['productId']}"
                

                if codigo in produtos_existentes:
                    #print(f"Produto já existe: {p} - {codigo_norm}")
                    ...
                    
                else:
                    print(produtos_existentes)
                    print(f"produto não existe {codigo}")
                    
                    candidatos.append(p)            # lista "bruta" (pode ter duplicados)
                    produtos_a_cadastrar.append(p)  # mantém a lista original para depuração

            # 2) Remover duplicados preservando ordem (chave = codigo PRODTESTE)
            vistos = set()
            candidatos_unicos = []
            for p in candidatos:
                cod = f"PRODTESTE{p['productId']}"
                if cod in vistos:
                    continue
                vistos.add(cod)
                candidatos_unicos.append(p)

            # 3) Registrar cada produto uma única vez

            print(candidatos_unicos)
            print(len(candidatos_unicos))
            
            for p in candidatos_unicos:
                tributacao = identifica_tributacao(p['productCategory'])
                if tributacao.get('status') == 'erro':
                    print(f"Erro ao identificar tributação: {tributacao.get('mensagem')}")
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
                    print(p["productId"] in produtos_existentes)
                    incluir_produto(APP_KEY, APP_SECRET, payload)
                    time.sleep(1)  # Para evitar problemas de limite de requisições
                    print(f"Produto cadastrado: {payload['descricao']}")

                    # opcional: atualiza o conjunto local para evitar reprocesso em execuções contínuas
                    #_existentes_norm.add(payload["codigo"])

                    # se quiser, pode postergar um refresh completo da lista do Omie para após o loop
                    # lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=800,
                    #                      apenas_importado_api="N", filtrar_apenas_omiepdv="N")
                    # produtos_existentes = [str(prod['codigo']) for prod in lp['produto_servico_cadastro']]

                except Exception as e:
                    print(f"Erro ao cadastrar produto {payload['descricao']}: {e}")
                    erros_ao_cadastrar.append((payload, str(e)))

            
            """
            import pandas as pd 

            df = pd.DataFrame(produtos_a_cadastrar)
            df.to_excel('produtos_a_cadastrar.xlsx')

            df_erros = pd.DataFrame(erros_ao_cadastrar, columns=['produto', 'erro'])
            df_erros.to_excel('erros_ao_cadastrar.xlsx')
            
            cria_corpo_do_pedido_de_venda(days=day,codigo_pedido_integracao=codigo_pedido_integracao + day, numero_pedido=pedido + day)
