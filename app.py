import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Análise de Concorrência – Meta Ads")
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
