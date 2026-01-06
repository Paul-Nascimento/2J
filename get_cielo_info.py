import requests

def get_sales():
    url = (
        "https://api-digital.cielo.com.br/"
        "cielo-bff-extc-proxy/bff-extc/v1/detalhadoLancamentos/listReceivableReleases"
        "?filters=[]"
        "&startDate=2025-12-01"
        "&endDate=2025-12-07"
        "&pageIndex=1"
        "&pageSize=50"
        "&lncmQtPrclTrns=0,0"
    )

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmRFF2cHA0LUxHUkdObUMtQmdJZHItbzFOUkR0Q0gydXlkcnVFTFlPOU4wIn0.eyJleHAiOjE3NjUxMjU4NzgsImlhdCI6MTc2NTEyNTI3OCwianRpIjoiMmJiNmM3YjktZjBiOC00ZjMxLTk0NGQtMTcxNTg2Y2ZmNzk2IiwiaXNzIjoiaHR0cHM6Ly9yaHNzby5lbnRlcnByaXNldHJuLmNvcnA6NDQzL2F1dGgvcmVhbG1zL011bGVzb2Z0UFJEIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijc1NTEyMjQ4LTdiZjctNDczNi04MTFhLTQ0MWJkZmFiMGUyZCIsInR5cCI6IkJlYXJlciIsImF6cCI6Ijk0NjRhNGEyLTI0M2EtNGNhOS05ODRiLWRhZjY3NDhlNGY3YyIsInNlc3Npb25fc3RhdGUiOiJmNDc3MzU0ZS02YWI4LTQ3ZjktYTk1OC00OGI5MzY5YjJmMzkiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6ImY0NzczNTRlLTZhYjgtNDdmOS1hOTU4LTQ4YjkzNjliMmYzOSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SWQiOiI5NDY0YTRhMi0yNDNhLTRjYTktOTg0Yi1kYWY2NzQ4ZTRmN2MiLCJjbGllbnRIb3N0IjoiMTAuODIuMzAuNiIsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC05NDY0YTRhMi0yNDNhLTRjYTktOTg0Yi1kYWY2NzQ4ZTRmN2MiLCJjbGllbnRBZGRyZXNzIjoiMTAuODIuMzAuNiJ9.E5R3b10zABus6pMVCMNtCxUsjg5wDMzbjWl7ws4g8zBpKf5tn6aUa5ELI6F91lUKuHvRFtnIL6-ybuMG4VzQevm_fV72SMcv4Hb3cVaNYDd_UVBHPxaVXUi6f6Mj6CfCw9VfKyqvZ2foi0b2uvysCSOXHR86DtT6_BpiP9KgbYZ7grjhkjsJXrUL1ZdwREb0DFoZo96cBvmAQHC-Zz9JdhYOmCcH70w66ONud3oBbrRpXYvJJYdjX4Tb7Ts0ZhJQxvXtS02VA1qLWuMZLljC6hnAb8Jq6wgEieb_KRHJTKFSJpU2Ce0ssdSU0qN5zebBl6lEFKGYqvgdm133pFW6sw",
        "content-type": "application/json",
        "origin": "https://minhaconta2.cielo.com.br",
        "referer": "https://minhaconta2.cielo.com.br/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "userid": "c098713fc3988e54df0626fc00345c112b3689fbbbfa60d00bd65f4854735fba",
    }

    resp = requests.get(url, headers=headers)

    print("Status:", resp.status_code)
    print(resp.text)

