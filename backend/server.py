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

password_system = "1234"


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
users = {}
salt = os.urandom(16)
salt2 = os.urandom(16)


# Define el modelo de usuario
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    key = db.Column(db.String(120), nullable=False)
    # cifrar con una clave del sistema
    secret_key = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.key}', '{self.secret_key}')"


db.create_all()


@app.route("/signup", methods=["POST"])
@cross_origin(origin="*")
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    kdf_2 = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt2,
        iterations=480000,
    )
    # Corregido para derivar la clave correctamente
    key = kdf.derive(password.encode())

    #
    secret_key_original = Fernet.generate_key()
    secret_key = Fernet.encrypt(
        secret_key_original, kdf_2.derive(password_system, salt2)
    )

    user = User(email=username, key=key, secret_key=secret_key)
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
    stored_key = user.key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # Asegúrate de que 'salt' esté definida en algún lugar
        iterations=480000,
    )
    derived_key = kdf.derive(password.encode())
    print(stored_key)

    if derived_key == stored_key:
        return jsonify({"message": "Correct sesion", "token": generate_token(username)})
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
