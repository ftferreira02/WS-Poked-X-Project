from django.shortcuts import render
from django.core.paginator import Paginator
from app.forms import PokemonSearchForm
from app.forms import ComparePokemonForm
from app.sparql_client import run_query, run_construct_query
from app.models.geral_model import PokemonManager
import math
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.http import JsonResponse
from app.sparql_client import dbpedia_data_already_loaded


# Lista de tipos para o dropdown de filtros.
POKEMON_TYPES = [
    'normal', 'fire', 'water', 'electric', 'grass', 'ice',
    'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug',
    'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'
]

# New categories based on inferred classes and SPIN rules
POKEMON_CATEGORIES = {
    'dual_type': 'Dual Type',
    'glass_cannon': 'Glass Cannon',
    'legendary': 'Legendary',
    'mega': 'Mega Evolution',
    'strong': 'Strong',
    'old_gen': 'Old Generation'
}

def search_pokemon(request):
    form = PokemonSearchForm(request.GET or None)
    name_filter = request.GET.get("name", "").strip()
    type_filter = request.GET.get("type", "").strip().lower()
    category_filter = request.GET.get("category", "").strip().lower()
    sort_option = request.GET.get("sort", "")
    pokemons = []

    # Se o formulário for válido, atualiza o name_filter (caso use o campo "name" do form).
    if form.is_valid():
        name_filter = form.cleaned_data.get('name', '').strip()

    # Lógica de busca combinando nome, tipo e categoria
    if category_filter:
        pokemons = PokemonManager.search_by_category(category_filter)
        if name_filter or type_filter:
            # Filter the category results further if name or type filters are present
            if name_filter:
                pokemons = [p for p in pokemons if name_filter.lower() in p.name.lower()]
            if type_filter:
                pokemons = [p for p in pokemons if p.primary_type == type_filter or 
                           (p.secondary_type and p.secondary_type == type_filter)]
    elif name_filter and type_filter:
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
        'active_category': category_filter,
        'sort_option': sort_option,
        'pokemon_types': POKEMON_TYPES,
        'pokemon_categories': POKEMON_CATEGORIES,
    }

    return render(request, 'pokemon_search_form.html', context)

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

    max_height = max([p.height for p in pokemons if p.height], default=1.0)

    MAX_DISPLAY_HEIGHT_PX = 400  # max height in pixels for tallest Pokémon

    for p in pokemons:
        if p.height:
            scale = MAX_DISPLAY_HEIGHT_PX / max_height
            p.scaled_height = f"{int(p.height * scale)}px"
        else:
            p.scaled_height = "100px"

    
    # Round up to nearest multiple of 5 for cleaner ruler
    rounded_max = math.ceil(max_height / 5.0) * 5
    tick_interval = rounded_max // 5  # 5 ticks total
    ticks = list(range(0, rounded_max + 1, tick_interval))

    tick_height_px = lambda value: (value / max_height) * MAX_DISPLAY_HEIGHT_PX

    tick_data = [{
        "label": tick,
        "top_px": MAX_DISPLAY_HEIGHT_PX - tick_height_px(tick)
    } for tick in ticks]

    return render(request, 'compare_pokemon.html', {
        'form': form,
        'pokemons': pokemons,
        'tick_data': tick_data,
        'max_display_height': MAX_DISPLAY_HEIGHT_PX,
        'max_pokemon_height': max_height,
        'selected_pokemons': pokemons
    })

def export_pokemon_rdf(request, pokemon_id):
    query = PokemonManager.get_construct_rdf_query_by_id(pokemon_id)
    rdf_data = run_construct_query(query)
    return HttpResponse(rdf_data, content_type="text/turtle")

TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0", "electric": "#F8D030",
    "grass": "#78C850", "ice": "#98D8D8", "fighting": "#C03028", "poison": "#A040A0",
    "ground": "#E0C068", "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8", "dark": "#705848",
    "steel": "#B8B8D0", "fairy": "#EE99AC"
}

def all_evolution_chains(request):
    chains = PokemonManager.get_all_evolution_chains()
    
    nodes = []
    edges = []

    for chain in chains:
        for p in chain:
            color = TYPE_COLORS.get(p['primary_type'], '#ccc')
            nodes.append({
                "id": p["id"],
                "label": f"#{p['number']} {p['name']}",
                "shape": "image",
                "image": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p['number']}.png",
                "title": f"{p['name']} {p['primary_type'].capitalize()}",
                "color": {
                    "border": color,
                    "background": "white",
                    "highlight": {"border": color, "background": "#f8f8f8"}
                }
            })

        for i in range(len(chain) - 1):
            edges.append({
                "from": chain[i]["id"],
                "to": chain[i+1]["id"]
            })
    print("🧪 Nodes:", nodes)
    context = {
        
        "nodes_json": json.dumps(list(nodes)),
        "edges_json": json.dumps(edges)
        
    }
    return render(request, 'evolution_chain.html', context)



  
def pokemon_stats(request, pokemon_id):
    # First, check if the Pokemon exists
    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    ASK {{
        <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> a pdx:Pokemon .
    }}
    """
    exists = run_query(query)
    if not exists.get("boolean", False):
        return render(request, 'stats.html', {'error': 'Pokémon not found.'})

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

def check_dbpedia_status(request, name):
    exists = dbpedia_data_already_loaded(name)
    return JsonResponse({"name": name, "exists": exists})

