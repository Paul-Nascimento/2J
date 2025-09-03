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

# ------------------------------
# PIPELINE DE TESTE
# ------------------------------

def run_pipeline(rede, token):
    api = ZigAPI(rede, token)

    # Período para teste (últimos 7 dias)
    hoje = datetime.today()
    dtfim = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    dtinicio = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    #dtinicio = dtfim
    print("=== 1. Buscando lojas ===")
    lojas = api.get_lojas()
    if not lojas:
        print("Nenhuma loja encontrada ou erro na requisição.")
        return
    print(f"Lojas encontradas: {len(lojas)}")

    # Escolhe a primeira loja para os próximos testes
    loja_id = lojas[0]["id"]
    print(f"Usando Loja: {loja_id} - {lojas[0]['name']}")

    print("\n=== 2. Saída de Produtos ===")
    produtos = api.get_saida_produtos(dtinicio, dtfim, loja_id)
    pprint.pprint(produtos)
    print(f"Produtos encontrados: {len(produtos) if produtos else 0}")

    import pandas as pd

    df = pd.DataFrame(produtos)
    df.to_excel('produtoszig.xlsx')

    exit()

    print("\n=== 3. Faturamento ===")
    faturamento = api.get_faturamento(dtinicio, dtfim, loja_id)
    valor_total = sum(item.get("value", 0) for item in faturamento) if faturamento else 0
    print(f"Faturamento total: R$ {valor_total / 100:.2f}")
    df = pd.DataFrame(faturamento)
    df.to_excel("saida_faturamento.xlsx", index=False)    

    print("\n=== 4. Detalhes de Faturamento (Máquinas) ===")
    detalhes = api.get_detalhes_maquinas(dtinicio, dtfim, loja_id)
    print(f"Máquinas encontradas: {len(detalhes) if detalhes else 0}")
    df = pd.DataFrame(detalhes)
    df.to_excel("saida_detalhes.xlsx", index=False)    


    print("\n=== 5. Invoices ===")
    invoices = api.get_invoices(dtinicio, dtfim, loja_id)
    print(f"Notas fiscais encontradas: {len(invoices) if invoices else 0}")

    df = pd.DataFrame(invoices)
    df.to_excel("saida_checkins.xlsx", index=False)    


    print("\n=== 6. Check-ins ===")
    checkins = api.get_checkins(dtinicio, dtfim, loja_id)
    print(f"Check-ins encontrados: {len(checkins) if checkins else 0}")

    df = pd.DataFrame(checkins)
    df.to_excel("saida_checkins.xlsx", index=False)    

    # Exibe um resumo consolidado
    resumo = {
        "lojas": len(lojas),
        "produtos": len(produtos) if produtos else 0,
        "faturamento_total": valor_total / 100,
        "detalhes_maquinas": len(detalhes) if detalhes else 0,
        "invoices": len(invoices) if invoices else 0,
        "checkins": len(checkins) if checkins else 0,
    }

    print("\n=== RESUMO FINAL ===")
    print(json.dumps(resumo, indent=2, ensure_ascii=False))

# ------------------------------
# EXECUÇÃO
# ------------------------------

if __name__ == "__main__":
    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"
    run_pipeline(REDE, TOKEN)
