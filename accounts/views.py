from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


import sys

def persona_login(request):
    user = authenticate(assertion=request.POST['assertion'])
    if user:
        login(request, user)
    return HttpResponse('OK')

def persona_logout(request):
    request.POST['assertion'] = None

