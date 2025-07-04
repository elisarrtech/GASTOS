import streamlit as st
import pandas as pd
import plotly.express as px

# Carga de datos
@st.cache_data
def cargar_datos():
    # ... aquí tu código de carga de CSV y procesamiento
    return df, meses

df, meses = cargar_datos()

# === FILTROS ===
busqueda_rapida = st.sidebar.text_input("🔍 Búsqueda rápida por concepto")
informe_alertas_only = st.sidebar.checkbox("🔍 Solo conceptos con sobrepresupuesto")
st.sidebar.header("Filtros")
categoria_filtro = st.sidebar.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
estado_filtro = st.sidebar.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
variacion_filtro = st.sidebar.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])
mes_filtro = st.sidebar.selectbox("Mes", ["Todos"] + meses)
presupuesto_filtro = st.sidebar.slider("Filtrar por presupuesto", min_value=0, max_value=int(df["Presupuesto"].max()), value=(0, int(df["Presupuesto"].max())))

# Botón para descargar informe
if st.sidebar.button("📄 Descargar Informe HTML"):
    if informe_alertas_only:
        df_informe = df[df["Total"] > df["Presupuesto"]]
    else:
        df_informe = df
    resumen_html = generar_informe_html(df_informe)
    st.sidebar.download_button("📄 Descargar Informe", data=resumen_html, file_name="informe_gastos.html", mime="text/html")
# === Resto del Dashboard ===

# Título y KPIs
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# Tabs
principal, historico = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])

with principal:
    st.subheader("📋 Registros (Editable)")
    edited_df = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic", key="editar_gastos")

    if st.button("💾 Guardar Cambios"):
        edited_df.to_csv("data/gastos_mensuales.csv", index=False)
        st.success("✅ Datos guardados correctamente.")
        st.cache_data.clear()

    st.divider()

    # Gráficos principales
    st.subheader("📊 Comparativo por Categoría")
    cat_data = df_filtrado.groupby("Categoría")[meses].sum().reset_index()
    st.plotly_chart(px.bar(cat_data, x="Categoría", y=meses, barmode="group", title="Gastos por Categoría"), use_container_width=True)

    st.subheader("📊 Comparativo por Estado")
    estado_data = df_filtrado.groupby("Estado")[meses].sum().reset_index()
    st.plotly_chart(px.bar(estado_data, x="Estado", y=meses, barmode="group", title="Gastos por Estado"), use_container_width=True)

    if "Año" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Año")
        anio_data = df_filtrado.groupby("Año")[meses].sum().reset_index()
        st.plotly_chart(px.bar(anio_data, x="Año", y=meses, barmode="group", title="Gastos por Año"), use_container_width=True)

    if "Quincena" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Quincena")
        quincena_data = df_filtrado.groupby("Quincena")[meses].sum().reset_index()
        st.plotly_chart(px.bar(quincena_data, x="Quincena", y=meses, barmode="group", title="Gastos por Quincena"), use_container_width=True)

    st.divider()

    # Alertas
    st.subheader("🚨 Alertas de Presupuesto")
    alertas = edited_df[edited_df["Total"] > edited_df["Presupuesto"]]
    if not alertas.empty:
        st.warning("⚠️ Conceptos que superan el presupuesto")
        st.dataframe(alertas, use_container_width=True)
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")
    st.dataframe(edited_df.style.applymap(colorear_estado, subset=["Estado"]), use_container_width=True)

    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

with historico:
    st.subheader("📈 Histórico por Mes")
    resumen = df.groupby("Categoría")[meses].sum()
    st.dataframe(resumen, use_container_width=True)
    st.plotly_chart(px.line(resumen.T, title="Evolución Histórica por Categoría"), use_container_width=True)
