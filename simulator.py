import sqlite3
import random
from datetime import datetime, timedelta

def generar_datos_prueba(cantidad=100):
    # Conexión a tu base de datos local en la Helios 18
    # Asegúrate de que la carpeta 'data' exista
    try:
        conn = sqlite3.connect('data/registry.db')
        cur = conn.cursor()
        
        nombres = ["Liam", "Emma", "Noah", "Mateo", "Sara", "Lucas", "Mia", "Benjamin", "Lucia", "Julian"]
        apellidos = ["Gonzalez", "Gutierrez", "Rodriguez", "Perez", "Velez", "Martinez", "Lopez", "Garcia"]
        tipos_sangre = ["O Rh+", "O Rh-", "A Rh+", "A Rh-", "B Rh+", "B Rh-", "AB Rh+", "AB Rh-"]
        generos = ["Masculino", "Femenino"]
        estados = ["Vivo", "Fallecido"]
        causas = ["Natural", "Accidente", "Enfermedad Cardiovascular", "Infección", "Falla Orgánica"]

        print(f"🚀 Iniciando simulación para GS Digital...")

        for i in range(cantidad):
            nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
            genero = random.choice(generos)
            
            # Generamos un rango de edad amplio (de 0 a 90 años)
            # 32850 días son aproximadamente 90 años
            dias_atras = random.randint(0, 32850)
            fecha_nac = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            sangre = random.choice(tipos_sangre)
            peso = round(random.uniform(2.5, 90.0), 2)
            talla = round(random.uniform(48.0, 190.0), 2)
            
            # El 90% de los datos serán "Vivo" para que tus gráficas se vean realistas
            estado_vital = "Vivo" if random.random() > 0.1 else "Fallecido"
            causa_fallecimiento = random.choice(causas) if estado_vital == "Fallecido" else None

            cur.execute('''
                INSERT INTO infants (
                    nombre, genero, fecha_nacimiento, tipo_sangre, 
                    padre, madre, peso, talla, estado, causa_difusion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, genero, fecha_nac, sangre, 
                "Padre Test", "Madre Test", peso, talla, 
                estado_vital, causa_fallecimiento
            ))

        conn.commit()
        conn.close()
        print(f"✅ ¡Simulación finalizada! {cantidad} registros creados con éxito.")

    except sqlite3.OperationalError as e:
        print(f"❌ Error: No se encontró la base de datos. {e}")
        print("💡 Asegúrate de ejecutar primero la creación de la tabla.")

if __name__ == "__main__":
    generar_datos_prueba(100)