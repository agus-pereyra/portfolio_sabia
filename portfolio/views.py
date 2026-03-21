from .models import Collection, Picture, Video
from django.views.generic import DetailView, ListView
from django.shortcuts import render
import random

def about(request):
    return render(request, 'about.html')

def collections_list(request):
    year = request.GET.get('year')

    if year:
        collections = Collection.objects.filter(captured_at__year=year).order_by('-captured_at')
    else:
        collections = Collection.objects.all().order_by('-captured_at')
    
    years = Collection.objects.dates('captured_at', 'year', order='DESC')

    return render(request, 'portfolio/collections_list.html', {
        'collections': collections,
        'years': years,
        'active_year': year,
    })

def get_random_media(request):
    pictures = list(Picture.objects.all().order_by('?')[:12])
    videos = list(Video.objects.all().order_by('?')[:3])

    for p in pictures:
        p.media_type = 'picture'
    for v in videos:
        v.media_type = 'video'
        
    random_media = pictures + videos
    random.shuffle(random_media)

    return render(request, 'portfolio/includes/picture_grid_items.html', {'random_media': random_media})

class CollectionDetailView(DetailView):
    model = Collection
    template_name = 'portfolio/collection_detail.html'
    context_object_name = 'collection'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections_all'] = Collection.objects.all().order_by('-captured_at')
        return context

class HomeView(ListView):
    model = Collection
    template_name = 'portfolio/index.html'
    context_object_name = 'collections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections_all'] = Collection.objects.all().order_by('-captured_at')
        
        pictures = list(Picture.objects.all().order_by('?')[:12])
        videos = list(Video.objects.all().order_by('?')[:3])

        for p in pictures:
            p.media_type = 'picture'
        for v in videos:
            v.media_type = 'video'
            
        random_media = pictures + videos
        random.shuffle(random_media)

        context['random_media'] = random_media
        return context

    def get_queryset(self):
            return Collection.objects.filter(is_featured=True).order_by('-captured_at')