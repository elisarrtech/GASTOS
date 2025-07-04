import streamlit as st
import pandas as pd
import plotly.express as px

# === IMPORTACIONES PERSONALIZADAS ===
from utils.data_loader import cargar_datos, limpiar_monto
from utils.styles import colorear_estado
from utils.alerts import calcular_alertas

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")

# === ESTILOS PERSONALIZADOS ===
st.markdown("""
<style>
    body {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# === CARGA DE DATOS ===
df = cargar_datos("data/gastos_mensuales.csv")

# Meses y limpieza
meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
for mes in meses:
    df[mes] = df[mes].apply(limpiar_monto)

# === SIDEBAR - FILTROS ===
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

# === PESTAÑAS PRINCIPALES ===
tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])

# === TAB 1: DASHBOARD PRINCIPAL ===
with tab1:

    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>📊 Dashboard de Gastos Mensuales</h1>", unsafe_allow_html=True)
    st.caption("<p style='text-align: center; font-size: 1.1em;'>Monitorea, controla y analiza tus gastos de forma simple y visual.</p>", unsafe_allow_html=True)

    st.subheader("📋 Registros Filtrados (Editable)")
    edited_df = st.data_editor(
        df_filtrado,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Estado": st.column_config.SelectboxColumn(
                options=["PAGADO", "NO PAGADO"],
                required=True
            )
        },
        key="editar_gastos"
    )

    if st.button("💾 Guardar Cambios"):
        edited_df.to_csv("data/gastos_mensuales.csv", index=False)
        st.success("✅ Datos guardados correctamente.")
        st.cache_data.clear()

    st.divider()
    st.subheader("🔑 Indicadores Principales")

    total_anual = edited_df[meses].sum().sum()
    promedio_mensual = total_anual / len(meses)
    total_conceptos = len(edited_df)
    total_pagado = edited_df[edited_df["Estado"] == "PAGADO"][meses].sum().sum()
    total_no_pagado = edited_df[edited_df["Estado"] == "NO PAGADO"][meses].sum().sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Total Gastado Anual", f"${total_anual:,.2f}")
    col2.metric("💰 Total Pagado", f"${total_pagado:,.2f}")
    col3.metric("⏳ Pendiente por Pagar", f"${total_no_pagado:,.2f}")
    col4.metric("📅 Promedio Mensual", f"${promedio_mensual:,.2f}")

    st.divider()

    st.subheader("📈 Gastos por Mes")
    gastos_por_mes = edited_df[meses].sum().reset_index()
    gastos_por_mes.columns = ["Mes", "Total"]
    fig_bar = px.bar(gastos_por_mes, x="Mes", y="Total", title="Total por Mes", color="Mes")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📊 Distribución por Categoría")
    gastos_por_categoria = edited_df.groupby("Categoría")[meses].sum().sum(axis=1).reset_index(name="Total")
    fig_pie = px.pie(gastos_por_categoria, names="Categoría", values="Total", title="Distribución por Categoría")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    st.subheader("🚨 Alertas de Presupuesto")
    alertas_df = calcular_alertas(edited_df, meses)

    if not alertas_df.empty:
        st.warning("⚠️ ¡Hay conceptos que exceden su presupuesto!")
        st.dataframe(alertas_df, use_container_width=True)
    else:
        st.success("✅ Todos los conceptos están dentro del presupuesto.")

    st.divider()

    st.subheader("📄 Tabla con Estado Visual")
    styled_df = edited_df.style.applymap(colorear_estado, subset=["Estado"])
    st.dataframe(styled_df, use_container_width=True)

    st.divider()

    st.subheader("📤 Exportar Datos")
    st.download_button(
        label="📥 Descargar CSV",
        data=edited_df.to_csv(index=False),
        file_name="gastos_exportados.csv",
        mime="text/csv"
    )

    st.divider()

# === TAB 2: HISTÓRICO MENSUAL ===
with tab2:
    st.markdown("## 📈 Histórico de Gastos por Mes")

    resumen_mensual = edited_df[meses].sum().reset_index()
    resumen_mensual.columns = ["Mes", "Total Gastado"]

    st.dataframe(resumen_mensual, use_container_width=True)

    fig_hist = px.line(resumen_mensual, x="Mes", y="Total Gastado", title="Evolución de Gastos por Mes", markers=True)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()
