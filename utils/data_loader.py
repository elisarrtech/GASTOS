import pandas as pd

def limpiar_monto(valor):
    try:
        return float(str(valor).replace("$", "").replace(",", ""))
    except:
        return 0.0

def cargar_datos(ruta_csv):
    df = pd.read_csv(ruta_csv)
    return df

