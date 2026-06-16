# dashboard - desafio dos dados
# importando módulos
import streamlit as st
import pandas as pd


def preparar_grafico(df, coluna):
    dados = (
        df.groupby(coluna)
        .agg(
            total_entregas=("id_entrega", "count"),
            entregas_atrasadas=("entrega_atrasada", "sum")
        )
        .reset_index()
    )

    ordem = (
        dados.sort_values(
            by="entregas_atrasadas",
            ascending=False
        )[coluna]
        .unique()
        .tolist()
    )

    dados[coluna] = pd.Categorical(
        dados[coluna],
        categories=ordem,
        ordered=True
    )

    return dados.sort_values(coluna)

def colorir_atrasadas(row):
    if row.entrega_atrasada:
        return ['color:#FF5050'] * len(row)

    return [''] * len(row)


#### configuracoes e calculos
# a pagina vai ocupar toda a tela
st.set_page_config(
    page_title="Dashboard de Monitoramento Logístico"
)

st.title("Dashboard de Monitoramento Logístico")

# tabela com dados
df = pd.DataFrame({
    "id_entrega":     [ 301,       302,        303,        304,       305,            306,        307,       308,        309,        310        ],
    "transportadora": [ "RotaMax", "ViaCargo", "FlashLog", "RotaMax", "ViaCargo",     "FlashLog", "RotaMax", "ViaCargo", "FlashLog", "ViaCargo" ],
    "regiao":         [ "Sudeste", "Sul",      "Nordeste", "Norte",   "Centro-Oeste", "Sul",      "Sul",     "Sudeste",  "Norte",    "Nordeste" ],
    "prazo":          [ 3,         5,          4,          6,         2,              5,          6,         3,          5,          4          ],
    "dias_reais":     [ 7,         5,          9,          4,         6,              12,         9,         4,          5,          8          ]
})

df["atraso"] = df["dias_reais"] - df["prazo"]  # adicionar tabela de atraso

df["entrega_atrasada"] = df["atraso"] > 0  # adicionar campo booleano de entrega atrasada


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

#### KPIs

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    total = len(df_filtrado)
    atrasadas = df_filtrado["entrega_atrasada"].sum()

    percentual = (
        int((atrasadas / total) * 100)
        if total > 0
        else 0
    )

    st.metric("Entregas atrasadas",
        f"{atrasadas}/{total} ({percentual:.0f}%)"
    )
    st.progress(percentual)

with kpi2:
    media_atrasos = (
        df_filtrado.loc[
            df_filtrado["entrega_atrasada"],
            "atraso"
        ].mean()
    )

    if pd.isna(media_atrasos):
        media_atrasos = 0

    st.metric(
        "Média de tempo de atraso",
        f"{media_atrasos:.0f} dias"
    )

with kpi3:
    maior_atraso = df_filtrado["atraso"].max()

    if pd.isna(maior_atraso):
        maior_atraso = 0

    st.metric(
        "Maior atraso",
        f"{maior_atraso} dias"
    )


#### Gráficos

col1, col2 = st.columns(2)

with col1:
    st.subheader("Entregas por transportadora")

    dados_grafico = preparar_grafico(
        df_filtrado,
        "transportadora"
    )

    st.bar_chart(
        data=dados_grafico,
        x="transportadora",
        y=["entregas_atrasadas", "total_entregas"],
        x_label="Transportadora",
        stack=False,
        color=["#b22222", "#0068c9"],
        height=400,
    )

with col2:
    st.subheader("Entregas por região")

    dados_grafico = preparar_grafico(
        df_filtrado,
        "regiao"
    )


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

st.dataframe(
    df_ranking
    .style.apply(colorir_atrasadas, axis=1),
    hide_index=True,
    column_config={
        "id_entrega": st.column_config.NumberColumn("ID entrega"),
        "prazo": st.column_config.NumberColumn("Prazo", format="%d dias"),
        "dias_reais": st.column_config.NumberColumn("Dias reais", format="%d dias"),
        "atraso": st.column_config.NumberColumn("Atraso", format="%d dias"),
        "entrega_atrasada": None  # st.column_config.CheckboxColumn("Entrega atrasada"),
    })
