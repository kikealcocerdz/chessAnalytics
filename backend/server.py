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

password_system = b"abcdeofio"


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




# Define el modelo de usuario
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    # cifrar con una clave del sistema
    secret_key = db.Column(db.String(120), nullable=False)
    salt = db.Column(db.String(120), nullable=False)
    user_chess = db.Column(db.String(120), nullable=False)
    salt_2 = db.Column(db.String(120), nullable=False)

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
    salt_password = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_password,
        iterations=480000,
    )
    salt_user = os.urandom(16)
    kdf_2 = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_user,
        iterations=480000,
    )
    # Generamos el fernet con la master key
    master_key = base64.urlsafe_b64encode(kdf_2.derive(password_system))
    f_master_key = Fernet(master_key)

    # Generar una clave secreta sin codificar
    secret_key_original = Fernet.generate_key()

    # Cifrar la clave secreta con el fernet de la master key
    secret_key_encrypted = f_master_key.encrypt(secret_key_original)

    password_encrypted = kdf.derive(password.encode())

    f_user = Fernet(secret_key_original)
    user_encrypted = f_user.encrypt(user_chess.encode())

    # Crear un nuevo usuario en la base de datos
    user = User(
        email=username,
        password_hash=password_encrypted,
        secret_key=secret_key_encrypted,
        salt=salt_user,
        salt_2=salt_password,
        user_chess=user_encrypted,
    )
    # faltaria añadir dos columnas a la base de datos que corresponden a user y salt
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
    user_password = user.password_hash
    secret_key = user.secret_key
    user_chess = user.user_chess
    salt_password = user.salt_2
    salt_user = user.salt
    if user is None:
        return jsonify({"message": "No existe cuenta"}), 401

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

    password_encrypted = kdf.derive(password.encode())
    if user_password != password_encrypted:
        return jsonify({"message": "No es valida la contraseña"})

    # Para verificar el usuario tenemos que decodificar la clave secreta, por lo que necesitamos la clave del sistema y crear su Fernet
    master_key = base64.urlsafe_b64encode(kdf_2.derive(password_system))
    f_master_key = Fernet(master_key)
    # Esa secret_key se saca de la base de datos
    secret_key_decrypt = f_master_key.decrypt(secret_key)

    f_user = Fernet(secret_key_decrypt)
    # Ese user_chess es de la base de datos
    user_decrypted = f_user.decrypt(user_chess)
    # Ese user es el que introduce el usuario para acceder a chess.com Con data.get(user)
    if user_decrypted != user_chess:
        return jsonify({"message": "El usuario no es válido", "token": generate_token(username), "user_chess": user_decrypted.decode()})


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
