import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.message import EmailMessage
import os

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

def enviar_alerta_email(destinatario, asunto, mensaje):
    email = EmailMessage()
    email["From"] = os.getenv("EMAIL_USER")
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(email)

# === CARGA DE DATOS ===
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/gastos_mensuales.csv")
    df["Monto"] = df["Monto"].replace('[\$,]', '', regex=True).astype(float)
    df["Presupuesto"] = df["Presupuesto"].replace('[\$,]', '', regex=True).astype(float)
    return df

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

# === INTERFAZ ===
st.title("📊 Dashboard de Gastos Mensuales")

df = cargar_datos()

with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    mes_filtro = st.selectbox("Mes", ["Todos"] + sorted(df["Mes"].unique()))

# === TABS ===
tab1, tab2 = st.tabs(["Dashboard Principal", "Histórico Mensual"])

with tab1:
    df_filtrado = df.copy()
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
    if mes_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_filtro]

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
    st.subheader("🔑 Indicadores Principales")

    total_anual = edited_df["Monto"].sum()
    total_pagado = edited_df[edited_df["Estado"] == "PAGADO"]["Monto"].sum()
    total_no_pagado = edited_df[edited_df["Estado"] == "NO PAGADO"]["Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
    col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
    col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

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

        # enviar_alerta_email(
        #     destinatario=os.getenv("EMAIL_TO"),
        #     asunto="🚨 Alerta de Presupuesto",
        #     mensaje="Hay conceptos que han superado su presupuesto asignado. Revisa el dashboard."
        # )

        st.info("⚠️ Alerta detectada. (Envío de email desactivado temporalmente)")
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")
    st.dataframe(
        edited_df.style.applymap(colorear_estado, subset=["Estado"]),
        use_container_width=True
    )

    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

with tab2:
    st.subheader("📈 Histórico de Gastos por Mes")

    resumen_mensual = df.groupby("Mes")["Monto"].sum().reset_index()
    st.dataframe(resumen_mensual, use_container_width=True)

    fig_hist = px.line(resumen_mensual, x="Mes", y="Monto", title="Evolución de Gastos por Mes", markers=True)
    st.plotly_chart(fig_hist, use_container_width=True)
