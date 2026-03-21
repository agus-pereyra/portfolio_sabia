from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from .models import Collaborator, Collection, Picture, Video
from .custom_fields import MultipleImageField, MultipleVideoField

class CollectionForm(forms.ModelForm):
    captured_at = forms.DateField(
        label="Fecha de la Colección",
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m', '%Y-%m-%d']
    )

    upload_multiple_pictures = MultipleImageField(label="Cargar Imágenes", required=False)

    upload_multiple_videos = MultipleVideoField(label="Cargar Videos", required=False)
    
    class Meta:
        model = Collection
        fields = '__all__'
        widgets = {
            'captured_at': forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        }
        
    def clean_captured_at(self):
        data = self.cleaned_data['captured_at']
        return data

class PictureInline(admin.TabularInline):
    model = Picture
    extra = 0
    readonly_fields = ('id_collection', 'width', 'height', 'preview')
    fields = ('id_collection', 'image', 'width', 'height', 'preview')
    classes = ('collapse', 'open')
    list_display = ('id_collection', 'collection.slug')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return ""
    
@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_collection', 'get_collection_slug')
    
    list_filter = ('id_collection',)
    
    search_fields = ('id_collection__title', 'id_collection__slug')

    def get_collection_slug(self, obj):
        return obj.collection.slug if obj.id_collection else "⚠️ SIN COLECCIÓN"
    get_collection_slug.short_description = 'Collection Slug'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_collection')
    list_filter = ('id_collection',)
    
class VideoInline(admin.TabularInline):
    model = Video
    extra = 0
    readonly_fields = ('id_collection', 'width', 'height', 'duration', 'preview')
    fields = ('id_collection', 'file', 'width', 'height', 'duration', 'preview')
    classes = ('collapse', 'open')
    list_display = ('id_collection', 'collection.slug')

    def preview(self, obj):
        if obj.file:
            return format_html(
                '''<video src="{}" style="width: 150px; height: auto; border-radius: 4px;" 
                   controls muted preload="metadata">
                   </video>''', 
                obj.file.url
            )
        return ""
    
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)} # slug automático mientras se escribe el título
    search_fields = ('title',)
    inlines = [PictureInline, VideoInline]
    filter_horizontal = ('collaborators',)

    form = CollectionForm

    list_display = ('title', 'slug',  'is_featured', 'get_photos_count', 'get_videos_count', 'captured_at')
    
    list_editable = ('is_featured',)
    
    list_filter = ('is_featured', 'captured_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'captured_at', 'is_featured')
        }),
        ('Portadas (Elegir solo una)', {
            'classes': ('collapse', 'open'),
            'fields': ('cover', 'cover_video'),
            'description': 'Si seleccionas una foto de portada, asegúrate de que el video de portada esté vacío.'
        }),
        ('Carga de Archivos', {
            'classes': ('collapse', 'open'),
            'fields': ('upload_multiple_pictures', 'upload_multiple_videos'),
        }),
    )

    def get_photos_count(self, obj):
        return obj.get_photos_count()
    get_photos_count.short_description = "Fotos"

    def get_videos_count(self, obj):
        return obj.get_videos_count()
    get_videos_count.short_description = "Videos"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['upload_multiple'] = MultipleImageField(
            label="Cargar Imágenes",
            required=False
        )
        if obj:
            form.base_fields['cover_photo'].queryset = Picture.objects.filter(collection=obj)
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        photos = request.FILES.getlist('upload_multiple')
        if photos:
            last_count = obj.pictures.count()
            
            new_pictures = []
            for i, f in enumerate(photos, start=1):
                new_pic = Picture.objects.create(
                    collection=obj, 
                    image=f,
                    id_collection=f"{last_count + i}_{slugify(obj.title)}"
                )
                new_pictures.append(new_pic)
            
            if not obj.cover and not obj.cover_video and new_pictures:
                obj.cover = new_pictures[0]
                obj.save()
        
        videos = request.FILES.getlist('upload_multiple_videos')
        if videos:
            last_vid_count = obj.videos.count()
            
            new_videos = []
            for i, v in enumerate(videos, start=1):
                new_vid = Video.objects.create(
                    collection=obj,
                    file=v,
                    id_collection=f"vid_{last_vid_count + i}_{slugify(obj.title)}"
                )
                new_videos.append(new_vid)
            
            if not obj.cover_video and not obj.cover and new_videos:
                obj.cover_video = new_videos[0]
                obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and 'cover' in form.base_fields:
            form.base_fields['cover'].queryset = Picture.objects.filter(collection=obj)
        return form

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'genre')
    list_filter = ('genre', 'role')
    classes = ('collapse', 'open')