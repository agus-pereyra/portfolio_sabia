from .models import Collection

def global_side_menu(request):
    menu_items = Collection.objects.all().order_by('-captured_at')
    
    return {'menu_collections': menu_items}