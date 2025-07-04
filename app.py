import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos Mensuales")

# --- Función para cargar datos ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("data/HOJA DE GASTOS.xlsx", engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# --- Cargar datos ---
df = cargar_datos()

if df is not None:
    st.success("Archivo cargado correctamente.")

    # Limpiar filas vacías
    df.columns = df.columns.str.strip()
    df = df.dropna(how='all')

    # --- Procesar categorías ---
    categoria_actual = None
    subcategorias = []

    for index, row in df.iterrows():
        primera_celda = str(row.iloc[0]).strip()

        if primera_celda and not primera_celda.startswith("Unnamed"):
            categoria_actual = primera_celda
            with st.expander(f"📁 {categoria_actual}", expanded=False):
                st.dataframe(df.iloc[[index]], use_container_width=True)
        else:
            continue

else:
    st.warning("No se pudo cargar el archivo. Verifica que esté en la carpeta correcta.")
