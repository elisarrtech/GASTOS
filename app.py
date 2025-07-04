# === FILTROS ===
busqueda_rapida = st.sidebar.text_input("🔍 Búsqueda rápida por concepto")
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
    variacion_filtro = st.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])
    # Nuevos filtros:
    mes_filtro = st.selectbox("Mes", ["Todos"] + meses)
    presupuesto_filtro = st.slider("Filtrar por presupuesto", min_value=0, max_value=int(df["Presupuesto"].max()), value=(0, int(df["Presupuesto"].max())))
busqueda_rapida = st.sidebar.text_input("🔍 Búsqueda rápida por concepto")
with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    estado_filtro = st.selectbox("Estado", ["Todos", "PAGADO", "NO PAGADO"])
    variacion_filtro = st.selectbox("Variación (%)", ["Todos", "Positiva", "Negativa"])

# === APLICAR FILTROS ===
if busqueda_rapida:
    df_filtrado = df[df["Concepto"].str.contains(busqueda_rapida, case=False, na=False)]
else:
    df_filtrado = df.copy()
if busqueda_rapida:
    df_filtrado = df[df["Concepto"].str.contains(busqueda_rapida, case=False, na=False)]
else:
    df_filtrado = df.copy()
df_filtrado = df.copy()
if categoria_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
if estado_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
if variacion_filtro != "Todos":
    if variacion_filtro == "Positiva":
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] > 0]
    else:
        df_filtrado = df_filtrado[df_filtrado["Variación (%)"] < 0]
if mes_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado[mes_filtro] > 0]
df_filtrado = df_filtrado[(df_filtrado["Presupuesto"] >= presupuesto_filtro[0]) & (df_filtrado["Presupuesto"] <= presupuesto_filtro[1])]
