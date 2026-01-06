import pandas as pd
from omie import *

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

APP_KEY = '4123090876905' #YUSER
APP_SECRET = 'fec203d2b600db8491d1b3ed793e2e83'


filepath = r'D:\Projetos\2J\produtos_yuzer_pmg_v2.xlsx'
df = pd.read_excel(filepath)
#df = pd.read_excel(filepath)

#ZIG    
lp = listar_produtos(APP_KEY, APP_SECRET, pagina=1, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
lp2 = listar_produtos(APP_KEY, APP_SECRET, pagina=2, registros_por_pagina=1000, apenas_importado_api="N", filtrar_apenas_omiepdv="N")
PREFIXO_EMPRESA = 'PMG-'

#df.to_excel(r'D:\Projetos\2J\produtos_yuser.xlsx', index=False)

#produtos_existentes = [str(prod['codigo']) for prod in lp['produto_servico_cadastro']]
produtos_existentes = [
    str(prod['codigo'])
    for prod in (lp['produto_servico_cadastro'] + lp2['produto_servico_cadastro'])
]


print(df.head()) 
print(df.columns) 
print(produtos_existentes)


for index, p in df.iterrows():
    categoria = p['CATEGORIA'].strip().upper()
    UF_ORIGEM =  "DF"
    UF_DESTINO = "DF"
    tributacao = identifica_tributacao_evento_por_subcategoria(categoria, UF_ORIGEM, UF_DESTINO)
    valor_unitario = p['PREÇO']
    id_produto =p['ID']
    descricao = f'{p['DESCRIÇÃO'][:105]}__'

    codigo_produto = f'{PREFIXO_EMPRESA}{id_produto}'
    print(produtos_existentes)
    if codigo_produto not in produtos_existentes:
        if tributacao.get('status') == 'erro':
            #print(f"Erro ao identificar tributação: {tributacao.get('mensagem')}")
            continue

        payload = {
            "codigo_produto_integracao": f'{PREFIXO_EMPRESA}{id_produto}',
            "codigo": f'{PREFIXO_EMPRESA}{id_produto}',
            "descricao": descricao,
            "unidade": "UN",
            "ncm": tributacao['ncm'],
            "valor_unitario": valor_unitario,
            "cst_pis": tributacao['pis_cofins_cst'],
            "cst_cofins": tributacao['pis_cofins_cst'],
            "cfop": tributacao['cfop'],
            "csosn_icms": tributacao['icms_cst'],
        }

        
        print(f'Cadastrando produto {payload}')
        
        try:
            cd = incluir_produto(APP_KEY, APP_SECRET, payload)
            print(cd)
            time.sleep(5)  # Para evitar problemas de limite de requisições
            print(f"Produto cadastrado: {payload['descricao']}")
        except RuntimeError as e:
            print(f"Erro ao cadastrar produto {payload['descricao']}: {e}")
            print('tentando novamente')

            nome_ajustado = payload['descricao'] + "__"
            payload['descricao'] = nome_ajustado
            cd = incluir_produto(APP_KEY, APP_SECRET, payload)
            print(cd)
            time.sleep(5) 
            print(f"Produto cadastrado na segunda tentativa: {payload['descricao']}")

        
    