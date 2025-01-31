import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from xml.etree import ElementTree as ET
from datetime import datetime
import plotly.express as px

# Configuração do layout do Streamlit
st.set_page_config(page_title="Dashboard de Projetos de Carbono", layout="wide")

# Estilização customizada
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFFF;
        color: #2E8B57;
        font-family: 'Arial', sans-serif;
    }
    .main {
        background-color: #FFFFFF;
        color: #2E8B57;
    }
    h1, h2, h3 {
        color: #2E8B57;
    }
    .sidebar .sidebar-content {
        background-color: #E3F6E3;
        color: #2E8B57;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Carregar dados da planilha
xlsx_path = "projetos_info_verra.xlsx"
df = pd.read_excel(xlsx_path)

# Converter a coluna de datas
df["Data da última verificaçao"] = pd.to_datetime(df["Data da última verificaçao"], errors='coerce')
df["Data de termino"] = pd.to_datetime(df["Data de termino"], errors='coerce')

# ** Filtros condicionais **
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

# Função para carregar coordenadas do KML
def carregar_coordenadas_kml(kml_path):
    try:
        tree = ET.parse(kml_path)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        coordenadas_list = []
        placemarks = root.findall(".//kml:Placemark", ns)
        for placemark in placemarks:
            coords = placemark.find(".//kml:coordinates", ns)
            if coords is not None:
                coordenadas = coords.text.strip().split()
                pontos = [(float(coord.split(",")[1]), float(coord.split(",")[0])) for coord in coordenadas]
                if pontos:
                    coordenadas_list.append(pontos)
        return coordenadas_list
    except Exception as e:
        st.warning(f"Erro ao carregar o arquivo KML {kml_path}: {e}")
        return []

# Mapa interativo
st.header("Mapa dos Projetos de Carbono")
m = folium.Map(location=[-3.0, -60.0], zoom_start=4, tiles="OpenStreetMap")

for index, row in filtered_df.iterrows():
    project_id = str(row["Program Registartion Number"])
    kml_path = f"/Users/avasconcellos/alvaro/proj_carbono/{project_id}.kml"
    if os.path.exists(kml_path):
        coordenadas_list = carregar_coordenadas_kml(kml_path)
        tooltip_info = row["Nome do projeto"]
        for coordenadas in coordenadas_list:
            folium.Polygon(
                locations=coordenadas,
                color="#2E8B57",
                weight=3,
                fill=True,
                fill_color="#B0EACD",
                fill_opacity=0.6,
                tooltip=folium.Tooltip(tooltip_info, sticky=True)
            ).add_to(m)

st_folium(m, width=1200, height=750)

# **Gráficos**
st.header("Gráficos dos Projetos Filtrados")

# Gráfico 1: Pizza com Nome do Projeto x Área do Projeto
fig_pizza = px.pie(
    filtered_df,
    names="Nome do projeto",
    values="Área Total",
    title="Distribuição da Área por Projeto",
    height=500,
    color_discrete_sequence=["#2E8B57", "#6AB187", "#A1DAB4", "#76C2AF"]
)
st.plotly_chart(fig_pizza, use_container_width=True)

# Gráfico 2: Barras horizontais
filtered_df_termino = filtered_df[filtered_df["Data de termino"].notna()]
filtered_df_termino["Ano de termino"] = filtered_df_termino["Data de termino"].dt.year

fig_termino = px.bar(
    filtered_df_termino.sort_values("Ano de termino"),
    x="Ano de termino",
    y="Nome do projeto",
    title="Ano de Término dos Projetos",
    labels={"Nome do projeto": "Projeto", "Ano de termino": "Ano de Término"},
    orientation="h",
    height=600,
    color_discrete_sequence=["#2E8B57"]
)
fig_termino.update_traces(
    text=filtered_df_termino["Ano de termino"],
    textposition="outside"
)

st.plotly_chart(fig_termino, use_container_width=True)

# Gráfico 3: Nome do Projeto x Créditos de Carbono Gerados
fig_creditos = px.bar(
    filtered_df,
    x="Nome do projeto",
    y="Geraçao média anual estimada (tCO2-eq/ha/ano)",
    title="Quantidade de Créditos Gerados por Projeto",
    labels={"Nome do projeto": "Projeto", "Geraçao média anual estimada (tCO2-eq/ha/ano)": "Créditos Gerados (tCO2-eq/ha/ano)"},
    height=500,
    color_discrete_sequence=["#76C2AF"]
)
st.plotly_chart(fig_creditos, use_container_width=True)

# Exibição da tabela filtrada
st.header("Tabela de Projetos Filtrados")
st.dataframe(filtered_df)
