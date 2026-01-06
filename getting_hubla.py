import requests
import pandas as pd

token = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJyb2xlcGxheVNlc3Npb25zIjp7ImVTTEhPZHVJZjFWdWVUb2FUajJiMkIwZkFSUDIiOjExfSwicm9sZXBsYXlVc2VySWQiOiJlU0xIT2R1SWYxVnVlVG9hVGoyYjJCMGZBUlAyIiwicm9sZXBsYXlSZXNvdXJjZXMiOlsic2FsZXMiLCJwcm9kdWN0cyIsInJlcG9ydHMiLCJtZW1iZXJzIiwiY2xpZW50cyIsImFmZmlsaWF0ZXMiLCJjb3Vwb25zIiwicmVmdW5kcyIsIndhbGxldCIsImludGVncmF0aW9ucyIsImhvbWUiLCJzdWJzY3JpcHRpb25zIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnMiLCJtZW1iZXJzX2FyZWFfbm90aWZpY2F0aW9uc19jb21tZW50X2FwcHJvdmFsIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfY29tbWVudF9tZW50aW9uIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfY29udGVudF9ldmFsdWF0aW9uIiwibWVtYmVyc19hcmVhX25vdGlmaWNhdGlvbnNfdGFza19hcHByb3ZhbCIsInJvbGVwbGF5Il0sImhhc0NvbXBsZXRlZE1GQSI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2NoYXRwYXktY2QxMjAiLCJhdWQiOiJjaGF0cGF5LWNkMTIwIiwiYXV0aF90aW1lIjoxNzY1MTEwMzQ5LCJ1c2VyX2lkIjoiQU1RRERiZ3huZ2dRYUVTbXRONHRHakYzNHNQMiIsInN1YiI6IkFNUUREYmd4bmdnUWFFU210TjR0R2pGMzRzUDIiLCJpYXQiOjE3NjUxMTAzNDksImV4cCI6MTc2NTExMzk0OSwiZW1haWwiOiJmaW5hbmNlaXJvQGpvdmVtZG92aW5oby5jb20uYnIiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInBob25lX251bWJlciI6Iis1NTYxOTkzMjY1NzY3IiwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJmaW5hbmNlaXJvQGpvdmVtZG92aW5oby5jb20uYnIiXSwicGhvbmUiOlsiKzU1NjE5OTMyNjU3NjciXX0sInNpZ25faW5fcHJvdmlkZXIiOiJjdXN0b20ifX0.nFdc86V_iAu0i86D7-bRyAMTBztC1Iz7StczndSsgugK9sMRnqOG1vwTkWZ5ZjDXwaw3DkKGrM1XO3wdcli50lZXKB3YMgif61ReqjkWobs3O-BGaCWwj32a3CLU6YaHA8ZVS8tTs-nRvsIn3fMbg4kkAv6tN4Wtz6UitmYcMLfSuLYuxE1s_tjrUZthUpWrFXkDB5CyqgiKAI91xAVr5HRevuen1SMzXR0Z7hqLmBQfYbL1i1s94qB0YeiMS8NRDdjVNiw0JR1PT9bprOtqeWL4xag82H7hHg2IyM7gh9JTq8hs3AkUVe-64_Z91fujjz8YQLqFie5TsiSUlI34_Q'

def get_products(token):
    url = 'https://backend-bff-product.platform.hub.la/api/v1/products/list'

    payload = {"page": 1, "pageSize": 25, "orderBy": "createdAt", "orderDir": "DESC", "filters": {"search": ""}}

    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response)
    if response.status_code == 201:
        print(response.json())
        return response.json().get("products", [])
 
def login():

    key = 'AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'
    payload = {"returnSecureToken": True, "email": "financeiro@jovemdovinho.com.br", "password": "2jFinanceiro", "clientType":"CLIENT_TYPE_WEB"}

    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'

    headers = {
        "Content-Type":"application/json"
    }
    response = requests.post(url,json=payload,headers=headers)

    #print(response.json())
    
    return response.json().get("idToken", None),response.json().get("refreshToken", None)

def get_secure_token(id_token):
    url = 'https://securetoken.googleapis.com/v1/token?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8'

    headers = {
        "Content-Type":"application/json",

    }
    payload = {
        "grant_type":"refresh_token",
        "refresh_token":id_token
    }

    response = requests.post(url,headers=headers,json=payload)

    #print(response.json())
    return response.json().get("access_token", None),response.json().get("refresh_token", None),response.json().get("user_id", None)

def get_sign_in(sign_in_token,user_id): #Bearer
    url ='https://backend-bff-web.platform.hub.la/api/v1/user/roleplay/sign-in'

    headers = {
        "Content-Type": "application/json",
        "Authorization": sign_in_token,
        "Accept": "application/json, text/plain, */*",
    }

    payload = {
        "roleplayUserId":"eSLHOduIf1VueToaTj2b2B0fARP2"
    }
    
    response = requests.post(url, headers=headers,json=payload)
    

    return response.text
    #return response.json().get("acess_token", None)

