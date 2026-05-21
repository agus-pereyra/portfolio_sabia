from django.urls import path
from .views import CollectionDetailView, HomeView, about, collections_list, get_random_media

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('', collections_list, name='collection_list'),
    path('albums/detail/<slug:slug>/', CollectionDetailView.as_view(), name='collection_detail'),
    path('about/', about, name='about'),
    path('get-random-media/', get_random_media, name='get_random_media')
]