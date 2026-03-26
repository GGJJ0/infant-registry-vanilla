import sqlite3
import os

# Ruta dinámica para encontrar la DB desde la lógica
DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/registry.db')

def verify_credentials(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscamos el rol si coinciden nombre y clave
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", 
                       (username, password))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"Error en Auth: {e}")
        return None