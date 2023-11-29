from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.x509.oid import NameOID
from cryptography import x509
import jwt
import datetime 
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import base64
from flask import send_file
from cryptography.hazmat.primitives.asymmetric import padding

# Genera un token JWT para el usuario


app = Flask(__name__)
CORS(app)
DB_NAME = "users.db"
# ESTAS CONTRASEÑAS NO DEBERÍAN ESTAR AQUÍ Y DEBEN SER AÑADIDAS COMO VARIABLE DE ENTORNO, PERO AHORA MISMO NO ESTÁ IMPLEMENTADO
password_system = b"abcdeofio"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
clave_user = b"1234"
clave_autoridad = b"autoridad"
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
    salt_master_key = os.urandom(16)
    kdf_2 = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_master_key,
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
        salt=salt_master_key,
        salt_2=salt_password,
        user_chess=user_encrypted,
    )
    key_user = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
    os.mkdir(str(user_chess))
    with open(str(user_chess)+"/key_user.pem", "wb") as f:
        f.write(key_user.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(),
    ))
    # faltaria añadir dos columnas a la base de datos que corresponden a user y salt
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"message": "No se pudo crear el usuario"}, 400

    return {"message": "Usuario creado exitosamente"}

@app.route("/claves", methods=["POST", "GET"])
@cross_origin(origin="*")
def claves():
    autoridad_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
    #Aqui abria que coger las variables que queremos firmar como los puntos con el nombre del usuario
    with open("AC1/keyac.pem", "wb") as f:
        f.write(autoridad_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(clave_autoridad), #esto debería sacarse de un fichero de configuración

    ))
    return {"message": "Claves generadas exitosamente"}, 200

    


