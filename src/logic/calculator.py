from datetime import datetime

def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        now = datetime.now()
        diff = now - birth_date

        if diff.days < 0:
            return {"text": "Fecha futura"}

        years = diff.days // 365
        remaining_days = diff.days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        
        # Cálculo de horas y minutos
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        return {
            "years": years,
            "months": months,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "text": f"{years}y {months}m {days}d, {hours:02d}:{minutes:02d}h"
        }
    except Exception as e:
        print(f" Error en calculator: {e}")
        return {"text": "Error en fecha"}