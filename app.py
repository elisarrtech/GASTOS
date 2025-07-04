import streamlit as st
import pandas as pd
import plotly.express as px

# FUNCIONES AUXILIARES

def cargar_datos():
    df = pd.read_csv("data/gastos_mensuales.csv")
    df["Monto"] = df["Monto"].replace('[\$,]', '', regex=True).astype(float)
    df["Presupuesto"] = df["Presupuesto"].replace('[\$,]', '', regex=True).astype(float)
    return df

def calcular_variacion(row):
    if row['Presupuesto'] == 0:
        return 0
    return round(((row['Monto'] - row['Presupuesto']) / row['Presupuesto']) * 100, 2)

def calcular_alertas(df):
    alertas = df.groupby("Concepto").agg({"Monto": "sum", "Presupuesto": "max"}).reset_index()
    alertas = alertas[alertas["Monto"] > alertas["Presupuesto"]]
    return alertas

def colorear_estado(val):
    if val == "PAGADO":
        return 'background-color: #d4edda; color: #155724; text-align: center'
    elif val == "NO PAGADO":
        return 'background-color: #f8d7da; color: #721c24; text-align: center'
    else:
        return ''

def colorear_variacion(val):
    if val > 0:
        return 'background-color: #f8d7da; color: #721c24; text-align: center'
    elif val < 0:
        return 'background-color: #d4edda; color: #155724; text-align: center'
    else:
        return ''

# === INTERFAZ ===
st.title("📊 Dashboard de Gastos Mensuales")

# Cargar datos
df = cargar_datos()
df["Variación (%)"] = df.apply(calcular_variacion, axis=1)

