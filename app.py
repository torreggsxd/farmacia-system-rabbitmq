from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import os
from uuid import uuid4

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request,
)
from mysql.connector import Error
from werkzeug.security import generate_password_hash

from auth import auth
from crud_config import TABLAS_CRUD
from db import get_connection
from rabbitmq_service import (
    RabbitMQNoDisponible,
    publicar_operacion,
)
from ventas_service import (
    ErrorBaseDatos,
    ErrorTemporalBaseDatos,
    ErrorVenta,
    registrar_venta_en_bd,
)


# ==========================================================
# CONFIGURACIÓN GENERAL DE FLASK
# ==========================================================

app = Flask(__name__)

CORS(app)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY",
    "farmacia-demo-clave-secreta-2026",
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    hours=8
)

jwt = JWTManager(app)

app.register_blueprint(
    auth,
    url_prefix="/api",
)


# ==========================================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================================

ROLES_PERMITIDOS = {
    "administrador",
    "empleado",
}

ENDPOINTS_PUBLICOS = {
    "inicio",
    "mostrar_login",
    "mostrar_sistema",
    "favicon",
    "estado_sistema",
    "static",
    "auth.login",
}

TABLAS_TRANSACCIONALES = {
    "venta",
    "detalle_venta",
    "factura",
}


def obtener_rol_actual():
    """
    Obtiene el rol almacenado dentro del token JWT.
    """
    datos_token = get_jwt()

    return str(
        datos_token.get("rol") or ""
    ).strip().lower()


def usuario_es_administrador():
    return obtener_rol_actual() == "administrador"


def validar_permiso_modificacion(tabla):
    """
    Solo los administradores pueden agregar, editar
    o eliminar usuarios.
    """
    if (
        tabla == "usuario"
        and not usuario_es_administrador()
    ):
        return jsonify({
            "error": (
                "Solo un administrador puede modificar "
                "los usuarios del sistema"
            )
        }), 403

    return None


@app.before_request
def proteger_rutas_del_sistema():
    """
    Protege las rutas de datos utilizando JWT.

    Las páginas HTML se permiten porque el token se encuentra
    en localStorage y JavaScript lo envía posteriormente.
    """
    if request.method == "OPTIONS":
        return None

    if request.endpoint is None:
        return None

    if request.endpoint in ENDPOINTS_PUBLICOS:
        return None

    verify_jwt_in_request()

    rol = obtener_rol_actual()

    if rol not in ROLES_PERMITIDOS:
        return jsonify({
            "error": (
                "El usuario autenticado no tiene un rol "
                "autorizado para utilizar el sistema"
            )
        }), 403

    return None


# ==========================================================
# RESPUESTAS DE ERROR JWT
# ==========================================================

@jwt.unauthorized_loader
def token_faltante(mensaje):
    return jsonify({
        "error": "La sesión es obligatoria",
        "detalle": mensaje,
    }), 401


@jwt.invalid_token_loader
def token_invalido(mensaje):
    return jsonify({
        "error": "El token de sesión no es válido",
        "detalle": mensaje,
    }), 422


@jwt.expired_token_loader
def token_expirado(jwt_header, jwt_payload):
    return jsonify({
        "error": (
            "La sesión expiró. "
            "Inicia sesión nuevamente."
        )
    }), 401


# ==========================================================
# PÁGINAS DEL SISTEMA
# ==========================================================

@app.route("/", methods=["GET"])
def inicio():
    return redirect(
        url_for("mostrar_login")
    )


@app.route("/login", methods=["GET"])
def mostrar_login():
    return render_template(
        "login.html"
    )


@app.route("/sistema", methods=["GET"])
def mostrar_sistema():
    return render_template(
        "index.html"
    )


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return "", 204


@app.route("/estado", methods=["GET"])
def estado_sistema():
    return jsonify({
        "servicio": "farmacia-api",
        "estado": "activo",
        "rabbitmq": "integrado",
    }), 200


# ==========================================================
# FUNCIONES AUXILIARES DEL CRUD
# ==========================================================

def obtener_configuracion(tabla):
    """
    Devuelve la configuración de una tabla permitida.
    """
    return TABLAS_CRUD.get(tabla)


