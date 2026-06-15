import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página do Dashboard
st.set_page_config(page_title="Dashboard de Monitoramento Logístico", layout="wide")

st.title("📊 Dashboard Inteligente de Monitoramento Logístico")
st.markdown("Consolidação de dados operacionais e apoio a análises estratégicas em tempo real.")
st.markdown("---")

# 1. Base de Dados Simplificada (Fornecida no Enunciado)
dados = {
    "id_entrega": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310],
    "transportadora": ["RotaMax", "ViaCargo", "FlashLog", "RotaMax", "ViaCargo", "FlashLog", "RotaMax", "ViaCargo", "FlashLog", "ViaCargo"],
    "regiao": ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste", "Sul", "Sul", "Sudeste", "Norte", "Nordeste"],
    "prazo_days": [3, 5, 4, 6, 2, 5, 6, 3, 5, 4],
    "dias_reais": [7, 5, 9, 4, 6, 12, 9, 4, 5, 8]
}

df = pd.DataFrame(dados)

# 2. Realização dos Cálculos e Regras de Negócio
df["Status"] = df.apply(lambda row: "Atrasada" if row["dias_reais"] > row["prazo_days"] else "No Prazo", axis=1)
df["Dias de Desvio"] = df["dias_reais"] - df["prazo_days"]

# 3. Recursos de Análise: Filtros Interativos na Barra Lateral
st.sidebar.header("🎯 Filtros do Painel")
transportadoras_selecionadas = st.sidebar.multiselect(
    "Filtrar por Transportadora:",
    options=df["transportadora"].unique(),
    default=df["transportadora"].unique()
)

regioes_selecionadas = st.sidebar.multiselect(
    "Filtrar por Região:",
    options=df["regiao"].unique(),
    default=df["regiao"].unique()
)

# Aplicando os filtros ao DataFrame de exibição
df_filtrado = df[(df["transportadora"].isin(transportadoras_selecionadas)) & (df["regiao"].isin(regioes_selecionadas))]

# 4. Estrutura Mínima: Indicadores de Atraso de Alto Nível (KPIs)
total_entregas = len(df_filtrado)
atrasadas = len(df_filtrado[df_filtrado["Status"] == "Atrasada"])
taxa_atraso = (atrasadas / total_entregas * 100) if total_entregas > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📦 Total de Entregas Monitoradas", value=total_entregas)
with col2:
    st.metric(label="⚠️ Entregas Atrasadas", value=atrasadas, delta=f"{atrasadas} críticas", delta_color="inverse")
with col3:
    st.metric(label="🚨 Taxa Geral de Atraso", value=f"{taxa_atraso:.1f}%")

st.markdown("---")

# 5. Visualizações Gráficas Dinâmicas
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🏢 Comparação entre Transportadoras")
    # Gráfico agrupando o total de atrasos por empresa
    df_transp = df_filtrado.groupby(["transportadora", "Status"]).size().reset_index(name="Quantidade")
    fig_transp = px.bar(df_transp, x="transportadora", y="Quantidade", color="Status",
                        barmode="group", color_discrete_map={"Atrasada": "#EF553B", "No Prazo": "#636EFA"},
                        labels={"transportadora": "Transportadora", "Quantidade": "Nº de Entregas"})
    st.plotly_chart(fig_transp, use_container_width=True)

with col_graf2:
    st.subheader("📍 Análise de Atrasos por Região")
    # Gráfico focado em entender quais regiões geográficas estão sofrendo mais
    df_regiao = df_filtrado.groupby(["regiao", "Status"]).size().reset_index(name="Quantidade")
    fig_regiao = px.bar(df_regiao, y="regiao", x="Quantidade", color="Status",
                        orientation="h", color_discrete_map={"Atrasada": "#EF553B", "No Prazo": "#636EFA"},
                        labels={"regiao": "Região", "Quantidade": "Nº de Entregas"})
    st.plotly_chart(fig_regiao, use_container_width=True)

st.markdown("---")

# 6. Priorização Visual dos Maiores Problemas Operacionais
st.subheader("🚨 Priorização Operacional: Ranking de Crises (Maiores Desvios)")
st.markdown("Esta tabela ordena as entregas com base no impacto real no cliente (Dias de Desvio negativos significam entregas adiantadas).")

# Ordenando do maior atraso para o menor (Critério de priorização)
df_ranking = df_filtrado.sort_values(by="Dias de Desvio", ascending=False)

# Função para estilização e destaque automático na tabela
def estila_status(val):
    if val == "Atrasada":
        return "background-color: #FFC7CE; color: #9C0006; font-weight: bold;"
    return "background-color: #C6EFCE; color: #006100;"

st.dataframe(
    df_ranking.style.map(estila_status, subset=["Status"]),
    use_container_width=True
)
