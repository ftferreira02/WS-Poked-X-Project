from django.shortcuts import render
from django.core.paginator import Paginator
from app.forms import PokemonSearchForm
from app.sparql_client import run_query
from app.models.geral_model import PokemonManager
from django.views.decorators.csrf import csrf_exempt

# Lista de tipos para o dropdown de filtros.
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

    # Se o formulário for válido, atualiza o name_filter (caso use o campo "name" do form).
    if form.is_valid():
        name_filter = form.cleaned_data.get('name', '').strip()

    # Lógica de busca combinando nome e tipo
    if name_filter and type_filter:
        pokemons = PokemonManager.search_by_name_and_type(name_filter, type_filter)
    elif name_filter:
        pokemons = PokemonManager.search_by_name(name_filter)
    elif type_filter:
        pokemons = PokemonManager.search_by_type(type_filter)
    else:
        pokemons = PokemonManager.get_all_pokemons()

    # Ordenação
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

    # Paginação (exemplo: 40 Pokémon por página)
    paginator = Paginator(pokemons, 40)
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
