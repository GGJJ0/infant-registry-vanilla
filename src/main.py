from flask import Flask, request, jsonify, send_from_directory
from database.db_manager import DBManager
# Importamos la lógica pero la usaremos solo si es necesario validar
from logic.calculator import calculate_age 

app = Flask(__name__, static_folder='ui')
db = DBManager()

# --- 1. RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    # Esto sirve el CSS y el JS automáticamente desde la carpeta ui/
    return send_from_directory(app.static_folder, path)

# --- 2. RUTAS DE LA API ---

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # Credenciales maestras de GS Digital
    if username == 'GGJJ' and password == 'Banana123':
        return jsonify({"success": True, "username": username})
    
    return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

@app.route('/add_infant', methods=['POST'])
def add_infant():
    try:
        data = request.json
        # Opcional: Validamos la edad antes de guardar para asegurar que calculator.py funcione
        calculate_age(data.get('birth_date'))
        db.add_infant(data)
        return jsonify({"success": True, "message": "Registro exitoso"})
    except Exception as e:
        print(f"Error en add_infant: {e}")
        return jsonify({"success": False, "message": "Error al procesar el registro"}), 500

@app.route('/get_infants', methods=['GET'])
def get_infants():
    try:
        # Traemos los datos crudos, el script.js se encarga del segundero
        infants = db.get_all_infants()
        return jsonify(infants)
    except Exception as e:
        print(f"Error en get_infants: {e}")
        return jsonify({"error": "No se pudieron cargar los registros"}), 500

if __name__ == '__main__':
    # host='0.0.0.0' es el puente entre el contenedor y tu Helios 18
    app.run(host='0.0.0.0', port=8080, debug=True)