from django.urls import path
from .views import CollectionDetailView, HomeView, about

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('collection/<slug:slug>/', CollectionDetailView.as_view(), name='collection_detail'),
    path('about/', about, name='about'),
]