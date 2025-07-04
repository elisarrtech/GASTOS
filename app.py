import streamlit as st
import pandas as pd
import plotly.express as px

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
    .stButton button {
        background-color: #2980b9;
        color: white;
        border-radius: 8px;
        padding: 0.4em 0.8em;
    }
    .estado-pagado {
        background-color: #d4edda;
        color: #155724;
    }
    .estado-no-pagado {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# === FUNCIONES AUXILIARES ===
def limpiar_monto(valor):
    try:
        return float(str(valor).replace("$", "").replace(",", ""))
    except:
        return 0.0

def colorear_estado(val):
    if val == "Pagado":
        return 'background-color: #d4edda; color: #155724'
    elif val == "Sin pagar":
        return 'background-color: #f8d7da; color: #721c24'
    else:
        return ''

# === CARGA DE DATOS ===
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/gastos_mensuales.csv")
    if "Estado" not in df.columns:
        df["Estado"] = "Sin pagar"
    return df

df = cargar_datos()

# Meses y limpieza
meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
for mes in meses:
    df[mes] = df[mes].apply(limpiar_monto)

# === INTERFAZ PRINCIPAL ===
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

# === TABLA EDITABLE CON ESTADO INTEGRADO ===
st.subheader("📋 Registros Filtrados")
edited_df = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Estado": st.column_config.SelectboxColumn(
            options=["Pagado", "Sin pagar"],
            required=True
        )
    },
    key="editar_gastos"
)

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

    # === ESTADO DE PAGOS - BARRA DE PROGRESO ===
    total_pagado = len(edited_df[edited_df["Estado"] == "Pagado"])
    total_saldo = len(edited_df[edited_df["Estado"] == "Sin pagar"])

    st.subheader("📊 Estado de Pagos")
    st.progress(total_pagado / (total_pagado + total_saldo))
    st.caption(f"{total_pagado} de {total_pagado + total_saldo} conceptos pagados ({int((total_pagado / (total_pagado + total_saldo) * 100))}% pagados)")

    # === TABLA CON ESTILO DE ESTADO ===
    styled_df = edited_df.style.applymap(colorear_estado, subset=["Estado"])
    st.dataframe(styled_df, use_container_width=True)

    # === ACTUALIZAR ESTADO INLINE EN CADA FILA ===
    for index, row in edited_df.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['Concepto']}**")
        with col2:
            estado_actual = row.get("Estado", "Sin pagar")
            nuevo_estado = "Pagado" if estado_actual == "Sin pagar" else "Sin pagar"
            if st.button(f"{estado_actual} ➤ {nuevo_estado}", key=f"toggle_{index}"):
                edited_df.at[index, "Estado"] = nuevo_estado
                edited_df.to_csv("data/gastos_mensuales.csv", index=False)
                st.rerun()
