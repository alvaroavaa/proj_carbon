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

        raw_content = raw_content.replace(
            'xsi:schemaLocation="http://www.opengis.net/kml/2.2 http://schemas.opengis.net/kml/2.2.0/ogckml22.xsd http://www.google.com/kml/ext/2.2 http://code.google.com/apis/kml/schema/kml22gx.xsd"',
            ''
        )
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

    except Exception:
        return None

def plotar_mapa(df, kml_directory):
    projetos_unicos = df["Nome do projeto"].unique()
    cores_projetos = {projeto: f'#{random.randint(0, 0xFFFFFF):06x}' for projeto in projetos_unicos}

    # Inicializa o mapa
    m = folium.Map(location=[-3.0, -60.0], zoom_start=4, tiles="OpenStreetMap")

    # Adiciona os polígonos dos projetos ao mapa
    for _, row in df.iterrows():
        project_id = row["Program Registartion Number"]
        nome_projeto = row["Nome do projeto"]
        cor_projeto = cores_projetos[nome_projeto]
        kml_path = f"{kml_directory}/{project_id}.kml"

        coordenadas_list = carregar_coordenadas_kml(kml_path)
        if coordenadas_list:
            coordenadas_list = [coords for coords in coordenadas_list if coords]
            if coordenadas_list:
                tooltip_info = nome_projeto
                for coordenadas in coordenadas_list:
                    folium.Polygon(
                        locations=coordenadas,
                        color=cor_projeto,
                        weight=3,
                        fill=True,
                        fill_color=cor_projeto,
                        fill_opacity=0.6,
                        tooltip=tooltip_info
                    ).add_to(m)

    # Criar a legenda posicionada no lado direito
    legend_html = """
    <div style="
        position: fixed;
        top: 10px; right: 10px; width: 300px; height: auto;
        background-color: white; border: 2px solid grey; z-index:9999;
        font-size: 14px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Legenda dos Projetos</b><br>
    """
    for projeto, cor in cores_projetos.items():
        legend_html += f'<i style="background:{cor}; width:12px; height:12px; display:inline-block; margin-right:8px;"></i> {projeto}<br>'

    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    return m, cores_projetos
