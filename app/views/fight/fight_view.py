from django.shortcuts import render, redirect
from app.models.fight.fight_model import PokemonFight
from app.models.fight.battle_queries import save_battle_result, get_battle_history
import json
from app.forms import PokemonSelectionForm
from app.models.geral_model import PokemonManager
from app.models.fight.battle_queries import delete_battle
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils.http import urlencode
from app.sparql_client import run_query


def pokemon_selection_view(request):
    """View for selecting Pokémon to battle"""
    form = PokemonSelectionForm()
    
    if request.method == 'POST':
        form = PokemonSelectionForm(request.POST)
        if form.is_valid():
            # Get the selected Pokémon IDs from hidden fields
            pokemon1_id = form.cleaned_data['pokemon1_id']
            pokemon2_id = form.cleaned_data['pokemon2_id']
            
            # Redirect to the battle view with the selected Pokémon
            return redirect('pokemon_battle', pokemon1_id=pokemon1_id, pokemon2_id=pokemon2_id)
    
    # Get all Pokémon for JavaScript
    all_pokemons = PokemonManager.get_all_pokemons()
    pokemon_data = []
    
    # Get strong Pokemon data using inferred pdx:isStrong property
    strong_pokemon_query = """
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    SELECT ?pokemon ?name WHERE {
        ?pokemon pdx:isStrong true ;
                 sc:name ?name .
    }
    """
    strong_results = run_query(strong_pokemon_query)
    strong_pokemon_names = set()
    if strong_results and "results" in strong_results and "bindings" in strong_results["results"]:
        for binding in strong_results["results"]["bindings"]:
            if "name" in binding:
                strong_pokemon_names.add(binding["name"]["value"])
    
    # Add isStrong flag to pokemon data
    for p in all_pokemons:
        pokemon_data.append({
            'id': p.id,
            'name': p.name,
            'number': p.number,
            'isStrong': p.name in strong_pokemon_names
        })
    
    return render(request, 'pokemon_selection.html', {
        'form': form,
        'pokemon_data_json': json.dumps(pokemon_data)
    })

def pokemon_battle_view(request, pokemon1_id="0", pokemon2_id="1", simulate="true"):
    """View for the actual battle simulation"""

    simulate = request.GET.get("simulate", "true").lower() == "true"


    # Create fight with selected Pokémon
    fight = PokemonFight(pokemon1_id, pokemon2_id)

    battle_logs = []
    hp_progress = []

    # Initial message
    battle_logs.append("A wild Pokémon appeared...")

    # Battle simulation
    while not fight.is_battle_over():
        fight.execute_turn()
        battle_logs.extend(fight.logs[-2:])  # Two attacks per turn
        hp_progress.append({
            "hp1": fight.current_hp1,
            "hp2": fight.current_hp2,
        })

    # Initial HP state
    hp_progress.insert(0, {
        "hp1": fight.pokemon1["hp"],
        "hp2": fight.pokemon2["hp"]
    })

    battle_history = get_battle_history()
    print("Debug - Battle History:", battle_history)  # Debug output
    for battle in battle_history:
        print(f"Debug - Battle entry: {battle}")  # Debug each entry

    # Save the final result
    if simulate:
        # Save battle result in the RDF database
        save_battle_result(fight.pokemon1, fight.pokemon2, fight.winner)

    # Template context
    context = {
        "pokemon1": fight.pokemon1,
        "pokemon2": fight.pokemon2,
        "logs": battle_logs,
        "hp_progress": hp_progress,
        "winner": fight.winner["name"],
        "logs_json": json.dumps(battle_logs),
        "hp_progress_json": json.dumps(hp_progress),
        "battle_history": battle_history
    }

    return render(request, "fight.html", context)

@csrf_exempt
def delete_battle_view(request, battle_id):
    print(f"Debug - Received battle_id: {battle_id}")
    print(f"Debug - Request method: {request.method}")
    print(f"Debug - GET params: {request.GET}")
    
    pokemon1_id = request.GET.get('pokemon1_id')
    pokemon2_id = request.GET.get('pokemon2_id')

    print(f"Debug - Pokemon IDs: {pokemon1_id}, {pokemon2_id}")

    if request.method == "POST":
        print(f"Debug - Deleting battle with ID: {battle_id}")
        delete_battle(battle_id)

    if pokemon1_id and pokemon2_id:
        base_url = reverse('pokemon_battle', kwargs={'pokemon1_id': pokemon1_id, 'pokemon2_id': pokemon2_id})
        query_string = urlencode({'simulate': 'false'})
        url = f"{base_url}?{query_string}"
        print(f"Debug - Redirecting to: {url}")
        return redirect(url)
    else:
        print("Debug - Redirecting to pokemon selection")
        return redirect('pokemon_selection')
