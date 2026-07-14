import pika, json, time
from db import get_db

def callback(ch, method, properties, body):
    msg = json.loads(body.decode())
    accion, tabla = msg.get("accion"), msg.get("tabla")
    print(f" [->] Tarea: {accion} en {tabla}")
    
    try:
        conn = get_db()
        cur = conn.cursor()
        if accion == "insert":
            data = msg["data"]
            keys, vals = ", ".join(data.keys()), ", ".join(["%s"] * len(data))
            cur.execute(f"INSERT INTO {tabla} ({keys}) VALUES ({vals})", list(data.values()))
        elif accion == "update":
            data, id_field, id_val = msg["data"], msg["id_field"], msg["id"]
            set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
            cur.execute(f"UPDATE {tabla} SET {set_clause} WHERE {id_field}=%s", list(data.values()) + [id_val])
        elif accion == "delete":
            cur.execute(f"DELETE FROM {tabla} WHERE {msg['id_field']}=%s", (msg["id"],))
        
        conn.commit()
        conn.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f" [✓] Éxito: {accion}")
    except Exception as e:
        print(f" [X] Error: {e}")
        time.sleep(2)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='cola_operaciones', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='cola_operaciones', on_message_callback=callback)
print(" [*] Worker listo. Esperando...")
channel.start_consuming()