def serializar_valor(valor):
    """
    Convierte valores de MariaDB a valores compatibles
    con respuestas JSON.
    """
    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, (date, datetime)):
        return valor.isoformat()

    return valor


def serializar_registros(registros):
    resultado = []

    for registro in registros:
        fila = {}

        for columna, valor in registro.items():
            fila[columna] = serializar_valor(
                valor
            )

        resultado.append(fila)

    return resultado


def valor_vacio(valor):
    if valor is None:
        return True

    if (
        isinstance(valor, str)
        and valor.strip() == ""
    ):
        return True

    return False


def convertir_valor(
    nombre_campo,
    valor,
    configuracion_campo,
):
    """
    Convierte los datos enviados desde JavaScript
    al tipo necesario para MariaDB.
    """
    tipo = configuracion_campo.get(
        "tipo",
        "text",
    )

    if valor_vacio(valor):
        return None

    # ------------------------------------------------------
    # NÚMEROS
    # ------------------------------------------------------

    if tipo == "number":
        step = str(
            configuracion_campo.get(
                "step",
                "",
            )
        )

        try:
            if step == "1":
                numero = int(valor)
            else:
                numero = Decimal(
                    str(valor)
                )

        except (
            ValueError,
            TypeError,
            InvalidOperation,
        ) as error:
            raise ValueError(
                f"El campo '{nombre_campo}' debe "
                "contener un número válido"
            ) from error

        minimo = configuracion_campo.get(
            "min"
        )

        if minimo is not None:
            minimo_decimal = Decimal(
                str(minimo)
            )

            if numero < minimo_decimal:
                raise ValueError(
                    f"El campo '{nombre_campo}' "
                    f"no puede ser menor que {minimo}"
                )

        return numero

    # ------------------------------------------------------
    # SELECT RELACIONADO CON OTRA TABLA
    # ------------------------------------------------------

    if (
        tipo == "select"
        and configuracion_campo.get(
            "referencia"
        )
    ):
        try:
            return int(valor)

        except (
            ValueError,
            TypeError,
        ) as error:
            raise ValueError(
                f"El campo '{nombre_campo}' debe "
                "contener un ID válido"
            ) from error

    # ------------------------------------------------------
    # SELECT CON OPCIONES FIJAS
    # ------------------------------------------------------

    if (
        tipo == "select"
        and configuracion_campo.get(
            "opciones"
        )
    ):
        valor_texto = str(
            valor
        ).strip()

        opciones_validas = {
            str(opcion["valor"])
            for opcion
            in configuracion_campo["opciones"]
        }

        if valor_texto not in opciones_validas:
            raise ValueError(
                f"El valor del campo "
                f"'{nombre_campo}' no es válido"
            )

        return valor_texto

    # ------------------------------------------------------
    # FECHA
    # ------------------------------------------------------

    if tipo == "date":
        valor_texto = str(
            valor
        ).strip()

        try:
            date.fromisoformat(
                valor_texto
            )

        except ValueError as error:
            raise ValueError(
                f"El campo '{nombre_campo}' debe "
                "contener una fecha válida"
            ) from error

        return valor_texto

    # ------------------------------------------------------
    # TEXTO, CORREO, CONTRASEÑA Y TEXTAREA
    # ------------------------------------------------------

    valor_texto = str(
        valor
    ).strip()

    longitud_maxima = (
        configuracion_campo.get(
            "maxlength"
        )
    )

    if (
        longitud_maxima
        and len(valor_texto)
        > int(longitud_maxima)
    ):
        raise ValueError(
            f"El campo '{nombre_campo}' "
            f"permite como máximo "
            f"{longitud_maxima} caracteres"
        )

    return valor_texto


