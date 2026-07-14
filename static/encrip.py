import mysql.connector
from werkzeug.security import generate_password_hash

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="canelo16",
    database="farmacia"
)

cursor = conexion.cursor()



from werkzeug.security import generate_password_hash

contrasenas = [
    "123456", "abcdef", "qwerty", "password1",
    "mexico123", "sofia2025", "clave789",
    "vale1234", "miguel99", "fer2024",
    "jorge321", "dani2023", "ricardo12",
    "paola456", "andres789", "cami2026",
    "fernando1", "andrea22", "josepass",
    "natalia10", "roberto9", "karla888",
    "hugo2025", "gaby123", "alex2024",
    "paty321", "eduardo77", "vero999",
    "fran456", "isa2026"
]

for i, password in enumerate(contrasenas, start=1):
    cursor.execute(
        "UPDATE usuario SET contrasena=%s WHERE id_usuario=%s",
        (generate_password_hash(password), i)
    )

conexion.commit()