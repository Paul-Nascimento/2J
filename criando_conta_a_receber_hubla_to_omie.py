from omie import OmieContaReceberAPI

APP_KEY = '6327079006248'
APP_SECRET = '6d3cfc23d7eafa0b63a2878e8e5f01d8'

cr = OmieContaReceberAPI(APP_KEY, APP_SECRET)


cr.incluir_conta_receber(
    codigo_lancamento_integracao="1691776454",
    codigo_cliente_fornecedor=8666593613,
    data_vencimento="11/01/2026",
    valor_documento=100.00,
    codigo_categoria="1.01.88", #1.01.88 
    id_conta_corrente=8657749943,
)