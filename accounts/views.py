import sys

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect


def login(request):
    print('login', file=sys.stderr)
    # user = PersonaAuthenticationBackend().authenticate(request.POST['assertion'])
    user = authenticate(request.POST['assertion'])
    if user is not None:
        auth_login(request, user)
    return redirect('/')


def logout(request):
    auth_logout(request)
    return redirect('/')


