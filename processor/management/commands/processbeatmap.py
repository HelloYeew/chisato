import json
import time
import threading

import pika
from decouple import config
from django.core.management import BaseCommand
from pika.exceptions import StreamLostError
from sentry_sdk import capture_exception

from collection.models import BeatmapSet, Beatmap, Collection, CollectionBeatmap
from utility.osu_api.importer import import_beatmapset

RABBITMQ_HOST = config('RABBITMQ_HOST')
RABBITMQ_PORT = config('RABBITMQ_PORT', default=5672, cast=int)
RABBITMQ_USER = config('RABBITMQ_USER', default='guest')
RABBITMQ_PASSWORD = config('RABBITMQ_PASSWORD', default='guest')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
parameters = pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', credentials)


class Command(BaseCommand):
    help = 'Process the collection from RabbitMQ messages and listen for new messages'

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(parameters)
        connection.process_data_events(time_limit=2)
        channel = connection.channel()
        channel.exchange_declare(exchange='api-process', durable=True, exchange_type='direct')
        channel.queue_declare(queue='api-process-default', durable=True)
        channel.basic_consume(queue='api-process-default', on_message_callback=self.callback, auto_ack=True)
        try:
            self.stdout.write(self.style.SUCCESS(f'🐰 Waiting for messages'))
            channel.start_consuming()
        except StreamLostError:
            # check heartbeat
            connection.process_data_events(time_limit=2)
            # Try to reconnect (Deprecated : Use above code)
            # connection = pika.BlockingConnection(parameters)
            # channel = connection.channel()
            # channel.exchange_declare(exchange='api-process', durable=True, exchange_type='direct')
            # channel.queue_declare(queue='api-process-default', durable=True)
            # channel.basic_consume(queue='api-process-default', on_message_callback=self.callback, auto_ack=True)
            # channel.start_consuming()
            # channel.close()
            self.stdout.write(self.style.SUCCESS(f'🐰 Reconnected to RabbitMQ'))
            time.sleep(10)
        except KeyboardInterrupt:
            # Gracefully close the connection
            channel.stop_consuming()
            connection.close()
            self.stdout.write(self.style.SUCCESS(f'🐰 Closed connection to RabbitMQ'))

    def callback(self, ch, method, properties, body):
        """Callback from RabbitMQ consumer to create a new thread to process the message"""
        thread = threading.Thread(target=self.process, args=(body,))
        thread.start()
        print(f'🐰 Started thread {thread.name} to process message {body}')
        # Don't run the process parallel to not exceed the rate limit
        thread.join()
        # Print the message when the thread is done
        print(f'🐰 Thread {thread.name} finished processing message {body}')

    def process(self, body):
        """Process the message from RabbitMQ"""
        use_external_api = False
        try:
            self.stdout.write(self.style.SUCCESS(f'✉️ Received message {body}'))
            # Message example : {"UserId":1,"CollectionName":"All beatmaps","BeatmapSetId":1447300,
            # "BeatmapId":3180722,"BeatmapChecksum":"30cdfb2bbf1dd3d8f86a97ea9e606eda"}
            self.stdout.write(self.style.SUCCESS(f'🖥️ Processing message {body}'))
            # Convert message to dict
            message = json.loads(body)
            # Check that beatmapset and beatmap is available
            if BeatmapSet.objects.filter(beatmapset_id=message['BeatmapSetId']).exists():
                self.stdout.write(
                    self.style.SUCCESS(f'🗺️ Beatmapset {message["BeatmapSetId"]} already exists, skipping'))
            else:
                if int(message['BeatmapSetId']) == 0 or int(message['BeatmapSetId']) == -1:
                    self.stdout.write(
                        self.style.SUCCESS(f'🗺️ Beatmapset {message["BeatmapSetId"]} is -1 (local), skipping'))
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'🗺️ Beatmapset {message["BeatmapSetId"]} does not exist, importing'))
                    use_external_api = True
                    import_beatmapset(message['BeatmapSetId'])
                    self.stdout.write(self.style.SUCCESS(f'🗺️ Beatmapset {message["BeatmapSetId"]} has been imported'))
            if Beatmap.objects.filter(beatmap_id=message['BeatmapId']).exists():
                self.stdout.write(self.style.SUCCESS(f'🗺️ Beatmap {message["BeatmapId"]} already exists, skipping'))
            else:
                if int(message['BeatmapId']) == 0 or int(message['BeatmapId']) == -1:
                    self.stdout.write(self.style.SUCCESS(f'🗺️ Beatmap {message["BeatmapId"]} is 0 (local), skipping'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'🗺️ Beatmap {message["BeatmapId"]} does not exist, importing'))
                    use_external_api = True
                    import_beatmapset(message['BeatmapSetId'])
                    self.stdout.write(self.style.SUCCESS(f'🗺️ Beatmap {message["BeatmapId"]} has been imported'))
            # Check that collection exists
            if Collection.objects.filter(owner_id=message['UserId'], name=message['CollectionName']).exists():
                self.stdout.write(
                    self.style.SUCCESS(f'📕 Collection {message["CollectionName"]} already exists, skipping'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'📕 Collection {message["CollectionName"]} does not exist, creating'))
                Collection.objects.create(owner_id=message['UserId'], name=message['CollectionName'])
            # Add to collection
            self.stdout.write(self.style.SUCCESS(f'➕ Adding beatmap {message["BeatmapId"]} to collection'))
            if Collection.objects.filter(owner_id=message['UserId'], name=message['CollectionName']).exists():
                self.stdout.write(self.style.SUCCESS(
                    f'➕ Collection {message["CollectionName"]} already exists, checking that beatmap is not already in it'))
                if int(message['BeatmapId']) != 0 and int(message['BeatmapId']) != -1:
                    beatmap = Beatmap.objects.get(beatmap_id=message['BeatmapId'])
                    collection = Collection.objects.get(owner_id=message['UserId'], name=message['CollectionName'])
                    if CollectionBeatmap.objects.filter(collection=collection, beatmap=beatmap).exists():
                        self.stdout.write(self.style.SUCCESS(
                            f'➕ Beatmap {message["BeatmapId"]} already exists in collection {message["CollectionName"]}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f'➕ Beatmap {message["BeatmapId"]} does not exist in collection {message["CollectionName"]}, adding'))
                        CollectionBeatmap.objects.create(collection=collection, beatmap=beatmap)
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'➕ Beatmap {message["BeatmapId"]} is local (-1 or 0), skipping'))
            else:
                # This should never happen but just in case for safety
                self.stdout.write(
                    self.style.SUCCESS(f'➕ Collection {message["CollectionName"]} does not exist, skipping'))
            self.stdout.write(self.style.SUCCESS(f'✅️ Message {body} processed'))
            if use_external_api:
                self.stdout.write(self.style.SUCCESS(f'🛌 Sleeping for 1 seconds to avoid rate limiting'))
                time.sleep(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error processing message {body}'))
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            capture_exception(e)
