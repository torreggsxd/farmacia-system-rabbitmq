import mysql.connector
from mysql.connector import Error

# ==========================
# CONFIGURACIÓN DE MySQL
# ==========================

HOST = "localhost"
USER = "root"
PASSWORD = "canelo16"   # Cambia por tu contraseña de MySQL
DATABASE = "farmacia"
PORT = 3306


def get_connection():
    """
    Crea y devuelve una conexión a la base de datos.
    """

    try:
        conexion = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            port=PORT
        )

        if conexion.is_connected():
            print("✅ Conectado a MySQL")
            return conexion

    except Error as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        return None


def close_connection(conexion):
    """
    Cierra la conexión si está abierta.
    """

    if conexion and conexion.is_connected():
        conexion.close()
        print("🔒 Conexión cerrada")