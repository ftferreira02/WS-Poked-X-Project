from django.shortcuts import render, redirect
from app.models.fight.fight_model import PokemonFight
from app.models.fight.battle_queries import save_battle_result, get_battle_history
import json
from app.forms import PokemonSelectionForm
from app.models.geral_model import PokemonManager

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
    pokemon_data = [{'id': p.id, 'name': p.name, 'number': p.number} for p in all_pokemons]
    
    return render(request, 'pokemon_selection.html', {
        'form': form,
        'pokemon_data_json': json.dumps(pokemon_data)
    })

def pokemon_battle_view(request, pokemon1_id="0", pokemon2_id="1"):
    """View for the actual battle simulation"""
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

    # Save the final result
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