import streamlit as st
import streamlit_authenticator as stauth
import requests
import pandas as pd

# ✅ 1. Gera os hashes das senhas (fora do dicionário)
hashed_passwords = stauth.Hasher(["senha123", "segredo456"]).generate()

# ✅ 2. Define os usuários com os hashes prontos
users = {
    "usernames": {
        "agencia1": {
            "name": "Agência Alpha",
            "password": hashed_passwords[0]
        },
        "agencia2": {
            "name": "Agência Beta",
            "password": hashed_passwords[1]
        }
    }
}

# ✅ 3. Autenticador
authenticator = stauth.Authenticate(
    users, "ads-intelligence", "abcdef", cookie_expiry_days=1
)

# ✅ 4. Login
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status == None:
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