with st.sidebar:
    st.header("Filtros")
    año_filtro = st.selectbox("Año", ["Todos"] + sorted(df["Año"].unique()))
    banco_filtro = st.selectbox("Banco", ["Todos"] + sorted(df["Banco"].unique()))
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    mes_filtro = st.selectbox("Mes", ["Todos"] + sorted(df["Mes"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos"] + sorted(df["Estado"].unique()))
    quincena_filtro = st.selectbox("Quincena", ["Todas"] + sorted(df["Quincena"].unique()))
    variacion_filtro = st.selectbox("Variación", ["Todos", "Positiva", "Negativa"])

    busqueda_rapida = st.text_input("🔍 Búsqueda rápida por concepto")



# === TABS ===
tab1, tab2 = st.tabs(["Dashboard Principal", "Histórico Mensual"])

with tab1:
    df_filtrado = df.copy()

    # Aplicar búsqueda rápida
    if busqueda_rapida:
        df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(busqueda_rapida, case=False, na=False)]

    # Aplicar filtros avanzados
    if año_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == int(año_filtro)]
    if banco_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Banco"] == banco_filtro]
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
    if mes_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_filtro]
    if estado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
    if quincena_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Quincena"] == quincena_filtro]
    if variacion_filtro == "Positiva":
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] > 0]
    elif variacion_filtro == "Negativa":
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] < 0]

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

    st.divider()

    st.subheader("🏅 Top 5 Conceptos con Mayor Gasto")
    top_conceptos = edited_df.groupby("Concepto")["Monto"].sum().reset_index().sort_values(by="Monto", ascending=False).head(5)
    fig_top = px.bar(top_conceptos, x="Concepto", y="Monto", title="Top 5 Conceptos más Caros", color="Concepto")
    st.plotly_chart(fig_top, use_container_width=True)

    st.subheader("🔑 Indicadores Principales")

    total_anual = edited_df["Monto"].sum()
    total_pagado = edited_df[edited_df["Estado"] == "PAGADO"]["Monto"].sum()
    total_no_pagado = edited_df[edited_df["Estado"] == "NO PAGADO"]["Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
    col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
    col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

    with st.expander("📄 Generar Informes"):
        tabla_html = (
    edited_df[['Categoría', 'Concepto', 'Mes', 'Monto', 'Presupuesto', 'Estado', 'Variación (%)']]
    .style
    .applymap(lambda val: 'background-color: #d4edda;' if val == 'PAGADO' else ('background-color: #f8d7da;' if val == 'NO PAGADO' else ''), subset=['Estado'])
    .applymap(lambda val: 'background-color: #f8d7da;' if isinstance(val, (int, float)) and val > 0 else ('background-color: #d4edda;' if isinstance(val, (int, float)) and val < 0 else ''), subset=['Variación (%)'])
    .to_html(escape=False, index=False)
)

resumen = f"""
<html><head>
<style>
    body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
    h1, h2 {{ color: #2c3e50; }}
    ul {{ margin-left: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
</style>
</head><body>
<h1>Informe de Gastos Mensuales</h1>

<h2>Indicadores Clave</h2>
<ul>
<li>Total Anual: ${total_anual:,.2f}</li>
<li>Total Pagado: ${total_pagado:,.2f}</li>
<li>No Pagado: ${total_no_pagado:,.2f}</li>
</ul>

<h2>Recomendaciones</h2>
<ul>
<li>Revisa los conceptos con mayor gasto.</li>
<li>Ajusta presupuestos con variación positiva mayor al 10%.</li>
<li>Analiza los gastos por categoría y mes.</li>
</ul>

<h2>Detalle de Gastos</h2>
{tabla_html}

<p><em>Sugerencia:</em> Monitorea mensualmente los conceptos con alta variación y considera acciones de ajuste presupuestal.</p>
</body></html>
"""

    st.download_button(
            label="📄 Descargar Informe",
            data=resumen,
            file_name="informe_gastos.html",
            mime="text/html"
        )

    st.download_button(
            label="📄 Descargar Informe",
            data=resumen,
            file_name="informe_gastos.md",
            mime="text/markdown"
        )
    st.divider()

    gasto_mes = edited_df.groupby("Mes")["Monto"].sum().reset_index()
    fig_mes = px.bar(gasto_mes, x="Mes", y="Monto", title="Gasto Total por Mes", color="Mes")
    st.plotly_chart(fig_mes, use_container_width=True)

    gasto_cat = edited_df.groupby("Categoría")["Monto"].sum().reset_index()
    fig_cat = px.pie(gasto_cat, names="Categoría", values="Monto", title="Distribución por Categoría")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("💼 Nómina por Quincena")
    df_nomina = edited_df[edited_df["Categoría"] == "Nóminas"]
    if not df_nomina.empty:
        gasto_nomina = df_nomina.groupby(["Mes", "Quincena"])["Monto"].sum().reset_index()
        fig_nomina = px.bar(gasto_nomina, x="Mes", y="Monto", color="Quincena", barmode="group", title="Nómina por Quincena")
        st.plotly_chart(fig_nomina, use_container_width=True)
    else:
        st.info("No hay datos de nómina disponibles para mostrar.")

    st.subheader("🚨 Alertas de Presupuesto")
    alertas_df = calcular_alertas(edited_df)
    if not alertas_df.empty:
        st.warning("Hay conceptos que superan su presupuesto")
        st.dataframe(alertas_df)

        st.info("⚠️ Alerta detectada. (Envío de email desactivado temporalmente)")
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")

    styled_table = edited_df.style.applymap(colorear_estado, subset=["Estado"]).applymap(colorear_variacion, subset=["Variación (%)"])

    st.dataframe(styled_table, use_container_width=True)

    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

    # Exportar a Excel
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Gastos')
    st.download_button(
        label="📥 Exportar a Excel",
        data=output.getvalue(),
        file_name="gastos_exportados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab2:
    st.subheader("📈 Histórico de Gastos por Mes")

    resumen_mensual = df.groupby(["Año", "Mes"])["Monto"].sum().reset_index()
    st.dataframe(resumen_mensual, use_container_width=True)

    fig_hist = px.line(resumen_mensual, x="Mes", y="Monto", color="Año", title="Evolución de Gastos por Mes", markers=True)
    st.plotly_chart(fig_hist, use_container_width=True, key="hist_grafico")

    st.divider()

    st.subheader("📊 Comparativo: Gastado vs Presupuesto por Mes")

    comparativo = df.groupby("Mes").agg({"Monto": "sum", "Presupuesto": "sum"}).reset_index()
    fig_comp = px.bar(
        comparativo.melt(id_vars="Mes", value_vars=["Monto", "Presupuesto"], var_name="Tipo", value_name="Total"),
        x="Mes",
        y="Total",
        color="Tipo",
        barmode="group",
        title="Comparativo Mensual: Gastado vs Presupuesto"
    )
    st.plotly_chart(fig_comp, use_container_width=True, key="comparativo_grafico")
