import logging
from datetime import datetime

import requests
from decouple import config
from django.utils.timezone import make_aware

from collection.models import BeatmapSet, Beatmap
from utility.osu_api.services import get_raw_beatmapset_info
from utility.s3.static import get_static_s3_client, generate_static_url

logger = logging.getLogger(__name__)

S3_STATIC_BUCKET_NAME = config('S3_STATIC_BUCKET_NAME', default='chisato-static')


def import_beatmapset(beatmapset_id: int) -> BeatmapSet.objects:
    """Import beatmapset from osu! api"""
    result = get_raw_beatmapset_info(beatmapset_id)
    if not result:
        return None
    first_result = result[0]
    try:
        beatmapset = BeatmapSet.objects.get(beatmapset_id=first_result['beatmapset_id'])
        # try to update beatmapset
        beatmapset.artist = first_result['artist']
        beatmapset.artist_unicode = first_result['artist_unicode']
        beatmapset.title = first_result['title']
        beatmapset.title_unicode = first_result['title_unicode']
        beatmapset.source = first_result['source']
        beatmapset.tags = first_result['tags']
        beatmapset.video = first_result['video'] == '1'
        beatmapset.storyboard = first_result['storyboard'] == '1'
        beatmapset.bpm = first_result['bpm']
        beatmapset.approved = first_result['approved']
        beatmapset.approved_date = make_aware(datetime.strptime(first_result['approved_date'], '%Y-%m-%d %H:%M:%S'))
        beatmapset.submit_date = make_aware(datetime.strptime(first_result['submit_date'], '%Y-%m-%d %H:%M:%S'))
        beatmapset.last_update = make_aware(datetime.strptime(first_result['last_update'], '%Y-%m-%d %H:%M:%S'))
        beatmapset.genre_id = int(first_result['genre_id'])
        beatmapset.language_id = first_result['language_id']
        beatmapset.favorite_count = first_result['favourite_count']
        beatmapset.play_count = first_result['playcount']
        beatmapset.save()
    except BeatmapSet.DoesNotExist:
        beatmapset = BeatmapSet.objects.create(
            beatmapset_id=first_result['beatmapset_id'],
            artist=first_result['artist'],
            artist_unicode=first_result['artist_unicode'],
            title=first_result['title'],
            title_unicode=first_result['title_unicode'],
            source=first_result['source'],
            tags=first_result['tags'],
            video=first_result['video'] == '1',
            storyboard=first_result['storyboard'] == '1',
            bpm=first_result['bpm'],
            approved=first_result['approved'],
            approved_date=make_aware(datetime.strptime(first_result['approved_date'], '%Y-%m-%d %H:%M:%S')) if first_result['approved_date'] else None,
            submit_date=make_aware(datetime.strptime(first_result['submit_date'], '%Y-%m-%d %H:%M:%S')) if first_result['submit_date'] else None,
            last_update=make_aware(datetime.strptime(first_result['last_update'], '%Y-%m-%d %H:%M:%S')) if first_result['last_update'] else None,
            genre_id=int(first_result['genre_id']),
            language_id=first_result['language_id'],
            favorite_count=first_result['favourite_count'],
            play_count=first_result['playcount']
        )
    for beatmap in result:
        try:
            beatmap_object = Beatmap.objects.get(beatmap_id=beatmap['beatmap_id'])
            # try to update beatmap
            beatmap_object.creator = beatmap['creator']
            beatmap_object.creator_id = beatmap['creator_id']
            beatmap_object.checksum = beatmap['file_md5']
            beatmap_object.version = beatmap['version']
            beatmap_object.total_length = beatmap['total_length']
            beatmap_object.hit_length = beatmap['hit_length']
            beatmap_object.count_total = int(beatmap['count_normal']) + int(beatmap['count_slider']) + int(
                beatmap['count_spinner'])
            beatmap_object.count_normal = beatmap['count_normal']
            beatmap_object.count_slider = beatmap['count_slider']
            beatmap_object.count_spinner = beatmap['count_spinner']
            beatmap_object.diff_drain = beatmap['diff_drain']
            beatmap_object.diff_size = beatmap['diff_size']
            beatmap_object.diff_overall = beatmap['diff_overall']
            beatmap_object.diff_approach = beatmap['diff_approach']
            beatmap_object.play_mode = beatmap['mode']
            beatmap_object.approved = beatmap['approved']
            beatmap_object.last_update = make_aware(datetime.strptime(beatmap['last_update'], '%Y-%m-%d %H:%M:%S'))
            beatmap_object.difficulty_rating = beatmap['difficultyrating']
            beatmap_object.play_count = beatmap['playcount']
            beatmap_object.pass_count = beatmap['passcount']
            beatmap_object.bpm = beatmap['bpm']
            beatmap_object.save()
        except Beatmap.DoesNotExist:
            Beatmap.objects.create(
                beatmap_id=beatmap['beatmap_id'],
                beatmapset=beatmapset,
                creator=beatmap['creator'],
                creator_id=beatmap['creator_id'],
                checksum=beatmap['file_md5'],
                version=beatmap['version'],
                total_length=beatmap['total_length'],
                hit_length=beatmap['hit_length'],
                count_total=int(beatmap['count_normal']) + int(beatmap['count_slider']) + int(
                    beatmap['count_spinner']),
                count_normal=beatmap['count_normal'],
                count_slider=beatmap['count_slider'],
                count_spinner=beatmap['count_spinner'],
                diff_drain=beatmap['diff_drain'],
                diff_size=beatmap['diff_size'],
                diff_overall=beatmap['diff_overall'],
                diff_approach=beatmap['diff_approach'],
                play_mode=beatmap['mode'],
                approved=beatmap['approved'],
                last_update=make_aware(datetime.strptime(beatmap['last_update'], '%Y-%m-%d %H:%M:%S')),
                difficulty_rating=beatmap['difficultyrating'],
                play_count=beatmap['playcount'],
                pass_count=beatmap['passcount'],
                bpm=beatmap['bpm']
            )

    logger.info(f"✅ Beatmapset {beatmapset.title} imported and updated.")

    # Upload beatmapset picture to S3
    s3_client = get_static_s3_client()
    card_pic = requests.get(f"https://assets.ppy.sh/beatmaps/{beatmapset.beatmapset_id}/covers/card.jpg")
    list_pic = requests.get(f"https://assets.ppy.sh/beatmaps/{beatmapset.beatmapset_id}/covers/list.jpg")
    cover_pic = requests.get(f"https://assets.ppy.sh/beatmaps/{beatmapset.beatmapset_id}/covers/cover.jpg")
    fullsize_pic = requests.get(f"https://assets.ppy.sh/beatmaps/{beatmapset.beatmapset_id}/covers/fullsize.jpg")
    thumbnail_pic = requests.get(f"https://b.ppy.sh/thumb/{beatmapset.beatmapset_id}l.jpg")

    card_path = f"beatmapset/{beatmapset.beatmapset_id}/covers/card.jpg"
    list_path = f"beatmapset/{beatmapset.beatmapset_id}/covers/list.jpg"
    cover_path = f"beatmapset/{beatmapset.beatmapset_id}/covers/cover.jpg"
    fullsize_path = f"beatmapset/{beatmapset.beatmapset_id}/covers/fullsize.jpg"
    thumbnail_path = f"beatmapset/{beatmapset.beatmapset_id}/covers/thumbnail.jpg"

    if ("Access Denied" or "Not Found") not in str(card_pic.content) and card_pic.status_code == 200:
        try:
            s3_client.put_object(
                Bucket=S3_STATIC_BUCKET_NAME,
                Key=card_path,
                Body=card_pic.content,
                ContentType="image/jpeg",
                ACL="public-read",
                CacheControl="max-age=31536000"
            )
            logger.info(f"✅ Uploaded card.jpg to S3 for beatmapset {beatmapset.beatmapset_id}.")
        except Exception as e:
            logger.critical(f"❌ Failed to upload card.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : {e}")
    else:
        logger.warning(f"❌ Failed to upload card.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : File not found.")
    if ("Access Denied" or "Not Found") not in str(list_pic.content) and list_pic.status_code == 200:
        try:
            s3_client.put_object(
                Bucket=S3_STATIC_BUCKET_NAME,
                Key=list_path,
                Body=list_pic.content,
                ContentType="image/jpeg",
                ACL="public-read",
                CacheControl="max-age=31536000"
            )
            logger.info(f"✅ Uploaded list.jpg to S3 for beatmapset {beatmapset.beatmapset_id}.")
        except Exception as e:
            logger.critical(f"❌ Failed to upload list.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : {e}")
    else:
        logger.warning(f"❌ Failed to upload list.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : File not found.")
    if ("Access Denied" or "Not Found") not in str(cover_pic.content) and cover_pic.status_code == 200:
        try:
            s3_client.put_object(
                Bucket=S3_STATIC_BUCKET_NAME,
                Key=cover_path,
                Body=cover_pic.content,
                ContentType="image/jpeg",
                ACL="public-read",
                CacheControl="max-age=31536000"
            )
            logger.info(f"✅ Uploaded cover.jpg to S3 for beatmapset {beatmapset.beatmapset_id}.")
        except Exception as e:
            logger.critical(f"❌ Failed to upload cover.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : {e}")
    else:
        logger.warning(f"❌ Failed to upload cover.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : File not found.")
    if ("Access Denied" or "Not Found") not in str(fullsize_pic.content) and fullsize_pic.status_code == 200:
        try:
            s3_client.put_object(
                Bucket=S3_STATIC_BUCKET_NAME,
                Key=fullsize_path,
                Body=fullsize_pic.content,
                ContentType="image/jpeg",
                ACL="public-read",
                CacheControl="max-age=31536000"
            )
            logger.info(f"✅ Uploaded fullsize.jpg to S3 for beatmapset {beatmapset.beatmapset_id}.")
        except Exception as e:
            logger.critical(f"❌ Failed to upload fullsize.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : {e}")
    else:
        logger.warning(f"❌ Failed to upload fullsize.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : File not found.")
    if ("Access Denied" or "Not Found") not in str(thumbnail_pic.content) and thumbnail_pic.status_code == 200:
        try:
            s3_client.put_object(
                Bucket=S3_STATIC_BUCKET_NAME,
                Key=thumbnail_path,
                Body=thumbnail_pic.content,
                ContentType="image/jpeg",
                ACL="public-read",
                CacheControl="max-age=31536000"
            )
            logging.info(f"✅ Uploaded thumbnail.jpg to S3 for beatmapset {beatmapset.beatmapset_id}.")
        except Exception as e:
            logger.critical(f"❌ Failed to upload thumbnail.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : {e}")
    else:
        logger.warning(f"❌ Failed to upload thumbnail.jpg to S3 for beatmapset {beatmapset.beatmapset_id}. : File not found.")

    beatmapset.card_picture_url = generate_static_url(card_path)
    beatmapset.list_picture_url = generate_static_url(list_path)
    beatmapset.cover_picture_url = generate_static_url(cover_path)
    beatmapset.full_size_picture_url = generate_static_url(fullsize_path)
    beatmapset.thumbnail_picture_url = generate_static_url(thumbnail_path)
    beatmapset.save()
    logger.info(f"✅ Updated beatmapset {beatmapset.beatmapset_id} with new cover urls.")

    return beatmapset
