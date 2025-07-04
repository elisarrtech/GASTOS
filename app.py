import streamlit as st
import pandas as pd
import os

# Configuración inicial
st.set_page_config(page_title="📊 Gastos Mensuales", layout="wide")

# Ruta del archivo
ARCHIVO_GASTOS = "data/gastos.csv"

# Cargar datos
@st.cache_data
def cargar_datos():
    if not os.path.exists(ARCHIVO_GASTOS):
        return pd.DataFrame(columns=["Categoría", "Concepto", "Junio", "Julio", "Agosto",
                                      "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    return pd.read_csv(ARCHIVO_GASTOS)

df = cargar_datos()

# Limpiar valores y convertir a números
def limpiar_monto(valor):
    try:
        return float(str(valor).replace("$", "").replace(",", ""))
    except:
        return 0.0

# Convertir meses a numéricos
meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
for mes in meses:
    df[mes] = df[mes].apply(limpiar_monto)

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
    df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(concepto_busqueda, case=False)]

# Mostrar tabla editable
st.subheader("📋 Registros Filtrados")
edited_df = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic", key="editar_gastos")

# Guardar cambios
if st.button("💾 Guardar Cambios"):
    edited_df.to_csv(ARCHIVO_GASTOS, index=False)
    st.success("✅ Datos guardados correctamente.")
    st.cache_data.clear()  # Limpiar caché para recargar datos actualizados

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

# Formulario para agregar nuevo concepto
st.subheader("➕ Añadir Nuevo Concepto")
with st.form("form_nuevo_concepto"):
    nueva_categoria = st.selectbox("Categoría", df["Categoría"].unique().tolist() + ["Otra..."])
    if nueva_categoria == "Otra...":
        nueva_categoria = st.text_input("Escribe la nueva categoría")
    nuevo_concepto = st.text_input("Nombre del Concepto")
    nuevos_valores = [st.number_input(f"{mes}", min_value=0.0, format="%.2f") for mes in meses]
    submitted = st.form_submit_button("Agregar")

    if submitted and nuevo_concepto:
        nuevo_registro = {
            "Categoría": nueva_categoria,
            "Concepto": nuevo_concepto,
            **{mes: val for mes, val in zip(meses, nuevos_valores)}
        }
        df_nuevo = pd.DataFrame([nuevo_registro])
        df_final = pd.concat([edited_df, df_nuevo], ignore_index=True)
        df_final.to_csv(ARCHIVO_GASTOS, index=False)
        st.success("✅ Concepto agregado y guardado.")
        st.cache_data.clear()
        st.experimental_rerun()
