import streamlit as st
import pandas as pd
import plotly.express as px

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")

# === CARGA DE DATOS ===
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/gastos_mensuales.csv")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    for mes in meses:
        df[mes] = df[mes].replace('[\$,]', '', regex=True).astype(float)
    df["Total"] = df[meses].sum(axis=1)
    df["Variación (%)"] = round(((df["Total"] - df["Presupuesto"]) / df["Presupuesto"]) * 100, 2)
    return df, meses

def colorear_estado(val):
    if val == "PAGADO":
        return 'background-color: #d4edda; color: #155724; text-align: center'
    elif val == "NO PAGADO":
        return 'background-color: #f8d7da; color: #721c24; text-align: center'
    return ''

# === DATOS ===
df, meses = cargar_datos()
total_anual = df[meses].sum().sum()
total_pagado = df[df["Estado"] == "PAGADO"][meses].sum().sum()
total_no_pagado = df[df["Estado"] == "NO PAGADO"][meses].sum().sum()

# === FILTROS ===
busqueda_rapida = st.sidebar.text_input("🔍 Búsqueda rápida por concepto")
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
    variacion_filtro = st.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])
    mes_filtro = st.selectbox("Mes", ["Todos"] + meses)
    presupuesto_filtro = st.slider("Filtrar por presupuesto", min_value=0, max_value=int(df["Presupuesto"].max()), value=(0, int(df["Presupuesto"].max())))

# === APLICAR FILTROS ===
if busqueda_rapida:
    df_filtrado = df[df["Concepto"].str.contains(busqueda_rapida, case=False, na=False)]
else:
    df_filtrado = df.copy()

if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
if estado_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
if variacion_filtro != "Todos":
    if variacion_filtro == "Positiva":
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] > 0]
    else:
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] < 0]
if mes_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado[mes_filtro] > 0]

df_filtrado = df_filtrado[(df_filtrado["Presupuesto"] >= presupuesto_filtro[0]) & (df_filtrado["Presupuesto"] <= presupuesto_filtro[1])]

# === KPIS ===
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# === TABS ===
tabs = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])

with tabs[0]:
    st.subheader("📋 Registros (Editable)")
    edited_df = st.data_editor(
        df_filtrado,
        use_container_width=True,
        num_rows="dynamic",
        key="editar_gastos"
    )

    if st.button("💾 Guardar Cambios"):
        edited_df.to_csv("data/gastos_mensuales.csv", index=False)
        st.success("✅ Datos guardados correctamente.")
        st.cache_data.clear()

    # === GRÁFICOS MEJORADOS ===
    st.subheader("📊 Comparativo por Categoría")
    categoria_data = df_filtrado.groupby("Categoría")[mes_filtro if mes_filtro != "Todos" else meses].sum().reset_index()
    fig_cat = px.bar(categoria_data, x="Categoría", y=categoria_data.columns[1:], barmode="group", title="Comparativo por Categoría")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("📊 Comparativo por Estado")
    estado_data = df_filtrado.groupby("Estado")[mes_filtro if mes_filtro != "Todos" else meses].sum().reset_index()
    fig_estado = px.bar(estado_data, x="Estado", y=estado_data.columns[1:], barmode="group", title="Comparativo por Estado")
    st.plotly_chart(fig_estado, use_container_width=True)

    if "Año" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Año")
        anio_data = df_filtrado.groupby("Año")[mes_filtro if mes_filtro != "Todos" else meses].sum().reset_index()
        fig_anio = px.bar(anio_data, x="Año", y=anio_data.columns[1:], barmode="group", title="Comparativo por Año")
        st.plotly_chart(fig_anio, use_container_width=True)

    if "Quincena" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Quincena")
        quincena_data = df_filtrado.groupby("Quincena")[mes_filtro if mes_filtro != "Todos" else meses].sum().reset_index()
        fig_quincena = px.bar(quincena_data, x="Quincena", y=quincena_data.columns[1:], barmode="group", title="Comparativo por Quincena")
        st.plotly_chart(fig_quincena, use_container_width=True)

    # === ALERTAS ===
    st.subheader("🚨 Alertas de Presupuesto")
    alertas_df = edited_df[edited_df["Total"] > edited_df["Presupuesto"]]
    if not alertas_df.empty:
        st.warning("⚠️ Conceptos que exceden el presupuesto")
        st.dataframe(alertas_df, use_container_width=True)
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")
    st.dataframe(
        edited_df.style.applymap(colorear_estado, subset=["Estado"]),
        use_container_width=True
    )

    # === EXPORTACIÓN ===
    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

with tabs[1]:
    st.subheader("📈 Histórico por Mes")
    resumen = df.groupby("Categoría")[meses].sum()
    st.dataframe(resumen, use_container_width=True)

    fig_hist = px.line(resumen.T, title="Evolución Histórica por Categoría")
    st.plotly_chart(fig_hist, use_container_width=True)
