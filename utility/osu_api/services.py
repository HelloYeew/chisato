import requests
from decouple import config

OSU_API_KEY = config('OSU_API_KEY', default='')
OSU_API_URL = 'https://osu.ppy.sh/api'


def get_raw_beatmap_info(beatmap_id: int) -> dict:
    """Get beatmap info from osu! api"""
    response = requests.get(f'{OSU_API_URL}/get_beatmaps', params={
        'k': OSU_API_KEY,
        'b': beatmap_id
    })
    return response.json()


def get_raw_beatmapset_info(beatmapset_id: int) -> dict:
    """Get beatmapset info from osu! api"""
    response = requests.get(f'{OSU_API_URL}/get_beatmaps', params={
        'k': OSU_API_KEY,
        's': beatmapset_id
    })
    return response.json()
