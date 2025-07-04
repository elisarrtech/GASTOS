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

# --- Limpiar y convertir montos a números ---
def limpiar_montos(df):
    meses = ['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    for mes in meses:
        df[mes] = df[mes].str.replace('[,$]', '', regex=True).astype(float)
    return df

# --- Cargar datos ---
df = cargar_datos()

if df is not None and not df.empty:
    st.success("Datos cargados correctamente.")

    # Mostrar resumen rápido
    st.markdown("### 📋 Resumen General")
    st.write(f"- **Total de conceptos:** {len(df)}")

    # Limpiar montos para poder operar con ellos
    df_clean = limpiar_montos(df.copy())

    # Calcular total por categoría
    st.markdown("### 🧮 Totales por categoría")
    df_total_categoria = df_clean.groupby('Categoría')[['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].sum()
    st.dataframe(df_total_categoria, use_container_width=True)

    # Gráfico de barras
    st.markdown("### 📊 Total de gastos por categoría")
    df_total_categoria['Total'] = df_total_categoria.sum(axis=1)
    fig = px.bar(df_total_categoria.reset_index(), x='Categoría', y='Total', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar datos por categoría
    if 'Categoría' in df.columns:
        categorias_unicas = df['Categoría'].unique()
    else:
        st.error("No se encontró la columna 'Categoría'. Verifica el archivo.")
        st.stop()

    for categoria in categorias_unicas:
        with st.expander(f"📁 {categoria}", expanded=False):
            df_categoria = df[df['Categoría'] == categoria].drop(columns=['Categoría']).reset_index(drop=True)
            edited_df = st.data_editor(df_categoria, use_container_width=True, key=f"edit_{categoria}")
            st.write("Datos actualizados:")
            st.dataframe(edited_df)

else:
    st.warning("No se pudieron cargar los datos o el archivo está vacío.")
