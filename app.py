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
    return df

# === FUNCIONES AUXILIARES ===
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
    return ''

# === DATOS Y VARIABLES ===
df = cargar_datos()
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
df, total_pagado, total_no_pagado = calcular_totales_por_estado(df, meses)
total_anual = df[meses].sum().sum()

# === FILTROS ===
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
    variacion_filtro = st.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])

df_filtrado = df.copy()
if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
if estado_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
if variacion_filtro != "Todos" and "Variación (%)" in df_filtrado.columns:
    if variacion_filtro == "Positiva":
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] > 0]
    else:
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] < 0]

# === KPIs ===
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# === TABLAS Y GRÁFICOS ===
st.subheader("📋 Registros Filtrados")
st.dataframe(df_filtrado.style.applymap(colorear_estado, subset=["Estado"]), use_container_width=True)

st.subheader("📈 Gastos por Mes")
total_mensual = df_filtrado[meses].sum().reset_index()
total_mensual.columns = ["Mes", "Total"]
fig = px.bar(total_mensual, x="Mes", y="Total", color="Mes", title="Total por Mes")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Distribución por Categoría")
gastos_categoria = df_filtrado.groupby("Categoría")[meses].sum().sum(axis=1).reset_index(name="Total")
fig_cat = px.pie(gastos_categoria, names="Categoría", values="Total", title="Distribución por Categoría")
st.plotly_chart(fig_cat, use_container_width=True)

st.subheader("🚨 Alertas de Presupuesto")
alertas = calcular_alertas(df_filtrado, meses)
if not alertas.empty:
    st.warning("⚠️ Conceptos que exceden el presupuesto")
    st.dataframe(alertas, use_container_width=True)
else:
    st.success("Todos los conceptos están dentro del presupuesto")

# === INFORME HTML ===
with st.expander("📄 Generar Informe HTML"):
    resumen_html = f"""
    <html><head><style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1, h2 {{ color: #2c3e50; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
    </style></head><body>
    <h1>Informe de Gastos</h1>
    <h2>Indicadores Principales</h2>
    <ul>
    <li>Total Anual: ${total_anual:,.2f}</li>
    <li>Total Pagado: ${total_pagado:,.2f}</li>
    <li>No Pagado: ${total_no_pagado:,.2f}</li>
    </ul>
    <h2>Detalle</h2>
    {df_filtrado.to_html(index=False)}
    </body></html>
    """
    st.download_button("📄 Descargar Informe HTML", data=resumen_html, file_name="informe_gastos.html", mime="text/html")

# === EXPORTACIÓN ===
st.download_button("📥 Descargar CSV", data=df.to_csv(index=False), file_name="gastos_exportados.csv")

# === SEGUNDA PESTAÑA: HISTÓRICO ===
tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])
with tab2:
    st.subheader("📈 Histórico por Mes")
    resumen = df.groupby("Categoría")[meses].sum()
    st.dataframe(resumen, use_container_width=True)

    fig_hist = px.line(resumen.T, title="Evolución Histórica por Categoría")
    st.plotly_chart(fig_hist, use_container_width=True)
