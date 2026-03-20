from django.contrib import admin

from .models import Collaborator, Collection, Picture, Video

class PictureInline(admin.TabularInline):
    model = Picture
    extra = 3 # espacios vacíos a mostrar por defecto
    readonly_fields = ('width', 'height')

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

    def get_photos_count(self, obj):
        return obj.get_photos_count()
    get_photos_count.short_description = "Fotos"

    def get_videos_count(self, obj):
        return obj.get_videos_count()
    get_videos_count.short_description = "Videos"

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'genre')
    list_filter = ('genre', 'role')

admin.site.register(Picture)
admin.site.register(Video)