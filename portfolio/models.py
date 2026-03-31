from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django_resized import ResizedImageField

from moviepy import VideoFileClip
from PIL import Image
from io import BytesIO
import datetime
import os

class Collaborator(models.Model):
    first_name = models.CharField(max_length=20, verbose_name='Nombre/s')
    last_name = models.CharField(max_length=30, verbose_name='Apellido/s')
    role = models.CharField(max_length=100, blank=True, null=True, verbose_name='Rol', help_text='(ej. Fotógrafo/a, Maquillador/a, etc)')
    contact = models.URLField(blank=True, null=True, verbose_name='Contacto', help_text='(URL ej. Instagram, Portfolio, etc)')
    
    class Gender(models.TextChoices):
        MASCULINE = 'M', 'Masculino'
        FEMENINE = 'F', 'Femenino'
        OTHER = 'O', 'Otro'
    
    genre = models.CharField(max_length=1, choices=Gender.choices, default=Gender.OTHER, verbose_name='Género')

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.role}'
    
    class Meta:
        verbose_name = 'Colaborador/a'
        verbose_name_plural = 'Colaboradores'

class Collection(models.Model):
    title = models.CharField(max_length=40, verbose_name='Título')
    slug = models.SlugField(unique=True, blank=True, null=True)

    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    collaborators = models.ManyToManyField(Collaborator, blank=True, related_name='collections', verbose_name='Colaboladores')

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Fecha de publicación')
    captured_at = models.DateField(blank=True, null=True, verbose_name='Fecha de captura')

    is_featured = models.BooleanField(verbose_name='Destacar', default=False, help_text='(Mostrar en Home)')

    cover =  models.ForeignKey(
        'Media', 
        on_delete=models.SET_NULL, 
        related_name='cover_for', 
        verbose_name='Portada',
        limit_choices_to={'type': 'image'},
        null=True, blank=True
    )
    cover_video = models.ForeignKey(
        'Media',
        on_delete=models.SET_NULL, 
        related_name='cover_video_for', 
        verbose_name='Portada Animada', 
        help_text='(Previsualización de video como portada)',
        limit_choices_to={'type': 'video'},
        null=True, blank=True,
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.cover and self.cover_video:
            raise ValidationError(
                "Una colección no puede tener foto y video de portada al mismo tiempo. "
                "Por favor, elige solo uno."
                )

    def get_photos_count(self):
        return self.media_items.filter(type='image').count()
    
    def get_videos_count(self):
        return self.media_items.filter(type='video').count()
    
    def get_media_count(self):
        return self.media_items.count()
    
    def get_first_media(self):
        return self.media_items.filter(order=0).first()

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name = 'Colección'
        verbose_name_plural = 'Colecciones'
        ordering = ['-captured_at']

class Media(models.Model):
    TYPE_CHOICES = [
        ('image', 'Imágen'),
        ('video', 'Video')
    ]

    type = models.CharField(choices=TYPE_CHOICES, default='image', max_length=10, verbose_name='Tipo de Archivo')

    collection = models.ForeignKey(
        Collection, 
        on_delete=models.SET_NULL, 
        related_name="media_items", 
        verbose_name='Album de Pertenencia',
        blank=True, 
        null=True, 
        )    

    image_file = ResizedImageField(
        size=[2048, 2048], # máximo width y height
        quality=100, 
        force_format='WEBP',
        upload_to='portfolio/media/images/', 
        verbose_name='Archivo de la Imágen',
        width_field='width',
        height_field='height',
        null=True, 
        blank=True,
        )
    
    video_file = models.FileField(
        upload_to='portfolio/media/videos/', 
        verbose_name='Archivo del Video', 
        null=True, 
        blank=True
        )
    
    duration = models.DurationField(help_text='HH:MM:SS', verbose_name='Duración', null=True, blank=True, )
    thumbnail = models.ImageField(upload_to='portfolio/media/thumbnails/', verbose_name='Miniatura', null=True, blank=True)

    width = models.IntegerField(editable=False, null=True, verbose_name='Ancho', help_text='px')
    height = models.IntegerField(editable=False, null=True, verbose_name='Alto', help_text='px')

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    captured_at = models.DateField(blank=True, null=True, verbose_name='Fecha de captura')

    id_collection = models.CharField(max_length=255, null=True, editable=False, db_index=True, unique=True, verbose_name='ID')

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def save(self, *args, **kwargs):
        if self.collection and not self.captured_at:
            self.captured_at = self.collection.captured_at

        if not self.id_collection and self.collection:
            base_slug = slugify(self.collection.title)
            
            collection_media = Media.objects.filter(collection=self.collection)
            counter = collection_media.count() + 1
            
            candidate_id = f"{counter}_{base_slug}"
            
            while Media.objects.filter(id_collection=candidate_id).exists():
                counter += 1
                candidate_id = f"{counter}_{base_slug}"
                
            self.id_collection = candidate_id

        if self.type == 'image' and self.image_file:
            if not self.width or not self.height:
                img = Image.open(self.image_file)
                self.width, self.height = img.size   
        
        if not self.thumbnail:
                img = Image.open(self.image_file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                img.thumbnail((300, 300)) 
                
                temp_thumb = BytesIO()
                img.save(temp_thumb, format='WEBP', quality=60) 
                temp_thumb.seek(0)
                
                base_name = os.path.basename(self.image_file.name).split('.')[0]
                img_path = f"thumb_img_{base_name}.webp"
                
                self.thumbnail.save(img_path, ContentFile(temp_thumb.read()), save=False)

        super().save(*args, **kwargs)
             
        if self.type == 'video' and self.video_file:        
            update_flag = False
            if not self.duration or not self.width or not self.height:
                try:
                    video = VideoFileClip(self.video_file.path)
                    self.width, self.height = video.size
                    self.duration = datetime.timedelta(seconds=round(video.duration,2))
                    
                    if not self.thumbnail:
                        frame_time = min(1.0, video.duration / 2) if video.duration else 0
                        frame = video.get_frame(frame_time)

                        img_path = f"thumb_{os.path.basename(self.video_file.name)}.webp"
                        new_img = Image.fromarray(frame)
                        temp_thumb = BytesIO()
                        new_img.save(temp_thumb, format='WEBP', quality=70)
                        temp_thumb.seek(0)

                        self.thumbnail.save(img_path, ContentFile(temp_thumb.read()), save=False)
                
                    video.close()
                    update_flag = True

                except Exception as e:
                    print(f'Error al procesar el video: {e}')
        
            if update_flag:
                super().save(update_fields=['width', 'height', 'duration', 'thumbnail'])
    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'
        ordering = ['order']

    def __str__(self):
        if self.id_collection:
            return f'{self.id_collection} - {self.type}'
        return f'Untitled - {self.type}'