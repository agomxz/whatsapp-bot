from math import pow

def calculate_financing(price: float, down_payment: float) -> str:
    """
    Calcula planes de financiamiento con base en:
    - Enganche
    - Precio del auto
    - Tasa de interés anual fija: 10%
    - Plazos de 3 a 6 años
    """
    try:
        financed_amount = price - down_payment
        annual_rate = 0.10
        monthly_rate = annual_rate / 12

        results = []
        for years in range(3, 7):
            n = years * 12
            M = financed_amount * (monthly_rate * pow(1+monthly_rate, n)) / (pow(1+monthly_rate, n) - 1)
            results.append(
                f"{years} años ({n} meses): mensualidad = ${M:,.2f}"
            )

        return "\n".join(results)

    except Exception as e:
        return f"Error en cálculo: {e}"