def preparar_datos(
    tabla,
    datos,
    edicion=False,
):
    """
    Valida los datos enviados desde los formularios.

    Cuando se crea o modifica una contraseña, se genera
    automáticamente su hash.
    """
    configuracion = obtener_configuracion(
        tabla
    )

    if not configuracion:
        raise ValueError(
            "La tabla solicitada no está autorizada"
        )

    if not isinstance(datos, dict):
        raise ValueError(
            "Los datos enviados no tienen "
            "un formato válido"
        )

    resultado = {}

    for (
        nombre_campo,
        configuracion_campo,
    ) in configuracion["campos"].items():

        campo_presente = (
            nombre_campo in datos
        )

        valor = datos.get(
            nombre_campo
        )

        # Dejar la contraseña vacía durante una edición
        # conserva la contraseña anterior.
        if (
            tabla == "usuario"
            and nombre_campo == "contrasena"
            and edicion
            and valor_vacio(valor)
        ):
            continue

        if (
            edicion
            and configuracion_campo.get(
                "preservar_vacio_edicion"
            )
            and valor_vacio(valor)
        ):
            continue

        if (
            edicion
            and not campo_presente
        ):
            continue

        requerido = configuracion_campo.get(
            "requerido",
            False,
        )

        if (
            requerido
            and valor_vacio(valor)
        ):
            raise ValueError(
                f"El campo '{nombre_campo}' "
                "es obligatorio"
            )

        if (
            not campo_presente
            and not requerido
        ):
            resultado[nombre_campo] = None
            continue

        valor_convertido = convertir_valor(
            nombre_campo,
            valor,
            configuracion_campo,
        )

        # Normalizar el correo.
        if (
            tabla == "usuario"
            and nombre_campo == "correo"
            and valor_convertido
        ):
            valor_convertido = str(
                valor_convertido
            ).lower()

        # Cifrar la contraseña.
        if (
            tabla == "usuario"
            and nombre_campo == "contrasena"
            and valor_convertido
        ):
            valor_convertido = (
                generate_password_hash(
                    str(valor_convertido)
                )
            )

        resultado[nombre_campo] = (
            valor_convertido
        )

    return resultado


def obtener_error_mariadb(
    error,
    accion,
):
    """
    Convierte errores de MariaDB en mensajes comprensibles.
    """
    numero_error = getattr(
        error,
        "errno",
        None,
    )

    if numero_error == 1062:
        return (
            "No se pudo completar la operación porque "
            "existe un registro duplicado.",
            409,
        )

    if numero_error == 1451:
        return (
            "No se puede eliminar el registro porque "
            "está relacionado con otra tabla.",
            409,
        )

    if numero_error == 1452:
        return (
            "Uno de los identificadores relacionados "
            "no existe en la base de datos.",
            409,
        )

    if numero_error == 1406:
        return (
            "Uno de los valores supera la "
            "longitud permitida.",
            400,
        )

    if numero_error == 1366:
        return (
            "Uno de los valores enviados tiene "
            "un tipo incorrecto.",
            400,
        )

    if numero_error == 1146:
        return (
            "Falta una tabla requerida en MariaDB. "
            "Revisa la estructura de la base de datos.",
            500,
        )

    return (
        f"Error de MariaDB al {accion}: {str(error)}",
        500,
    )


# ==========================================================
# CONFIGURACIÓN DEL CRUD
# ==========================================================

@app.route(
    "/configuracion-crud",
    methods=["GET"],
)
def configuracion_crud():
    return jsonify(
        TABLAS_CRUD
    ), 200


# ==========================================================
# REGISTRAR VENTA CON RESPALDO RABBITMQ
# ==========================================================

