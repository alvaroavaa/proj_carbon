import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from mapa_projetos import plotar_mapa
from graficos_projetos import plotar_graficos
from datetime import datetime
import os

# Configuração do layout
st.set_page_config(page_title="Dashboard de Projetos de Carbono", layout="wide")

# Caminho do diretório KML
kml_directory = "."

# Carregar dados da planilha
xlsx_path = "projetos_info_verra_020225.xlsx"
df = pd.read_excel(xlsx_path)

# Preprocessamento de dados
df = df[df["Program Registartion Number"].notna()]
df["Program Registartion Number"] = df["Program Registartion Number"].apply(lambda x: str(int(x)).strip())
df["Data da última verificaçao"] = pd.to_datetime(df["Data da última verificaçao"], format="%d/%m/%Y", errors='coerce')
df["Data de termino"] = pd.to_datetime(df["Data de termino"], format="%d/%m/%Y", errors='coerce')

# Listar arquivos KML disponíveis
kml_files = {f.split(".")[0] for f in os.listdir(kml_directory) if f.endswith(".kml")}

# Filtrar projetos com arquivos KML correspondentes
df = df[df["Program Registartion Number"].isin(kml_files)]

# **Filtros no Sidebar**
with st.sidebar.expander("Filtros", expanded=True):
    estado_filter = st.multiselect("Filtrar por Estado", options=df["State"].unique(), default=[])
    filtered_df = df[df["State"].isin(estado_filter)] if estado_filter else df

# **Gerar o mapa**
mapa, cores_projetos = plotar_mapa(filtered_df, kml_directory)

# **Exibir o mapa**
st.header("Mapa dos Projetos de Carbono")
st_folium(mapa, width=1200, height=750)

# **Exibir a legenda separada para evitar loops**
st.subheader("Legenda dos Projetos")
for projeto, cor in cores_projetos.items():
    st.markdown(f'<span style="background-color:{cor}; width:20px; height:20px; display:inline-block; margin-right:10px;"></span> {projeto}', unsafe_allow_html=True)

# **Gráficos**
plotar_graficos(filtered_df)
