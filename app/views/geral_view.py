from django.shortcuts import render
from app.forms import PokemonSearchForm
from app.sparql_client import run_query
from app.models.geral_model import PokemonManager
from django.views.decorators.csrf import csrf_exempt

def search_pokemon(request):
    pokemons = []
    name_filter = ''
    
    # Instanciando o formulário
    form = PokemonSearchForm(request.GET)
    
    if form.is_valid():
        name_filter = form.cleaned_data['name']
        
        if name_filter:
            pokemons = PokemonManager.search_by_name(name_filter)
        else:
            pokemons = PokemonManager.get_all_pokemons()
        
    return render(request, 'search.html', {'form': form, 'pokemons': pokemons})


def pokemon_stats(request, pokemon_id):
    stats = PokemonManager.get_stats_by_id(pokemon_id)
    if stats is None:
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

    return render(request, 'stats.html', {
        'stats': stats
    })
    
@csrf_exempt
def ask_pokemon_question(request):
    all_pokemon = PokemonManager.get_all_pokemons()
    pokemon_names = [p.name for p in all_pokemon]

    color_class = ""
    result_text = None
    pokemon_name = ""
    property_uri = ""
    value_uri = ""

    if request.method == "POST":
        pokemon_name = request.POST.get("pokemon", "").strip()
        property_uri = request.POST.get("property", "").strip()
        value_uri = request.POST.get("value", "").strip()

        if pokemon_name and property_uri and value_uri:
            is_true = PokemonManager.ask_question_about_pokemon(pokemon_name, property_uri, value_uri)
            if is_true:
                color_class = "result-true"
                result_text = "Yes, that is correct!"
            else:
                color_class = "result-false"
                result_text = "No, that is incorrect."

    return render(request, "ask_question.html", {
        "all_pokemon_names": pokemon_names,
        "result_text": result_text,
        "color_class": color_class,
        "pokemon": pokemon_name,
        "property_uri": property_uri,
        "value_uri": value_uri
    })