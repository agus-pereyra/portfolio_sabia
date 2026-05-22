from .models import Collection

def global_side_menu(request):
    menu_items = (
        Collection.objects
        .select_related('cover', 'cover_video')
        .order_by('-captured_at')
    )
    return {'menu_collections': menu_items}