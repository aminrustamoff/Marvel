from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listening/<int:pk>', views.listening, name='listening'),
    path('reading', views.reading, name='reading'),
    path('api/submit/', views.SubmitAnswersView.as_view(), name='submit-answers'),
    path('results/<int:submission_id>', views.view_results, name='view-results'),
]