import streamlit as st
import pandas as pd

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos_mensuales.csv")

df = cargar_datos()
meses = ["Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Formulario
st.title("➕ Añadir Nuevo Concepto")
st.markdown("Completa los campos para agregar un nuevo gasto.")

col1, col2 = st.columns(2)
with col1:
    nueva_categoria = st.selectbox("Categoría", list(df["Categoría"].unique()) + ["Otra..."])
    if nueva_categoria == "Otra...":
        nueva_categoria = st.text_input("Escribe una nueva categoría")

with col2:
    nuevo_concepto = st.text_input("Nombre del Concepto")

valores = []
for mes in meses:
    valor = st.number_input(f"{mes}", min_value=0.0, format="%.2f")
    valores.append(valor)

if st.button("Guardar Nuevo Gasto"):
    nuevo_registro = {
        "Categoría": [nueva_categoria],
        "Concepto": [nuevo_concepto],
        **{mes: [val] for mes, val in zip(meses, valores)}
    }
    df_nuevo = pd.DataFrame(nuevo_registro)
    df_actualizado = pd.concat([df, df_nuevo], ignore_index=True)
    df_actualizado.to_csv("data/gastos_mensuales.csv", index=False)
    st.success("✅ Concepto agregado correctamente.")
    st.cache_data.clear()
