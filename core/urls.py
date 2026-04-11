from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listening/<int:pk>', views.listening, name='listening'),
    path('reading', views.reading, name='reading'),
]