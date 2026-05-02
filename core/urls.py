from django.urls import path #type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('main/', views.main, name='main'),
    path('main/listening/<int:pk>', views.listening, name='listening'),
    path('main/reading/<int:pk>', views.reading, name='reading'),
    path('main/writing/<int:pk1>/<int:pk2>', views.writing, name='writing'),
    path('api/submit/listening/', views.SubmitListeningAnswersView.as_view(), name='submit-answers-listening'),
    path('api/submit/reading/', views.SubmitReadingAnswersView.as_view(), name='submit-answers-reading'),
    path('api/submit/writing/', views.SubmitWritingAnswersView.as_view(), name='submit-answers-writing'),
    path('results/', views.view_results, name='view_results'),
    path('results/<str:session_id>/', views.view_results_detail, name='view_results_detail'),
    path('student-result/<str:session_id>/', views.student_full_result, name='student_full_result'),
    path('results/<int:session_id>/download-pdf/', views.download_session_pdf, name='download_session_pdf'),
]