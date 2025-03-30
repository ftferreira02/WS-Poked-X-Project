# webproj/urls.py
from django.contrib import admin
from django.urls import path
from app.views.geral_view import search_pokemon
from app.views.geral_view import pokemon_stats
from app.views.fight.fight_view import pokemon_battle_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pokemon/search/', search_pokemon, name='search_pokemon'),
    path('stats/', pokemon_stats, name='stats'),
    path('battle/', pokemon_battle_view, name='battle'),
]



### codigo lia
# # Mapping/routing das URLs para este projeto.
# from django.http import HttpResponse
# from django.urls import path
# from app.Views.stats.stats_view import stats_page

# def home(request):
#     return HttpResponse("Django está a funcionar!")

# urlpatterns = [
#     path('', home),
#     path('stats/', stats_page, name='stats'),
# ]