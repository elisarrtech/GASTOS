# utils/alerts.py
import pandas as pd

def calcular_alertas(df, meses):
    """Analiza si los gastos superan el presupuesto asignado."""
    df_alertas = []
    for _, row in df.iterrows():
        gasto_total = row[meses].sum()
        presupuesto = row.get("Presupuesto", 0)
        if presupuesto > 0 and gasto_total > presupuesto:
            df_alertas.append({
                "Concepto": row["Concepto"],
                "Gasto Total": gasto_total,
                "Presupuesto": presupuesto,
                "Exceso": gasto_total - presupuesto
            })
    return pd.DataFrame(df_alertas)
