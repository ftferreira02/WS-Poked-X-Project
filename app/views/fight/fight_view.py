from django.shortcuts import render
from app.models.fight.fight_model import PokemonFight
from app.models.fight.battle_queries import save_battle_result, get_battle_history
import json

def pokemon_battle_view(request):
    # Pokémon padrão (Charizard vs Charmander)
    fight = PokemonFight("4", "6")

    battle_logs = []
    hp_progress = []

    # Mensagem inicial
    battle_logs.append("A wild Pokémon appeared...")

    # Simulação da batalha
    while not fight.is_battle_over():
        fight.execute_turn()
        battle_logs.extend(fight.logs[-2:])  # Dois ataques por turno
        hp_progress.append({
            "hp1": fight.current_hp1,
            "hp2": fight.current_hp2,
        })

    # Estado inicial dos HP
    hp_progress.insert(0, {
        "hp1": fight.pokemon1["hp"],
        "hp2": fight.pokemon2["hp"]
    })

    # Guardar resultado final
    save_battle_result(fight.pokemon1, fight.pokemon2, fight.winner)

    # Buscar histórico
    battle_history = get_battle_history()

    # Contexto do template
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