def get_merchants():
   

    url = "https://minhaconta2.cielo.com.br/accounts/merchants"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,pt-PT;q=0.8,pt;q=0.7",
        "authorization": "Bearer eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2Iiwia2lkIjpudWxsLCJjdHkiOiJKV1QiLCJwMmMiOjgxOTIsInAycyI6IjN4TUlKWldVdkFoQjFMTksifQ.L2ECPCsGCtJI2zZfMHXN_xYPvEnSQcNEjE1ktXrNhOaF6M-5uddknw.4sv_YZiD367lzGQh0kJDAw.5yzVr_HDtHvmPwOgWGNIMjsDQGoOvs-jrnVlivvtvngUrPqYekOCRXM8zvQSOzB1y9JrCP1L0dAw_uA3J1YWqh8a6Vu7zGk98-blmE8V8uVOiWt2qEvSf9oLBxs_V3oa9M1JjVT6kXUgW4HGk-b1OqsXcpKrpFLcUFAU19mofDu-ZPcEWLoQcbQzhW-UBalY-xHdB6xf8MSlrIBs9HVpipnUVTFWNaK6Qz76jvTvy0btWBBDdqgcLtI7BCI176XFGHjsganUDAb8CxmL2zjUw6zxtXmuL4f7hT0MxjduFL_OdmjS5Ba6SpJIPaYqSyOPKthrkHBZsjgzfx9mynNT--tQ6DZyEn9nnmt087F9Eit4DuJWW5BR4wndHspiegQN_vhz2FbCKYd1Nokb4U1iipDWRAXYyvmf5JuMDsT1KmrDW-jMyE0Vnb7ECRt6SzPA-EfPGk76SBbgVS_Euj1I3xm5kqcXFn2b2JX8XkXg0uIq0rQNvE9p1RE8eka3nupTtIvnJepsHoy_yFjNGJoqn1VmHGBPLkQhVQ-zT9vSc5XIF1BanLuMgfySASOJnBAr9l22zfSDEWmNgAieLaMjIum9pTjurE3gXHFO1T5e5ERCEdkCCxs2EpVAeE7-sIr91wGetKLodLlLhQMdEbAfiXScL0D76jPM82KbxZZjHbeMPMwGGIBPahsum4LSnAnBAcOmBgEzWhL1u9wnMSZ-vQtwSHfPmI0Nt5CbvLwAzrofmYknPKN9tberYXYxM8gg6f92WUIUFV-IDfAPHvvdBw8VkAWGnvYvEbTEhsfrlhr9G5x7NHQ-xKGbdHBdK2Ga5NecVIGNngh1__Wfb2H08XbZN7X0702JvBoUMrAQBp_Q_hYXif0Wkd5MRXNWNqvm3ia3sjrRhLIeHKT9jszwcjz-HxutPN1hafmE2UFutgSy1YZhJNWmF3-97x71kat2YXlkROxqtYEAQfuX9U7V-PkyZCukEcRSs-zNte2p9TN5QmuiTixluo21EnmQQzrNlIfydkPaSNSoPXgJVDulsQcllX8-FAkxwqs36XFybjotoI-aU6NJJa7NyikEZIgl1TtLBsTJAE1NfX7QAm0tXBkMLwtL1_v3Y5a9obT2TtabMTp2yrGvGK0mD-bfrt360P2vo5BSz9dVHIbrV9Qd85-takTzyc_rGFuy-7WJpfWnFbF1XI8cVaONDB_YT1YSOIgzaEXyotxaGhMM4nXW6BDoT4CYtcwVU8wWImse0Rno2upNTtLrkpX67KeARlg2cM-KT6ssqOVOQrFIfwZ8uuFgl9oWM65Ssc3xp0tkYuDcveLRgDZwD-fpmxynBs7_xED4Ywax0FFylVB_GTEtrwKEiSfOkmkgB5G2flD5A3y_OHlgzBcIv_Iq83hb0dLCeM9FsJKqkZQaKU0_qz159R1pJtB21rxWlxDH5HWFHGERQAXnIbt7jAkj8TraKdc2ijJ5veVpKE4I1uRqvvK-8DrSSZtPw7auLEUPMUgu9Rl93p0CoILYsyhZOAqekUaJfExBlYnYgYJjiYEhXdvfHHeD9tNqeBiCKi0gWjEYeR7j8QUfNkvtu4BU_nxrTJItHCR8_s9BWrhIu6-0_Kq6q5tICLAhZVBnJ8qrfFWmK0tOuIEplGLp-4n-MGZG6aYPEoeFRWT7sXBOjvr-5SmbHAbBQyjK5sYsATGEjlOOYqtAdPcrqlyO_MJY7d03j8rlmJUbsMy3pMRD0vczIfVbppNuLJklehPzjGmumH80A419JLVVscyYTOT5i-jQ1rNTvTi3zAgXyzxJ9Qg1R23MO5X6Bfh6Ls0xW8rSm5XMiZCXXvTV9J-oeFQw7GAucW_wpbjEFMT_M4BisYqsg077m25zFm5Nkf5N2Y82I11C8wsQEUOE7QnPPKG2mOlgbiKDlb04WPsJvhjfs7YAEevVS-bLx2wbzxJGNEfGnUj3hhClJ42tLxLkdTZIecEw1zo6nhbWMvXoMNcKujTQgXc2xv3bWhqrBsjVa9VFeZjC0SHduwszZqLq57LauuiOscAyDc_7aVSN-Oiv2OR0S-vTOHtrNKkXQZAz0QAWkqlF0HbZGUIzSLy3Vd2NoWpT8ODW9cmbLtEV39SvZDn59niLiMK3kAObIXvK84KXzlq1wlvAuVO6pZUH7yQ5TtQNe0tRaN-ezMQh5tGo_eDixVaOnWnGD4Bm7S0DRdWgW7Z209SA9bU9YX5pB36j28_wQreddADHy25qSYdjTNSWUqbGpREHScpBxBatTedQ3EPXW6qY8vvqix5ePeJdN3xDtij4PkElEaZpWv7x4OvX0Ihn4jcZ8D4jE_LuQQhNvCbPx0Uz2q-VNc-LekygrEi0YDFQ5fjercDxhUyu3YhWeSmZV1bwOsHDXk8D_3P9GyeSJxCuWA9PvU2QFt2XHn92tEoyVPJSNxnBzzpIjyaE4tHP3lXy0qUqGrKvmAXqDXOcKrH8i9MEeyQrDwLPLD3vp3PbkmdxJEobWw3RD3CQbCtxyBig7n1gm8_J3WKdeedRDWIZbElCV4bzrbDVucRieq__FwVNY6rwAaOxpkT46jf6BP1vyCRWtDbxBLo1uU658S5o5sVoJjKwbSdH7u45SOpzZaZTMBjcNGxTUiYoWbP7xEBSo6P1BR0Se0LlzrODxghDq7qLOmVNiqaAWtWv1YA_Q10Ne5taz4U6sje7u7WxnRa0ztknSCXlQNjQ3J0b6lUirefv3tTeVwAX8_GWFq0EL4nKwSFsUCGFozlPY7LYUH_TKCvh7xCzquGrqLB0Vj-hh_MIOxjT9F5zxvH7VxXj2r5Ghih6zVIE_yVZpAVXYM3C2o8WB8FAtpJj1DgD-by-FXM3ZRE3oML8CFH3Hb-hBLljUT1GhbDEJ1Rw0UXLviZkegZNXcsBp8I0dz1pTfRQzR6VvuTkSdkAGAbie1zevmCZN4BSaETruou5SHusqWkSht7cYnIYAf8zqLxH1vo3icOSFWhcYBe1YFJW8qkuYSQusz8vn-urDk_j4IIxIy3UIMWzy9ls9N_kTKLwblW6HUGeN56k2hxbxLLpfRind_tdT_V2y69mLNyiC_EqfFtDST3iwmU1uMPV7PUtJpgIvPxGV7PynX91RCXSVPWn3Rl2XJSWY4WLDRrBk9vkCKCKlW43ucTKOQl15W73ZYQNLYcLJPR82fZcjxUKarlwkH6RQgZqFy62qAU1xnYfhV0xoNRwm9EKDivOTdqpQEZK9ORNgAFLp1CEq7eOCz-PXRIWxnpu9FHkEHwDNPSEOvQY0sKm35zNoEGUT6OPlDIHMZS5LyyidX4p3V-ZAvUe_ZgEE0xALbV_HJuLkYQ94jtvoxpMZ72l1PE-sqImrugDRFVP5f-jcDENutOmbvjBv34wyKbApvMtn_8nG6wvra4dbBYHXUbmCQXS4honwv7j1BxZWh1V2LV5JHIt_8mBTJmvaECYxMjcWuVdStKFR0kJU3hmGYarXz4r6r314Xz_QOb6OWSw4qlWyCYuR8iBotUImPl8O4oxz97r8Bh2rpYw4QbyJ8CkAJzbxs7c0mQUtK0xMhfzNB6olunyO0QlQb5_KIau2eYd2cWJrC5wTgg8rJCTxMN80zRNugd8sWaGnG0vn-3cftYKmP0QwrW2u_2kLfId8ACPZFeqm47j1Jca0HP2Uok8rtG3XMh-IBmNO6IjLz4pyj8Myr9c35kkP_FAZPfNbEN0QrbhHXzygj365dlIgZZTw0gHqKnFqxa6CiisppODa7XGGWkr7jySrI4AoYuCMrZCDASTJtYkSW7fYiuCoQ-rJnyMKJ22qe03-IY8FbFNWVNgCz1UIcH2XOJg-BA2zN_8DTw4NleVN8uPMJL2mlq050cEk8CItHk_qIpndbQaTlsQyftM_VHqv2QU9DzZwAJRuLL9TMQdLfR3fBj5Q6fEpb6CWjtgX36TqJkxmVkA0A31xJ7Vf6TvyJi46um_OL8F7JmTtBdTbQT4T2dFpL_reTys4Z3D7PCyd9MwV58wxieo-U87T70gggWK6UCB9uEEZWcta16QcWFhwZPkB5VCmxH5LbrD7roL09wAExt3hwujGo2QZxh0f9XNfDxD2czHHJQyjJrSGLziKQE_9R_yTC_5rT12OBOPS6F_RVq8Bxa8nGGD4Cd-hQQuL2stl41h_W1JjTw16hqyieTg5hbJu1jo7O6RcyUGr1AQr-fu_1UY-tb_XEva0qBTIwA2PiBdtygW4pZ6dY9DpSQNP2JbIs711xmwfLl7Ku8xi7LI1wq-oaHijs3-0R08F_npccrswsXbNOUNSsz1utkfmK_-MnGPFf9EtwN2RhZe-WxTpC-6jeVRo-wigQdb2QXZH7-dCifFoMEIyjlw40TS9B5jg_nu_heWGe5unAYXfq5LPjwE0nRdST9tLtS9faInWwrY47vcw--d2Z5l-UbpYxL3HOAC6QnZpUllbSCgEu5PhcX7-8yYTd-kLsUo4RhpK4pGK6DhRdD3syatn0EfM4KY-3yL8RlK--A2-URISb2mVg2uN2Dq7Arx.gHFyqlDP2wBZIKRpEUksGw",
        "client-id": "SITE",
        "client-name": "SITE",
        "referer": "https://minhaconta2.cielo.com.br/site/recebiveis/detalhado/lancamentos",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.text)

