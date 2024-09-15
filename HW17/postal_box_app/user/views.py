from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/user')
        else:
            return HttpResponse('Invalid login details')
    return render(request, 'login.html', context=context)

def register(request):
    return HttpResponse("Register Page")

def logout_view(request):
    logout(request)
    return redirect('/login/')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()
        return redirect('/login')
    else:
        return render(request, 'register.html')

def user_page(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'user_page.html', context)
