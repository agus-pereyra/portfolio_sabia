from django.db import models
from django.utils.text import slugify

class Collaborator(models.Model):
    first_name = models.CharField(max_length=20, verbose_name='Nombre/s')
    last_name = models.CharField(max_length=30, verbose_name='Apellido')
    role = models.CharField(max_length=100, blank=True, null=True, verbose_name='Rol (ej. Fotógrafo/a, Maquillador/a, etc)')
    contact = models.URLField(blank=True, null=True, verbose_name='Contacto (URL ej. Instagram, Portfolio, etc)')
    
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
    collaborators = models.ManyToManyField(Collaborator, blank=True, related_name='collections')

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Fecha de publicación')
    captured_at = models.DateField(blank=True, null=True, verbose_name='Fecha de captura')

    is_featured = models.BooleanField(verbose_name='Destacar', default=False, help_text='(Mostrar en Home)')

    cover =  models.ForeignKey(
        'Picture', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cover'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_photos_count(self):
        return self.pictures.count()
    
    def get_videos_count(self):
        return self.videos.count()

    def get_total_items(self):
        return self.get_photos_count() + self.get_videos_count

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name = 'Colección'
        verbose_name_plural = 'Colecciones'
        ordering = ['-captured_at']

class Picture(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Título')

    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True, related_name="pictures")
    image = models.ImageField(upload_to='portfolio/images/', 
                              verbose_name='Archivo de la Imágen',
                              width_field='width',
                              height_field='height')

    width = models.IntegerField(editable=False, null=True)
    height = models.IntegerField(editable=False, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    captured_at = models.DateField(blank=True, null=True, verbose_name='Fecha de captura')
    
    id_collection = models.CharField(max_length=255, null=True, editable=False, db_index=True, unique=True) 

    def save(self, *args, **kwargs):
        if self.collection:
            self.captured_at = self.collection.captured_at
        if not self.id_collection:
            pictures_in_col = Picture.objects.filter(collection=self.collection)
            current_count = pictures_in_col.count()            
            self.id_collection = f"{current_count + 1}_{slugify(self.collection.title)}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.id_collection:
            return f'{self.id_collection}'
        return 'No ID'
        
    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'
        ordering = ['-captured_at']

class Video(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Título')

    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, blank=True, null=True, related_name="videos")
    video_file = models.FileField(upload_to='portfolio/videos/', verbose_name='Archivo del Video')
    
    duration = models.DurationField(null=True, blank=True, help_text='HH:MM:SS', verbose_name='Duración')

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    captured_at = models.DateField(blank=True, null=True, verbose_name='Fecha de captura')

    def __str__(self):
        if self.title:
            return f'{self.title} - {self.duration}'
        return f'Sín título - {self.duration}'
    
    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-captured_at']