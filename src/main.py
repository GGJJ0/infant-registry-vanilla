import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# --- CONFIGURACIÓN DE RUTAS ---
# BASE_DIR es la carpeta 'src'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# La carpeta 'ui' está un nivel arriba de 'src' según tu estructura de archivos
UI_DIR = os.path.join(os.path.dirname(BASE_DIR), 'ui')

# La carpeta 'data' también está un nivel arriba de 'src'
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'data', 'registry.db')

app = Flask(__name__, static_folder=UI_DIR)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

# --- SERVIR INTERFAZ ---
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# --- API DE INFANTES (CRUD COMPLETO) ---

# 1. LEER (Get all)
@app.route('/api/infants', methods=['GET'])
def get_infants():
    conn = get_db_connection()
    infants = conn.execute('SELECT * FROM infants ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in infants])

# 2. CREAR (Post)
@app.route('/api/infants', methods=['POST'])
def add_infant():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO infants (nombre, genero, fecha_nacimiento, tipo_sangre, padre, madre, peso, talla, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['nombre'], data['genero'], data['fecha_nacimiento'], 
          data['tipo_sangre'], data['padre'], data['madre'], 
          data['peso'], data['talla'], 'Vivo'))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"message": "Registrado con éxito", "id": new_id}), 201

# 3. ACTUALIZAR / EDITAR (Put)
@app.route('/api/infants/<int:id>', methods=['PUT'])
def update_infant(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE infants 
        SET nombre=?, genero=?, fecha_nacimiento=?, tipo_sangre=?, padre=?, madre=?, peso=?, talla=?, estado=?
        WHERE id=?
    ''', (data['nombre'], data['genero'], data['fecha_nacimiento'], 
          data['tipo_sangre'], data['padre'], data['madre'], 
          data['peso'], data['talla'], data.get('estado', 'Vivo'), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Registro actualizado correctamente"}), 200

# 4. ELIMINAR (Delete)
@app.route('/api/infants/<int:id>', methods=['DELETE'])
def delete_infant(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM infants WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Registro eliminado"}), 200

# --- API DE ESTADÍSTICAS PARA GRÁFICAS ---
@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    # Conteo por Género para el gráfico de pastel
    gen_data = conn.execute('SELECT genero, COUNT(*) as total FROM infants GROUP BY genero').fetchall()
    generos = {row['genero']: row['total'] for row in gen_data}
    
    # Conteo por Tipo de Sangre para el gráfico de barras
    blood_data = conn.execute('SELECT tipo_sangre, COUNT(*) as total FROM infants GROUP BY tipo_sangre').fetchall()
    sangre = {row['tipo_sangre']: row['total'] for row in blood_data}
    
    conn.close()
    return jsonify({"generos": generos, "sangre": sangre})

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # IMPORTANTE: host='0.0.0.0' es obligatorio para Docker
    app.run(host='0.0.0.0', port=8080, debug=True)