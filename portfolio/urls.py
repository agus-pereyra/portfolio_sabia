from django.urls import path
from .views import CollectionDetailView, HomeView, about, collections_list

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('albums/', collections_list, name='collections_list'),
    path('albums/detail/<slug:slug>/', CollectionDetailView.as_view(), name='collection_detail'),
    path('about/', about, name='about'),
]