from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from app.models.fight.fight_model import PokemonManager

def battle(request, pokemon_id1, pokemon_id2):
    # Obter os detalhes dos dois Pokémons
    pokemon1 = PokemonManager.get_stats_by_id(pokemon_id1)
    pokemon2 = PokemonManager.get_stats_by_id(pokemon_id2)
    
    if not pokemon1 or not pokemon2:
        return HttpResponse("Erro: Pokémon não encontrado.", status=404)
    
    # Calcula as fraquezas de cada Pokémon contra o outro
    weakness1 = pokemon2.get_weakness(pokemon1.primary_type)  # Fraqueza do pokemon2 contra o pokemon1
    weakness2 = pokemon1.get_weakness(pokemon2.primary_type)  # Fraqueza do pokemon1 contra o pokemon2

    # Calcula o dano com base na fraqueza, defesa e ataque
    damage_to_pokemon1 = (pokemon2.attack * weakness1) - pokemon1.defense
    damage_to_pokemon2 = (pokemon1.attack * weakness2) - pokemon2.defense
    
    # Calcula a saúde restante após o dano
    health_left_pokemon1 = max(0, pokemon1.health - damage_to_pokemon1)
    health_left_pokemon2 = max(0, pokemon2.health - damage_to_pokemon2)
    
    # Determina o vencedor
    if health_left_pokemon1 > health_left_pokemon2:
        winner = pokemon1.name
        result = f"{pokemon1.name} venceu a batalha!"
    elif health_left_pokemon1 < health_left_pokemon2:
        winner = pokemon2.name
        result = f"{pokemon2.name} venceu a batalha!"
    else:
        result = "A batalha terminou em empate!"
    
    # Retorna uma resposta em texto simples
    response_text = (
        f"Batalha entre {pokemon1.name} e {pokemon2.name}:\n\n"
        f"{pokemon1.name} - Saúde restante: {health_left_pokemon1}\n"
        f"{pokemon2.name} - Saúde restante: {health_left_pokemon2}\n\n"
        f"{result}"
    )
    
    return HttpResponse(response_text)
