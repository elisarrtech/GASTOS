import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos_mensuales.csv")

df = cargar_datos()

# Meses disponibles
meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Convertir meses a numéricos
for mes in meses:
    df[mes] = df[mes].apply(lambda x: float(str(x).replace("$", "").replace(",", "")) if isinstance(x, str) else x)

# Título
st.title("📄 Gestión de Gastos Mensuales")
st.markdown("### Filtra, edita y analiza tus gastos fácilmente.")

# Filtros
col1, col2 = st.columns(2)
with col1:
    categoria_filtro = st.selectbox("🔍 Filtrar por Categoría", ["Todas"] + df["Categoría"].unique().tolist())
with col2:
    concepto_busqueda = st.text_input("🔎 Buscar por Concepto")

# Aplicar filtros
df_filtrado = df.copy()
if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
if concepto_busqueda:
    df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(concepto_busqueda, case=False, na=False)]

# Mostrar tabla editable
st.subheader("📋 Registros Filtrados")
edited_df = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic", key="editar_gastos")

# Guardar cambios
if st.button("💾 Guardar Cambios"):
    edited_df.to_csv("data/gastos_mensuales.csv", index=False)
    st.success("✅ Datos guardados correctamente.")
    st.cache_data.clear()  # Limpiar caché para recargar datos actualizados

# Solo graficar si hay datos
if not edited_df.empty:
    # KPIs
    st.subheader("📈 KPIs Principales")
    total_por_mes = edited_df[meses].sum()
    total_anual = total_por_mes.sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Anual", f"${total_anual:,.2f}")
    with col2:
        st.metric("📅 Promedio Mensual", f"${total_anual / len(meses):,.2f}")
    with col3:
        st.metric("📌 Número de Conceptos", len(edited_df))

    # Gráfico de barras por mes
    st.subheader("📉 Gastos por Mes")
    grafico_barras = edited_df[meses].sum().reset_index()
    grafico_barras.columns = ["Mes", "Total"]
    fig_bar = px.bar(grafico_barras, x="Mes", y="Total", title="Gasto Total por Mes")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de torta por categoría
    st.subheader("🥧 Distribución por Categoría")
    grafico_categoria = edited_df.groupby("Categoría")[meses].sum().sum(axis=1).reset_index(name="Total")
    fig_pie = px.pie(grafico_categoria, names="Categoría", values="Total", title="Distribución por Categoría")
    st.plotly_chart(fig_pie, use_container_width=True)
