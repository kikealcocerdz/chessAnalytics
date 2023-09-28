from flask import Flask, request, jsonify
import hashlib
import os
from flask_cors import CORS, cross_origin
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)
CORS(app)

# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.

users = {}


@app.route("/signup", methods=["POST"])
@cross_origin(origin="*")
def signup():
    salt = os.urandom(16)
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
    key = kdf.derive(password.encode())  # Corregido para derivar la clave correctamente
    secret_key = Fernet.generate_key()
    users[username] = [
        key,
        secret_key,
    ]
    return {"message": "Cuenta creada exitosamente"}, 201


@app.route("/login", methods=["POST"])
@cross_origin(origin="*")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username not in users:
        return jsonify({"message": "Usuario no encontrado"}), 401

    stored_key = users[username][0]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # Asegúrate de que 'salt' esté definida en algún lugar
        iterations=480000,
    )
    derived_key = kdf.derive(password.encode())

    if stored_key == derived_key:
        return jsonify({"message": "Inicio de sesión exitoso"})
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401


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
    return jsonify(r)  # Añadida la función 'jsonify' para enviar una respuesta JSON


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
