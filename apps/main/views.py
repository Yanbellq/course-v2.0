from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

def dashboard(request):
    return render(request, 'user/index.html')

def auth(request):
    return render(request, 'user/auth.html')

def categories(request):
    return render(request, 'user/categories.html')
