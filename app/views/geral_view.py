from django.shortcuts import render
from django.core.paginator import Paginator
from app.forms import PokemonSearchForm
from app.forms import ComparePokemonForm
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

# def select_pokemon(request):
#     all_pokemons = PokemonManager.get_all_pokemons()
#     choices = [(str(p.number), f"#{p.number} - {p.name}") for p in all_pokemons]

#     if request.method == "POST":
#         form = ComparePokemonForm(request.POST)
#         form.fields['pokemons'].choices = choices

#         if form.is_valid():
#             selected_ids = form.cleaned_data['pokemons']
#             return compare_pokemon(request, selected_ids)  # call directly or redirect with params
#     else:
#         form = ComparePokemonForm()
#         form.fields['pokemons'].choices = choices

#     return render(request, 'select_pokemon_form.html', {'form': form})

# def compare_pokemon(request, selected_ids=None):
#     if not selected_ids:
#         selected_ids = request.GET.getlist('pokemon_ids')
#     selected_ids = [int(pid) for pid in selected_ids if str(pid).isdigit()][:5]

#     pokemons = PokemonManager.get_pokemon_with_physical_info(selected_ids)

#     return render(request, 'compare_pokemon.html', {
#         'pokemons': pokemons
#     })

def compare_and_select_pokemon(request):
    form = ComparePokemonForm()
    selected_ids = []

    if request.method == "POST":
        selected_str = request.POST.get("pokemons", "")
        selected_ids = selected_str.split(",") if selected_str else []
        selected_ids = [int(pid) for pid in selected_ids if pid.isdigit()]
        print("🧪 Selected IDs:", selected_ids)

    pokemons = []
    if selected_ids:
        pokemons = PokemonManager.get_pokemon_with_physical_info(selected_ids)

    # Apply height scaling
    SCALE = 100  # 1 meter = 100px
    print("SCALE:", SCALE)
    for p in pokemons:
        try:
            p.scaled_height = f"{int(float(p.height) * SCALE)}px" if p.height is not None else "100px"
        except Exception as e:
            print(f"⚠️ Error scaling {p.name} height ({p.height}):", e)
            p.scaled_height = "200px"

    return render(request, 'compare_pokemon.html', {
        'form': form,
        'pokemons': pokemons
    })

def pokemon_stats(request, pokemon_id):
    stats = PokemonManager.get_stats_by_id(pokemon_id)
    if stats is None:
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

    return render(request, 'stats.html', {
        'stats': stats
    })