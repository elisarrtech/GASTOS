import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos_mensuales.csv")

df = cargar_datos()

# Limpiar montos
def limpiar_monto(valor):
    try:
        return float(str(valor).replace("$", "").replace(",", ""))
    except:
        return 0.0

meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
for mes in meses:
    df[mes] = df[mes].apply(limpiar_monto)

# Título con icono
st.markdown("<h1 style='text-align: center;'>📄 Dashboard de Gastos Mensuales</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em;'>Filtra, edita y analiza tus gastos fácilmente.</p>", unsafe_allow_html=True)

# Sidebar - Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + list(df["Categoría"].unique()))
    concepto_busqueda = st.text_input("Buscar Concepto")

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
    st.cache_data.clear()

# Solo graficar si hay datos
if not edited_df.empty:
    # KPIs
    total_anual = edited_df[meses].sum().sum()
    promedio_mensual = total_anual / len(meses)
    total_conceptos = len(edited_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Anual", f"${total_anual:,.2f}")
    with col2:
        st.metric("📅 Promedio Mensual", f"${promedio_mensual:,.2f}")
    with col3:
        st.metric("📌 Número de Conceptos", total_conceptos)

    # Gráfico de barras por mes
    st.subheader("📉 Gastos por Mes")
    grafico_barras = edited_df[meses].sum().reset_index()
    grafico_barras.columns = ["Mes", "Total"]
    fig_bar = px.bar(grafico_barras, x="Mes", y="Total", title="Gasto Total por Mes", color="Mes")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de torta por categoría
    st.subheader("🥧 Distribución por Categoría")
    grafico_categoria = edited_df.groupby("Categoría")[meses].sum().sum(axis=1).reset_index(name="Total")
    fig_pie = px.pie(grafico_categoria, names="Categoría", values="Total", title="Distribución por Categoría")
    st.plotly_chart(fig_pie, use_container_width=True)

def colorear_estado(val):
    if val == "Pagado":
        return 'background-color: #d4edda; color: #155724'  # Verde claro
    elif val == "Sin pagar":
        return 'background-color: #f8d7da; color: #721c24'  # Rojo claro
    else:
        return ''

# Solo mostrar columnas relevantes y aplicar estilo
columnas_estado = [col for col in df_filtrado.columns if col.startswith("Estado_")]
df_mostrar = df_filtrado.drop(columns=columnas_estado, errors='ignore')

# Mostrar tabla con estilo
st.subheader("📋 Registros Filtrados")
styled_df = df_mostrar.style.applymap(colorear_estado, subset=[col for col in df_mostrar.columns if "Estado" in col])
st.dataframe(styled_df)

for index, row in edited_df.iterrows():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.text(row["Concepto"])
    with col2:
        estado_actual = row.get("Estado", "Sin pagar")
        if st.button(f"{estado_actual} 🔄", key=f"toggle_{index}"):
            nuevo_estado = "Pagado" if estado_actual == "Sin pagar" else "Sin pagar"
            edited_df.at[index, "Estado"] = nuevo_estado
            edited_df.to_csv("data/gastos_mensuales.csv", index=False)
            st.experimental_rerun()
    with col3:
        st.markdown(f"<div style='color: {'green' if estado_actual == 'Pagado' else 'red'};'>●</div>", unsafe_allow_html=True)

total_pagado = len(df[df["Estado"] == "Pagado"])
total_saldo = len(df[df["Estado"] == "Sin pagar"])

fig = px.pie(
    pd.DataFrame({"Estado": ["Pagado", "Sin pagar"], "Cantidad": [total_pagado, total_saldo]}),
    names="Estado",
    values="Cantidad",
    title="Estado de Pagos",
    color_discrete_map={"Pagado": "green", "Sin pagar": "red"}
)
st.plotly_chart(fig, use_container_width=True)
