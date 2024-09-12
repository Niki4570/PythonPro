from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, 'home.html')

def login(request):
    return HttpResponse("Login Page")

def register(request):
    return HttpResponse("Register Page")
