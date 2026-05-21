from django.core.management.base import BaseCommand
from django.core.files import File
from portfolio.models import Media
import os

class Command(BaseCommand):
    help = 'Reprocesa las imágenes locales con la configuración actual de Django-Resized y las sube a S3'

    def handle(self, *args, **options):
        imagenes = Media.objects.filter(type='image')
        total = imagenes.count()

        self.stdout.write(self.style.SUCCESS(f"Iniciando optimización de {total} imágenes..."))

        for index, media in enumerate(imagenes, 1):
            if media.image_file:
                ruta_local = os.path.join('media', media.image_file.name)
                
                if os.path.exists(ruta_local):
                    self.stdout.write(f"[{index}/{total}] Procesando y subiendo al bucket: {media.image_file.name}")
                    
                    try:
                        with open(ruta_local, 'rb') as f:
                            media.image_file.save(os.path.basename(ruta_local), File(f), save=True)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Error al procesar {media.image_file.name}: {str(e)}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Alerta: No se encontró el archivo local en {ruta_local}"))

        self.stdout.write(self.style.SUCCESS("¡Proceso de optimización masiva finalizado con éxito!"))