import sqlite3
import os

class DBManager:
    def __init__(self, db_path="/app/data/registry.db"):
        self.db_path = db_path
        # Asegurar que el directorio data exista dentro del contenedor
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        """Crea una conexión a la base de datos SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        return conn

    def _create_tables(self):
        """Crea las tablas necesarias para el sistema de GS Digital."""
        query_infants = """
        CREATE TABLE IF NOT EXISTS infants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            infant_name TEXT NOT NULL,
            gender TEXT,
            birth_date TEXT NOT NULL,
            father_name TEXT,
            mother_name TEXT,
            blood_type TEXT,
            weight REAL,
            size REAL,
            status TEXT DEFAULT 'Estable',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        query_users = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query_infants)
        cursor.execute(query_users)
        
        # Insertar usuario por defecto si no existe
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ('GGJJ', 'Banana123', 'admin'))
        
        conn.commit()
        conn.close()

    def add_infant(self, data):
        """Guarda un nuevo registro de infante."""
        query = """
        INSERT INTO infants (infant_name, gender, birth_date, father_name, mother_name, blood_type, weight, size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            data['infant'], data['gender'], data['birth_date'],
            data['father'], data['mother'], data.get('bt_i', 'O+'),
            data['weight'], data['size']
        ))
        conn.commit()
        conn.close()

    def get_all_infants(self):
        """Retorna todos los infantes registrados."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM infants ORDER BY created_at DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows