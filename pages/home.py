import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos.csv")

df = cargar_datos()

st.title("📊 Dashboard de Gastos Personales")
st.markdown("Filtrá y analizá tus gastos fácilmente.")

# Campo de texto para búsqueda personalizada
filtro_texto = st.text_input("🔍 Buscar en conceptos o descripciones")

# Filtrar por concepto si se selecciona uno
conceptos_unicos = df["concepto"].unique().tolist()
concepto_seleccionado = st.selectbox("📌 Filtrar por concepto", ["Todos"] + conceptos_unicos)

# Aplicar filtros
df_filtrado = df.copy()

if concepto_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["concepto"] == concepto_seleccionado]

if filtro_texto:
    df_filtrado = df_filtrado[
        df_filtrado.apply(lambda row: filtro_texto.lower() in " ".join(row.astype(str).str.lower()), axis=1)
    ]

# Mostrar datos filtrados
st.subheader("📋 Registros filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Gastado", f"${df_filtrado['monto'].sum():,.2f}")

with col2:
    st.metric("📉 Promedio por Gasto", f"${df_filtrado['monto'].mean():,.2f}")

with col3:
    st.metric("📅 Número de Registros", len(df_filtrado))

# Gráfico de barras por concepto
st.subheader("📈 Gastos por Concepto")
grafico_barras = px.bar(
    df_filtrado.groupby("concepto")["monto"].sum().reset_index(),
    x="concepto",
    y="monto",
    title="Total de Gastos por Concepto"
)
st.plotly_chart(grafico_barras, use_container_width=True)

# Gráfico de torta
st.subheader("🥧 Distribución de Gastos")
fig_pie = px.pie(
    df_filtrado,
    names="concepto",
    values="monto",
    title="Distribución de Gastos por Concepto"
)
st.plotly_chart(fig_pie, use_container_width=True)
