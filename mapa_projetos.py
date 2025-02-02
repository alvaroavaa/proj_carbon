import folium
from xml.etree import ElementTree as ET
import os
import random
import streamlit as st

def remove_namespaces(element):
    for elem in element.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
    return element

def carregar_coordenadas_kml(kml_path):
    try:
        with open(kml_path, 'r', encoding='utf-8') as file:
            raw_content = file.read()

        root = ET.fromstring(raw_content)
        root = remove_namespaces(root)

        coordenadas_list = []
        for placemark in root.findall(".//Placemark"):
            polygon_coords = placemark.find(".//LinearRing/coordinates")
            if polygon_coords is not None:
                coordenadas = polygon_coords.text.strip().split()
                pontos = [(float(coord.split(",")[1]), float(coord.split(",")[0])) for coord in coordenadas]
                coordenadas_list.append(pontos)

        return coordenadas_list if coordenadas_list else None

    except Exception as e:
        return None

# Cache do mapa
@st.cache_resource
def plotar_mapa(df, kml_directory):
    projetos_unicos = df["Nome do projeto"].unique()
    cores_projetos = {projeto: f'#{random.randint(0, 0xFFFFFF):06x}' for projeto in projetos_unicos}

    m = folium.Map(location=[-3.0, -60.0], zoom_start=4, tiles="OpenStreetMap")

    for _, row in df.iterrows():
        project_id = row["Program Registartion Number"]
        nome_projeto = row["Nome do projeto"]
        cor_projeto = cores_projetos[nome_projeto]
        kml_path = os.path.join(kml_directory, f"{project_id}.kml")

        coordenadas_list = carregar_coordenadas_kml(kml_path)
        if coordenadas_list:
            for coordenadas in coordenadas_list:
                folium.Polygon(
                    locations=coordenadas,
                    color=cor_projeto,
                    weight=3,
                    fill=True,
                    fill_color=cor_projeto,
                    fill_opacity=0.6,
                    tooltip=nome_projeto
                ).add_to(m)

    return m, cores_projetos
