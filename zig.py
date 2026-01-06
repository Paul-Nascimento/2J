import json
from datetime import datetime, timedelta
import pprint

# Classe da API (mesma estrutura que criamos antes)
import requests

class ZigAPI:
    BASE_URL = "https://api.zigcore.com.br/integration"

    def __init__(self, rede, token):
        self.rede = rede
        self.headers = {"Authorization": token}

    def _request(self, endpoint, params):
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erro na requisição para {endpoint}: {e}")
            return None

    def get_lojas(self):
        return self._request("/erp/lojas", {"rede": self.rede})

    def get_saida_produtos(self, dtinicio, dtfim, loja):
        return self._request("/erp/saida-produtos", {"dtinicio": dtinicio, "dtfim": dtfim, "loja": loja})

    def get_faturamento(self, dtinicio, dtfim, loja):
        return self._request("/erp/faturamento", {"dtinicio": dtinicio, "dtfim": dtfim, "loja": loja})

    def get_detalhes_maquinas(self, dtinicio, dtfim, loja):
        return self._request("/erp/faturamento/detalhesMaquinaIntegrada", {"dtinicio": dtinicio, "dtfim": dtfim, "loja": loja})

    def get_invoices(self, dtinicio, dtfim, loja, page=1):
        return self._request("/erp/invoice", {"dtinicio": dtinicio, "dtfim": dtfim, "loja": loja, "page": page})

    def get_checkins(self, desde, dtfim, loja, page=1):
        return self._request("/erp/checkins", {"desde": desde, "dtfim": dtfim, "loja": loja, "page": page})

# ----------------
# 
# --------------

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

