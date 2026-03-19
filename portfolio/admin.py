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
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [PictureInline, VideoInline]
    filter_horizontal = ('collaborators',)

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'role', 'genre')
    list_filter = ('genre', 'role')

admin.site.register(Picture)
admin.site.register(Video)