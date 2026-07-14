from datetime import date
from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP
)

from mysql.connector import Error

from db import get_connection


ERRORES_TEMPORALES_MARIADB = {
    1040,
    1042,
    1043,
    1129,
    1130,
    1205,
    1213,
    2002,
    2003,
    2006,
    2013,
    2055
}


ROLES_TRABAJADORES = {
    "admin",
    "administrador",
    "empleado",
    "trabajador"
}


class ErrorVenta(ValueError):
    pass


class ErrorTemporalBaseDatos(
    RuntimeError
):
    pass


class ErrorBaseDatos(
    RuntimeError
):
    pass


def es_error_temporal(error):
    return getattr(
        error,
        "errno",
        None
    ) in ERRORES_TEMPORALES_MARIADB


def validar_productos(productos):
    if (
        not isinstance(productos, list)
        or not productos
    ):
        raise ErrorVenta(
            "La venta debe contener "
            "por lo menos un producto"
        )

    agrupados = {}

    for posicion, elemento in enumerate(
        productos,
        start=1
    ):
        if not isinstance(elemento, dict):
            raise ErrorVenta(
                f"El producto de la posición "
                f"{posicion} no es válido"
            )

        try:
            id_producto = int(
                elemento.get("id_producto")
            )

            cantidad_decimal = Decimal(
                str(
                    elemento.get("cantidad")
                )
            )

            if (
                cantidad_decimal
                != cantidad_decimal
                .to_integral_value()
            ):
                raise ValueError

            cantidad = int(
                cantidad_decimal
            )

        except (
            TypeError,
            ValueError,
            InvalidOperation
        ) as error:
            raise ErrorVenta(
                f"El producto de la posición "
                f"{posicion} tiene un ID "
                "o cantidad inválidos"
            ) from error

        if id_producto <= 0:
            raise ErrorVenta(
                "El identificador del producto "
                "no es válido"
            )

        if cantidad <= 0:
            raise ErrorVenta(
                "La cantidad debe ser mayor "
                "que cero"
            )

        agrupados[id_producto] = (
            agrupados.get(
                id_producto,
                0
            )
            + cantidad
        )

    return agrupados


def validar_datos_venta(datos):
    if not isinstance(datos, dict):
        raise ErrorVenta(
            "Los datos de la venta "
            "no son válidos"
        )

    fecha_venta = (
        datos.get("fecha")
        or date.today().isoformat()
    )

    try:
        fecha_venta = (
            date.fromisoformat(
                str(fecha_venta)
            ).isoformat()
        )

    except ValueError as error:
        raise ErrorVenta(
            "La fecha de venta no es válida"
        ) from error

    try:
        id_cliente = int(
            datos.get("id_cliente")
        )

        id_usuario = int(
            datos.get("id_usuario")
        )

    except (
        TypeError,
        ValueError
    ) as error:
        raise ErrorVenta(
            "El cliente o el empleado "
            "no tienen un identificador válido"
        ) from error

    if id_cliente <= 0:
        raise ErrorVenta(
            "El cliente no es válido"
        )

    if id_usuario <= 0:
        raise ErrorVenta(
            "El empleado autenticado "
            "no es válido"
        )

    productos = validar_productos(
        datos.get("productos")
    )

    return {
        "fecha": fecha_venta,
        "id_cliente": id_cliente,
        "id_usuario": id_usuario,
        "productos": productos
    }


