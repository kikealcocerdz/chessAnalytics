from flask import Flask, request
from flask_cors import CORS, cross_origin
import requests
from cryptography.fernet import Fernet

app = Flask(__name__)
CORS(app)

# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.
key = Fernet.generate_key()
fernet = Fernet(key)

users = {}

@app.route('/signup', methods=['POST'])
@cross_origin(origin='*')
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return {'message': 'El usuario ya existe'}, 400

    users[username] = password  # Almacena la contraseña en texto plano (debes mejorar la seguridad)

    return {'message': 'Cuenta creada exitosamente'}, 201
  
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and fernet.decrypt(users[username]) == password.encode():
        return {'message': 'Inicio de sesión exitoso'}
    else:
        return {'message': 'Credenciales incorrectas'}, 401

@app.route('/get_data')
@cross_origin(origin='*')
def get_data():
    r = requests.get("http://ergast.com/api/f1/current/last/results.json")
    r = r.json()
    return r

# Running app
if __name__ == '__main__':
    app.run(debug=True, port=8080)
