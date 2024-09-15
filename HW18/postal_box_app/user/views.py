from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from user.forms import LoginForm, RegisterForm


def login_view(request):
    context = {}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect('/user')
        else:
            return HttpResponse('Invalid login details')
    context['login_form'] = LoginForm
    return render(request, 'login.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('/login/')

def register_view(request):
    context = {}
    if request.method == 'POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"],
                                password=form.cleaned_data["password"],
                                last_name=form.cleaned_data["last_name"],
                                first_name=form.cleaned_data["first_name"],
                                email=form.cleaned_data["email"])
            user.save()
            return redirect('/login')
    else:
        context['reg_form'] = RegisterForm
        return render(request, 'register.html', context=context)

def user_page(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'user_page.html', context)
