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


✅ Filtro por concepto
✅ Búsqueda personalizada
✅ Visualización de gráficos y KPIs


🛠️ Parte 1: Mejorar el Dashboard (Streamlit)
Suponemos que tienes:
Un archivo gastos.csv con columnas como: fecha, concepto, monto, categoria, etc.
El proyecto está desplegado en Streamlit Cloud
📁 Estructura recomendada del proyecto



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
