from django.http import HttpResponse
from app.models.fight.fight_model import FightManager, PokemonFight

def pokemon_battle(request):
    charizard_id = "6"
    charmander_id = "4"
    
    fight = PokemonFight(charizard_id, charmander_id)
    text = []

    def format_pokemon_info(pokemon, current_hp):
        return (
            f"ID: {pokemon['id']}\n"
            f"Nome: {pokemon['name']}\n"
            f"HP: {current_hp}/{pokemon['hp']}\n"
            f"Tipo Primário: {pokemon.get('primaryType', 'Desconhecido')}\n"
            f"Tipo Secundário: {pokemon.get('secondaryType') or 'Nenhum'}\n"
            f"Stats:\n"
            f"  - Ataque: {pokemon['attack']}\n"
            f"  - Defesa: {pokemon['defense']}\n"
            f"  - Ataque Especial: {pokemon['spAttack']}\n"
            f"  - Defesa Especial: {pokemon['spDefense']}\n"
            f"  - Velocidade: {pokemon['speed']}\n"
        )

    text.append("⚔️ INÍCIO DA BATALHA")
    text.append("\n🔹 Pokémon 1:")
    text.append(format_pokemon_info(fight.pokemon1, fight.current_hp1))
    
    text.append("🔸 Pokémon 2:")
    text.append(format_pokemon_info(fight.pokemon2, fight.current_hp2))
    
    turn = 1
    while not fight.is_battle_over():
        fight.execute_turn()
        turn_logs = fight.logs[-2:] if len(fight.logs) >= 2 else fight.logs
        
        text.append(f"\n🔁 TURNO {turn}")
        for log in turn_logs:
            text.append(f"  {log}")
        text.append(
            f"  {fight.pokemon1['name']} HP: {fight.current_hp1}/{fight.pokemon1['hp']}\n"
            f"  {fight.pokemon2['name']} HP: {fight.current_hp2}/{fight.pokemon2['hp']}"
        )
        turn += 1

    text.append("\n🏁 FIM DA BATALHA")
    text.append(f"🏆 Vencedor: {fight.winner['name']}")
    
    return HttpResponse("\n".join(text), content_type="text/plain")
