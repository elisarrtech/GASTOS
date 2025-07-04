import streamlit as st
import pandas as pd
import plotly.express as px

# === CARGA DE DATOS ===
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/gastos_mensuales.csv")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    for mes in meses:
        df[mes] = df[mes].replace('[\$,]', '', regex=True).astype(float)
    return df

def calcular_totales_por_estado(df, meses):
    df["Total"] = df[meses].sum(axis=1)
    pagado = df[df["Estado"] == "PAGADO"][meses].sum().sum()
    no_pagado = df[df["Estado"] == "NO PAGADO"][meses].sum().sum()
    return df, pagado, no_pagado

def calcular_alertas(df, meses):
    df["Total"] = df[meses].sum(axis=1)
    alertas = df[df["Total"] > df["Presupuesto"]]
    return alertas

def colorear_estado(val):
    if val == "PAGADO":
        return 'background-color: #d4edda; color: #155724; text-align: center'
    elif val == "NO PAGADO":
        return 'background-color: #f8d7da; color: #721c24; text-align: center'
    else:
        return ''

# === INTERFAZ ===
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos por Mes")

# === DATOS ===
df = cargar_datos()
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
df, total_pagado, total_no_pagado = calcular_totales_por_estado(df, meses)
total_anual = df[meses].sum().sum()

# === FILTROS ===
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))

# Aplicar filtros
df_filtrado = df.copy()
if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]

# === VISUALIZACIÓN ===
st.subheader("📋 Tabla de Gastos")
st.dataframe(df_filtrado.style.applymap(colorear_estado, subset=["Estado"]), use_container_width=True)

st.subheader("🔑 Indicadores Principales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

st.subheader("📈 Gastos por Mes")
total_mensual = df_filtrado[meses].sum().reset_index()
total_mensual.columns = ["Mes", "Total"]
fig = px.bar(total_mensual, x="Mes", y="Total", color="Mes", title="Total por Mes")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Alertas de Presupuesto")
alertas = calcular_alertas(df_filtrado, meses)
if not alertas.empty:
    st.warning("⚠️ Conceptos que exceden el presupuesto")
    st.dataframe(alertas, use_container_width=True)
else:
    st.success("Todos los conceptos están dentro del presupuesto")

# === EXPORTACIÓN ===
st.download_button("📥 Descargar CSV", data=df.to_csv(index=False), file_name="gastos_exportados.csv")