def registrar_venta_en_bd(
    datos,
    operacion_id
):
    datos_validados = validar_datos_venta(
        datos
    )

    operacion_id = str(
        operacion_id or ""
    ).strip()

    if not operacion_id:
        raise ErrorVenta(
            "La operación no tiene identificador"
        )

    if len(operacion_id) > 36:
        raise ErrorVenta(
            "El identificador de operación "
            "es demasiado largo"
        )

    conexion = None
    cursor = None

    try:
        try:
            conexion = get_connection()

        except Error as error:
            if es_error_temporal(error):
                raise ErrorTemporalBaseDatos(
                    str(error)
                ) from error

            raise ErrorBaseDatos(
                str(error)
            ) from error

        except Exception as error:
            raise ErrorTemporalBaseDatos(
                str(error)
            ) from error

        if conexion is None:
            raise ErrorTemporalBaseDatos(
                "MariaDB no está disponible"
            )

        conexion.start_transaction()

        cursor = conexion.cursor(
            dictionary=True
        )

        # Evita procesar dos veces una venta
        # reenviada por RabbitMQ.
        cursor.execute(
            """
            SELECT
                operacion_id,
                id_venta,
                id_factura
            FROM operaciones_procesadas
            WHERE operacion_id = %s
            LIMIT 1
            """,
            (operacion_id,)
        )

        operacion_anterior = (
            cursor.fetchone()
        )

        if operacion_anterior:
            conexion.commit()

            return {
                "estado": "YA_PROCESADA",
                "operacion_id": operacion_id,
                "duplicada": True,

                "venta": {
                    "id_venta":
                        operacion_anterior[
                            "id_venta"
                        ]
                },

                "factura": {
                    "id_factura":
                        operacion_anterior[
                            "id_factura"
                        ]
                },

                "detalles": []
            }

        fecha_venta = (
            datos_validados["fecha"]
        )

        id_cliente = (
            datos_validados["id_cliente"]
        )

        id_usuario = (
            datos_validados["id_usuario"]
        )

        productos = (
            datos_validados["productos"]
        )

        # Validar cliente.
        cursor.execute(
            """
            SELECT
                id_cliente,
                nombre
            FROM cliente
            WHERE id_cliente = %s
            LIMIT 1
            """,
            (id_cliente,)
        )

        cliente = cursor.fetchone()

        if not cliente:
            raise ErrorVenta(
                f"No existe el cliente "
                f"con ID {id_cliente}"
            )

        # Validar empleado autenticado.
        cursor.execute(
            """
            SELECT
                id_usuario,
                nombre,
                apellido,
                rol
            FROM usuario
            WHERE id_usuario = %s
            LIMIT 1
            """,
            (id_usuario,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            raise ErrorVenta(
                "El empleado autenticado "
                "no existe"
            )

        rol_usuario = str(
            usuario.get("rol") or ""
        ).strip().lower()

        if (
            rol_usuario
            not in ROLES_TRABAJADORES
        ):
            raise ErrorVenta(
                "El usuario autenticado "
                "no es un trabajador autorizado"
            )

        # Crear venta temporalmente en cero.
        cursor.execute(
            """
            INSERT INTO venta
            (
                fecha,
                total,
                id_cliente,
                id_usuario
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                fecha_venta,
                Decimal("0.00"),
                id_cliente,
                id_usuario
            )
        )

        id_venta = cursor.lastrowid

        total_venta = Decimal(
            "0.00"
        )

        detalles = []

        for (
            id_producto,
            cantidad
        ) in productos.items():

            cursor.execute(
                """
                SELECT
                    id_producto,
                    nombre,
                    precio,
                    stock
                FROM producto
                WHERE id_producto = %s
                FOR UPDATE
                """,
                (id_producto,)
            )

            producto = cursor.fetchone()

            if not producto:
                raise ErrorVenta(
                    f"No existe el producto "
                    f"con ID {id_producto}"
                )

            if producto["precio"] is None:
                raise ErrorVenta(
                    f"El producto "
                    f"'{producto['nombre']}' "
                    "no tiene precio"
                )

            stock_actual = int(
                producto["stock"] or 0
            )

            if stock_actual < cantidad:
                raise ErrorVenta(
                    f"Stock insuficiente para "
                    f"'{producto['nombre']}'. "
                    f"Disponible: {stock_actual}; "
                    f"solicitado: {cantidad}"
                )

            precio_unitario = Decimal(
                str(producto["precio"])
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            subtotal = (
                precio_unitario
                * Decimal(cantidad)
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )

            cursor.execute(
                """
                INSERT INTO detalle_venta
                (
                    cantidad,
                    precio_unitario,
                    subtotal,
                    id_venta,
                    id_producto
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    cantidad,
                    precio_unitario,
                    subtotal,
                    id_venta,
                    id_producto
                )
            )

            id_detalle = (
                cursor.lastrowid
            )

            cursor.execute(
                """
                UPDATE producto
                SET stock = stock - %s
                WHERE id_producto = %s
                """,
                (
                    cantidad,
                    id_producto
                )
            )

            total_venta += subtotal

            detalles.append({
                "id_detalle": id_detalle,
                "id_producto": id_producto,
                "producto":
                    producto["nombre"],
                "cantidad": cantidad,
                "precio_unitario": float(
                    precio_unitario
                ),
                "subtotal": float(
                    subtotal
                )
            })

        total_venta = total_venta.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        cursor.execute(
            """
            UPDATE venta
            SET total = %s
            WHERE id_venta = %s
            """,
            (
                total_venta,
                id_venta
            )
        )

        cursor.execute(
            """
            INSERT INTO factura
            (
                fecha_emision,
                total,
                id_venta
            )
            VALUES (%s, %s, %s)
            """,
            (
                fecha_venta,
                total_venta,
                id_venta
            )
        )

        id_factura = (
            cursor.lastrowid
        )

        cursor.execute(
            """
            INSERT INTO operaciones_procesadas
            (
                operacion_id,
                tipo,
                id_venta,
                id_factura
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                operacion_id,
                "REGISTRAR_VENTA",
                id_venta,
                id_factura
            )
        )

        conexion.commit()

        nombre_usuario = " ".join(
            parte
            for parte in [
                usuario.get("nombre"),
                usuario.get("apellido")
            ]
            if parte
        ).strip()

        return {
            "estado": "GUARDADA",
            "operacion_id": operacion_id,
            "duplicada": False,

            "venta": {
                "id_venta": id_venta,
                "fecha": fecha_venta,
                "total": float(
                    total_venta
                ),
                "id_cliente": id_cliente,
                "cliente":
                    cliente["nombre"],
                "id_usuario": id_usuario,
                "usuario":
                    nombre_usuario
            },

            "factura": {
                "id_factura": id_factura,
                "fecha_emision":
                    fecha_venta,
                "total": float(
                    total_venta
                )
            },

            "detalles": detalles
        }

    except ErrorVenta:
        if conexion is not None:
            conexion.rollback()

        raise

    except Error as error:
        if conexion is not None:
            conexion.rollback()

        if es_error_temporal(error):
            raise ErrorTemporalBaseDatos(
                str(error)
            ) from error

        raise ErrorBaseDatos(
            str(error)
        ) from error

    except ErrorTemporalBaseDatos:
        if conexion is not None:
            conexion.rollback()

        raise

    except ErrorBaseDatos:
        if conexion is not None:
            conexion.rollback()

        raise

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        raise ErrorBaseDatos(
            str(error)
        ) from error

    finally:
        if cursor is not None:
            cursor.close()

        if (
            conexion is not None
            and conexion.is_connected()
        ):
            conexion.close()