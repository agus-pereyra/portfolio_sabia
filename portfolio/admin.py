from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from .models import Collaborator, Collection, Media
from .custom_fields import MultipleMediaField
from .widgets import CoverSelectWidget

class MediaInLine(SortableInlineAdminMixin, admin.TabularInline):
    model = Media
    extra = 0
    fields = ('order',  'get_preview', 'duration', 'width', 'height')
    readonly_fields = ('type', 'get_preview', 'id_collection', 'duration', 'width', 'height')
    ordering = ('order',)
    classes = ('collapse', 'open')

    def get_preview(self, obj):
        if obj.type == 'image' and obj.image_file:
            return format_html(
                '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                'border-radius:4px;display:block;" />',
                obj.image_file.url,
            )
        if obj.type == 'video':
            if obj.video_file:
                return format_html(
                    '<video src="{}" autoplay muted loop playsinline '
                    'style="width:120px;height:80px;object-fit:cover;'
                    'border-radius:4px;display:block;"></video>',
                    obj.video_file.url,
                )
            if obj.thumbnail:
                return format_html(
                    '<img src="{}" style="width:120px;height:80px;object-fit:cover;'
                    'border-radius:4px;display:block;" />',
                    obj.thumbnail.url,
                )
        return "—"
    get_preview.short_description = 'Preview'
 
    def get_fields(self, request, obj=None):
        base = ['order', 'type', 'id_collection', 'get_preview', 'width', 'height']
        return base

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
    readonly_fields = ('id_collection', 'width', 'height', 'duration', 'thumbnail', 'get_preview')
 
    def get_preview(self, obj):
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
class CollectionAdmin(SortableAdminBase, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    inlines = [MediaInLine]
    filter_horizontal = ('collaborators',)
    form = CollectionForm

    list_display = ('title', 'slug',  'is_featured', 'get_photos_count', 'get_videos_count', 'captured_at')
    list_editable = ('is_featured',)
    list_filter = ('is_featured', 'captured_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'captured_at', 'is_featured', 'collaborators')
        }),
        ('Portada', {
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

# class PictureInline(admin.TabularInline):
#     model = Picture
#     extra = 0
#     readonly_fields = ('id_collection', 'width', 'height', 'preview')
#     fields = ('id_collection', 'image', 'width', 'height', 'preview')
#     classes = ('collapse', 'open')
#     list_display = ('id_collection', 'collection.slug')

#     def preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
#         return ""
    
# @admin.register(Picture)
# class PictureAdmin(admin.ModelAdmin):
#     list_display = ('id', 'id_collection', 'get_collection_slug')
    
#     list_filter = ('id_collection',)
    
#     search_fields = ('id_collection__title', 'id_collection__slug')

#     def get_collection_slug(self, obj):
#         return obj.collection.slug if obj.id_collection else "⚠️ SIN COLECCIÓN"
#     get_collection_slug.short_description = 'Collection Slug'


# @admin.register(Video)
# class VideoAdmin(admin.ModelAdmin):
#     list_display = ('id', 'id_collection')
#     list_filter = ('id_collection',)
    
# class VideoInline(admin.TabularInline):
#     model = Video
#     extra = 0
#     readonly_fields = ('id_collection', 'width', 'height', 'duration', 'preview')
#     fields = ('id_collection', 'file', 'width', 'height', 'duration', 'preview')
#     classes = ('collapse', 'open')
#     list_display = ('id_collection', 'collection.slug')

#     def preview(self, obj):
#         if obj.file:
#             return format_html(
#                 '''<video src="{}" style="width: 150px; height: auto; border-radius: 4px;" 
#                    controls muted preload="metadata">
#                    </video>''', 
#                 obj.file.url
#             )
#         return ""
    