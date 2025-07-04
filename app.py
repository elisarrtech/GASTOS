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
        df['Presupuesto'] = ""

    # Limpiar montos para operaciones
    df_clean = limpiar_montos(df.copy())

    # Mostrar KPIs generales
    st.markdown("### 📊 KPIs Generales")
    total_gastos = df_clean[['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].sum().sum()
    promedio_mensual = total_gastos / 7
    st.metric(label="Total de gastos anuales", value=f"${total_gastos:,.2f}")
    st.metric(label="Promedio mensual", value=f"${promedio_mensual:,.2f}")

    # Mostrar totales por categoría
    st.markdown("### 🧮 Totales por categoría")
    df_total_categoria = df_clean.groupby('Categoría')[['Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].sum()
    df_total_categoria['Total Anual'] = df_total_categoria.sum(axis=1)
    st.dataframe(df_total_categoria, use_container_width=True)

    # Gráfico comparativo por categoría
    st.markdown("### 📈 Comparativa de gastos por categoría")
    fig = px.bar(df_total_categoria.reset_index(), x='Categoría', y='Total Anual', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar datos editables por categoría
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
