import requests, json
url = "https://app.omie.com.br/api/v1/geral/produtos/"

APP_KEY = '5521527811800'
APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'
infos = [{"pagina":1,"registros_por_pagina":1,"apenas_importado_api":"N","filtrar_apenas_omiepdv":"N"}]

print(infos)
payload = {
  "call":"ListarProdutos",
  "app_key":APP_KEY,
  "app_secret":APP_SECRET,
  "param":infos
}
#r = requests.post(url, json=payload, timeout=30)
#print("OK?", r.status_code, r.text[:4000])