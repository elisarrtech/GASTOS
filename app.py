# === Resto del Dashboard ===

# Título y KPIs
st.title("📊 Dashboard de Gastos Mensuales")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Anual", f"${total_anual:,.2f}")
col2.metric("✅ Pagado", f"${total_pagado:,.2f}")
col3.metric("⏳ No Pagado", f"${total_no_pagado:,.2f}")

# Tabs
principal, historico = st.tabs(["📊 Dashboard Principal", "📈 Histórico Mensual"])

with principal:
    st.subheader("📋 Registros (Editable)")
    edited_df = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic", key="editar_gastos")

    if st.button("💾 Guardar Cambios"):
        edited_df.to_csv("data/gastos_mensuales.csv", index=False)
        st.success("✅ Datos guardados correctamente.")
        st.cache_data.clear()

    st.divider()

    # Gráficos principales
    st.subheader("📊 Comparativo por Categoría")
    cat_data = df_filtrado.groupby("Categoría")[meses].sum().reset_index()
    st.plotly_chart(px.bar(cat_data, x="Categoría", y=meses, barmode="group", title="Gastos por Categoría"), use_container_width=True)

    st.subheader("📊 Comparativo por Estado")
    estado_data = df_filtrado.groupby("Estado")[meses].sum().reset_index()
    st.plotly_chart(px.bar(estado_data, x="Estado", y=meses, barmode="group", title="Gastos por Estado"), use_container_width=True)

    if "Año" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Año")
        anio_data = df_filtrado.groupby("Año")[meses].sum().reset_index()
        st.plotly_chart(px.bar(anio_data, x="Año", y=meses, barmode="group", title="Gastos por Año"), use_container_width=True)

    if "Quincena" in df_filtrado.columns:
        st.subheader("📊 Comparativo por Quincena")
        quincena_data = df_filtrado.groupby("Quincena")[meses].sum().reset_index()
        st.plotly_chart(px.bar(quincena_data, x="Quincena", y=meses, barmode="group", title="Gastos por Quincena"), use_container_width=True)

    st.divider()

    # Alertas
    st.subheader("🚨 Alertas de Presupuesto")
    alertas = edited_df[edited_df["Total"] > edited_df["Presupuesto"]]
    if not alertas.empty:
        st.warning("⚠️ Conceptos que superan el presupuesto")
        st.dataframe(alertas, use_container_width=True)
    else:
        st.success("Todos los conceptos están dentro del presupuesto")

    st.subheader("📄 Tabla con Estado Visual")
    st.dataframe(edited_df.style.applymap(colorear_estado, subset=["Estado"]), use_container_width=True)

    st.download_button("📥 Descargar CSV", data=edited_df.to_csv(index=False), file_name="gastos_exportados.csv")

with historico:
    st.subheader("📈 Histórico por Mes")
    resumen = df.groupby("Categoría")[meses].sum()
    st.dataframe(resumen, use_container_width=True)
    st.plotly_chart(px.line(resumen.T, title="Evolución Histórica por Categoría"), use_container_width=True)
