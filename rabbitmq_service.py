import json
import os
from datetime import datetime, timezone

import pika
from pika.exceptions import AMQPError


RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "127.0.0.1"
)

RABBITMQ_PORT = int(
    os.getenv(
        "RABBITMQ_PORT",
        "5672"
    )
)

RABBITMQ_USER = os.getenv(
    "RABBITMQ_USER",
    "farmacia"
)

RABBITMQ_PASSWORD = os.getenv(
    "RABBITMQ_PASSWORD",
    "farmacia123"
)

RABBITMQ_VHOST = os.getenv(
    "RABBITMQ_VHOST",
    "/"
)

COLA_OPERACIONES = os.getenv(
    "RABBITMQ_QUEUE",
    "farmacia.operaciones"
)

COLA_ERRORES = os.getenv(
    "RABBITMQ_ERROR_QUEUE",
    "farmacia.errores"
)


class RabbitMQNoDisponible(RuntimeError):
    pass


def crear_conexion():
    """
    Crea una conexión con RabbitMQ.
    """
    credenciales = pika.PlainCredentials(
        RABBITMQ_USER,
        RABBITMQ_PASSWORD
    )

    parametros = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credenciales,
        heartbeat=60,
        blocked_connection_timeout=30,
        connection_attempts=3,
        retry_delay=2
    )

    try:
        return pika.BlockingConnection(
            parametros
        )

    except AMQPError as error:
        raise RabbitMQNoDisponible(
            f"No fue posible conectar con RabbitMQ: {error}"
        ) from error


def declarar_colas(canal):
    """
    Declara las colas durables utilizadas por el sistema.
    """
    canal.queue_declare(
        queue=COLA_OPERACIONES,
        durable=True
    )

    canal.queue_declare(
        queue=COLA_ERRORES,
        durable=True
    )


def publicar_operacion(
    mensaje,
    cola=COLA_OPERACIONES,
    encabezados=None
):
    """
    Publica un mensaje persistente en RabbitMQ.
    """
    conexion = None

    try:
        conexion = crear_conexion()

        canal = conexion.channel()

        declarar_colas(canal)

        canal.confirm_delivery()

        cuerpo = json.dumps(
            mensaje,
            ensure_ascii=False,
            default=str
        ).encode("utf-8")

        propiedades = pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
            content_encoding="utf-8",
            message_id=str(
                mensaje.get(
                    "operacion_id",
                    ""
                )
            ),
            timestamp=int(
                datetime.now(
                    timezone.utc
                ).timestamp()
            ),
            headers=encabezados or {}
        )

        confirmado = canal.basic_publish(
            exchange="",
            routing_key=cola,
            body=cuerpo,
            properties=propiedades,
            mandatory=True
        )

        if confirmado is False:
            raise RabbitMQNoDisponible(
                "RabbitMQ no confirmó el mensaje"
            )

        return True

    except RabbitMQNoDisponible:
        raise

    except AMQPError as error:
        raise RabbitMQNoDisponible(
            f"No fue posible publicar el mensaje: {error}"
        ) from error

    finally:
        if (
            conexion is not None
            and conexion.is_open
        ):
            conexion.close()


def publicar_error(
    mensaje,
    detalle_error
):
    """
    Mueve una operación inválida a la cola de errores.
    """
    mensaje_error = {
        **mensaje,
        "error": str(detalle_error),
        "fecha_error": datetime.now(
            timezone.utc
        ).isoformat()
    }

    return publicar_operacion(
        mensaje_error,
        cola=COLA_ERRORES
    )