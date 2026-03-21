from django.urls import path
from .views import contact_view


urlpatterns = [
    path('submit/', contact_view, name='contact_submit'),
]