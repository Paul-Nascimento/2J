import requests
from typing import Any, Dict, Optional


class YuzerIntegration:
    """
    Integração elementar com a Yuzer (Eagle).

    - Faz login e guarda o token em memória
    - Busca eventos (salesPanels)
    - Busca produtos por evento
    - Busca produtos (catálogo)

    Obs.: aqui está "cru" e direto, sem refresh de token.
    """

    def __init__(
        self,
        username: str,
        password: str,
        *,
        base_api: str = "https://api.eagle.yuzer.com.br",
        base_login: str = "https://login.eagle.yuzer.com.br",
        timeout: int = 60,
    ):
        self.username = username
        self.password = password
        self.base_api = base_api.rstrip("/")
        self.base_login = base_login.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.token: Optional[str] = None

    # ---------------------------
    # Auth
    # ---------------------------
    def authenticate(self) -> str:
        """
        Replica o curl:
          POST https://login.eagle.yuzer.com.br/api/auth/login
          body: {"password":"...","username":"..."}
        """
        url = f"{self.base_login}/api/auth/login"
        payload = {"username": self.username, "password": self.password}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://eagle.yuzer.com.br",
            "Referer": "https://eagle.yuzer.com.br/",
        }

        resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()
        token = data.get("token")
        if not token:
            raise RuntimeError(f"Login OK, mas token não veio. Response: {data}")

        self.token = token
        return token

    def _auth_headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError("Sem token. Chame authenticate() primeiro.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://eagle.yuzer.com.br",
            "Referer": "https://eagle.yuzer.com.br/",
        }

    # ---------------------------
    # Endpoints
    # ---------------------------
    def get_events(
        self,
        page: int = 1,
        per_page: int = 10,
        status: str = "ALL",
        q: str = "",
        sort: str = "desc",
        sort_column: str = "id",
    ) -> Dict[str, Any]:
        """
        POST https://api.eagle.yuzer.com.br/api/salesPanels/search
        """
        url = f"{self.base_api}/api/salesPanels/search"
        payload = {
            "status": status,
            "page": page,
            "perPage": per_page,
            "q": q,
            "sort": sort,
            "sortColumn": sort_column,
        }

        resp = self.session.post(
            url, json=payload, headers=self._auth_headers(), timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_event_products(
        self,
        sales_panel_id: str,
        page: int = 1,
        per_page: int = 10,
        status: str = "ALL",
        date_from: Optional[str] = None,  # ex: "2026-01-10T16:00:00.000Z"
        date_to: Optional[str] = None,    # ex: "2026-01-11T05:00:00.000Z"
        currency: str = "BRL",
        expand_combo: bool = False,
        sort: str = "desc",
        sort_column: str = "count",
        q: str = "",
    ) -> Dict[str, Any]:
        """
        POST https://api.eagle.yuzer.com.br/api/salesPanels/{id}/products/search
        """
        url = f"{self.base_api}/api/salesPanels/{sales_panel_id}/products/search"

        payload: Dict[str, Any] = {
            "status": status,
            "page": page,
            "perPage": per_page,
            "currency": currency,
            "expandCombo": expand_combo,
            "sortColumn": sort_column,
            "q": q,
            "sort": sort,
        }

        if date_from:
            payload["from"] = date_from
        if date_to:
            payload["to"] = date_to

        resp = self.session.post(
            url, json=payload, headers=self._auth_headers(), timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_products(
        self,
        page: int = 1,
        per_page: int = 10,
        status: str = "ALL",
        q: str = "",
        sort: str = "desc",
        sort_column: str = "id",
    ) -> Dict[str, Any]:
        """
        POST https://api.eagle.yuzer.com.br/api/products/search
        """
        url = f"{self.base_api}/api/products/search"
        payload = {
            "status": status,
            "page": page,
            "perPage": per_page,
            "q": q,
            "sort": sort,
            "sortColumn": sort_column,
        }

        resp = self.session.post(
            url, json=payload, headers=self._auth_headers(), timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------
# Exemplo de uso (igual ao seu fluxo)
# ---------------------------
if __name__ == "__main__":
    yuzer = YuzerIntegration("financeiroverrieverri@gmail.com", "Bpo@123")
    token = yuzer.authenticate()

    events = yuzer.get_events()
    event = events["content"][1]
    #print("Evento:", event)

    id_evento = event["id"]

    dados_do_evento = yuzer.get_event_products(
        id_evento,
        date_from="2026-01-10T16:00:00.000Z",
        date_to="2026-01-11T05:00:00.000Z",
    )
    #print("Produtos do evento:", dados_do_evento)

    # catálogo de produtos
    produtos = yuzer.get_products(per_page=2)
    #print("Produtos:", produtos)
