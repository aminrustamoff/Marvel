from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("<h1><b>Hello, World!</b></h1>")