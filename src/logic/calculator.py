from datetime import datetime

def get_detailed_age(birth_date_str):
    """
    Calcula la edad exacta desde una fecha en formato ISO (YYYY-MM-DDTHH:MM)
    hasta el momento actual.
    """
    try:
        # Convertimos el texto de la DB a objeto de fecha
        birth_date = datetime.fromisoformat(birth_date_str)
        now = datetime.now()
        
        diff = now - birth_date
        
        # Cálculos manuales para precisión vanilla
        years = now.year - birth_date.year
        months = now.month - birth_date.month
        
        if now.day < birth_date.day:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
            
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        return {
            "years": years,
            "months": months,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": secs,
            "text": f"{years}y {months}m {days}d, {hours:02d}:{minutes:02d}:{secs:02d}"
        }
    except Exception as e:
        print(f"Error detectado: {e}") # Ahora sí usas la 'e'
        return {"text": "Error en fecha"}