def calcular_plan(precio_auto, enganche, tasa=0.10, plazo_anios=3):
    monto = precio_auto - enganche
    r = tasa / 12
    n = plazo_anios * 12
    pmt = (monto * r) / (1 - (1 + r) ** -n)
    return round(pmt, 2)