# app/views/fight/fight_view.py
from django.http import JsonResponse
from django.http import HttpResponse
from app.sparql_client import run_query

def search_pokemon(request):
    query = """
    PREFIX ex: <http://example.org/pokemon/>

    SELECT ?pokemon WHERE {
      ?pokemon a ex:Pokemon .
    }
    """
    results = run_query(query)

    pokemons = [binding["pokemon"]["value"] for binding in results["results"]["bindings"]]
    return JsonResponse({"results": pokemons})

