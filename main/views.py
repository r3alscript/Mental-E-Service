from django.shortcuts import render
import requests

def Home(request):
    return render(request, 'main/index.html')