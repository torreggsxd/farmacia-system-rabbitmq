from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from mysql.connector import Error
from db import get_connection

app = Flask(__name__)
CORS(app)


# ==================================================
# PÁGINA PRINCIPAL
# ==================================================

@app.route("/")
def index():
    return render_template("index.html")


# ==================================================
# PRODUCTO - CONSULTAR
# ==================================================

@app.route("/producto", methods=["GET"])
def obtener_productos():
    conexion = None
    cursor = None

    try:
        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": "No fue posible conectar con MariaDB"
            }), 500

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM producto
            ORDER BY id_producto
        """)

        productos = cursor.fetchall()

        return jsonify(productos), 200

    except Error as error:
        print("Error al consultar productos:", error)

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==================================================
# PRODUCTO - AGREGAR
# ==================================================

@app.route("/producto", methods=["POST"])
def agregar_producto():
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({
                "error": "No se recibieron datos del producto"
            }), 400

        nombre = datos.get("nombre")
        descripcion = datos.get("descripcion")
        precio = datos.get("precio")
        stock = datos.get("stock")
        fecha_caducidad = datos.get("fecha_caducidad")
        id_categoria = datos.get("id_categoria")
        id_proveedor = datos.get("id_proveedor")

        if not nombre or not str(nombre).strip():
            return jsonify({
                "error": "El nombre del producto es obligatorio"
            }), 400

        if precio in (None, ""):
            return jsonify({
                "error": "El precio es obligatorio"
            }), 400

        if stock in (None, ""):
            return jsonify({
                "error": "El stock es obligatorio"
            }), 400

        try:
            precio = float(precio)
            stock = int(stock)
        except (TypeError, ValueError):
            return jsonify({
                "error": "El precio y el stock deben ser valores numéricos"
            }), 400

        if precio < 0:
            return jsonify({
                "error": "El precio no puede ser negativo"
            }), 400

        if stock < 0:
            return jsonify({
                "error": "El stock no puede ser negativo"
            }), 400

        descripcion = descripcion or None
        fecha_caducidad = fecha_caducidad or None
        id_categoria = id_categoria or None
        id_proveedor = id_proveedor or None

        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": "No fue posible conectar con MariaDB"
            }), 500

        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO producto
            (
                nombre,
                descripcion,
                precio,
                stock,
                fecha_caducidad,
                id_categoria,
                id_proveedor
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre.strip(),
            descripcion,
            precio,
            stock,
            fecha_caducidad,
            id_categoria,
            id_proveedor
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Producto registrado correctamente",
            "id_producto": cursor.lastrowid
        }), 201

    except Error as error:
        if conexion:
            conexion.rollback()

        print("Error al agregar producto:", error)

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==================================================
# PRODUCTO - EDITAR
# ==================================================

@app.route("/producto/<int:id_producto>", methods=["PUT"])
def editar_producto(id_producto):
    conexion = None
    cursor = None

    try:
        datos = request.get_json(silent=True)

        if not datos:
            return jsonify({
                "error": "No se recibieron datos para actualizar"
            }), 400

        nombre = datos.get("nombre")
        descripcion = datos.get("descripcion")
        precio = datos.get("precio")
        stock = datos.get("stock")
        fecha_caducidad = datos.get("fecha_caducidad")
        id_categoria = datos.get("id_categoria")
        id_proveedor = datos.get("id_proveedor")

        if not nombre or not str(nombre).strip():
            return jsonify({
                "error": "El nombre del producto es obligatorio"
            }), 400

        if precio in (None, ""):
            return jsonify({
                "error": "El precio es obligatorio"
            }), 400

        if stock in (None, ""):
            return jsonify({
                "error": "El stock es obligatorio"
            }), 400

        try:
            precio = float(precio)
            stock = int(stock)
        except (TypeError, ValueError):
            return jsonify({
                "error": "El precio y el stock deben ser valores numéricos"
            }), 400

        if precio < 0:
            return jsonify({
                "error": "El precio no puede ser negativo"
            }), 400

        if stock < 0:
            return jsonify({
                "error": "El stock no puede ser negativo"
            }), 400

        descripcion = descripcion or None
        fecha_caducidad = fecha_caducidad or None
        id_categoria = id_categoria or None
        id_proveedor = id_proveedor or None

        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": "No fue posible conectar con MariaDB"
            }), 500

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id_producto
            FROM producto
            WHERE id_producto = %s
        """, (id_producto,))

        producto = cursor.fetchone()

        if not producto:
            return jsonify({
                "error": "El producto no existe"
            }), 404

        cursor.execute("""
            UPDATE producto
            SET
                nombre = %s,
                descripcion = %s,
                precio = %s,
                stock = %s,
                fecha_caducidad = %s,
                id_categoria = %s,
                id_proveedor = %s
            WHERE id_producto = %s
        """, (
            nombre.strip(),
            descripcion,
            precio,
            stock,
            fecha_caducidad,
            id_categoria,
            id_proveedor,
            id_producto
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Producto actualizado correctamente"
        }), 200

    except Error as error:
        if conexion:
            conexion.rollback()

        print("Error al editar producto:", error)

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==================================================
# PRODUCTO - ELIMINAR
# ==================================================

