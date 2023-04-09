import pika
from decouple import config
from pika.exceptions import StreamLostError

RABBITMQ_HOST = config('RABBITMQ_HOST')
RABBITMQ_PORT = config('RABBITMQ_PORT', default=5672, cast=int)
RABBITMQ_USER = config('RABBITMQ_USER', default='guest')
RABBITMQ_PASSWORD = config('RABBITMQ_PASSWORD', default='guest')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials)

DATABASE_PROCESS_EXCHANGE_NAME = 'database-process'


def get_rabbitmq_publish_database_process_channel(queue_name: str = 'default') -> pika.adapters.blocking_connection.BlockingChannel:
    """Return RabbitMQ channel with queue and exchange"""
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
    except StreamLostError:
        # Try to reconnect
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
    channel.exchange_declare(exchange='database-process', durable=True, exchange_type='direct')
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=DATABASE_PROCESS_EXCHANGE_NAME, queue=queue_name, routing_key=queue_name)
    channel.basic_qos(prefetch_count=1, global_qos=False)
    return channel
