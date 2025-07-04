import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos Mensuales")

# --- Carga del archivo ---
@st.cache_data
def cargar_datos():
    try:
        # Usamos engine='openpyxl' para archivos .xlsx
        df = pd.read_excel("data/HOJA DE GASTOS.xlsx", engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

df = cargar_datos()

if df is not None:
    st.success("Archivo cargado correctamente.")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No se pudo cargar el archivo. Asegúrate de que está en la carpeta correcta.")
