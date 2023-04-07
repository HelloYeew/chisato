import pika
from decouple import config

RABBITMQ_HOST = config('RABBITMQ_HOST')
RABBITMQ_PORT = config('RABBITMQ_PORT', default=5672, cast=int)
RABBITMQ_USER = config('RABBITMQ_USER', default='guest')
RABBITMQ_PASSWORD = config('RABBITMQ_PASSWORD', default='guest')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials)
connection = pika.BlockingConnection(parameters)


def get_rabbitmq_channel(queue_name: str = ''):
    """Return RabbitMQ channel"""
    channel = connection.channel()
    # channel.exchange_declare(exchange='osu-collec
    return channel