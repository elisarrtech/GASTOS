import pandas as pd

# Datos ficticios
data = {
    "Categoría": [
        "Nóminas", "Nóminas", "Nóminas", "Nóminas", "Nóminas",
        "Seguros y fianzas", "Seguros y fianzas", "IMSS", "Poder Ejecutivo",
        "Gastos de oficina", "AMEX", "Comisiones", "Comisiones"
    ],
    "Concepto": [
        "Armando Arvizu", "Miriam Ruiz", "Victoria Méndez", "Oscar Rodríguez", "Sonia Luna",
        "Seguro de empresa GNP", "Seguro de vida Santander",
        "Cuota patronal", "Trámite vehicular",
        "Internet", "Telefonía",
        "Promotor 1 Omar", "Promotor 2 Alex"
    ],
    "Junio": ["$4,182"] * 13,
    "Julio": ["$4,182"] * 13,
    "Agosto": ["$4,182"] * 13,
    "Septiembre": ["$4,182"] * 13,
    "Octubre": ["$4,182"] * 13,
    "Noviembre": ["$4,182"] * 13,
    "Diciembre": ["$4,182"] * 13
}

# Crear DataFrame
df = pd.DataFrame(data)

# Guardar como CSV
df.to_csv("hoja_ejemplo_gastos.csv", index=False, encoding="utf-8")

print("Archivo CSV creado exitosamente.")
