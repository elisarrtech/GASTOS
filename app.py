import streamlit as st
import pandas as pd

# Configuración
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("📊 Dashboard de Gastos Mensuales")

# --- Función para cargar y limpiar datos ---
@st.cache_data
def cargar_datos():
    try:
        # Leer el archivo sin header
        df = pd.read_excel("data/HOJA DE GASTOS.xlsx", header=None, engine='openpyxl')

        # Limpiar filas completamente vacías
        df = df.dropna(how='all').reset_index(drop=True)

        # Detectar categorías y construir DataFrame final
        categoria_actual = None
        registros = []

        for idx, row in df.iterrows():
            val = str(row[0]).strip() if not pd.isna(row[0]) else ""

            if val and len(val) < 50 and not val.startswith("Unnamed") and not val.isdigit():
                categoria_actual = val
                continue

            if categoria_actual and len(row) >= 2:
                concepto = str(row[0]).strip() if not pd.isna(row[0]) else ""
                if concepto == "":
                    continue

                # Asegurar que siempre haya 8 columnas (Concepto + 7 meses)
                data = [categoria_actual, concepto] + [row[i] if i < len(row) else "" for i in range(1, 9)]
                registros.append(data)

        # Crear nuevo DataFrame con estructura limpia
        columnas = ['Categoría', 'Concepto', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        df_limpio = pd.DataFrame(registros, columns=columnas)

        return df_limpio

    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# --- Cargar datos ---
df = cargar_datos()

if df is not None:
    st.success("Datos cargados correctamente.")

    # Mostrar resumen rápido
    st.markdown("### 📋 Resumen General")
    total_categorias = df['Categoría'].nunique()
    total_conceptos = len(df)
    st.write(f"- **Total de categorías:** {total_categorias}")
    st.write(f"- **Total de conceptos:** {total_conceptos}")

    # Mostrar datos por categoría
    categorias_unicas = df['Categoría'].unique()

    for categoria in categorias_unicas:
        with st.expander(f"📁 {categoria}", expanded=False):
            df_categoria = df[df['Categoría'] == categoria].drop(columns=['Categoría']).reset_index(drop=True)
            edited_df = st.data_editor(df_categoria, use_container_width=True, key=f"edit_{categoria}")

else:
    st.warning("No se pudieron cargar los datos.")
