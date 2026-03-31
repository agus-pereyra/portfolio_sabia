from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from django.urls import reverse
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase, SortableAdminMixin
from .models import Collaborator, Collection, Media
from .custom_fields import MultipleMediaField
from .widgets import CoverSelectWidget

class MediaInLine(SortableInlineAdminMixin, admin.TabularInline):
    model = Media
    extra = 0
    readonly_fields = ('type', 'get_preview', 'formatted_duration', 'width', 'height', 'duration')
    ordering = ('order',)
    classes = ('collapse', 'open')

    def formatted_duration(self, obj):
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}:{int(minutes):02d}:{seconds:05.2f}"
        return "—"
    formatted_duration.short_description = 'Duración'

    def get_preview(self, obj):
        if not obj.pk:
            return "—"
        
        change_url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.pk])
        
        if obj.thumbnail:
            return format_html(
                '<a href="{}" target="_blank" title="Editar este archivo en una pestaña nueva">'
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block; transition: opacity 0.2s;" '
                'onmouseover="this.style.opacity=0.7" onmouseout="this.style.opacity=1" />'
                '</a>',
                change_url,
                obj.thumbnail.url,
            )
        
        if obj.type == 'image' and obj.image_file:
            return format_html(
                '<a href="{}" target="_blank" title="Editar este archivo en una pestaña nueva">'
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block; transition: opacity 0.2s;" '
                'onmouseover="this.style.opacity=0.7" onmouseout="this.style.opacity=1" />'
                '</a>',
                change_url,
                obj.image_file.url,
            )
        if obj.type == 'video' and obj.video_file:
            return format_html(
                '<a href="{}" target="_blank" title="Editar este archivo en una pestaña nueva">'
                '<video src="{}" autoplay muted loop playsinline '
                'style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block; transition: opacity 0.2s;" '
                'onmouseover="this.style.opacity=0.7" onmouseout="this.style.opacity=1"></video>'
                '</a>',
                change_url,
                obj.video_file.url,
            )
        return "—"
    get_preview.short_description = 'Preview (Click para editar)'
 
    def get_fields(self, request, obj=None):
        return ['order', 'type', 'get_preview', 'formatted_duration', 'width', 'height']

    class Media:
        """JS necesario para el drag-and-drop de orden"""
        js = ('admin/js/jquery.init.js',)

class CollectionForm(forms.ModelForm):
    captured_at = forms.DateField(
        label="Fecha de la Colección",
        widget=forms.DateInput(attrs={'type': 'month'}, format='%Y-%m'),
        input_formats=['%Y-%m', '%Y-%m-%d']
    )

    upload_media = MultipleMediaField(label="Cargar Archivos", required=False)
    
    class Meta:
        model = Collection
        fields = '__all__'
        widgets = {
            'cover': CoverSelectWidget(),
            'cover_video': CoverSelectWidget(),
        }
        
    def clean_captured_at(self):
        return self.cleaned_data['captured_at']

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_collection', 'type', 'collection', 'order', 'get_preview')
    list_filter = ('type', 'collection')
    search_fields = ('id_collection', 'collection__title', 'collection__slug')
    ordering = ('collection', 'order')
    readonly_fields = ('id_collection', 'width', 'height', 'formatted_duration', 'thumbnail', 'get_preview')
    
    def formatted_duration(self, obj):
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}:{int(minutes):02d}:{seconds:05.2f}"
        return "—"
    formatted_duration.short_description = 'Duración'

    def get_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block;" />',
                obj.thumbnail.url,
            )
        
        if obj.type == 'image' and obj.image_file:
            return format_html(
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block;" />',
                obj.image_file.url,
            )
        if obj.type == 'video' and obj.video_file:
            return format_html(
                '<video src="{}" autoplay muted loop playsinline '
                'style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block;"></video>',
                obj.video_file.url,
            )
        return "—"
    get_preview.short_description = 'Preview'

@admin.register(Collection)
class CollectionAdmin(SortableAdminMixin, SortableAdminBase, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    inlines = [MediaInLine]
    filter_horizontal = ('collaborators',)
    form = CollectionForm

    list_display = ('is_featured', 'featured_order', 'title', 'slug', 'get_photos_count', 'get_videos_count', 'captured_at')
    list_filter = ('is_featured', 'captured_at')
    list_display_links = ('title',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'captured_at', 'is_featured', 'collaborators')
        }),
        ('Portada', {
            'classes' : ('collapse', 'open'),
            'fields': ('cover', 'cover_video'),
            'description': 'Seleccionar como portada una imagen ó un video'
        }),
        ('Carga de Archivos', {
            'fields': ('upload_media',),
        }),
    )

    def get_photos_count(self, obj):
        return obj.get_photos_count()
    get_photos_count.short_description = "Fotos"

    def get_videos_count(self, obj):
        return obj.get_videos_count()
    get_videos_count.short_description = "Videos"

    def get_media_count(self, obj):
        return obj.get_media_count()
    get_videos_count.short_description = "Archivos"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            if 'cover' in form.base_fields:
                form.base_fields['cover'].queryset = Media.objects.filter(
                    collection=obj, type='image'
                )
                form.base_fields['cover'].widget.can_add_related = False
                form.base_fields['cover'].widget.can_change_related = False
                form.base_fields['cover'].widget.can_delete_related = False

            if 'cover_video' in form.base_fields:
                form.base_fields['cover_video'].queryset = Media.objects.filter(
                    collection=obj, type='video'
                )
                form.base_fields['cover_video'].widget.can_add_related = False
                form.base_fields['cover_video'].widget.can_change_related = False
                form.base_fields['cover_video'].widget.can_delete_related = False
        
        else:
            if 'cover' in form.base_fields:
                form.base_fields['cover'].queryset = Media.objects.none()
            if 'cover_video' in form.base_fields:
                form.base_fields['cover_video'].queryset = Media.objects.none()

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
 
        files = request.FILES.getlist('upload_media')
        if not files:
            return
 
        media_field = MultipleMediaField()
        new_images = []
        new_videos = []
 
        for i, f in enumerate(files, start=1):
            if media_field.is_image(f):
                media = Media.objects.create(
                    collection=obj,
                    type='image',
                    image_file=f,
                    order=obj.media_items.count() + i,
                )
                new_images.append(media)
            elif media_field.is_video(f):
                media = Media.objects.create(
                    collection=obj,
                    type='video',
                    video_file=f,
                    order=obj.media_items.count() + i,
                )
                new_videos.append(media)
 
        if not obj.cover and not obj.cover_video:
            if new_images:
                obj.cover = new_images[0]
                obj.save()
            elif new_videos:
                obj.cover_video = new_videos[0]
                obj.save()

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'genre')
    list_filter = ('genre', 'role')
    classes = ('collapse', 'open')