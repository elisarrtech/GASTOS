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
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
    variacion_filtro = st.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])

# === APLICAR FILTROS ===
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

# === KPIS ===
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# === TAB 1 ===
tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])

with tab1:
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

    st.subheader("📈 Gastos por Mes")
    total_mensual = edited_df[meses].sum().reset_index()
    total_mensual.columns = ["Mes", "Total"]
    fig_mes = px.bar(total_mensual, x="Mes", y="Total", color="Mes", title="Total por Mes")
    st.plotly_chart(fig_mes, use_container_width=True)

    st.subheader("📊 Distribución por Categoría")
    gastos_categoria = edited_df.groupby("Categoría")[meses].sum().sum(axis=1).reset_index(name="Total")
    fig_cat = px.pie(gastos_categoria, names="Categoría", values="Total", title="Distribución por Categoría")
    st.plotly_chart(fig_cat, use_container_width=True)

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
        {edited_df.to_html(index=False)}
        </body></html>
        """
        st.download_button("📄 Descargar Informe HTML", data=resumen_html, file_name="informe_gastos.html", mime="text/html")

with tab2:
    st.subheader("📈 Histórico por Mes")
    resumen = df.groupby("Categoría")[meses].sum()
    st.dataframe(resumen, use_container_width=True)

    fig_hist = px.line(resumen.T, title="Evolución Histórica por Categoría")
    st.plotly_chart(fig_hist, use_container_width=True)
