import streamlit as st
import pandas as pd

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
    quincenas = ['JUNIO Q1', 'JUNIO Q2', 'JULIO Q1', 'JULIO Q2', 'AGOSTO Q1', 'AGOSTO Q2',
                 'SEPTIEMBRE Q1', 'SEPTIEMBRE Q2', 'OCTUBRE Q1', 'OCTUBRE Q2',
                 'NOVIEMBRE Q1', 'NOVIEMBRE Q2', 'DICIEMBRE Q1', 'DICIEMBRE Q2']
    for q in quincenas:
        if q in df.columns:
            df[q] = df[q].str.replace('[,$]', '', regex=True).astype(float)
    return df

# --- Cargar datos ---
df = cargar_datos()

if df is not None and not df.empty:
    st.success("Datos cargados correctamente.")

    # Asegurar columna de tipo si no existe
    if 'Tipo' not in df.columns:
        df['Tipo'] = 'Mensual'

    # Limpiar montos para operaciones
    df_clean = limpiar_montos(df.copy())

    # ---- FILTRO POR CATEGORÍA ----
    categorias = ['Todas'] + list(df['Categoría'].unique())
    categoria_seleccionada = st.selectbox("Selecciona una categoría", categorias)

    # Filtrar datos
    if categoria_seleccionada != 'Todas':
        df_filtrado = df[df['Categoría'] == categoria_seleccionada]
    else:
        df_filtrado = df.copy()

    # ---- Mostrar tabla según tipo ----
    if categoria_seleccionada == 'Nóminas':
        st.markdown("### 🗂 Datos de Nóminas por Quincena")
        cols_quincena = ['Categoría', 'Concepto', 'Tipo'] + [col for col in df.columns if 'Q' in col]
        df_nomina = df_filtrado[cols_quincena]
        edited_df = st.data_editor(df_nomina, use_container_width=True, key="nomina")
    else:
        st.markdown("### 🗂 Datos mensuales")
        cols_mensuales = ['Categoría', 'Concepto', 'Tipo'] + [col for col in df.columns if 'Q' not in col and col not in ['Categoría', 'Concepto', 'Tipo']]
        df_mensual = df_filtrado[cols_mensuales]
        edited_df = st.data_editor(df_mensual, use_container_width=True, key="mensual")

    # Opcional: mostrar datos actualizados
    with st.expander("🔍 Ver datos actualizados"):
        st.dataframe(edited_df, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos o el archivo está vacío.")
