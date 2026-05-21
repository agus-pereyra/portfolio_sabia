import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings


MEDIA_CONTENT_TYPES = {
    '.webp': 'image/webp',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.webm': 'video/webm',
}

CACHE_CONTROL = 'max-age=31536000, public'


class Command(BaseCommand):
    help = 'Aplica Cache-Control a todos los objetos existentes en S3 (copy-in-place)'

    def handle(self, *args, **options):
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket)

        total = 0
        updated = 0
        skipped = 0
        errors = 0

        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                total += 1

                ext = ('.' + key.rsplit('.', 1)[-1].lower()) if '.' in key else ''
                content_type = MEDIA_CONTENT_TYPES.get(ext, 'application/octet-stream')

                try:
                    head = s3.head_object(Bucket=bucket, Key=key)
                    existing_cc = head.get('CacheControl', '')
                    if existing_cc == CACHE_CONTROL:
                        skipped += 1
                        continue

                    s3.copy_object(
                        Bucket=bucket,
                        CopySource={'Bucket': bucket, 'Key': key},
                        Key=key,
                        MetadataDirective='REPLACE',
                        CacheControl=CACHE_CONTROL,
                        ContentType=content_type,
                    )
                    updated += 1
                    self.stdout.write(f'[{updated}] OK: {key}')
                except ClientError as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f'Error en {key}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nListo. Total: {total} | Actualizados: {updated} | Ya tenían cache: {skipped} | Errores: {errors}'
        ))
