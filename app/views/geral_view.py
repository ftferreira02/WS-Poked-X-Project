from django.shortcuts import render
from app.forms import PokemonSearchForm
from app.sparql_client import run_query
from app.models.geral_model import PokemonManager


POKEMON_TYPES = [
    'normal', 'fire', 'water', 'electric', 'grass', 'ice',
    'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug',
    'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'
]

def search_pokemon(request):
    form = PokemonSearchForm(request.GET or None)
    name_filter = request.GET.get("name", "").strip()
    type_filter = request.GET.get("type", "").strip().lower()
    pokemons = []

    if form.is_valid():
        name_filter = form.cleaned_data.get('name', '').strip()

    if name_filter and type_filter:
        pokemons = PokemonManager.search_by_name_and_type(name_filter, type_filter)
    elif name_filter:
        pokemons = PokemonManager.search_by_name(name_filter)
    elif type_filter:
        pokemons = PokemonManager.search_by_type(type_filter)
    else:
        pokemons = PokemonManager.get_all_pokemons()

    context = {
        'form': form,
        'pokemons': pokemons,
        'name_filter': name_filter,
        'active_type': type_filter, 
        'pokemon_types': POKEMON_TYPES,
    }

    return render(request, 'pokemon_search_form.html', context)


def pokemon_stats(request, pokemon_id):
    stats = PokemonManager.get_stats_by_id(pokemon_id)
    if stats is None:
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

    return render(request, 'stats.html', {
        'stats': stats
    })