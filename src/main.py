import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# --- CONFIGURACIÓN DE RUTAS DINÁMICAS ---
# Si existe /app, estamos en Docker. Si no, estamos en desarrollo local.
APP_ROOT = "/app" if os.path.exists("/app") else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UI_DIR = os.path.join(APP_ROOT, 'ui')
DB_PATH = os.path.join(APP_ROOT, 'data', 'registry.db')

app = Flask(__name__, static_folder=UI_DIR, static_url_path='')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- SERVIDOR DE ARCHIVOS ESTÁTICOS (Interfaz) ---
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# --- API DE INFANTES (CRUD COMPLETO) ---

@app.route('/api/infants', methods=['GET'])
def get_infants():
    try:
        conn = get_db_connection()
        # Nombre de tabla 'registry' verificado en tu DB
        infants = conn.execute('SELECT * FROM registry ORDER BY id DESC').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in infants])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/infants', methods=['POST'])
def add_infant():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO registry (nombre, genero, fecha_nacimiento, tipo_sangre, padre, madre, peso, talla, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['nombre'], data['genero'], data['fecha_nacimiento'], 
              data['tipo_sangre'], data['padre'], data['madre'], 
              data['peso'], data['talla'], data.get('estado', 'Vivo')))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"message": "Registrado", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/infants/<int:id>', methods=['PUT'])
def update_infant(id):
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE registry 
            SET nombre=?, genero=?, fecha_nacimiento=?, tipo_sangre=?, padre=?, madre=?, peso=?, talla=?, estado=?
            WHERE id=?
        ''', (data['nombre'], data['genero'], data['fecha_nacimiento'], 
              data['tipo_sangre'], data['padre'], data['madre'], 
              data['peso'], data['talla'], data.get('estado', 'Vivo'), id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/infants/<int:id>', methods=['DELETE'])
def delete_infant(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM registry WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        gen_data = conn.execute('SELECT genero, COUNT(*) as total FROM registry GROUP BY genero').fetchall()
        blood_data = conn.execute('SELECT tipo_sangre, COUNT(*) as total FROM registry GROUP BY tipo_sangre').fetchall()
        conn.close()
        return jsonify({
            "generos": {row['genero']: row['total'] for row in gen_data},
            "sangre": {row['tipo_sangre']: row['total'] for row in blood_data}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' permite conexión externa desde Docker
    app.run(host='0.0.0.0', port=8080, debug=True)