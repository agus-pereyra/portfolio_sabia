from django.core.management.base import BaseCommand
from django.db.models import Q
from portfolio.models import Media
from PIL import Image
from io import BytesIO


class Command(BaseCommand):
    help = 'Backfill width/height for image rows where either dimension is NULL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without writing to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        qs = (
            Media.objects
            .filter(type='image')
            .exclude(image_file='')
            .filter(image_file__isnull=False)
            .filter(Q(width__isnull=True) | Q(height__isnull=True))
            .only('pk', 'id_collection', 'image_file', 'width', 'height')
        )

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No rows to backfill.'))
            return

        self.stdout.write(f'Found {total} image(s) with NULL width or height.')
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — no changes will be written.\n'))

        ok = 0
        failed = 0

        for index, media in enumerate(qs.iterator(), 1):
            prefix = f'[{index}/{total}] {media.id_collection or media.pk}'
            try:
                with media.image_file.open('rb') as f:
                    raw = f.read()

                img = Image.open(BytesIO(raw))
                w, h = img.size

                if not dry_run:
                    Media.objects.filter(pk=media.pk).update(width=w, height=h)

                self.stdout.write(f'{prefix}: {w}×{h}')
                ok += 1

            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'{prefix}: {exc}'))
                failed += 1

        suffix = ' (dry run)' if dry_run else ''
        msg = f'\nDone{suffix}: {ok} updated, {failed} failed.'
        self.stdout.write(self.style.SUCCESS(msg) if failed == 0 else self.style.WARNING(msg))
