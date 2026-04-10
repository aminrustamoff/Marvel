from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return render(request, 'core/main.html')

def listening(request):
    return render(request, 'core/listening.html')

def reading(request):
    return render(request, 'core/reading.html')
