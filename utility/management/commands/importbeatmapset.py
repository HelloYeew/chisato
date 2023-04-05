from django.core.management import BaseCommand

from utility.osu_api.importer import import_beatmapset


class Command(BaseCommand):
    help = 'Import a beatmapset from osu!api'

    def add_arguments(self, parser):
        parser.add_argument('beatmapset_id', type=int)

    def handle(self, *args, **options):
        beatmapset_id = options['beatmapset_id']
        self.stdout.write(self.style.SUCCESS(f'Importing beatmapset {beatmapset_id}'))
        result = import_beatmapset(beatmapset_id)
        self.stdout.write(self.style.SUCCESS(f'Imported beatmapset {result.title}!'))
