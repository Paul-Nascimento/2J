import pandas as pd
from omie import incluir_pedido_venda

def identifica_tributacao_evento_por_subcategoria(
    subcategoria: str,
    uf_origem: str = "DF",
    uf_destino: str = "DF",
    regime: str = "lucro_presumido",
) -> dict:
    """
    Sugerir CFOP, ICMS (CST), PIS/COFINS (CST) e NCM por SUBCATEGORIA
    para vendas em EVENTO a CONSUMIDOR FINAL no regime LUCRO PRESUMIDO.

    Regras gerais aplicadas:
      • Interno (mesma UF): CFOP começa com 5 (ex.: 5.102, 5.405)
      • Interestadual (UFs diferentes): CFOP começa com 6 (ex.: 6.102, 6.405)
      • Bebidas alcoólicas e refrigerantes/água/energéticos:
          - PIS/COFINS monofásico: "04"
          - ICMS (CST) com ST: 60
          - CFOP x.405 (mercadoria sujeita a ST)
      • Alimentos/embalagens/outros (revenda comum):
          - PIS/COFINS: "01" (regra típica no LP)
          - ICMS (CST): 00
          - CFOP x.102 (revenda)

    Retorna:
      { cfop: str, icms_cst: str, pis_cofins_cst: str, ncm: str, status: "ok"|"fallback" }
    """

    # Normaliza entradas
    sub = (subcategoria or "").strip().upper()
    uf_origem = (uf_origem or "").strip().upper()
    uf_destino = (uf_destino or "").strip().upper()

    # Prefixo CFOP por UF
    prefixo_cfop = "5" if uf_origem == uf_destino else "6"

    # ------- Grupos por SUBCATEGORIA -------
    vinhos = {"VINHOS TINTOS", "VINHOS BRANCOS", "VINHOS ROSES", "VINHOS ESPUMANTE"}
    cervejas = {"CERVEJAS", "CHOPP", "CHOPE", "CERVEJAS ESPECIAIS"}
    destilados = {"WHISKY", "GIN", "VODKA", "CACHAÇA", "CACHAÇA ARTESANAL", "LICOR"}
    refri_agua_energeticos = {"REFRIGERANTES", "SUCOS", "ÁGUA", "AGUA", "ENERGÉTICOS"}

    carnes_e_pratos = {"CARNE", "KAFTA", "ALCATRA", "PICANHA", "LINGUIÇA", "FRANGO", "BEIRUTI"}
    queijos_frios = {"QUEIJOS", "FRIOS", "LATICÍNIOS"}
    sobremesas = {"SOBREMESAS", "DOCES", "SORVETES"}
    molhos_condimentos = {"MOLHOS", "CONDIMENTOS", "TEMPEROS"}
    paes_massas = {"PÃES", "PÃES DE ALHO", "PAES", "TAPIOCAS", "TORTAS", "MASSAS"}
    embalagens_desc = {"EMBALAGENS", "COPOS", "GUARDANAPOS", "DESCARTÁVEIS"}
    outros = {"OUTROS", "DIVERSOS"}

    # ------- SUGESTÃO DE NCM POR GRUPO -------
    # (ajuste conforme catálogo real)
    if sub in vinhos:
        ncm = "22042100"         # Vinhos de uvas frescas
        icms_cst = "60"          # ST na revenda varejo é frequente
        pis_cofins_cst = "04"    # Monofásico
        cfop = f"{prefixo_cfop}.405"
    elif sub in cervejas:
        ncm = "22030000"         # Cervejas de malte
        icms_cst = "60"
        pis_cofins_cst = "04"
        cfop = f"{prefixo_cfop}.405"
    elif sub in destilados:
        ncm = "22089000"         # Bebidas destiladas diversas
        icms_cst = "60"
        pis_cofins_cst = "04"
        cfop = f"{prefixo_cfop}.405"
    elif sub in refri_agua_energeticos:
        ncm = "22021000"         # Águas/sodas/refris (ajuste se sucos 2009.x)
        icms_cst = "60"
        pis_cofins_cst = "04"
        cfop = f"{prefixo_cfop}.405"

    elif sub in carnes_e_pratos:
        ncm = "16025000"         # Preparações de carne bovina (genérico p/ pratos prontos)
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in queijos_frios:
        ncm = "04069000"         # Queijos
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in sobremesas:
        ncm = "21069090"         # Outras preparações alimentícias
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in molhos_condimentos:
        ncm = "21039090"         # Outros molhos/condimentos
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in paes_massas:
        ncm = "19059090"         # Produtos de padaria
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in embalagens_desc:
        ncm = "39231090"         # Artigos de plástico p/ embalagem
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    elif sub in outros:
        ncm = "21069090"
        icms_cst = "00"
        pis_cofins_cst = "01"
        cfop = f"{prefixo_cfop}.102"
    else:
        # Fallback conservador
        ncm = "22089000"
        icms_cst = "60"          # assume ST/monofásico em cenário de bebidas
        pis_cofins_cst = "04"
        cfop = f"{prefixo_cfop}.405"

    return {
        "cfop": cfop,                 # "5.102", "5.405", "6.102", "6.405" etc.
        "icms_cst": icms_cst,         # Ex.: "00", "20", "40", "60", "90"
        "pis_cofins_cst": pis_cofins_cst,  # "01" (LP), "04" (monofásico), etc.
        "ncm": ncm,
        "status": "ok" if sub else "fallback",
        "contexto": {
            "regime": regime,
            "operacao": "evento_consumidor_final",
            "uf_origem": uf_origem,
            "uf_destino": uf_destino,
        },
    }

