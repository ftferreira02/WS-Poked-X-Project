from django.shortcuts import render
from django.core.paginator import Paginator
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
    sort_option = request.GET.get("sort", "")
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

    if sort_option == "name_asc":
        pokemons.sort(key=lambda p: p.name.lower())
    elif sort_option == "name_desc":
        pokemons.sort(key=lambda p: p.name.lower(), reverse=True)
    elif sort_option == "id_asc":
        pokemons.sort(key=lambda p: p.number)
    elif sort_option == "id_desc":
        pokemons.sort(key=lambda p: p.number, reverse=True)
    elif sort_option == "exp_asc":
        pokemons.sort(key=lambda p: p.exp if p.exp is not None else 0)
    elif sort_option == "exp_desc":
        pokemons.sort(key=lambda p: p.exp if p.exp is not None else 0, reverse=True)

    # 👉 PAGINATION
    paginator = Paginator(pokemons, 40)  # 20 Pokémon per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'pokemons': page_obj,
        'page_obj': page_obj,
        'name_filter': name_filter,
        'active_type': type_filter, 
        'sort_option': sort_option,
        'pokemon_types': POKEMON_TYPES,
    }

    return render(request, 'pokemon_search_form.html', context)

def scale_visualization(request):
    selected_ids = request.GET.getlist('pokemon_ids')  # list of numbers or IDs
    selected_ids = [int(pid) for pid in selected_ids if pid.isdigit()][:5]  # limit to 5

    pokemons = PokemonManager.get_pokemon_with_physical_info(selected_ids)

    return render(request, 'scale_view.html', {
        'pokemons': pokemons
    })


def pokemon_stats(request, pokemon_id):
    stats = PokemonManager.get_stats_by_id(pokemon_id)
    if stats is None:
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

    return render(request, 'stats.html', {
        'stats': stats
    })