def lg_cielo():
    import requests

    url = "https://api-digital.cielo.com.br/cielo-digital-security-sys/oauth-digital/v1/authentication"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,pt-PT;q=0.8,pt;q=0.7",
        "content-type": "application/json",
        "origin": "https://minhaconta2.cielo.com.br",
        "referer": "https://minhaconta2.cielo.com.br/",
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "tokenkey": "0cAFcWeA5yrPtUjuUH22jVWyQx8TkLt7cR421aeQO_CnvWm9Se3HNGyr9FQSREeJXqR5Wz3Bj2InknNzWM9vUNIU-ADE8QEsI8uZMs_aSMHuWAqIoobmXTz53buPVZC36EHbje9XzXgdgcFwPyC1T0oG8OoSnvybtRdC-WtwEX0sZ5S04M8MksJzmVVkphZbglzV109tyRM9QmBmiKB7oB15yGCTToKnP2fGoDL_UesDEmO_akWsGcF2UJcg7ZsfRwnhZdXeT9PoCluHqChM-93mYBhP-2dZlzrGgRl9LNW09RvldigvjlT8lMsiU2I47FUfyGP0r0Uei6FOSFPPNsBNjq--ZUZF-EnQgY63Z_zFo8FvgCP7qlXl3JJzGAJReILWq6u_p3gszTKNaAV8_pP9TKP1iGf7kU6xSu91n_eMdErEkuy-UnwBiVmg2j0j_2uoihCtPX5T-NFzlN-h4MgweRbuQPiviaa_vZMTywEjtr0hZthHkvI5HqxxcrVk1qTEb1u1-QOkI3w87pTqBKgJegWjxYIAYDpfgMtPxlT25d6svV-SW9emMwqHNGB_18P6_CPVXUL8Ph9pQ8DvYtJo6Y6LoJha0wmqGt5fN2P4PtCSu21smDO7ws-PT5v2tlIiRYAqiWy18U58DINBL4V9qLeQ6jF45aT7tNNAYnY1snu1O-vLzS9IQkXOkdAhx488jyfLp4x3LvnDca0LngQ5HFGBoxfALP9fPUyfzs0UWNBXdNdPh8hj0WHJvfJw1pbZ-qyHcVbQ3eMdd6sRGD5oRnfmOKKMH3OLWxJ-pbpdgtDEXy8MAMwjwAErT0LK1p8lv664EbLw57GCki3QgX9H39kBZMNujETnRIbPK3Gf7u80Bp-93BkWhOlO2wf9RITdLOm9pdg1Jx4rtDvfUyborYSIIenqcAwSfz8-dTeV36SUUynHr9vd_uiC79a-yl8SmRvs0nJFzk2wgmshYAa2P764jUgqy_97nGDY1JugmLWDCsEAaVTsmhx5LAJ0gJeuYriSl9kfbXYNjQ7Wx6VoT2noFbWXsTzvhub0nMLE-8iMo2J0SuJqVe9sV2cfSLzDybqx4f-3ckDjUp7pvFp0hbC3wDNyTdSzfWC2Do5NHZakJwrDKPKugMnYBxruKrnwVAlXAQP9i8GocKfYXcpK6RYcv4pWL6PLHOeVFWw34nppAH9PFYmGleOQHAehTKPRhpMZGmxILTop9zeJUCAP4StE_gzuWGFHl8hnER48WkhuOFXFfVWxhxl-2H1OF5oqLwKtkbnKn34SMB_8m2j7jS42qu_lH4lImjdwkdxBHd_413qi2QTNvr1M_81RomE6Elz-p5MURui2x4J8_6uLc72oWOy57yzanIjeFRP7XwhOaxVrbvhuHYIdYETuHNi_xDGbFN3qwm2bizc5jwPsCPOpb7EhSg-RDdFniTWmUS2mMRvxVeOZ1nsc4snM20H9N2wBUpTEdBh9Z8ihVTtBQZddM7m7pqGr_5VGac2cWFYpoggsWi-6EUMAQ-wvCFBWWtz54YNVtVDvWw6KiSBYHlO6z5TmapB-GWXS3rvea1m8mFeeimIuD_QkbTKjPBLuKWAsrda_dO_aXTZC2lSOcJ1hlZhFbi0AoX-1920FIMMZLnTFz_kX9_df4lMGaf5U4FeBjfWPn1",
    }

    payload = {
        "password": "250998",
        "username": "arthurloboabreu@gmail.com",
        "activeMerchant": "1097386276",
        "hierarchyLevel": "POINT_OF_SALE",
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.status_code)
    print(response.text)


lg_cielo()