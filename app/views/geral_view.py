from django.shortcuts import render
from app.forms import PokemonSearchForm
from app.sparql_client import run_query
from app.models.geral_model import PokemonManager

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
        
    return render(request, 'pokemon_search_form.html', {'form': form, 'pokemons': pokemons})


def pokemon_stats(request, pokemon_id):
    stats = PokemonManager.get_stats_by_id(pokemon_id)

    if stats is None:
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

    return render(request, 'stats.html', {
        'stats': stats
    })