import streamlit as st
import plotly.express as px
import os

# Função para plotar os gráficos
def plotar_graficos(filtered_df):
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

    # Gráfico 2: Barras horizontais com Ano de término
    filtered_df_termino = filtered_df[filtered_df["Data de termino"].notna()].copy()
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

    # Exibir a tabela filtrada
    st.header("Tabela de Projetos Filtrados")
    st.dataframe(filtered_df)