@app.route(
    "/registrar-venta",
    methods=["POST"],
)
def registrar_venta_transaccional():
    datos_recibidos = request.get_json(
        silent=True
    )

    if not isinstance(
        datos_recibidos,
        dict
    ):
        return jsonify({
            "estado": "ERROR",
            "error": (
                "No se recibieron datos "
                "JSON válidos"
            )
        }), 400

    datos = dict(
        datos_recibidos
    )

    # El empleado se obtiene exclusivamente
    # del token JWT.
    try:
        id_usuario = int(
            get_jwt_identity()
        )

    except (
        TypeError,
        ValueError
    ):
        return jsonify({
            "estado": "ERROR",
            "error": (
                "El empleado autenticado "
                "no tiene un ID válido"
            )
        }), 400

    # Sobrescribe cualquier id_usuario enviado
    # manualmente desde el navegador.
    datos["id_usuario"] = id_usuario

    datos["fecha"] = (
        datos.get("fecha")
        or date.today().isoformat()
    )

    operacion_id = str(
        datos.get("operacion_id")
        or uuid4()
    ).strip()

    if (
        not operacion_id
        or len(operacion_id) > 36
    ):
        return jsonify({
            "estado": "ERROR",
            "error": (
                "El identificador de "
                "operación no es válido"
            )
        }), 400

    datos["operacion_id"] = (
        operacion_id
    )

    mensaje_rabbit = {
        "operacion_id": operacion_id,
        "tipo": "REGISTRAR_VENTA",

        "datos": {
            "fecha":
                datos.get("fecha"),

            "id_cliente":
                datos.get("id_cliente"),

            "id_usuario":
                id_usuario,

            "productos":
                datos.get("productos")
        }
    }

    try:
        resultado = (
            registrar_venta_en_bd(
                datos,
                operacion_id
            )
        )

        duplicada = (
            resultado.get("estado")
            == "YA_PROCESADA"
        )

        return jsonify({
            "mensaje": (
                "La venta ya había sido procesada"
                if duplicada
                else
                "Venta registrada correctamente"
            ),
            **resultado
        }), 200 if duplicada else 201

    except ErrorVenta as error:
        return jsonify({
            "estado": "ERROR",
            "operacion_id":
                operacion_id,
            "error": str(error)
        }), 400

    except ErrorTemporalBaseDatos as error:
        print(
            "[RABBITMQ] MariaDB no disponible:",
            error
        )

        try:
            publicar_operacion(
                mensaje_rabbit
            )

            return jsonify({
                "estado": "PENDIENTE",
                "operacion_id":
                    operacion_id,
                "mensaje": (
                    "MariaDB no está disponible. "
                    "La venta fue respaldada en "
                    "RabbitMQ y será procesada "
                    "automáticamente."
                )
            }), 202

        except RabbitMQNoDisponible as error_rabbit:
            return jsonify({
                "estado": "NO_GUARDADA",
                "operacion_id":
                    operacion_id,
                "error": (
                    "MariaDB y RabbitMQ no "
                    "están disponibles."
                ),
                "detalle":
                    str(error_rabbit)
            }), 503

    except ErrorBaseDatos as error:
        print(
            "[VENTA] Error de base de datos:",
            error
        )

        return jsonify({
            "estado": "ERROR",
            "operacion_id":
                operacion_id,
            "error": (
                "Ocurrió un error de "
                "base de datos"
            ),
            "detalle": str(error)
        }), 500

    except Exception as error:
        print(
            "[VENTA] Error inesperado:",
            error
        )

        return jsonify({
            "estado": "ERROR",
            "operacion_id":
                operacion_id,
            "error": (
                "Ocurrió un error inesperado "
                "al registrar la venta"
            ),
            "detalle": str(error)
        }), 500


# ==========================================================
# CRUD GENÉRICO: CONSULTAR
# ==========================================================