def request_user():
    data = request.json
    user = data.get("user_chess")
    #Coge la clave privada del usuario
    with open(str(user)+"/key_user.pem", 'rb') as f:
        key_data = f.read()

    key = serialization.load_pem_private_key(
    key_data,
    password=clave_user, 
)

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Rellenar datos.
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ChessAnalytics"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
    
    ])).add_extension(
    x509.SubjectAlternativeName([
        # Describir para que sitio web utilizaremos el certificado.
        x509.DNSName("http://localhost:5173/dashboard"),
    ]),
    critical=False,
    # Firmar con la privada (del usuario).
    ).sign(key, hashes.SHA256())
    # Escribir en disco.
    key_filepath = "/home/kikealcocerdz/Documents/year-3/CRI-SEG-INF/chessAnalytics/AC1/solicitudes/"+str(user)+"_csr.pem"

    with open(key_filepath, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    return {"message": "Solicitud enviada correctamente"}, 200    
        
def firma_user():
    #Obtenemso el usuario
    data = request.json
    user = data.get("user_chess")
    #Accedemos a su clave
    with open(str(user)+ "/key_user.pem", "rb") as f2:
        key_user = f2.read()
        key_user= serialization.load_pem_private_key(
            key_user,
            password=clave_user,
        )
    #Accedemos al certificado de la autoridad
    with open("AC1/ac1cert.pem", "rb") as ac:
        cert_autoridad=ac.read()
        cert_autoridad=x509.load_pem_x509_certificate(cert_autoridad)
        
    #Comprobamos el certificado de la autoridad
    try:
        cert_autoridad.public_key().verify(
            cert_autoridad.signature,
            cert_autoridad.tbs_certificate_bytes,
            cert_autoridad.signature_algorithm_parameters,
            cert_autoridad.signature_hash_algorithm
        )
    except Exception as e:
        print("El certificado de la autoridad es falso", e)
    else:
        print("El certificado de la autoridad es verdadero")
    #Obtenemos el mensaje que vamos a firmar    
    with open(str(user)+"/mensaje", "rb") as f:
        info_firma=f.read()
    #Firmamos el mensaje con la clave privada del usuario    
    signature = key_user.sign(
        info_firma,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    #Creamos el pem de la firma que se abrirá desde el sistema para comprobarla
    with open(str(user)+"/signature", "wb") as f:
        f.write(signature)

@app.route("/firma", methods=["POST"])
@cross_origin(origin="*")
def firma():
    data = request.json
    user = data.get("user_chess")
    #El usuario realiza el resquest (csr)
    request_user()
    print("Procesando")
    #Se lee el archivo serial
    with open("AC1/serial", "r") as serial:
        NUMERO_SERIAL_DE_LA_AUTORIDAD = serial.read().strip()

    #Limpiamos el index.txt
    with open("AC1/index.txt", "w") as index:
        index.write("")
        
    #Certificamos en linea la petición, y espera hasta que se haya creado    
    while not os.path.isfile("AC1/nuevoscerts/" + NUMERO_SERIAL_DE_LA_AUTORIDAD + ".pem"):
        pass
    #Tiempo que necesitamos para poder acceder al mismo fichero
    time.sleep(1)
    #Movemos el certificado a la carpeta privada de cada usuario
    os.rename("AC1/nuevoscerts/"+ NUMERO_SERIAL_DE_LA_AUTORIDAD + ".pem", str(user)+ "/"+ str(user)+ "certificado.pem")
    #Abrimos el certificado creado y lo verificamos
    with open(str(user)+ "/"+ str(user)+ "certificado.pem", "rb") as file:
        cert_bytes=file.read()
        cert= x509.load_pem_x509_certificate(cert_bytes)
    #Llave de la autoridad para verificar el certificado
    with open("AC1/privado/ca1key.pem", "rb") as f2:
        key = f2.read()
        key= serialization.load_pem_private_key(
            key,
            password=clave_autoridad,
        )
    #Verificacion
    try:
        key.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            cert.signature_algorithm_parameters,
            cert.signature_hash_algorithm
        )
    except Exception as e:
        print("El certificado del usuario es falso", e)
    else:
        print("El certificado del usuario es valido.")
    #Escribimos el mensaje a firmar
    info_firma = ("stats_blitz: {stats_blitz}, stats_bullet: {stats_bullet}, stats_daily: {stats_daily}, stats_rapid: {stats_rapid}").encode("utf-8")
    with open(str(user)+"/mensaje", "wb") as f:
        f.write(info_firma)
    #El usuario firma    
    firma_user()
    #Abre la firma y la verifica 
    with open(str(user)+"/signature", "rb") as f:
        signature=f.read()
    try:
        cert.public_key().verify(
            signature,
            info_firma,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
    except Exception as e:
        print("La firma del usuario es inválida:", e)
    else:
        print("La firma del usuario es válida.")
    #Para la escritura de datos en terminal
    try:
        with open("AC1/ac1cert.pem", "rb") as file:
            cert_autoridad = x509.load_pem_x509_certificate(file.read())
    except FileNotFoundError:
        print("No se pudo encontrar el archivo del certificado.")
        
   

    # Extrae la información que se printea en terminal
    subject = cert_autoridad.subject
    issuer = cert_autoridad.issuer
    serial_number = cert_autoridad.serial_number
    not_valid_before = cert_autoridad.not_valid_before
    not_valid_after = cert_autoridad.not_valid_after

    print("Subject:")
    for attribute in subject:
        print(f"  {attribute.oid}: {attribute.value}")
    print(f"Issuer: {issuer}")
    print(f"Serial number: {serial_number}")
    print(f"Not valid before: {not_valid_before}")
    print(f"Not valid after: {not_valid_after}")

    signature = cert_autoridad.signature
    signature_algorithm = cert_autoridad.signature_hash_algorithm

    print(f"Signature: {signature}")
    print(f"Signature Algorithm: {signature_algorithm.name}")

    return {"message": "Puntuaciones firmadas correctamente ya en tu dispositivo"}, 200




    




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
    salt_master_key = user.salt
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
        salt=salt_master_key,
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
        return jsonify({"message": "El usuario no es válido", "token": 1, "user_chess": user_decrypted.decode()})


# Running app
if __name__ == "__main__":
    app.run(debug=True, port=8080)