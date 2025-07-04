import pandas as pd
import streamlit as st

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos.csv")

df = cargar_datos()
