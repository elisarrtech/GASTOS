# IMPORTACIONES
import streamlit as st
import pandas as pd
import plotly.express as px

# === TABLA INDEPENDIENTE DE DEUDAS ===
deudas = [
    {"Concepto": "RENTA", "Monto": 300_000, "IVA": 0.16, "Total con IVA": 300_000 * 1.16},
    {"Concepto": "HONORARIOS CONTADOR", "Monto": 200_000, "IVA": 0.16, "Total con IVA": 200_000 * 1.16},
    {"Concepto": "LENIN", "Monto": 55_000, "IVA": 0.16, "Total con IVA": 55_000 * 1.16},
]
df_deudas = pd.DataFrame(deudas)
df_deudas["Monto"] = df_deudas["Monto"].map("${:,.2f}".format)
df_deudas["Total con IVA"] = df_deudas["Total con IVA"].map("${:,.2f}".format)
df_deudas["IVA"] = "16%"

# === FUNCIONES AUXILIARES ===
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

def generar_informe_html(df):
    resumen_total = df["Total"].sum()
    resumen_pagado = df[df["Estado"] == "PAGADO"]["Total"].sum()
    resumen_no_pagado = df[df["Estado"] == "NO PAGADO"]["Total"].sum()

    return f"""
    <html><head><style>
    body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
    h1 {{ color: #2c3e50; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
    .summary {{ background-color: #eef; padding: 10px; margin-top: 20px; }}
    </style></head><body>
    <h1>Informe de Gastos</h1>

    <div class="summary">
    <h2>Resumen General</h2>
    <p><strong>Total Anual:</strong> ${resumen_total:,.2f}</p>
    <p><strong>Total Pagado:</strong> ${resumen_pagado:,.2f}</p>
    <p><strong>No Pagado:</strong> ${resumen_no_pagado:,.2f}</p>
    </div>

    <div class="summary">
    <h2>Sugerencias de Mejora</h2>
    <ul>
        <li>Optimizar conceptos con variaciones positivas elevadas.</li>
        <li>Ajustar presupuestos sistemáticamente superados.</li>
        <li>Controlar categorías con mayor gasto anual.</li>
        <li>Revisar pagos para evitar acumulaciones de saldos.</li>
    </ul>
    </div>

    <h2>Detalle de Conceptos</h2>
    {df.to_html(index=False)}

    </body></html>
    """

# === CARGA DE DATOS ===
df, meses = cargar_datos()
total_anual = df[meses].sum().sum()
total_pagado = df[df["Estado"] == "PAGADO"][meses].sum().sum()
total_no_pagado = df[df["Estado"] == "NO PAGADO"][meses].sum().sum()

# === SIDEBAR ===
busqueda_rapida = st.sidebar.text_input("🔍 Búsqueda rápida por concepto")
informe_alertas_only = st.sidebar.checkbox("🔍 Solo conceptos con sobrepresupuesto")

st.sidebar.header("Filtros")
categoria_filtro = st.sidebar.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
estado_filtro = st.sidebar.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
variacion_filtro = st.sidebar.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])
mes_filtro = st.sidebar.selectbox("Mes", ["Todos"] + meses)
presupuesto_filtro = st.sidebar.slider("Filtrar por presupuesto", min_value=0, max_value=int(df["Presupuesto"].max()), value=(0, int(df["Presupuesto"].max())))

# === APLICAR FILTROS ===
df_filtrado = df.copy()
if busqueda_rapida:
    df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(busqueda_rapida, case=False, na=False)]
if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
if estado_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
if variacion_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Variación (%)"] > 0] if variacion_filtro == "Positiva" else df_filtrado[df_filtrado["Variación (%)"] < 0]
if mes_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado[mes_filtro] > 0]
df_filtrado = df_filtrado[(df_filtrado["Presupuesto"] >= presupuesto_filtro[0]) & (df_filtrado["Presupuesto"] <= presupuesto_filtro[1])]

if st.sidebar.button("📄 Descargar Informe HTML"):
    df_informe = df_filtrado[df_filtrado["Total"] > df_filtrado["Presupuesto"]] if informe_alertas_only else df_filtrado
    resumen_html = generar_informe_html(df_informe)
    st.sidebar.download_button("📄 Descargar Informe", data=resumen_html, file_name="informe_gastos.html", mime="text/html")

# === Resto del Dashboard ===

# Título y KPIs
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# === Tabla de Deudas Independiente ===
st.subheader("💳 Tabla de Deudas Mensuales")
st.dataframe(df_deudas, use_container_width=True)

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
