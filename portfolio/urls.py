from django.urls import path
from .views import CollectionDetailView, HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('collection/<slug:slug>/', CollectionDetailView.as_view(), name='collection_detail'),   
]