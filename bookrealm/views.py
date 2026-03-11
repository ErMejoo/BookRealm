from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.
def home(request):
    response = render(request, 'bookrealm/home.html')
    return response

def browse(request):
    response = render(request, 'bookrealm/browse.html')
    return response