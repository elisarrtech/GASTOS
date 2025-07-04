# === CALCULO DE VARIACION ===
def calcular_variacion(row):
    if row['Presupuesto'] == 0:
        return 0
    return round(((row['Monto'] - row['Presupuesto']) / row['Presupuesto']) * 100, 2)

# === INTERFAZ ===
st.title("📊 Dashboard de Gastos Mensuales")

df = cargar_datos()
df["Variación (%)"] = df.apply(calcular_variacion, axis=1)

with st.sidebar:
    st.header("Filtros")
    categoria_filtro = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    mes_filtro = st.selectbox("Mes", ["Todos"] + sorted(df["Mes"].unique()))

# === TABS ===
tab1, tab2 = st.tabs(["Dashboard Principal", "Histórico Mensual"])

with tab1:
    df_filtrado = df.copy()
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoría"] == categoria_filtro]
    if mes_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_filtro]

    st.subheader("📋 Registros (Editable)")
    edited_df = st.data_editor(
        df_filtrado,
        use_container_width=True,
        num_rows="dynamic",
        key="editar_gastos"
    )

    if st.button("💾 Guardar Cambios"):
        edited_df.to_csv("data/gastos_mensuales.csv", index=False)
        st.success("✅ Datos guardados correctamente.")
        st.cache_data.clear()

    st.divider()
    st.subheader("🔑 Indicadores Principales")

    total_anual = edited_df["Monto"].sum()
    total_pagado = edited_df[edited_df["Estado"] == "PAGADO"]["Monto"].sum()
    total_no_pagado = edited_df[edited_df["Estado"] == "NO PAGADO"]["Monto"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
    col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
    col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

    st.divider()

    gasto_mes = edited_df.groupby("Mes")["Monto"].sum().reset_index()
    fig_mes = px.bar(gasto_mes, x="Mes", y="Monto", title="Gasto Total por Mes", color="Mes")
    st.plotly_chart(fig_mes, use_container_width=True)

    gasto_cat = edited_df.groupby("Categoría")["Monto"].sum().reset_index()
    fig_cat = px.pie(gasto_cat, names="Categoría", values="Monto", title="Distribución por Categoría")
    st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("💼 Nómina por Quincena")
    df_nomina = edited_df[edited_df["Categoría"] == "Nóminas"]
    if not df_nomina.empty:
        gasto_nomina = df_nomina.groupby(["Mes", "Quincena"])["Monto"].sum().reset_index()
        fig_nomina = px.bar(gasto_nomina, x="Mes", y="Monto", color="Quincena", barmode="group", title="Nómina por Quincena")
        st.plotly_chart(fig_nomina, use_container_width=True)
    else:
        st.info("No hay datos de nómina disponibles para mostrar.")

    st.subheader("🚨 Alertas de Presupuesto")
    alertas_df = calcular_alertas(edited_df)
    if not alertas_df.empty:
        st.warning("Hay conceptos que superan su presupuesto")
        st.dataframe(alertas_df)

        # enviar_alerta_email(
        #     destinatario=os.getenv("EMAIL_TO"),
        #     asunto="🚨 Alerta de Presupuesto",
        #     mensaje="Hay conceptos que han superado su presupuesto asignado. Revisa el dashboard."
        # )

        st.info("⚠️ Alerta detectada. (Envío de email desactivado temporalmente)")
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")
    st.dataframe(
        edited_df.style.applymap(colorear_estado, subset=["Estado"]),
        use_container_width=True
    )

    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

with tab2:
    st.subheader("📈 Histórico de Gastos por Mes")

    resumen_mensual = df.groupby("Mes")["Monto"].sum().reset_index()
    st.dataframe(resumen_mensual, use_container_width=True)

    fig_hist = px.line(resumen_mensual, x="Mes", y="Monto", title="Evolución de Gastos por Mes", markers=True)
    st.plotly_chart(fig_hist, use_container_width=True, key="hist_grafico")

    st.divider()

    st.subheader("📊 Comparativo: Gastado vs Presupuesto por Mes")

    comparativo = df.groupby("Mes").agg({"Monto": "sum", "Presupuesto": "sum"}).reset_index()
    fig_comp = px.bar(
        comparativo.melt(id_vars="Mes", value_vars=["Monto", "Presupuesto"], var_name="Tipo", value_name="Total"),
        x="Mes",
        y="Total",
        color="Tipo",
        barmode="group",
        title="Comparativo Mensual: Gastado vs Presupuesto"
    )
    st.plotly_chart(fig_comp, use_container_width=True, key="comparativo_grafico")
