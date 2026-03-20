from .models import Collaborator, Collection, Picture, Video
from django.views.generic import DetailView, ListView
from django.shortcuts import render

def about(request):
    return render(request, 'about.html')

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
        return context

    def get_queryset(self):
            return Collection.objects.filter(is_featured=True).order_by('-captured_at')