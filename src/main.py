import http.server
import socketserver
import json
import os
from database.db_manager import DBManager
from logic.auth import verify_credentials

PORT = 8080
UI_DIR = os.path.join(os.path.dirname(__file__), 'ui')

class RegistryHandler(http.server.SimpleHTTPRequestHandler):
    db = DBManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # RUTA: LOGIN
        if self.path == '/api/login':
            role = verify_credentials(data.get('username'), data.get('password'))
            if role:
                self._send_json({"status": "success", "role": role, "username": data.get('username')})
            else:
                self._send_json({"status": "error", "message": "Credenciales inválidas"}, 401)

        # RUTA: REGISTRAR INFANTE (Nueva)
        elif self.path == '/api/infants':
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO infants (father_name, mother_name, infant_name, blood_type_f, 
                                        blood_type_m, blood_type_i, weight, size, gender, birth_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data['father'], data['mother'], data['infant'], data['bt_f'], 
                      data['bt_m'], data['bt_i'], data['weight'], data['size'], 
                      data['gender'], data['birth_date']))
                conn.commit()
                conn.close()
                self._send_json({"status": "success", "message": "Infante registrado correctamente"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), RegistryHandler) as httpd:
        print(f"🚀 GS Digital Engine corriendo en puerto {PORT}")
        httpd.serve_forever()