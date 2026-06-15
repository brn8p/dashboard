import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Dashboard de Monitoramento Logístico")

@st.cache_data
def get_data():
    df = pd.DataFrame({
        "id_entrega":     [ 301,       302,        303,        304,       305,            306,        307,       308,        309,        310        ],
        "transportadora": [ "RotaMax", "ViaCargo", "FlashLog", "RotaMax", "ViaCargo",     "FlashLog", "RotaMax", "ViaCargo", "FlashLog", "ViaCargo" ],
        "regiao":         [ "Sudeste", "Sul",      "Nordeste", "Norte",   "Centro-Oeste", "Sul",      "Sul",     "Sudeste",  "Norte",    "Nordeste" ],
        "prazo_days":     [ 3,         5,          4,          6,         2,              5,          6,         3,          5,          4          ],
        "dias_reais":     [ 7,         5,          9,          4,         6,              12,         9,         4,          5,          8          ]
    })
    return df

df = get_data()

df["atraso"] = df["dias_reais"] - df["prazo_days"]
df["entrega_atrasada"] = df["atraso"] > 0

total = len(df)
atrasadas = df["entrega_atrasada"].sum()
percentual = (atrasadas / total) * 100
maior_atraso = df["atraso"].max()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Entregas por Transportadora")

    dados_grafico = df.groupby("transportadora")["atraso"].sum().reset_index()
    dados_grafico = df.groupby("transportadora").agg(
        total_entregas=("id_entrega", "count"),
        entregas_atrasadas=("entrega_atrasada", "sum")
    ).reset_index()

    st.bar_chart(
        data=dados_grafico,
        x="transportadora",
        y=["total_entregas", "entregas_atrasadas"],
        stack=False,
        # color="transportadora"
    )

with col2:
    st.subheader("Entregas por região")

    # dados_grafico = df.groupby("regiao")["atraso"].sum().reset_index()
    dados_grafico = df.groupby("regiao").agg(
        total_entregas=("id_entrega", "count"),
        entregas_atrasadas=("entrega_atrasada", "sum")
    ).reset_index()

    st.bar_chart(
        data=dados_grafico,
        x="regiao",
        y=["total_entregas", "entregas_atrasadas"],
        stack=False,
        # color="regiao"
    )

df
