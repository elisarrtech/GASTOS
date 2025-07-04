import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos Mensuales")

# --- Función para cargar y limpiar datos ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("data/hoja_ejemplo_gastos.csv")
        df = df.dropna(how='all').reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# --- Limpiar montos a números ---
def limpiar_montos(df):
    meses = ['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    for mes in meses:
        df[mes] = df[mes].str.replace('[,$]', '', regex=True).astype(float)
    return df

# --- Cargar datos ---
df = cargar_datos()

if df is not None and not df.empty:
    st.success("Datos cargados correctamente.")

    # Asegurar que haya una columna de Presupuesto
    if 'Presupuesto' not in df.columns:
        df['Presupuesto'] = 0

    # Limpiar montos para operaciones
    df_clean = limpiar_montos(df.copy())

    # ---- FILTROS ----
    st.sidebar.header("🔍 Filtros")

    # Filtro por categoría
    categorias = ['Todas'] + list(df['Categoría'].unique())
    categoria_seleccionada = st.sidebar.selectbox("Selecciona una categoría", categorias)

    # Filtro por mes
    meses = ['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_seleccionado = st.sidebar.selectbox("Selecciona un mes", meses)

    # Búsqueda por nombre
    busqueda = st.sidebar.text_input("Buscar concepto", "")

    # Aplicar filtros
    df_filtrado = df.copy()
    if categoria_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoría'] == categoria_seleccionada]

    if busqueda:
        df_filtrado = df_filtrado[df_filtrado['Concepto'].str.contains(busqueda, case=False, na=False)]

    # Mostrar KPIs generales o filtrados
    st.markdown("### 📊 KPIs Generales")
    total_gastos = df_clean[meses].sum().sum()
    promedio_mensual = total_gastos / 7
    col1, col2 = st.columns(2)
    col1.metric(label="Total de gastos anuales", value=f"${total_gastos:,.2f}")
    col2.metric(label="Promedio mensual", value=f"${promedio_mensual:,.2f}")

    # Mostrar totales por categoría
    st.markdown("### 🧮 Totales por categoría")
    df_total_categoria = df_clean.groupby('Categoría')[meses].sum()
    df_total_categoria['Total Anual'] = df_total_categoria.sum(axis=1)
    st.dataframe(df_total_categoria, use_container_width=True)

    # Gráfico comparativo por categoría
    st.markdown("### 📈 Comparativa de gastos por categoría")
    fig = px.bar(df_total_categoria.reset_index(), x='Categoría', y='Total Anual', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar tabla filtrada editable
    st.markdown(f"### 🗂 Datos filtrados ({categoria_seleccionada} - {mes_seleccionado})")
    df_editable = df_filtrado[['Concepto', mes_seleccionado]].copy()
    edited_df = st.data_editor(df_editable, use_container_width=True)

    # Mostrar gráfico de barras por concepto
    if not df_editable.empty:
        st.markdown("### 📊 Gastos por concepto")
        fig_bar = px.bar(df_editable, x='Concepto', y=mes_seleccionado, text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos o el archivo está vacío.")
