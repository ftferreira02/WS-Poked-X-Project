# Mapping/routing das URLs para este projeto.
from django.http import HttpResponse
from django.urls import path
from app.Views.stats.stats_view import stats_page

def home(request):
    return HttpResponse("Django está a funcionar!")

urlpatterns = [
    path('', home),
    path('stats/', stats_page, name='stats'),
]
