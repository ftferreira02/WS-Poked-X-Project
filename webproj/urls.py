# webproj/urls.py
from django.contrib import admin
from django.urls import path
from app.views.geral_view import search_pokemon
from app.views.geral_view import pokemon_stats
from app.views.geral_view import compare_and_select_pokemon
from app.views.geral_view import ask_pokemon_question
from app.views.fight.fight_view import delete_battle_view, pokemon_battle_view
from app.views.fight.fight_view import pokemon_selection_view
from app.views.geral_view import export_pokemon_rdf
from app.views.geral_view import all_evolution_chains
from app.views.geral_view import check_dbpedia_status

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', search_pokemon, name='search_pokemon'),
    path('pokemon/stats/<int:pokemon_id>/', pokemon_stats, name='pokemon_stats'),
    path('battle/', pokemon_selection_view, name='battle'),
    path('battle/', pokemon_selection_view, name='pokemon_selection'),
    path('battle/<str:pokemon1_id>/<str:pokemon2_id>/', pokemon_battle_view, name='pokemon_battle'),
    path('fight/delete/<str:battle_id>/', delete_battle_view, name='delete_battle'),
    path('compare/', compare_and_select_pokemon, name='compare_pokemon'),
    path("pokemon/ask/", ask_pokemon_question, name="ask_question"),
    path('pokemon/export/id/<int:pokemon_id>/', export_pokemon_rdf, name='export_pokemon_rdf_by_id'),
    path('evolution/', all_evolution_chains, name='evolution_chain'),
    path("debug/dbpedia/<str:name>/", check_dbpedia_status, name='check_dbpedia_status'),




]



#ola

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