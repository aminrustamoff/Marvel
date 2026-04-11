from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import ListeningTest

# Create your views here.

def home(request):
    return render(request, 'core/main.html')

def listening(request, pk):
    test = get_object_or_404(ListeningTest, pk=pk)
    return render(request, 'core/listening.html', {'test' : test})

def reading(request):
    return render(request, 'core/reading.html')

# def get_duration_display(self):
#     if self.duration:
#         mins, secs = divmod(self.duration, 60)
#         return f"{mins}:{secs:02d}"
#     return "0:00"