def montar_lista_parcelas_(
    faturamento: List[Dict[str, Any]],
    produtos: List[Dict[str, Any]],
    data_vencimento: str ,
) -> Dict[str, Any]:
    """
    Gera as parcelas para o Omie e calcula internamente os totais/consolidações.

    Regras adicionais:
      • NÃO gerar parcelas para 'BÔNUS/BONUS'.
      • Gerar uma parcela para 'Valores em aberto' (se > 0) com meio_pagamento='99' (Outros) e percentual=0.00.

    Retorno:
      {"parcela": [
         {"data_vencimento","numero_parcela","percentual","valor","meio_pagamento"}, ...
      ]}
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

    # Mantemos um array com TODOS para datas; e outro só com válidos para parcelas (sem BONUS)
    pagamentos_para_datas = []
    pagamentos_validos = []

    for p in faturamento or []:
        val = int(p.get("value") or 0)
        if val <= 0:
            continue

        pagamentos_para_datas.append(p)

        pay_name = (p.get("paymentName") or "").strip()
        pay_norm = _norm(pay_name)

        # totais (todos os pagamentos > 0, inclusive BONUS)
        fat_por_payment_cents[pay_name] = fat_por_payment_cents.get(pay_name, 0) + val
        faturamento_das_maquinas_cents += val

        if "BONUS" in pay_norm:
            bonus_total_cents += val
            # NÃO entra em parcelas
        else:
            pagamentos_validos.append(p)

    # métricas
    faturamento_real_cents = faturamento_das_maquinas_cents - gorjeta_total_cents
    valores_em_aberto_cents = total_liquido_produtos_cents - gorjeta_total_cents - faturamento_real_cents
    receita_cents = faturamento_das_maquinas_cents - bonus_total_cents

    # ----------------- gerar parcelas OMIE -----------------
    parcelas = []
    percentuais = []

    total_cents = sum(int(p["value"]) for p in pagamentos_validos)

    # ordena por paymentId para determinismo
    pagamentos_validos.sort(key=lambda x: (x.get("paymentId") is None, x.get("paymentId")))

    for idx, p in enumerate(pagamentos_validos, start=1):
        val_cents = int(p.get("value") or 0)
        valor_reais = _cents_to_real(val_cents)
        perc = round((val_cents / total_cents) * 100.0, 2) if total_cents > 0 else 0.00
        percentuais.append(perc)

        if data_vencimento:
            dv = data_vencimento
        else:
            dv = _fmt_br_date_from_iso(p.get("eventDate"))

        meio = _map_meio_pagamento(p.get("paymentName"))

        parcelas.append({
            "data_vencimento": dv,
            "numero_parcela": idx,
            "percentual": perc,      # ajuste final abaixo
            "valor": valor_reais,
            "meio_pagamento": meio,
        })

    # Ajuste de arredondamento para fechar exatamente 100.00% dos pagamentos válidos
    if percentuais:
        soma_perc = round(sum(percentuais), 2)
        diff = round(100.00 - soma_perc, 2)
        parcelas[-1]["percentual"] = round(parcelas[-1]["percentual"] + diff, 2)

    # --------- parcela extra: 'Valores em aberto' -> Outros (99) ---------
    if valores_em_aberto_cents > 0:
        # data para 'em aberto': usa data_vencimento, senão a maior eventDate, senão hoje
        if data_vencimento:
            dv_aberto = data_vencimento
        else:
            # maior data entre os pagamentos (se existir)
            def _to_dt(iso):
                try:
                    return datetime.fromisoformat((iso or "").replace("Z", ""))
                except Exception:
                    return None
            datas = [ _to_dt(p.get("eventDate")) for p in (pagamentos_para_datas or []) ]
            datas = [d for d in datas if d is not None]
            if datas:
                dv_aberto = max(datas).strftime("%d/%m/%Y")
            else:
                dv_aberto = datetime.today().strftime("%d/%m/%Y")

        parcelas.append({
            "data_vencimento": dv_aberto,
            "numero_parcela": len(parcelas) + 1,
            "percentual": 0.00,  # não compõe % dos recebimentos
            "valor": _cents_to_real(valores_em_aberto_cents),
            "meio_pagamento": "99",  # Outros
        })

    # (opcional) log interno das métricas para auditoria:
    _resumo_interno = {
        "totais": {
            "produtos_total_bruto": _cents_to_real(total_bruto_produtos_cents),
            "produtos_total_descontos": _cents_to_real(total_descontos_produtos_cents),
            "produtos_total_liquido": _cents_to_real(total_liquido_produtos_cents),
            "gorjeta_total": _cents_to_real(gorjeta_total_cents),
            "faturamento_das_maquinas": _cents_to_real(faturamento_das_maquinas_cents),
            "faturamento_real": _cents_to_real(faturamento_real_cents),
            "valores_em_aberto": _cents_to_real(valores_em_aberto_cents),
            "bonus_total": _cents_to_real(bonus_total_cents),
            "receita": _cents_to_real(receita_cents),
        },
        "consolidados": {
            "por_paymentName": {k: _cents_to_real(v) for k, v in fat_por_payment_cents.items()},
            "por_produto": {
                desc: {
                    "quantidade": agg["quantidade"],
                    "valor_bruto": _cents_to_real(agg["valor_bruto_cents"]),
                    "desconto": _cents_to_real(agg["desconto_cents"]),
                    "valor_liquido": _cents_to_real(agg["valor_liquido_cents"]),
                }
                for desc, agg in produtos_por_desc_cents.items()
            },
        },
    }
    # print(_resumo_interno)

    return {"parcela": parcelas}
# PIPELINE DE TESTE
# ------------------------------

from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

def run_pipeline(
    rede: str,
    token: str,
    dia_ini: str,          # "YYYY-MM-DD"
    dia_fim: str,          # "YYYY-MM-DD"
    loja_id: Optional[int] = None,
    salvar_excel: Optional[str] = None,  # ex: "Produtos_ZIG_periodo.xlsx"
):
    """
    Itera do dia_ini ao dia_fim (inclusive), consulta saída de produtos
    e retorna um único DataFrame com todas as linhas agregadas.
    Se salvar_excel for informado, salva o .xlsx ao final.
    """

    api = ZigAPI(rede, token)

    # 1) Lojas
    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
        return pd.DataFrame()

    if loja_id is None:
        loja_id = lojas[0]["id"]
        print(f"Usando Loja: {loja_id} - {lojas[0]['name']}")
    else:
        # tenta localizar a loja para log
        loja_match = next((l for l in lojas if l.get("id") == loja_id), None)
        if loja_match:
            print(f"Usando Loja: {loja_id} - {loja_match.get('name')}")
        else:
            print(f"Usando Loja: {loja_id} (não encontrada na lista retornada)")

    # 2) Intervalo de datas
    d_ini = datetime.strptime(dia_ini, "%Y-%m-%d").date()
    d_fim = datetime.strptime(dia_fim, "%Y-%m-%d").date()
    if d_ini > d_fim:
        # inverte se vier trocado
        d_ini, d_fim = d_fim, d_ini

    print(f"Período: {d_ini} até {d_fim}")

    # 3) Loop diário e agregação
    frames = []
    dia = d_ini
    while dia <= d_fim:
        dt_str = dia.strftime("%Y-%m-%d")
        print(f"\n=== 2. Saída de Produtos — {dt_str} ===")
        try:
            produtos = api.get_saida_produtos(dt_str, dt_str, loja_id)
            import time
            time.sleep(2)  # para evitar limite de requisições
        except Exception as e:
            print(f"Erro ao consultar {dt_str}: {e}")
            dia += timedelta(days=1)
            continue

        if not produtos:
            print("Sem registros para este dia.")
            dia += timedelta(days=1)
            continue

        df_day = pd.DataFrame(produtos)
        # anota a data de referência pra facilitar filtros/agrupamentos depois
        df_day["data_referencia"] = dt_str
        frames.append(df_day)

        dia += timedelta(days=1)

    # 4) Concat final
    if not frames:
        print("Nenhum dado retornado no período.")
        return pd.DataFrame()

    df_all = pd.concat(frames, ignore_index=True)

    if salvar_excel:
        df_all.to_excel(salvar_excel, index=False)
        print(f"Arquivo salvo em: {salvar_excel}")

    return df_all


# ------------------------------
# EXECUÇÃO
# ------------------------------

if __name__ == "__main__":
    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    #run_pipeline(REDE, TOKEN)
    df_periodo = run_pipeline(
    rede=REDE,
    token=TOKEN,
    dia_ini="2025-05-16",
    dia_fim="2025-10-12",
    salvar_excel="Produtos_ZIG_2025.xlsx",
)
    print(df_periodo.shape, "linhas")
