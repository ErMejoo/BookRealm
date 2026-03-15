from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Follow
from datetime import datetime

# Create your views here.
def home(request):
    response = render(request, 'bookrealm/home.html')
    return response

def browse(request):
    response = render(request, 'bookrealm/browse.html')
    return response

@login_required
def follow_user(request, user_id):
    user_to_follow = User.objects.get(id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect(reverse('BookRealm:browse'))

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect(reverse('BookRealm:browse'))