from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listening', views.listening, name='listening'),
    path('reading', views.reading, name='reading'),
]