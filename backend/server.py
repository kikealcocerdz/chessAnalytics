from flask import Flask, request
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hmac
app = Flask(__name__)
CORS(app)

# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.

users = []


@app.route("/signup", methods=["POST"])
@cross_origin(origin="*")
def signup():

    data = request.json
    username = data.get("username")
    if username in users:
        return {"message": "El usuario ya existe"}, 400
    password = data.get("password")
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
    key = kdf.derive(b"password")
    secret_key = Fernet.generate_key()
    users[username] = [key,secret_key,] 
    return {"message": "Cuenta creada exitosamente"}, 201




@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    key = users[username][0]
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
    derived_key = kdf.derive(password.encode())
    kdf.verify(b"password", derived_key)

    if username not in users:
        return {"message": "Usuario no encontrado "}

    if  kdf.verify(b"password", derived_key):
        return {'message': 'Inicio de sesión exitoso'},
    else:
        return {"message": "Credenciales incorrectas"}, 401


@app.route("/view_users", methods=["GET"])
def view_users():
    # Verifica si la solicitud proviene de localhost para seguridad en desarrollo
    if request.remote_addr != "127.0.0.1":
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

@app.route("/get_data")
@cross_origin(origin="*")
def get_data():
    r = requests.get("http://ergast.com/api/f1/current/last/results.json")
    r = r.json()
    return r
# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
