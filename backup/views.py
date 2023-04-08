import json

from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from backup.forms import BackupFileUploadForm
from backup.models import OsuDatabaseBackupFile, CollectionDatabaseBackupFile
from collection.models import Collection
from utility.rabbitmq.connection import get_rabbitmq_database_process_channel, DATABASE_PROCESS_EXCHANGE_NAME
from utility.s3.collection import get_collection_s3_client

S3_COLLECTION_BUCKET_NAME = config('S3_COLLECTION_BUCKET_NAME', default='')
S3_COLLECTION_URL = config('S3_COLLECTION_URL', default='')
USE_DIGITALOCEAN_SPACES = config('USE_DIGITALOCEAN_SPACES', default=False, cast=bool)


def random_text(length: int = 16) -> str:
    """Return random character"""
    import random
    import string
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def generate_rabbitmq_database_process_message(user_id: int, file_type: str, file_name: str,
                                               file_url: str, default_collection_id: int,
                                               default_collection_name: Collection.objects) -> str:
    """Generate RabbitMQ message for database process"""
    return json.dumps({
        'user_id': user_id,
        'file_type': file_type,
        'file_name': file_name,
        'file_url': file_url,
        'default_collection_id': default_collection_id,
        'default_collection_name': default_collection_name
    })

@login_required
def home(request):
    # find latest backup file
    osu = OsuDatabaseBackupFile.objects.filter(owner=request.user).order_by('-created_at').first()
    collection = CollectionDatabaseBackupFile.objects.filter(owner=request.user).order_by('-created_at').first()
    return render(request, 'backup/home.html', {
        'osu': osu,
        'collection': collection,
    })


@login_required
def upload(request):
    if request.method == 'POST':
        form = BackupFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            osu_file = form.cleaned_data['osu_file']
            collection_file = form.cleaned_data['collection_file']
            # Random file name
            random_osu_filename = f"osu_{random_text()}.db"
            random_collection_filename = f"collection_{random_text()}.db"
            # Chane osu_file and collection_file name
            osu_file.name = random_osu_filename
            collection_file.name = random_collection_filename
            osu = OsuDatabaseBackupFile.objects.create(
                name=osu_file.name,
                owner=request.user,
                file_name=random_osu_filename,
                file=osu_file,
            )
            collection = CollectionDatabaseBackupFile.objects.create(
                name=collection_file.name,
                owner=request.user,
                file_name=random_collection_filename,
                file=collection_file,
            )
            s3_client = get_collection_s3_client()
            s3_client.upload_fileobj(
                osu_file,
                S3_COLLECTION_BUCKET_NAME,
                "osu/" + str(request.user.id) + "/" + random_osu_filename,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': osu_file.content_type
                }
            )
            s3_client.upload_fileobj(
                collection_file,
                S3_COLLECTION_BUCKET_NAME,
                "collection/" + str(request.user.id) + "/" + random_collection_filename,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': collection_file.content_type
                }
            )
            if USE_DIGITALOCEAN_SPACES:
                # Don't know is this a bug or not but digital ocean will add bucket name as primary folder name
                base_url = S3_COLLECTION_URL + "/" + S3_COLLECTION_BUCKET_NAME
            else:
                base_url = S3_COLLECTION_URL
            osu.url = base_url + "/osu/" + str(request.user.id) + "/" + random_osu_filename
            collection.url = base_url + "/collection/" + str(request.user.id) + "/" + random_collection_filename
            osu.save()
            collection.save()
            messages.success(request, 'Upload file successfully! Your file will be started to process in a few minutes. A process time will depend on your database size.')
            channel = get_rabbitmq_database_process_channel('database-process-default')
            channel.basic_publish(
                exchange=DATABASE_PROCESS_EXCHANGE_NAME,
                routing_key='database-process-default',
                body=generate_rabbitmq_database_process_message(
                    user_id=request.user.id,
                    file_type='osu',
                    file_name=random_osu_filename,
                    file_url=osu.url,
                    default_collection_id=Collection.objects.filter(owner=request.user, default_collection=True).first().id,
                    default_collection_name=Collection.objects.filter(owner=request.user, default_collection=True).first().name
                )
            )
            channel.basic_publish(
                exchange=DATABASE_PROCESS_EXCHANGE_NAME,
                routing_key='database-process-default',
                body=generate_rabbitmq_database_process_message(
                    user_id=request.user.id,
                    file_type='collection',
                    file_name=random_collection_filename,
                    file_url=collection.url,
                    default_collection_id=Collection.objects.filter(owner=request.user, default_collection=True).first().id,
                    default_collection_name=Collection.objects.filter(owner=request.user, default_collection=True).first().name
                )
            )
            return redirect('backup_home')
    else:
        form = BackupFileUploadForm()
    return render(request, 'backup/upload.html', {
        'form': form
    })
