from django.shortcuts import render
from app.models.fight.fight_model import PokemonFight
import json

def pokemon_battle_view(request):
    fight = PokemonFight("6", "4")  # Charizard vs Charmander
    battle_logs = []
    hp_progress = []

    battle_logs.append("A wild Pokemon appeared...")


    while not fight.is_battle_over():
        fight.execute_turn()
        # Guardamos cada turno como tu queres: um ataque de cada vez
        battle_logs.extend(fight.logs[-2:])  # Ataques desse turno
        hp_progress.append({
            "hp1": fight.current_hp1,
            "hp2": fight.current_hp2,
        })
    
    hp_progress.insert(0, {
        "hp1": fight.pokemon1["hp"],
        "hp2": fight.pokemon2["hp"]
    })

    # Enhanced context with all the data needed by the template
    context = {
        "pokemon1": fight.pokemon1,
        "pokemon2": fight.pokemon2,
        "logs": battle_logs,
        "hp_progress": hp_progress,
        "winner": fight.winner["name"]
    }
    

    context["logs_json"] = json.dumps(battle_logs)
    context["hp_progress_json"] = json.dumps(hp_progress)
    
    return render(request, "fight.html", context)