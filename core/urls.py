from django.urls import path #type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('main/', views.main, name='main'),
    path('main/listening/<int:pk>', views.listening, name='listening'),
    path('main/reading/<int:pk>', views.reading, name='reading'),
    path('api/submit/', views.SubmitListeningAnswersView.as_view(), name='submit-answers'),
    path('results/<str:session_id>/', views.view_results, name='view-results'),
]