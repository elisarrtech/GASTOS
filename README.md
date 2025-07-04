# GASTOS# 📊 Dashboard de Gastos Personales

Una aplicación web simple para visualizar, filtrar y analizar tus gastos personales usando [Streamlit](https://streamlit.io ).

## 🚀 Características

- ✅ Filtro por concepto
- ✅ Búsqueda personalizada
- ✅ KPIs principales (total gastado, promedio, cantidad de registros)
- ✅ Gráficos interactivos (barras y torta)
- ✅ Fácil de usar e integrar con datos CSV/Excel

## 📁 Estructura del Proyecto
GASTOS/
│
├── data/
│ └── gastos.csv # Tus datos
├── pages/
│ └── home.py # Página principal del dashboard
├── app.py # Archivo inicial
├── requirements.txt # Librerías necesarias
└── README.md # Descripción del proyecto


## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/elisarrtech/GASTOS.git 
   cd GASTOS

   profile
Qwen3-235B-A22B
12:52 am
Perfecto 👍

Voy a ayudarte a perfeccionar tu dashboard de gastos desde cero hasta un producto funcional, visual y profesional, con las funciones que mencionaste:

✅ Filtro por concepto
✅ Búsqueda personalizada
✅ Visualización de gráficos y KPIs
Y también vamos a mejorar el repositorio de GitHub para que sea más claro, usable y profesional.

🛠️ Parte 1: Mejorar el Dashboard (Streamlit)
Suponemos que tienes:
Un archivo gastos.csv con columnas como: fecha, concepto, monto, categoria, etc.
El proyecto está desplegado en Streamlit Cloud
📁 Estructura recomendada del proyecto


1
2
3
4
5
6
7
8
9
GASTOS/
│
├── data/
│   └── gastos.csv         # Tus datos
├── pages/
│   └── home.py            # Página principal del dashboard
├── app.py                 # Archivo inicial
├── requirements.txt       # Librerías necesarias
└── README.md              # Descripción del proyecto
🧮 Código ejemplo (pages/home.py)
python


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
⌄
⌄
⌄
⌄
⌄
⌄
import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data/gastos.csv")

df = cargar_datos()

st.title("📊 Dashboard de Gastos Personales")
st.markdown("Filtrá y analizá tus gastos fácilmente.")

# Campo de texto para búsqueda personalizada
filtro_texto = st.text_input("🔍 Buscar en conceptos o descripciones")

# Filtrar por concepto si se selecciona uno
conceptos_unicos = df["concepto"].unique().tolist()
concepto_seleccionado = st.selectbox("📌 Filtrar por concepto", ["Todos"] + conceptos_unicos)

# Aplicar filtros
df_filtrado = df.copy()

if concepto_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["concepto"] == concepto_seleccionado]

if filtro_texto:
    df_filtrado = df_filtrado[
        df_filtrado.apply(lambda row: filtro_texto.lower() in " ".join(row.astype(str).str.lower()), axis=1)
    ]

# Mostrar datos filtrados
st.subheader("📋 Registros filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Gastado", f"${df_filtrado['monto'].sum():,.2f}")

with col2:
    st.metric("📉 Promedio por Gasto", f"${df_filtrado['monto'].mean():,.2f}")

with col3:
    st.metric("📅 Número de Registros", len(df_filtrado))

# Gráfico de barras por concepto
st.subheader("📈 Gastos por Concepto")
grafico_barras = px.bar(
    df_filtrado.groupby("concepto")["monto"].sum().reset_index(),
    x="concepto",
    y="monto",
    title="Total de Gastos por Concepto"
)
st.plotly_chart(grafico_barras, use_container_width=True)

# Gráfico de torta
st.subheader("🥧 Distribución de Gastos")
fig_pie = px.pie(
    df_filtrado,
    names="concepto",
    values="monto",
    title="Distribución de Gastos por Concepto"
)
st.plotly_chart(fig_pie, use_container_width=True)
📦 Requerimientos (requirements.txt)
txt


1
2
3
4
streamlit
pandas
plotly
openpyxl  # Si usas Excel (.xlsx)
🌐 Parte 2: Mejorar el repositorio de GitHub
Como vimos antes, tu repositorio actual no tiene:

Descripción
Temas (topics)
Releases
Documentación
Vamos a crear un buen README.md.

📝 Ejemplo de README.md
markdown


1
2
3
4
5
6
7
8
9
10
11
12
13
14
⌄
⌄
# 📊 Dashboard de Gastos Personales

Una aplicación web simple para visualizar, filtrar y analizar tus gastos personales usando [Streamlit](https://streamlit.io ).

## 🚀 Características

- ✅ Filtro por concepto
- ✅ Búsqueda personalizada
- ✅ KPIs principales (total gastado, promedio, cantidad de registros)
- ✅ Gráficos interactivos (barras y torta)
- ✅ Fácil de usar e integrar con datos CSV/Excel

## 📁 Estructura del Proyecto

GASTOS/
│
├── data/
│ └── gastos.csv # Tus datos
├── pages/
│ └── home.py # Página principal del dashboard
├── app.py # Archivo inicial
├── requirements.txt # Librerías necesarias
└── README.md # Descripción del proyecto



1
2
3
4
5
6
7

## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/elisarrtech/GASTOS.git 
   cd GASTOS
Instala dependencias:
bash


1
pip install -r requirements.txt
Ejecuta la app:
bash


1
streamlit run app.py
📈 Datos Esperados
El archivo gastos.csv debe contener al menos estas columnas:

fecha: Fecha del gasto
concepto: Nombre del gasto o descripción
monto: Valor numérico del gasto
categoria: (Opcional) categoría del gasto
