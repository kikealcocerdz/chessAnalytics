from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy


# Genera un token JWT para el usuario
def generate_token(username):
    # Define la información del token
    payload = {
        "sub": username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
    }

    # Genera el token
    token = jwt.encode(payload, "secret", algorithm="HS256")

    return token


app = Flask(__name__)
CORS(app)
DB_NAME = "users.db"
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.
db = SQLAlchemy(app)

users = {}
salt = os.urandom(16)

# Define el modelo de usuario


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.key}', '{self.secret_key}')"


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
    # Corregido para derivar la clave correctamente
    key = kdf.derive(password.encode())
    secret_key = Fernet.generate_key()
    users[username] = [
        key,
        secret_key,
    ]
    return {"message": "Cuenta creada exitosamente"}, 201


@app.route("/login", methods=["GET", "POST"])
@cross_origin(origin="http://localhost:5173")
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
        return jsonify({"message": "Correct sesion", "token": generate_token(username)})
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
    # Añadida la función 'jsonify' para enviar una respuesta JSON
    return jsonify(r)


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
