from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from db import get_connection


auth = Blueprint("auth", __name__)


MAPA_ROLES = {
    "admin": "Administrador",
    "administrador": "Administrador",
    "empleado": "Empleado",
    "trabajador": "Empleado",
}


def normalizar_rol(rol):
    """
    Convierte las distintas formas del rol a un valor estándar.
    """
    rol_normalizado = str(
        rol or ""
    ).strip().lower()

    return MAPA_ROLES.get(
        rol_normalizado
    )


@auth.route("/login", methods=["POST"])
def login():
    datos = request.get_json(
        silent=True
    )

    if not isinstance(datos, dict):
        return jsonify({
            "message": (
                "No se recibieron datos JSON válidos"
            )
        }), 400

    correo = str(
        datos.get("correo", "")
    ).strip().lower()

    contrasena = str(
        datos.get("contrasena", "")
    )

    if not correo or not contrasena:
        return jsonify({
            "message": (
                "El correo y la contraseña "
                "son obligatorios"
            )
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "message": (
                    "No fue posible conectar "
                    "con MariaDB"
                )
            }), 503

        cursor = conexion.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id_usuario,
                nombre,
                apellido,
                correo,
                contrasena,
                rol
            FROM usuario
            WHERE LOWER(correo) = %s
            LIMIT 1
            """,
            (correo,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "message": (
                    "Correo o contraseña incorrectos"
                )
            }), 401

        rol = normalizar_rol(
            usuario.get("rol")
        )

        if rol is None:
            return jsonify({
                "message": (
                    "Este usuario no tiene un rol "
                    "autorizado para entrar al sistema"
                )
            }), 403

        hash_guardado = str(
            usuario.get("contrasena") or ""
        )

        try:
            contrasena_correcta = (
                check_password_hash(
                    hash_guardado,
                    contrasena
                )
            )

        except (
            ValueError,
            TypeError
        ):
            contrasena_correcta = False

        if not contrasena_correcta:
            return jsonify({
                "message": (
                    "Correo o contraseña incorrectos"
                )
            }), 401

        nombre_completo = " ".join(
            parte
            for parte in [
                usuario.get("nombre"),
                usuario.get("apellido")
            ]
            if parte
        ).strip()

        token = create_access_token(
            identity=str(
                usuario["id_usuario"]
            ),
            additional_claims={
                "rol": rol,
                "nombre": nombre_completo
            }
        )

        return jsonify({
            "message": (
                "Inicio de sesión exitoso"
            ),
            "token": token,
            "id_usuario": (
                usuario["id_usuario"]
            ),
            "nombre": nombre_completo,
            "rol": rol
        }), 200

    except Exception as error:
        print(
            "[LOGIN] Error:",
            error
        )

        return jsonify({
            "message": (
                "Error interno al iniciar sesión"
            )
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()