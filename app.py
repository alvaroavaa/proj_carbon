import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from mapa_projetos import plotar_mapa
from graficos_projetos import plotar_graficos
from datetime import datetime
import os

# Configuração do layout
st.set_page_config(page_title="Dashboard de Projetos de Carbono", layout="wide")

# Carregar dados da planilha
xlsx_path = "projetos_info_verra_020225.xlsx"
df = pd.read_excel(xlsx_path)

# Preprocessamento de dados
df = df[df["Program Registartion Number"].notna()]
df["Program Registartion Number"] = df["Program Registartion Number"].apply(lambda x: str(int(x)).strip())
df["Data da última verificaçao"] = pd.to_datetime(df["Data da última verificaçao"], format="%d/%m/%Y", errors='coerce')
df["Data de termino"] = pd.to_datetime(df["Data de termino"], format="%d/%m/%Y", errors='coerce')

# Listar arquivos KML disponíveis
kml_directory = "/proj_carbono"
kml_files = {f.split(".")[0] for f in os.listdir(kml_directory) if f.endswith(".kml")}

# Filtrar projetos com arquivos KML correspondentes
df = df[df["Program Registartion Number"].isin(kml_files)]

# **Filtros no Sidebar**
with st.sidebar.expander("Filtros", expanded=True):
    # Filtro 1: Estado
    estado_filter = st.multiselect("Filtrar por Estado", options=df["State"].unique(), default=[])
    filtered_df = df[df["State"].isin(estado_filter)] if estado_filter else df

    # Filtro 2: Empresa
    empresa_options = filtered_df["Nome da empresa executora"].unique()
    empresa_filter = st.multiselect("Filtrar por Empresa", options=empresa_options, default=[])
    filtered_df = filtered_df[filtered_df["Nome da empresa executora"].isin(empresa_filter)] if empresa_filter else filtered_df

    # Filtro 3: CCB (Cobenefício)
    ccb_filter = st.selectbox("Filtrar por CCB (Cobenefício)", ["Todos", "Sim", "Não"], index=0)
    if ccb_filter == "Sim":
        filtered_df = filtered_df[filtered_df["Possui co-benefícios? quais?"].notna()]
    elif ccb_filter == "Não":
        filtered_df = filtered_df[filtered_df["Possui co-benefícios? quais?"].isna()]

    # Filtro 4: Verificação nos últimos 5 anos
    verificado_filter = st.selectbox("Projetos verificados nos últimos 5 anos", ["Todos", "Sim", "Não"], index=0)
    cinco_anos_atras = datetime.now().year - 5
    if verificado_filter == "Sim":
        filtered_df = filtered_df[filtered_df["Data da última verificaçao"].dt.year >= cinco_anos_atras]
    elif verificado_filter == "Não":
        filtered_df = filtered_df[filtered_df["Data da última verificaçao"].dt.year < cinco_anos_atras]

    # Filtro 5: Tipo de Proponente
    proponentes_filter = st.selectbox("Tipo de Proponente", ["Todos", "Single", "Multiple"], index=0)
    if proponentes_filter == "Single":
        filtered_df = filtered_df[filtered_df["Grouped ou single project"] == "Single"]
    elif proponentes_filter == "Multiple":
        filtered_df = filtered_df[filtered_df["Grouped ou single project"] == "Multiple"]

    # Filtro 6: Tipo de Projeto
    tipo_projeto_filter = st.multiselect("Filtrar por Tipo de Projeto", options=filtered_df["Tipo do projeto (ARR,REDD, ALM, etc)"].unique(), default=[])
    filtered_df = filtered_df[filtered_df["Tipo do projeto (ARR,REDD, ALM, etc)"].isin(tipo_projeto_filter)] if tipo_projeto_filter else filtered_df

    # Filtro 7: Nota das empresas de rating
    rating_options = filtered_df["Nota da agencia de rating"].dropna().unique()
    rating_filter = st.multiselect("Filtrar por Nota das Empresas de Rating", options=rating_options, default=[])
    filtered_df = filtered_df[filtered_df["Nota da agencia de rating"].isin(rating_filter)] if rating_filter else filtered_df

# **Função Cacheada para o Mapa**
@st.cache_resource
def gerar_mapa(filtered_df, kml_directory):
    return plotar_mapa(filtered_df, kml_directory)

# **Mapa**
st.header("Mapa dos Projetos de Carbono")
mapa, cores_projetos = gerar_mapa(filtered_df, kml_directory)

# Exibir o mapa sem loop
with st.container():
    st_folium(mapa, width=1200, height=750)

# **Legenda**
st.subheader("Legenda dos Projetos")
for projeto, cor in cores_projetos.items():
    st.markdown(f'<span style="background-color:{cor}; width:20px; height:20px; display:inline-block; margin-right:10px;"></span> {projeto}', unsafe_allow_html=True)

# **Gráficos**
plotar_graficos(filtered_df)
