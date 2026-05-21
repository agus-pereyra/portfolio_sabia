from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db.models import Q
from portfolio.models import Media
from PIL import Image
from io import BytesIO
import os


class Command(BaseCommand):
    help = 'Genera archivos medium (900px WEBP) para todas las imágenes que no lo tengan'

    def handle(self, *args, **options):
        # NULL is what Django sets when the migration adds a new nullable field to existing rows.
        # Empty string covers any record saved without a medium file before this fix.
        imagenes = Media.objects.filter(
            type='image'
        ).filter(Q(medium_file__isnull=True) | Q(medium_file=''))
        total = imagenes.count()
        self.stdout.write(f'Imágenes sin medium_file: {total}')

        ok = 0
        errors = 0

        for index, media in enumerate(imagenes, 1):
            if not media.image_file:
                self.stdout.write(self.style.WARNING(f'[{index}/{total}] Sin image_file: {media}'))
                continue
            try:
                # Read the full file into memory first — required for S3-backed storage
                # where the FieldFile is not natively seekable by PIL.
                with media.image_file.open('rb') as f:
                    raw = f.read()

                img = Image.open(BytesIO(raw))
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail((900, 900))

                buf = BytesIO()
                img.save(buf, format='WEBP', quality=82)
                buf.seek(0)

                base_name = os.path.basename(media.image_file.name).split('.')[0]
                media.medium_file.save(
                    f'medium_{base_name}.webp',
                    ContentFile(buf.read()),
                    save=False,
                )
                # Use update_fields to avoid re-running the full Media.save() logic
                Media.objects.filter(pk=media.pk).update(medium_file=media.medium_file.name)
                ok += 1
                self.stdout.write(f'[{index}/{total}] OK: {media}')
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'[{index}/{total}] Error en {media}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nListo. Generados: {ok} | Errores: {errors}'
        ))