@app.route("/producto/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    conexion = None
    cursor = None

    try:
        conexion = get_connection()

        if conexion is None:
            return jsonify({
                "error": "No fue posible conectar con MariaDB"
            }), 500

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id_producto
            FROM producto
            WHERE id_producto = %s
        """, (id_producto,))

        producto = cursor.fetchone()

        if not producto:
            return jsonify({
                "error": "El producto no existe"
            }), 404

        cursor.execute("""
            DELETE FROM producto
            WHERE id_producto = %s
        """, (id_producto,))

        conexion.commit()

        return jsonify({
            "mensaje": "Producto eliminado correctamente"
        }), 200

    except Error as error:
        if conexion:
            conexion.rollback()

        print("Error al eliminar producto:", error)

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# ==================================================
# CLIENTE - CONSULTAR
# ==================================================

@app.route("/cliente", methods=["GET"])
def obtener_clientes():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cliente ORDER BY id_cliente")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# CATEGORÍA - CONSULTAR
# ==================================================

@app.route("/categoria", methods=["GET"])
def obtener_categorias():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categoria ORDER BY id_categoria")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# PROVEEDOR - CONSULTAR
# ==================================================

@app.route("/proveedor", methods=["GET"])
def obtener_proveedores():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedor ORDER BY id_proveedor")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# VENTA - CONSULTAR
# ==================================================

@app.route("/venta", methods=["GET"])
def obtener_ventas():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            v.id_venta,
            v.fecha,
            v.total,
            v.id_cliente,
            v.id_usuario,
            c.nombre AS cliente,
            u.nombre AS empleado
        FROM venta v
        LEFT JOIN cliente c
            ON v.id_cliente = c.id_cliente
        LEFT JOIN usuario u
            ON v.id_usuario = u.id_usuario
        ORDER BY v.id_venta
    """)

    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# FACTURA - CONSULTAR
# ==================================================

@app.route("/factura", methods=["GET"])
def obtener_facturas():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM factura ORDER BY id_factura")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# DETALLE DE VENTA - CONSULTAR
# ==================================================

@app.route("/detalle_venta", methods=["GET"])
def obtener_detalles_venta():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM detalle_venta ORDER BY id_detalle")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# USUARIO - CONSULTAR
# ==================================================

@app.route("/usuario", methods=["GET"])
def obtener_usuarios():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario ORDER BY id_usuario")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# FALLECIDO - CONSULTAR
# ==================================================

@app.route("/fallecido", methods=["GET"])
def obtener_fallecidos():
    conexion = get_connection()

    if conexion is None:
        return jsonify({
            "error": "No fue posible conectar con MariaDB"
        }), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fallecido ORDER BY id_fallecido")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(datos)


# ==================================================
# INICIAR SERVIDOR
# ==================================================

if __name__ == "__main__":
    print("Iniciando Sistema de Farmacia")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )