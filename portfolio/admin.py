from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Collaborator, Collection, Picture, Video

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class CollectionForm(forms.ModelForm):
    captured_at = forms.DateField(
        label="Fecha de la Colección",
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m', '%Y-%m-%d']
    )

    upload_multiple = MultipleFileField(
        label="Subida Masiva (Seleccioná muchas fotos)",
        required=False,
        help_text="Arrastrá los archivos aquí para subirlos todos juntos."
    )

    class Meta:
        model = Collection
        fields = '__all__'
        widgets = {
            'captured_at': forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        }
        
    def clean_captured_at(self):
        data = self.cleaned_data['captured_at']
        # Si por alguna razón llega solo el objeto fecha (que ya tiene día), 
        # Django lo maneja bien. El problema es la conversión del texto.
        return data

class PictureInline(admin.TabularInline):
    model = Picture
    extra = 0
    readonly_fields = ('id_collection', 'preview')
    fields = ('id_collection', 'image', 'preview')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return ""
    
class VideoInline(admin.StackedInline):
    model = Video
    extra = 1

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)} # slug automático mientras se escribe el título
    list_display = ('title', 'slug', 'is_featured', 'get_photos_count', 'get_videos_count', 'captured_at', 'created_at')
    search_fields = ('title',)
    inlines = [PictureInline, VideoInline]
    filter_horizontal = ('collaborators',)

    form = CollectionForm

    def get_photos_count(self, obj):
        return obj.get_photos_count()
    get_photos_count.short_description = "Fotos"

    def get_videos_count(self, obj):
        return obj.get_videos_count()
    get_videos_count.short_description = "Videos"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['upload_multiple'] = MultipleFileField(
            label="Cargar Imágenes",
            required=False
        )
        if obj:
            form.base_fields['cover_photo'].queryset = Picture.objects.filter(collection=obj)
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        files = request.FILES.getlist('upload_multiple')
        if files:
            last_count = obj.pictures.count()
            
            new_pictures = []
            for i, f in enumerate(files, start=1):
                new_pic = Picture.objects.create(
                    collection=obj, 
                    image=f,
                    id_collection=f"{last_count + i}_{slugify(obj.title)}"
                )
                new_pictures.append(new_pic)
            
            if not obj.cover and new_pictures:
                obj.cover = new_pictures[0]
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

admin.site.register(Picture)
admin.site.register(Video)