# Mapping/routing das URLs para este projeto.
from django.http import HttpResponse
from django.urls import path

def home(request):
    return HttpResponse("Django está a funcionar!")

urlpatterns = [
    path('', home),
]
