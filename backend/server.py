from flask import Flask, request
from flask_cors import CORS, cross_origin
import requests
from cryptography.fernet import Fernet
import hmac
import hashlib

app = Flask(__name__)
CORS(app)

# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.

users = []

@app.route('/signup', methods=['POST'])
@cross_origin(origin='*')
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return {'message': 'El usuario ya existe'}, 400
    secret_key = Fernet.generate_key()
    h = hmac.HMAC(secret_key, hashes.SHA256())
    users[username] = [password,secret_key]  # Almacena la contraseña en texto plano (debes mejorar la seguridad)

    return {'message': 'Cuenta creada exitosamente'}, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    secret_pasword=users[username][1]

    if username not in users:
        return {'message': 'Usuario no encontrado '}

    if username in users and secret_pasword == password.encode():
        return {'message': 'Inicio de sesión exitoso'},
    else:
        return {'message': 'Credenciales incorrectas'}, 401

@app.route('/view_users', methods=['GET'])
def view_users():
    # Verifica si la solicitud proviene de localhost para seguridad en desarrollo
    if request.remote_addr != '127.0.0.1':
        return "Acceso no permitido", 403

    # Obtén la lista de usuarios registrados (solo para fines de depuración)
    user_list = list(users.keys())

    # Construye una respuesta HTML con la lista de usuarios
    html_response = "<h1>Lista de Usuarios Registrados</h1>"
    html_response += "<ul>"
    for username in user_list:
        html_response += f"<li>{username}</li>"
    html_response += "</ul>"

    return html_response

@app.route('/get_data')
@cross_origin(origin='*')
def get_data():
    r = requests.get("http://ergast.com/api/f1/current/last/results.json")
    r = r.json()
    return r

# Running app
if __name__ == '__main__':
    app.run(debug=True, port=8080)