@app.route(
    "/<tabla>",
    methods=["GET"],
)
def consultar_registros(tabla):
    configuracion = obtener_configuracion(
        tabla
    )

    if not configuracion:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' "
                "no está autorizada"
            )
        }), 404

    conexion = None
    cursor = None

    try:
        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": (
                    "No fue posible conectar "
                    "con MariaDB"
                )
            }), 503

        pk = configuracion["pk"]

        campos_ocultos = set(
            configuracion.get(
                "ocultar_lista",
                [],
            )
        )

        # La contraseña nunca debe devolverse
        # al frontend.
        if tabla == "usuario":
            campos_ocultos.add(
                "contrasena"
            )

        columnas = [pk]

        for campo in configuracion["campos"]:
            if (
                campo != pk
                and campo not in campos_ocultos
            ):
                columnas.append(
                    campo
                )

        columnas_sql = ", ".join(
            f"`{columna}`"
            for columna in columnas
        )

        consulta = f"""
            SELECT {columnas_sql}
            FROM `{tabla}`
            ORDER BY `{pk}`
        """

        cursor = conexion.cursor(
            dictionary=True
        )

        cursor.execute(
            consulta
        )

        registros = cursor.fetchall()

        return jsonify(
            serializar_registros(
                registros
            )
        ), 200

    except Error as error:
        mensaje, codigo = obtener_error_mariadb(
            error,
            "consultar los registros",
        )

        print(
            f"[CRUD GET] /{tabla}:",
            error,
        )

        return jsonify({
            "error": mensaje
        }), codigo

    except Exception as error:
        print(
            f"[CRUD GET] Error inesperado "
            f"/{tabla}:",
            error,
        )

        return jsonify({
            "error": (
                "No fue posible consultar "
                "los registros"
            ),
            "detalle": str(error),
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()


# ==========================================================
# CRUD GENÉRICO: AGREGAR
# ==========================================================

@app.route(
    "/<tabla>",
    methods=["POST"],
)
def agregar_registro(tabla):
    configuracion = obtener_configuracion(
        tabla
    )

    if tabla in TABLAS_TRANSACCIONALES:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' no admite "
                "registros manuales. Utiliza el "
                "módulo especial Registrar Venta."
            )
        }), 405

    if not configuracion:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' "
                "no está autorizada"
            )
        }), 404

    permiso = validar_permiso_modificacion(
        tabla
    )

    if permiso is not None:
        return permiso

    conexion = None
    cursor = None

    try:
        datos_recibidos = request.get_json(
            silent=True
        )

        if datos_recibidos is None:
            return jsonify({
                "error": (
                    "No se recibieron datos "
                    "en formato JSON"
                )
            }), 400

        datos = preparar_datos(
            tabla,
            datos_recibidos,
            edicion=False,
        )

        if not datos:
            return jsonify({
                "error": (
                    "No hay campos para registrar"
                )
            }), 400

        columnas = list(
            datos.keys()
        )

        valores = [
            datos[columna]
            for columna in columnas
        ]

        columnas_sql = ", ".join(
            f"`{columna}`"
            for columna in columnas
        )

        marcadores = ", ".join(
            ["%s"] * len(columnas)
        )

        consulta = f"""
            INSERT INTO `{tabla}`
            ({columnas_sql})
            VALUES ({marcadores})
        """

        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": (
                    "No fue posible conectar "
                    "con MariaDB"
                )
            }), 503

        cursor = conexion.cursor()

        cursor.execute(
            consulta,
            valores,
        )

        conexion.commit()

        return jsonify({
            "mensaje": (
                f"{configuracion['singular']} "
                "registrado correctamente"
            ),
            configuracion["pk"]: (
                cursor.lastrowid
            ),
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Error as error:
        if conexion is not None:
            conexion.rollback()

        mensaje, codigo = obtener_error_mariadb(
            error,
            "registrar el registro",
        )

        print(
            f"[CRUD POST] /{tabla}:",
            error,
        )

        return jsonify({
            "error": mensaje
        }), codigo

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        print(
            f"[CRUD POST] Error inesperado "
            f"/{tabla}:",
            error,
        )

        return jsonify({
            "error": (
                "No fue posible registrar "
                "el registro"
            ),
            "detalle": str(error),
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()


# ==========================================================
# CRUD GENÉRICO: EDITAR
# ==========================================================

@app.route(
    "/<tabla>/<int:id_registro>",
    methods=["PUT"],
)
def editar_registro(
    tabla,
    id_registro,
):
    configuracion = obtener_configuracion(
        tabla
    )

    if tabla in TABLAS_TRANSACCIONALES:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' no admite "
                "modificaciones manuales. Utiliza "
                "el módulo especial de ventas."
            )
        }), 405

    if not configuracion:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' "
                "no está autorizada"
            )
        }), 404

    permiso = validar_permiso_modificacion(
        tabla
    )

    if permiso is not None:
        return permiso

    conexion = None
    cursor = None

    try:
        datos_recibidos = request.get_json(
            silent=True
        )

        if datos_recibidos is None:
            return jsonify({
                "error": (
                    "No se recibieron datos "
                    "en formato JSON"
                )
            }), 400

        datos = preparar_datos(
            tabla,
            datos_recibidos,
            edicion=True,
        )

        if not datos:
            return jsonify({
                "error": (
                    "No hay campos para actualizar"
                )
            }), 400

        pk = configuracion["pk"]

        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": (
                    "No fue posible conectar "
                    "con MariaDB"
                )
            }), 503

        cursor = conexion.cursor()

        cursor.execute(
            f"""
            SELECT `{pk}`
            FROM `{tabla}`
            WHERE `{pk}` = %s
            """,
            (id_registro,),
        )

        registro = cursor.fetchone()

        if not registro:
            return jsonify({
                "error": (
                    f"{configuracion['singular']} "
                    "no encontrado"
                )
            }), 404

        asignaciones = ", ".join(
            f"`{campo}` = %s"
            for campo in datos
        )

        valores = list(
            datos.values()
        )

        valores.append(
            id_registro
        )

        consulta = f"""
            UPDATE `{tabla}`
            SET {asignaciones}
            WHERE `{pk}` = %s
        """

        cursor.execute(
            consulta,
            valores,
        )

        conexion.commit()

        return jsonify({
            "mensaje": (
                f"{configuracion['singular']} "
                "actualizado correctamente"
            )
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Error as error:
        if conexion is not None:
            conexion.rollback()

        mensaje, codigo = obtener_error_mariadb(
            error,
            "actualizar el registro",
        )

        print(
            f"[CRUD PUT] /{tabla}/"
            f"{id_registro}:",
            error,
        )

        return jsonify({
            "error": mensaje
        }), codigo

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        print(
            f"[CRUD PUT] Error inesperado "
            f"/{tabla}/{id_registro}:",
            error,
        )

        return jsonify({
            "error": (
                "No fue posible actualizar "
                "el registro"
            ),
            "detalle": str(error),
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()


# ==========================================================
# CRUD GENÉRICO: ELIMINAR
# ==========================================================

@app.route(
    "/<tabla>/<int:id_registro>",
    methods=["DELETE"],
)
def eliminar_registro(
    tabla,
    id_registro,
):
    configuracion = obtener_configuracion(
        tabla
    )

    if tabla in TABLAS_TRANSACCIONALES:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' no admite "
                "eliminaciones manuales."
            )
        }), 405

    if not configuracion:
        return jsonify({
            "error": (
                f"La tabla '{tabla}' "
                "no está autorizada"
            )
        }), 404

    permiso = validar_permiso_modificacion(
        tabla
    )

    if permiso is not None:
        return permiso

    conexion = None
    cursor = None

    try:
        pk = configuracion["pk"]

        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": (
                    "No fue posible conectar "
                    "con MariaDB"
                )
            }), 503

        cursor = conexion.cursor()

        cursor.execute(
            f"""
            SELECT `{pk}`
            FROM `{tabla}`
            WHERE `{pk}` = %s
            """,
            (id_registro,),
        )

        registro = cursor.fetchone()

        if not registro:
            return jsonify({
                "error": (
                    f"{configuracion['singular']} "
                    "no encontrado"
                )
            }), 404

        cursor.execute(
            f"""
            DELETE FROM `{tabla}`
            WHERE `{pk}` = %s
            """,
            (id_registro,),
        )

        conexion.commit()

        return jsonify({
            "mensaje": (
                f"{configuracion['singular']} "
                "eliminado correctamente"
            )
        }), 200

    except Error as error:
        if conexion is not None:
            conexion.rollback()

        mensaje, codigo = obtener_error_mariadb(
            error,
            "eliminar el registro",
        )

        print(
            f"[CRUD DELETE] /{tabla}/"
            f"{id_registro}:",
            error,
        )

        return jsonify({
            "error": mensaje
        }), codigo

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        print(
            f"[CRUD DELETE] Error inesperado "
            f"/{tabla}/{id_registro}:",
            error,
        )

        return jsonify({
            "error": (
                "No fue posible eliminar "
                "el registro"
            ),
            "detalle": str(error),
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()


# ==========================================================
# MANEJO DE ERRORES HTTP
# ==========================================================

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return jsonify({
        "error": "Ruta no encontrada"
    }), 404


@app.errorhandler(405)
def metodo_no_permitido(error):
    return jsonify({
        "error": (
            "Método HTTP no permitido "
            "para esta ruta"
        )
    }), 405


# ==========================================================
# INICIAR SERVIDOR
# ==========================================================

if __name__ == "__main__":
    print("========================================")
    print(" SISTEMA DE FARMACIA")
    print(" CRUD genérico activo")
    print(" Autenticación JWT activa")
    print(" RabbitMQ integrado")
    print(" http://127.0.0.1:5000/login")
    print("========================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )