import json
import time

from pika.exceptions import AMQPError

from rabbitmq_service import (
    COLA_OPERACIONES,
    crear_conexion,
    declarar_colas,
    publicar_error,
    publicar_operacion
)

from ventas_service import (
    ErrorBaseDatos,
    ErrorTemporalBaseDatos,
    ErrorVenta,
    registrar_venta_en_bd
)


MAX_REINTENTOS = 20
SEGUNDOS_REINTENTO = 5


def enviar_a_errores(
    canal,
    metodo,
    mensaje,
    error
):
    try:
        publicar_error(
            mensaje,
            error
        )

        canal.basic_ack(
            delivery_tag=metodo.delivery_tag
        )

        print(
            "[ERROR] Operación movida a "
            "farmacia.errores"
        )

    except Exception as error_publicacion:
        print(
            "[ERROR] No fue posible mover el mensaje:",
            error_publicacion
        )

        canal.basic_nack(
            delivery_tag=metodo.delivery_tag,
            requeue=True
        )


def procesar_mensaje(
    canal,
    metodo,
    propiedades,
    cuerpo
):
    try:
        mensaje = json.loads(
            cuerpo.decode("utf-8")
        )

    except Exception as error:
        print(
            "[ERROR] Mensaje JSON inválido:",
            error
        )

        canal.basic_ack(
            delivery_tag=metodo.delivery_tag
        )

        return

    operacion_id = mensaje.get(
        "operacion_id"
    )

    tipo = mensaje.get(
        "tipo"
    )

    datos = mensaje.get(
        "datos"
    )

    encabezados = (
        propiedades.headers
        if propiedades and propiedades.headers
        else {}
    )

    reintentos = int(
        encabezados.get(
            "x-retry-count",
            0
        )
    )

    print()
    print("----------------------------------------")
    print("Mensaje recibido")
    print("Operación:", operacion_id)
    print("Tipo:", tipo)
    print("Reintento:", reintentos)
    print("----------------------------------------")

    if tipo != "REGISTRAR_VENTA":
        enviar_a_errores(
            canal,
            metodo,
            mensaje,
            "Tipo de operación no reconocido"
        )

        return

    try:
        resultado = registrar_venta_en_bd(
            datos,
            operacion_id
        )

        canal.basic_ack(
            delivery_tag=metodo.delivery_tag
        )

        print(
            "[OK] Venta procesada:",
            resultado["venta"]["id_venta"]
        )

    except ErrorTemporalBaseDatos as error:
        print(
            "[ESPERA] MariaDB no está disponible:",
            error
        )

        if reintentos >= MAX_REINTENTOS:
            enviar_a_errores(
                canal,
                metodo,
                mensaje,
                (
                    "Se superó el máximo de "
                    f"{MAX_REINTENTOS} reintentos. "
                    f"Último error: {error}"
                )
            )

            return

        time.sleep(
            SEGUNDOS_REINTENTO
        )

        try:
            publicar_operacion(
                mensaje,
                encabezados={
                    "x-retry-count": reintentos + 1
                }
            )

            canal.basic_ack(
                delivery_tag=metodo.delivery_tag
            )

            print(
                "[REINTENTO] Operación reenviada. "
                f"Intento {reintentos + 1}"
            )

        except Exception as error_rabbit:
            print(
                "[ERROR] No fue posible reenviar:",
                error_rabbit
            )

            canal.basic_nack(
                delivery_tag=metodo.delivery_tag,
                requeue=True
            )

    except ErrorVenta as error:
        print(
            "[ERROR] Venta inválida:",
            error
        )

        enviar_a_errores(
            canal,
            metodo,
            mensaje,
            error
        )

    except ErrorBaseDatos as error:
        print(
            "[ERROR] Error permanente de MariaDB:",
            error
        )

        enviar_a_errores(
            canal,
            metodo,
            mensaje,
            error
        )

    except Exception as error:
        print(
            "[ERROR] Error inesperado:",
            error
        )

        enviar_a_errores(
            canal,
            metodo,
            mensaje,
            error
        )


def iniciar_consumidor():
    while True:
        conexion = None

        try:
            print(
                "Conectando con RabbitMQ..."
            )

            conexion = crear_conexion()

            canal = conexion.channel()

            declarar_colas(canal)

            canal.basic_qos(
                prefetch_count=1
            )

            canal.basic_consume(
                queue=COLA_OPERACIONES,
                on_message_callback=procesar_mensaje,
                auto_ack=False
            )

            print("========================================")
            print(" CONSUMIDOR RABBITMQ ACTIVO")
            print(f" Cola: {COLA_OPERACIONES}")
            print(" Esperando operaciones...")
            print("========================================")

            canal.start_consuming()

        except KeyboardInterrupt:
            print(
                "Consumidor detenido por el usuario."
            )

            break

        except AMQPError as error:
            print(
                "RabbitMQ no está disponible:",
                error
            )

            print(
                "Reintentando en 5 segundos..."
            )

            time.sleep(5)

        except Exception as error:
            print(
                "Error del consumidor:",
                error
            )

            print(
                "Reintentando en 5 segundos..."
            )

            time.sleep(5)

        finally:
            if (
                conexion is not None
                and conexion.is_open
            ):
                conexion.close()


if __name__ == "__main__":
    iniciar_consumidor()