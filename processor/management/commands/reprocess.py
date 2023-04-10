import logging

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from backup.models import OsuDatabaseBackupFile, CollectionDatabaseBackupFile
from backup.views import generate_rabbitmq_database_process_message
from collection.models import Collection
from utility.rabbitmq.connection import get_rabbitmq_publish_database_process_channel, DATABASE_PROCESS_EXCHANGE_NAME

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send all latest backups to database process queue'

    def handle(self, *args, **options):
        # Get all latest backup of the user
        all_latest_osu_backup = []
        all_latest_collection_backup = []
        for user in User.objects.all():
            all_latest_osu_backup.append(OsuDatabaseBackupFile.objects.filter(owner=user).order_by('-created_at').first())
            all_latest_collection_backup.append(CollectionDatabaseBackupFile.objects.filter(owner=user).order_by('-created_at').first())
        rabbitmq_channel = get_rabbitmq_publish_database_process_channel('database-process-default')
        print('all_latest_osu_backup', all_latest_osu_backup)
        print('all_latest_collection_backup', all_latest_collection_backup)
        for osu_backup in all_latest_osu_backup:
            if not osu_backup:
                continue
            default_collection = Collection.objects.filter(owner=osu_backup.owner, default_collection=True).first()
            rabbitmq_channel.basic_publish(
                exchange=DATABASE_PROCESS_EXCHANGE_NAME,
                routing_key='database-process-default',
                body=generate_rabbitmq_database_process_message(
                    user_id=osu_backup.owner.id,
                    file_type='osu',
                    file_name=osu_backup.file_name,
                    file_url=osu_backup.url,
                    default_collection_id=default_collection.id,
                    default_collection_name=default_collection.name
                )
            )
        for collection_backup in all_latest_collection_backup:
            if not collection_backup:
                continue
            default_collection = Collection.objects.filter(owner=collection_backup.owner, default_collection=True).first()
            rabbitmq_channel.basic_publish(
                exchange=DATABASE_PROCESS_EXCHANGE_NAME,
                routing_key='database-process-default',
                body=generate_rabbitmq_database_process_message(
                    user_id=collection_backup.owner.id,
                    file_type='collection',
                    file_name=collection_backup.file_name,
                    file_url=collection_backup.url,
                    default_collection_id=default_collection.id,
                    default_collection_name=default_collection.name
                )
            )
        rabbitmq_channel.close()
        logger.info(f'✅ Queued all latest backups for processing ({len(all_latest_osu_backup)} osu! backups and {len(all_latest_collection_backup)} collection backups)')
