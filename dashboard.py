# dashboard - desafio dos dados
# importando módulos
import streamlit as st
import pandas as pd


#### configuracoes e calculos
# a pagina vai ocupar toda a tela
st.set_page_config(layout="wide")

st.title("Dashboard de Monitoramento Logístico")

# tabela com dados
df = pd.DataFrame({
    "id_entrega":     [ 301,       302,        303,        304,       305,            306,        307,       308,        309,        310        ],
    "transportadora": [ "RotaMax", "ViaCargo", "FlashLog", "RotaMax", "ViaCargo",     "FlashLog", "RotaMax", "ViaCargo", "FlashLog", "ViaCargo" ],
    "regiao":         [ "Sudeste", "Sul",      "Nordeste", "Norte",   "Centro-Oeste", "Sul",      "Sul",     "Sudeste",  "Norte",    "Nordeste" ],
    "Prazo":          [ 3,         5,          4,          6,         2,              5,          6,         3,          5,          4          ],
    "dias_reais":     [ 7,         5,          9,          4,         6,              12,         9,         4,          5,          8          ]
})

df["atraso"] = df["dias_reais"] - df["Prazo"] # adicionar tabela de atraso

df["entrega_atrasada"] = df["atraso"] > 0 # adicionar campo booleano de entrega atrasada

total = len(df) # quantidade total
atrasadas = df["entrega_atrasada"].sum() # quantidade atrasadas
percentual = int((atrasadas / total) * 100) # percentual atrasadas

#### Filtros

filtro_transp, filtro_regiao = st.columns(2)

with filtro_transp:
    sel_transp = st.multiselect(
        "Transportadora",
        options=df["transportadora"].unique(),
        default=df["transportadora"].unique(),
    )
    if sel_transp == []:
        sel_transp = df["transportadora"].unique()

with filtro_regiao:
    sel_regiao = st.multiselect(
        "Região",
        options=df["regiao"].unique(),
        default=df["regiao"].unique(),
    )
    if sel_regiao == []:
        sel_regiao = df["regiao"].unique()

df_filtrado = df[(df["transportadora"].isin(sel_transp)) & (df["regiao"].isin(sel_regiao))]

#### PKIs

pki1, pki2 = st.columns(2) # 2 colunas

with pki1: # coluna 1
    st.metric("Entregas atrasadas", f"{atrasadas}/{total} ({percentual:.0f}%)")
    st.progress(percentual)

with pki2: # coluna 2
    media_atrasos = df_filtrado["atraso"].sum() / df_filtrado["entrega_atrasada"].sum()
    st.metric("Média de tempo de atraso", f"{media_atrasos:.0f} dias")

# with pki3:


#### Gráficos

col1, col2 = st.columns(2) # 2 colunas

with col1: # coluna 1
    st.subheader("Entregas por transportadora")

    dados_grafico = df_filtrado.groupby("transportadora").agg(
        total_entregas=("id_entrega", "count"),
        entregas_atrasadas=("entrega_atrasada", "sum")
    ).reset_index()

    ordem_regioes = (
        dados_grafico.sort_values(by="entregas_atrasadas", ascending=False)["transportadora"]
        .unique()
        .tolist()
    )

    dados_grafico["transportadora"] = pd.Categorical(
        dados_grafico["transportadora"], categories=ordem_regioes, ordered=True
    )

    dados_grafico = dados_grafico.sort_values("transportadora")

    st.bar_chart(
        data=dados_grafico,
        x="transportadora",
        y=["entregas_atrasadas", "total_entregas"],
        x_label="Transportadora",
        stack=False,
        color=["#b22222", "#0068c9"],
        height=400,
    )

with col2:  # coluna 2
    st.subheader("Entregas por região")

    dados_grafico = df_filtrado.groupby("regiao").agg(
        total_entregas=("id_entrega", "count"),
        entregas_atrasadas=("entrega_atrasada", "sum")
    ).reset_index()

    ordem_regioes = (
        dados_grafico.sort_values(by="entregas_atrasadas", ascending=False)["regiao"]
        .unique()
        .tolist()
    )

    dados_grafico["regiao"] = pd.Categorical(
        dados_grafico["regiao"], categories=ordem_regioes, ordered=True
    )

    dados_grafico = dados_grafico.sort_values("regiao")

    st.bar_chart(
        data=dados_grafico,
        x="regiao",
        y=["entregas_atrasadas", "total_entregas"],
        x_label="Região",
        stack=False,
        color=["#b22222", "#0068c9"],
        height=400,
    )


#### tabela
df_ranking = df_filtrado.sort_values(by="atraso", ascending=False)

def destacar_atrasadas(row):
    style = [''] * len(row)

    if row.entrega_atrasada == 1:
        # Apply the style to specific columns or the whole row
        return ['color:#FF5050'] * len(row)

    return style

st.dataframe(
             df_ranking
             .style.apply(destacar_atrasadas, axis=1),
             hide_index=True,
             column_config= {
                "id_entrega": st.column_config.NumberColumn("ID entrega"),
                "Prazo": st.column_config.NumberColumn("Prazo", format="%d dias"),
                "dias_reais": st.column_config.NumberColumn("Dias reais", format="%d dias"),
                "atraso": st.column_config.NumberColumn("Atraso", format="%d dias"),
                "entrega_atrasada": None # st.column_config.CheckboxColumn("Entrega atrasada"),
             })
