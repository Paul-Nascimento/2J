import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class HublaIntegration:
    """
    Integração (extração) Hubla:
      - Autentica via Firebase (signInWithPassword -> refresh token -> roleplay sign-in -> custom token -> idToken)
      - Extrai offers (product ids)
      - Extrai invoices/sales (paid) por período
      - Normaliza os dados em um formato fácil de consumir

    Observação:
      - Os endpoints e chaves (Firebase key / gmpid etc.) foram mantidos como no seu código.
      - Se a Hubla mudar algum detalhe de payload/headers, ajuste aqui centralizado.
    """

    # Endpoints fixos (conforme seu script)
    FIREBASE_SIGNIN_PASSWORD_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    SECURETOKEN_URL = "https://securetoken.googleapis.com/v1/token"
    ROLEPLAY_SIGNIN_URL = "https://backend-bff-web.platform.hub.la/api/v1/user/roleplay/sign-in"
    FIREBASE_CUSTOMTOKEN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
    OFFERS_URL = "https://backend-bff-product.platform.hub.la/api/v1/filters/offers"
    INVOICES_LIST_URL = "https://backend-bff-web.platform.hub.la/api/v1/invoices/list"

    def __init__(
        self,
        email: str,
        password: str,
        firebase_api_key: str,
        roleplay_user_id: str,
        origin: str = "https://app.hub.la",
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        # Headers “x-*” que você estava mandando no custom token:
        x_client_version: str = "Chrome/JsCore/11.4.0/FirebaseCore-web",
        x_firebase_gmpid: str = "1:223497474066:web:7732a1419a7052e60108cb",
        timeout: int = 60,
    ):
        self.email = email
        self.password = password
        self.firebase_api_key = firebase_api_key
        self.roleplay_user_id = roleplay_user_id

        self.origin = origin
        self.user_agent = user_agent
        self.x_client_version = x_client_version
        self.x_firebase_gmpid = x_firebase_gmpid
        self.timeout = timeout

        self.session = requests.Session()

        # Tokens (preenchidos após login)
        self._login_id_token: Optional[str] = None
        self._login_refresh_token: Optional[str] = None

        self._secure_access_token: Optional[str] = None
        self._secure_refresh_token: Optional[str] = None
        self._secure_user_id: Optional[str] = None

        self._roleplay_custom_token: Optional[str] = None  # retorno do roleplay sign-in (texto)
        self._hubla_id_token: Optional[str] = None         # idToken final (usado nas APIs Hubla)

    # -------------------------
    # Helpers
    # -------------------------
    def _raise_for_bad_response(self, resp: requests.Response, context: str) -> None:
        if not resp.ok:
            raise RuntimeError(
                f"[{context}] HTTP {resp.status_code} - {resp.text[:1000]}"
            )

    @staticmethod
    def _to_iso_range(data_inicio_ddmmyyyy: str, data_fim_ddmmyyyy: str) -> Tuple[str, str]:
        """
        Converte dd/mm/yyyy para o intervalo ISO no formato que você já usava.
        """
        inicio_iso = datetime.strptime(data_inicio_ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%dT00:00:00-03:00")
        fim_iso = datetime.strptime(data_fim_ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%dT23:59:59-03:00")
        return inicio_iso, fim_iso

    @property
    def hubla_token(self) -> str:
        """
        Token final usado nas requests Hubla (Authorization).
        """
        if not self._hubla_id_token:
            raise RuntimeError("Você precisa chamar authenticate() antes de usar a Hubla.")
        return self._hubla_id_token

    # -------------------------
    # Auth flow (igual ao seu)
    # -------------------------
    def login_with_password(self) -> Tuple[str, str]:
        """
        Firebase: signInWithPassword -> retorna (idToken, refreshToken)
        """
        url = f"{self.FIREBASE_SIGNIN_PASSWORD_URL}?key={self.firebase_api_key}"
        payload = {
            "returnSecureToken": True,
            "email": self.email,
            "password": self.password,
            "clientType": "CLIENT_TYPE_WEB",
        }
        headers = {"Content-Type": "application/json"}

        resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "login_with_password")

        data = resp.json()
        self._login_id_token = data.get("idToken")
        self._login_refresh_token = data.get("refreshToken")

        if not self._login_id_token or not self._login_refresh_token:
            raise RuntimeError(f"[login_with_password] Resposta sem tokens esperados: {data}")

        return self._login_id_token, self._login_refresh_token

    def refresh_secure_token(self, refresh_token: str) -> Tuple[str, str, str]:
        """
        Firebase Secure Token:
          POST /token (grant_type=refresh_token) -> access_token, refresh_token, user_id
        Observação: no seu código você passa o *refresh token* aqui.
        """
        url = f"{self.SECURETOKEN_URL}?key={self.firebase_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "refresh_secure_token")

        data = resp.json()
        self._secure_access_token = data.get("access_token")
        self._secure_refresh_token = data.get("refresh_token")
        self._secure_user_id = data.get("user_id")

        if not self._secure_access_token or not self._secure_refresh_token or not self._secure_user_id:
            raise RuntimeError(f"[refresh_secure_token] Resposta sem campos esperados: {data}")

        return self._secure_access_token, self._secure_refresh_token, self._secure_user_id

    def roleplay_sign_in(self, bearer_access_token: str) -> str:
        """
        Hubla roleplay:
          POST /user/roleplay/sign-in
          Authorization: Bearer <secure_access_token>
          payload: roleplayUserId
        Retorna um texto (custom token) - no seu script era response.text.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": bearer_access_token,
            "Accept": "application/json, text/plain, */*",
        }
        payload = {"roleplayUserId": self.roleplay_user_id}

        resp = self.session.post(self.ROLEPLAY_SIGNIN_URL, json=payload, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "roleplay_sign_in")

        self._roleplay_custom_token = resp.text
        return self._roleplay_custom_token

    def exchange_custom_token_for_id_token(self, custom_token: str) -> str:
        """
        Firebase: signInWithCustomToken -> retorna idToken (que você usa nas APIs Hubla).
        """
        url = f"{self.FIREBASE_CUSTOMTOKEN_URL}?key={self.firebase_api_key}"

        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": self.origin,
            "referer": f"{self.origin}/",
            "user-agent": self.user_agent,
            "x-client-version": self.x_client_version,
            "x-firebase-gmpid": self.x_firebase_gmpid,
        }
        payload = {"returnSecureToken": True, "token": custom_token}

        resp = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "exchange_custom_token_for_id_token")

        data = resp.json()
        self._hubla_id_token = data.get("idToken")

        if not self._hubla_id_token:
            raise RuntimeError(f"[exchange_custom_token_for_id_token] Resposta sem idToken: {data}")

        return self._hubla_id_token

    def authenticate(self) -> str:
        """
        Fluxo completo:
          1) login senha -> refreshToken
          2) secure token (refresh) -> access_token
          3) roleplay sign-in -> custom token (texto)
          4) custom token -> idToken final
        """
        _, refresh = self.login_with_password()
        secure_access, _, _ = self.refresh_secure_token(refresh)
        custom_token = self.roleplay_sign_in(f"Bearer {secure_access}")
        return self.exchange_custom_token_for_id_token(custom_token)

    # -------------------------
    # Extração Hubla
    # -------------------------
    def get_offers(self) -> List[str]:
        """
        Retorna lista de offerIds (conforme seu get_offers).
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.hubla_token}",
        }

        resp = self.session.get(self.OFFERS_URL, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "get_offers")

        data = resp.json()

        owner = data.get("owner", [])
        #print(owner)
        #ids = [item.get("id") for item in owner if item.get("id")]
        return owner

    def get_sales(
        self,
        offer_ids: List[str],
        data_inicio_ddmmyyyy: str,
        data_fim_ddmmyyyy: str,
        page: int = 1,
        page_size: int = 25,
        status: Optional[List[str]] = None,
        date_range_by: str = "createdAt",
        order_by: str = "createdAt",
        order_direction: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """
        Busca invoices/sales (paid por padrão) no intervalo.
        """
        if status is None:
            status = ["paid"]

        start_iso, end_iso = self._to_iso_range(data_inicio_ddmmyyyy, data_fim_ddmmyyyy)

        payload = {
            "offerIds": offer_ids,
            "hasSelectedAll": True,
            "filters": {
                "startDate": start_iso,
                "endDate": end_iso,
                "status": status,
                "type": [],
                "paymentMethod": [],
                "search": "",
                "utmSource": "",
                "utmMedium": "",
                "utmCampaign": "",
                "utmContent": "",
                "utmTerm": "",
                "dateRangeBy": date_range_by,
            },
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by,
            "orderDirection": order_direction,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.hubla_token,  # exatamente como no seu script (sem Bearer)
        }

        resp = self.session.post(self.INVOICES_LIST_URL, headers=headers, json=payload, timeout=self.timeout)

        # No seu script você esperava 201
        if resp.status_code in (200, 201):
            data = resp.json()
            return data.get("items", [])

        # fallback: tenta GET (igual você fez)
        resp2 = self.session.get(self.INVOICES_LIST_URL, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp2, "get_sales_fallback_get")

        data2 = resp2.json()
        return data2.get("items", [])

    # -------------------------
    # Normalização opcional
    # -------------------------
    @staticmethod
    def normalize_sale(sale: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma 1 item bruto em algo mais "flat" e pronto pra virar DataFrame/CSV.
        """
        payer = (sale.get("payer") or {}).get("identity") or {}
        amount = sale.get("amountDetail") or {}
        products = amount.get("products") or []

        return {
            "sale_id": sale.get("id"),
            "created_at": sale.get("createdAt"),
            "payment_method": sale.get("paymentMethod"),
            "payer_full_name": payer.get("fullName"),
            "payer_email": payer.get("email"),
            "payer_document": payer.get("document"),
            "installment_fee": (amount.get("installmentFeeCents") or 0) / 100,
            "products": [
                {
                    "product_name": p.get("productName"),
                    "price": (p.get("priceCents") or 0) / 100,
                    "quantity": p.get("quantity"),
                }
                for p in products
            ],
        }

    def extract_sales_normalized(
        self,
        data_inicio_ddmmyyyy: str,
        data_fim_ddmmyyyy: str,
    ) -> List[Dict[str, Any]]:
        """
        1) pega offers
        2) pega sales
        3) normaliza tudo
        """
        offer_ids = self.get_offers()
        #print(offer_ids)
        
        sales = self.get_sales(offer_ids, data_inicio_ddmmyyyy, data_fim_ddmmyyyy)
        print(sales)
        exit()
        return [self.normalize_sale(s) for s in sales]

    # hubla_integration.py (dentro da classe HublaIntegration)

    def get_offers_full(self) -> list:
        """
        Retorna a lista completa de offers (com id, name, product{...}).
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.hubla_token}",
        }
        resp = self.session.get(self.OFFERS_URL, headers=headers, timeout=self.timeout)
        self._raise_for_bad_response(resp, "get_offers_full")

        data = resp.json()
        # no seu código antigo: data['owner']
        return data.get("owner", [])


    def get_offer_ids(self) -> list:
        """
        Só os IDs das offers (para filtrar invoices).
        """
        offers = self.get_offers_full()
        return [o["id"] for o in offers if o.get("id")]




if __name__ == "__main__":

    hubla =HublaIntegration("financeiro@jovemdovinho.com.br","2jFinanceiro",'AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8','eSLHOduIf1VueToaTj2b2B0fARP2')
    hubla.authenticate()

    offers = hubla.get_offers() #Para cadastro
    import pprint

    pprint.pprint(offers)


    offers_id = hubla.get_offer_ids() #Para consultar as vendas
    sales = hubla.get_sales(offers_id,'23/12/2025','24/12/2025')

    for sale in sales:

        import pprint

        pprint.pprint(sale)
        installment_fee_cents = sale['amount']['installmentFeeCents']
        id = sale['id']
        payment_method = sale['paymentMethod']

        product = sale['items'][0]

        offer_id =  product['offerId']
        price_cents = product['priceCents']
        product_name = product['productName']

        payer_email = sale['payer']['identity']['email']
        payer_name = sale['payer']['identity']['fullName']
        payer_cpf = sale['payer']['identity']['document']
        payer_id = sale['payer']['id']
        
        created_at = sale['createdAt']  # "2025-12-20T20:57:55.000Z"

        print(installment_fee_cents,product,offer_id,price_cents,product_name,payer_email,payer_name,payer_cpf,payment_method,created_at)

