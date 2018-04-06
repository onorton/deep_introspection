from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

@csrf_exempt
def index(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        if User.objects.filter(username=body['username']).count() != 0:
            return HttpResponse("{}",status=409)

        user = User.objects.create_user(body['username'], password=body['password'])
        user.save()
        login(request, user)
        return HttpResponse("{\"user\": " + str(user.id) + "}")

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return HttpResponse("{\"user\": " + str(request.user.id) + "}")

        body = json.loads(request.body.decode("utf-8"))
        username = body['username']
        password = body['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("{\"user\": " + str(user.id) + "}")
        else:
            return HttpResponse("{}", status=400)

@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponse("{}")