def get_identity_toolkit_token(token):
    url ="https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8"


    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://app.hub.la",
        "referer": "https://app.hub.la/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        
        # Esses headers "X-browser" não são validados pelo Firebase, mas manter não atrapalha:
        "x-browser-channel": "stable",
        "x-browser-copyright": "Copyright 2025 Google LLC. All Rights reserved.",
        "x-browser-validation": "Aj9fzfu+SaGLBY9Oqr3S7RokOtM=",
        "x-browser-year": "2025",
        
        # Firebase exige esse em alguns cenários (não obrigatório sempre)
        "x-client-version": "Chrome/JsCore/11.4.0/FirebaseCore-web",
        "x-firebase-gmpid": "1:223497474066:web:7732a1419a7052e60108cb"
    }

    payload = {
        "returnSecureToken":True,
        "token":token
    }
    
    response = requests.post(url, headers=headers,json=payload)

    #print(response.json())
    return response.json().get("idToken", None)


def get_auth(id_token):
    url ='https://hub.la/api/auth/get'

    headers = {
        "Content-Type":"application/json",
        "Authorization":id_token
        

    }

    paylaod = {}

    response = requests.post(url,headers=headers,json=paylaod)

    #print(response.json())


def get_sales(token):
    url = 'https://backend-bff-web.platform.hub.la/api/v1/invoices/list'

    payload = {"offerIds": #Offers são os próprios produtos
               ["ALlkzWMeFrwycRNw19oC","96Wbh48aWzrI5UC8UjLW","OGHHnQUurN1g9K5CcY0h","gaGQ1uKoyFB6jcSTSZ3P","yWeh6KDfsIppwQIFVFMh","2vzxITADDwr3Gu1G14F3","2SNoqTPW23ZIj0eB3tUM","B8MBdVWaSVpg83Jlcr8A","UCbHTmk6LRuEL3VIUnxg","WVMlcnsheUF96Id40p9F","aAqYdTaUy2W0LhTR51Om","0WEuQcx3YEz6z5mhfxX0","UcKSe5850jil4RkItkU4","DuuvbwRvV10zcMwK8m8o","UfAbFx0wQKZrhEpEkTYk","ZnND19flvfhZmrMgl32B","nwLR6HTKqWFAPkPnhyaz","H6ilwggXtHizMAXrLOyR","JVM4vHhOQZRcWnxrwTOS","LWLR05BXlDHqzbil12dE","NOG23JMmEWdQAc9QK9yi","NoE3sKbKpCWtt6Z8vbCd","TGPotdOk0WgIP5Uvf1Bx","kHGNAYcsO4Tthx7dkTWC","SPn6Lrz9vmGlbIzFmlhp","glF02K0Pn0Duur6brosZ","1vf5kttYiI411ULQe1W0","375EML74XD7BWTFhBj2F","881ooqYuXZDOEq14kM8r","BYkV8e9sSCpPkNhEM1Nh","Be08TwyBhlqyb5ZtWyJ4","Cr9Ljcr1ysQHdJVMqilX","WtvN6wkApF10w6SHgirs","Z9aIv5WYsae1O0ryi6s1","cg0TZ46EG7PEe9nbN15g","dhKwEu4Gb2QjZGKlSfLR","dxJfCgRHSCNHkKXe1LAS","gVbRpdxmoqH75WshpUmH","id472ywEnhC70cIvrrlI","n0yefJ3SjFzS3zbk4ZVf","uyMeajYgyrsBnZgjo3pg","YKIHX2OeTMCed2dticWt","OyitjCJOUn4fZplqcavL","icPHK5y94vKw1Pt286GP","eFctYMjTm79LYCB419a9","mUjxDLmKvL4XXeTede3A","TaLcxmucC8aptuNVG8Jw","DnNXA6aCvO4MSKNezj37","RfaoaeHxmDncHA4iyqXA","pgvR81x1yxx1iuivJ2iK","axh95w4xhUSCcuUT67vR","Izz3RKtJEjpAO8ITHP7Y","6PFtjLOp0SUVmQvr9ym1","TBrR8TniS5rxUjQWg6Xn","jx53u2K3quLUN908IuDS","o3ulcATKiUqaNqVhZXQg","kMhpHQyjU7wNbO199S91","11BUBuvfzrIiwbkeLPYm","Jv1PSyRQ5hWm3BgEySEO","izyepA9HsyXDsRitVq9b","sM4H8DZxEYb77XpzrmpM","Rh8I8qzqhHplxm6zEhj0","BJ5lQ2Ui6w6UtVPQDnt2","jU8iLomeTZRje4PyHlAW","1gtA7KoiXEDPnO7jMDyx","GmYkx1ABp952s2BqN1ac","6XIKDUOxdpgf70Fr4woM","GF6WtYXyjtibDDdVnFAi","l6GaOP3GDIfroBFv4KdM","enOhnTDwHg46NCE1VkLx","XY7kC8GV7OX06yIHdobt","CdWjwrxOFRDbhjyHFHW6","VudRFPCbuOKd9HGJZxxv","DXcHk0htNyK9blRpOKzP","XbCF41z9UQtQ2L0k9oQQ","exn08zScb4HDmcvmoCsW","bzgjaEfBKWMHYetgu3BP","9Ua6sKfW0mPtzsHWCgg6","K3eWcGsr6rnYLZlYSHGr","O6ddYSo8S5dpQPeNH5Zz","R7sHDOanFSNEJdNdyuQS","kwAO49REc27mvxk2DWxE","CvsRcUHTshMehJkU8hwA","JQ8UzlGMldeLpAMDjqEd","Zlsx4mIOdgZmZJ3IggIj","s4XEOzHUZvZ1PsaK987f","sanFv5eWjnX0T8zXyFu9","WvAHLx8fBwwF4vCP7MR2","cZY3KQRgUsHHEqsveioj","O2IZpF9lwCRlODytaik8","8ZaPa3I8e7K9XKEUjxyM","NCNCPxdmgZpq5tfWwImK","4RQV6b4cSXWLq9EIQXHy","7fS62US1GkKR2Ac3QURy","lKd4NVg5ilKfa6f9GVlp","pw9vl2m166F1EVro5zOU","sSrLeL0QSDfXxtFbExLk","eTFutueThMz5VMTYYbGH","2sIZj9W3dVX3l9VVsEO9","86yAd5MsjneSfcZR0Byk","B6rTnR6ci5HylIq9juj5","EXHctuig5BkAD5oPYQUs","JzdGKsHqXFXx6wEb7HTU","PAke0a4GYGOm9rqra0Lf","RLTKukJrKF7Q500ZRlgQ","VRD34UvMa6wyUWmr7YRi","ZsvWwdmNGLBgYtW5NXcQ","s4ROnLTL0oS7TcbVa8i4","vgQrhDoKyoJ0xKTDjRId","vr9TLSZZGXL7j7Vkh6CA","yA6YkGcjXz3daXHSx4w3","EpPZjKIHXYy4J9SFLf8S","HrOjt2yQ1uHhKUS43kVS","XduYoOntuPkjiXjCGvrF","et26NBIkwiAJRFZyMdWC","fhL49tF1dhSCOtEhnu47","grdfPcrSnGG3pYykbrv5","vE2BVETqSlG8Iuw7OSpH","J5eT7ZCV9VtGjobF17s3","r1e0YsBA353GWjDSlghx","vqIFF3YAD4qT3fEyqx7s","8hKK1JLEtDsGkGX6dMox","kPvINIdNLoQKxTC2uK0D","KuSJ6hxF0uRSNVezsdGB","JUPofqnU6mgHOD33IPNX","KcoACaLdJ2lHejblCunu","JdEHwekO592gtSSRZ65b","cFsrdtdg9czJCqmYC8Ca","evbwFsGtaXb6bbcivsX0","qqccOZPjbzuIdYQbisMT","gT7QCvtUQqUABi7ZgPXu","06fheheBCupSIEBQIYiB","I6ex2vTDBoW3HHZuMV64"],
               "hasSelectedAll":True,
               "filters":{"startDate":"2025-12-20T00:00:00-03:00","endDate":"2025-12-20T23:59:59-03:00",
                          "status":["paid"],
                          "type":[],
                          "paymentMethod":[],
                          "search":"",
                          "utmSource":"",
                          "utmMedium":"",
                          "utmCampaign":"",
                          "utmContent":"",
                          "utmTerm":"",
                          "dateRangeBy":"createdAt"},
                          "page":1,
                          "pageSize":25,
                          "orderBy":"createdAt",
                          "orderDirection":"DESC"}


    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    response = requests.post(url, headers=headers, json=payload)
    
    df = pd.DataFrame(response.json().get("items"))

    #df.to_excel(r'D:\Projetos\2J\hublasalex.xlsx', index=False)

    #print(response.json())
    if response.status_code == 201:
        #print(response.json())
        return response.json().get("items", [])



    response = requests.get(url, headers=headers)
    #print(response.json())

    return response.json()['items']

"""
Login > Token

Get-Secure-Token

Get-Sign-in-Token

Get-Identity-Toolkit-token


"""

#Processo de autenticação
login_token,refresh_login_token = login()
secure_token,refresh_secure_token,user_id = get_secure_token(refresh_login_token)
sigin_token = get_sign_in(f'Bearer {secure_token}',user_id)
toolkit_token = get_identity_toolkit_token(sigin_token)


import pprint
sales = get_sales(f'Bearer {toolkit_token}')

for sale in sales:
    #
    # print(sale['id'],sale['createdAt'],sale['customer']['fullName'],sale['totalAmount'])
    #pprint.pprint(sale)
    


    produtos = sale['amountDetail']['products']
    taxa_da_hubla = sale['amountDetail']['installmentFeeCents']

    for product in produtos:
        nome_do_produto = product['productName'] #Categoria no OMIE
        valor_do_produtos = product['priceCents'] / 100 
        print(product)

    print(taxa_da_hubla)

