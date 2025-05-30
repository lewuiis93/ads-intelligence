import streamlit as st
import streamlit_authenticator as stauth
import requests
import pandas as pd

users = {
    "usernames": {
        "agencia1": {
            "name": "Agência Alpha",
            "password": "pbkdf2:sha256:260000$LsBtK6Am6xY0NHYd$81bdb9b8b503ce6e922209ce1c122091aa1e34d0eb05a66ebfc226edb6d56cf9"
        },
        "agencia2": {
            "name": "Agência Beta",
            "password": "pbkdf2:sha256:260000$3ZHpPBJDbYDiNk3u$d905040f1709428274e28d3dca74f30f26bbd224c5ea1ef8d6d37f0543c6833b"
        }
    }
}

authenticator = stauth.Authenticate(
    users,
    "ads-intelligence-cookie",
    "abcdef",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", location="main")

if authentication_status is False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status is None:
    st.warning("Por favor, entre com usuário e senha.")
elif authentication_status:
    authenticator.logout("Sair", "sidebar")
    st.sidebar.success(f"Bem-vindo, {name} 👋")

    st.title("📊 Análise de Concorrentes – Facebook & Instagram")

    access_token = st.text_input("🔐 Access Token da Meta", type="password")
    page_id = st.text_input("📄 ID da Página (ex: 102103993633901)")
    cpm_est = st.slider("💰 CPM estimado (€)", 1, 20, 5)

    if st.button("🔍 Buscar Anúncios") and access_token and page_id:
        url = "https://graph.facebook.com/v18.0/ads_archive"
        params = {
            'access_token': access_token,
            'ad_type': 'POLITICAL_AND_ISSUE_ADS',
            'search_page_ids': page_id,
            'ad_reached_countries': ['PT', 'BR'],
            'limit': 25
        }

        res = requests.get(url, params=params).json()
        ads = res.get("data", [])

        if not ads:
            st.warning("⚠️ Nenhum anúncio encontrado ou token inválido.")
        else:
            results = []
            for ad in ads:
                texto = ad.get('ad_creative_body', 'Sem texto')
                inicio = ad.get('ad_delivery_start_time', 'Desconhecido')
                gasto = (10000 / 1000) * cpm_est
                results.append({
                    "Texto": texto,
                    "Início": inicio,
                    "Estimativa (€)": round(gasto, 2)
                })

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exportar CSV", csv, "anuncios_meta.csv", "text/csv")
            st.success(f"{len(ads)} anúncios encontrados!")