def monta_cabecalho(numero_pedido, codigo_pedido_integracao, dtajustada, qtd_parcelas=4):
    data =  {
        "codigo_cliente": 1743461622, # 'codigo_cliente_omie' na API ListarClientes
        "codigo_pedido_integracao": str(codigo_pedido_integracao), #Esse valor vem do zig
        "data_previsao": dtajustada, #Mesma data do faturamento
        "etapa": "10",
        "numero_pedido": str(numero_pedido), #Campo dinâmico
        "codigo_parcela": "999",
        "qtde_parcelas": qtd_parcelas,
        "origem_pedido": "API"
    }

    return data

def monta_parcelas(data_vencimento = "10/10/2025"):
    #Manual por enquanto
    data = {}
    data['parcela'] =[
            {
                "valor": 100_000.00,
                "meio_pagamento": "03",  # CREDITO
                "data_vencimento": data_vencimento,
                "numero_parcela": 1,
                "percentual": 100,
            }
        ]
    

    return data

def monta_informacoes_adicionais(codigo_categoria,codigo_conta_corrente):

    data =  {
        "codigo_categoria": codigo_categoria,
        "codigo_conta_corrente": codigo_conta_corrente, #nCodCC na api ListarContasCorrentes
        "consumidor_final": "S",
        "enviar_email": "N"
    }

    return data

def monta_det(planilha):
    df = pd.read_excel(planilha)
    print(df)
    data = []
    for index, p in df.iterrows():
        ide = {'codigo_item_integracao': str(index + 1), 'simples_nacional': 'N'}
        #tributacao = identifica_tributacao_evento_por_subcategoria(p['Subcategoria'], "DF", "DF")
        imposto =  {'cofins_padrao': {'cod_sit_trib_cofins': '06'},
              'icms': {'cod_sit_trib_icms': '41'},
              'pis_padrao': {'cod_sit_trib_pis': '06'}
              }
        

        produto = {'cfop': '5.405',
                'codigo_produto': p['CODIGO OMIE'], #Consultar na propria lista do OMIE
                'codigo_produto_integracao': p['CODIGO OMIE'],
                'descricao': f'{str(p['DESCRIÇÃO'])[:115]}__',
                'ncm': '0000.00.00',
                'quantidade': p['Quantidade'],
                'tipo_desconto': 'V',
                'unidade': 'UN',
                'valor_desconto': 0.0,
                'valor_unitario': p['Valor Unit.']
                }
        
        informacoes_adicionais = {'peso_bruto': 1, 'peso_liquido': 1}

        data.append({
            'ide': ide,
            'imposto': imposto,
            'inf_adic': informacoes_adicionais,
            'produto': produto
        })
    return data

APP_KEY = '4123090876905' #YUSER
APP_SECRET = 'fec203d2b600db8491d1b3ed793e2e83'

DE_PARA_YUZER_OMIE_CONTA_CONTABIL = {
    "ALIMENTOS": '1.01.01',
    "BEBIDAS": '1.01.94',
    "INGRESSOS": '1.01.99',
    "VENDA DE ROUPAS COPOS E ACESSÓRIOS": '1.01.91',
    "LOCAÇÃO DE ESPAÇOS": "1.01.96",
    "OUTROS CONSUMIVEIS": None,
    "BALEIRA": '1.01.89',
}

tipo_de_venda = 'INGRESSOS' #Informação vem da planilha
conta_corrente_micare =11831850443
filepath = r'D:\Projetos\2J\ingressos_bilheteria_digital_v3.xlsx'

codigo_categoria = DE_PARA_YUZER_OMIE_CONTA_CONTABIL[tipo_de_venda]
informacoes_adicionais = monta_informacoes_adicionais(codigo_categoria,conta_corrente_micare)


det = monta_det(filepath)
parcelas = monta_parcelas(data_vencimento='02/01/2026')
pedido = '590'
cabecalho = monta_cabecalho(pedido,pedido, '02/01/2026', 1)


pedido = {
    "cabecalho": cabecalho,
    "det": det,
    "informacoes_adicionais": informacoes_adicionais,
    "lista_parcelas": parcelas
}

print(f'Dados do pedido {pedido}')

import pprint

pprint.pprint(pedido)
#df = pd.DataFrame(pedido)
#df.to_excel('pedido_yuser.xlsx', index=False)
print('Enviando pedido para o OMIE...')
inclusao_do_pedido = incluir_pedido_venda(APP_KEY, APP_SECRET, pedido)
#print(inclusao_do_pedido)


