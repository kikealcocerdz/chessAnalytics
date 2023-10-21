from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import base64


# Generar una clave aleatoria para Fernet
fernet_key = Fernet.generate_key()

# Crear un objeto Fernet con la clave generada
fernet_cipher = Fernet(fernet_key)


password_system = "abcdeofio"


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
# ESTO ESTÁ EN CLARO Y NO DEBERÍA, AÑADIR VARIABLE DE ENTORNO
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
# Genera una clave para cifrar y descifrar las credenciales del usuario
# Debes almacenar esta clave de manera segura en un entorno de producción
# Puedes usar una variable de entorno para esto.
db = SQLAlchemy(app)
app.app_context().push()
salt_password = os.urandom(16)
salt_user = os.urandom(16)


# Define el modelo de usuario
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    # cifrar con una clave del sistema
    secret_key = db.Column(db.String(120), nullable=False)
    salt = db.Column(db.String(120), nullable=False)
    user_chess = db.Column(db.String(120), nullable=False)

    def _repr_(self):
        return f"User('{self.username}', '{self.key}', '{self.secret_key}')"


db.create_all()


@app.route("/signup", methods=["POST"])
@cross_origin(origin="*")
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user_chess = data.get("user_chess")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_password,
        iterations=480000,
    )

    kdf_2 = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_user,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf_2.derive(password_system))
    master_key = kdf_2.derive(key)
    f = Fernet(master_key)
    secret_key_original = Fernet.generate_key()
    f_user = Fernet(secret_key_original)
    password_encrypted = kdf.derive(password)
    user_encrypted = f_user.encrypt(user_chess)
    secret_key_encrypted = f.encrypt(secret_key_original)

    # Crear un nuevo usuario en la base de datos
    user = User(
        email=username,
        password_hash=password_encrypted,
        secret_key=secret_key_encrypted,
        salt=salt_user,
        user_chess=user_encrypted,
    )  # faltaria añadir dos columnas a la base de datos que corresponden a user y salt
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "No se pudo crear el usuario"}, 400

    return {"message": "Usuario creado exitosamente"}


@app.route("/login", methods=["GET", "POST"])
@cross_origin(origin="http://localhost:5173")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(email=username).first()
    if user is None:
        return jsonify({"message": "No existe cuenta"}), 401
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_user,  # Este salt tiene que ser el salt con el que derivamos la password
        iterations=480000,
    )
    password_encrypted = kdf.derive(password.encode())
    f = Fernet(kdf.derive(password_system.encode()))
    secret_key = f.decrypt(user.secret_key)
    f_user = Fernet(secret_key)
    user_decrypted = f_user.decrypt(user.user).decode()

    if user_decrypted == data.get("user_chess"):
        return {"message": "Inicio de sesión exitoso"}
    else:
        return {"message": "Credenciales inválidas"}, 401


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
