import streamlit as st
import pandas as pd

# Configuración
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos Mensuales")

# --- Función para cargar y limpiar datos ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("data/HOJA DE GASTOS.xlsx", header=None, engine='openpyxl')
        df.columns = df.iloc[0]
        df = df.drop(0).reset_index(drop=True)

        # Limpiar filas vacías y detectar categorías
        categorias = []
        categoria_actual = None
        cleaned_rows = []

        for idx, row in df.iterrows():
            val = str(row.iloc[0]).strip()
            if val and not val.startswith("Unnamed") and not val.isdigit() and len(val) < 30:
                categoria_actual = val
            categorias.append(categoria_actual)
            cleaned_rows.append(row.tolist())

        df_clean = pd.DataFrame(cleaned_rows, columns=df.columns)
        df_clean['Categoría'] = categorias
        df_clean.columns = ['Concepto', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre', 'Categoría']

        # Filtrar encabezados repetidos y filas irrelevantes
        df_clean = df_clean[~df_clean['Concepto'].str.contains('GASTO|CONCEPTO|NOMBRE|---', na=True)]
        df_clean = df_clean[df_clean['Concepto'].notna() & (df_clean['Concepto'] != '')]

        return df_clean[['Categoría', 'Concepto', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']]

    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# --- Cargar datos ---
df = cargar_datos()

if df is not None:
    st.success("Datos cargados correctamente.")

    # Mostrar datos por categoría
    categorias_unicas = df['Categoría'].unique()

    for categoria in categorias_unicas:
        with st.expander(f"📁 {categoria}", expanded=False):
            df_categoria = df[df['Categoría'] == categoria].drop(columns=['Categoría']).reset_index(drop=True)
            edited_df = st.data_editor(df_categoria, use_container_width=True, key=f"edit_{categoria}")
            st.write("Datos actualizados:")
            st.dataframe(edited_df)

else:
    st.warning("No se pudieron cargar los datos.")
