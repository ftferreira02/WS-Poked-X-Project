from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from app.models.fight.fight_model import PokemonManager as FightPokemonManager
from app.models.geral_model import PokemonManager as GeneralPokemonManager

def battle(request, pokemon_id1, pokemon_id2):
    # Obter os detalhes dos dois Pokémons usando o FightPokemonManager
    pokemon1 = FightPokemonManager.get_stats_by_id(pokemon_id1)
    pokemon2 = FightPokemonManager.get_stats_by_id(pokemon_id2)
    
    if not pokemon1 or not pokemon2:
        return HttpResponse("Erro: Pokémon não encontrado.", status=404)
    
    # Obter informações adicionais do GeneralPokemonManager
    pokemon1_general = GeneralPokemonManager.get_stats_by_id(pokemon_id1)
    pokemon2_general = GeneralPokemonManager.get_stats_by_id(pokemon_id2)
    
    # Complementar os objetos pokemon com as informações adicionais
    if pokemon1_general:
        pokemon1.name = pokemon1_general["name"]
        pokemon1.primary_type = pokemon1_general["primaryType"]
        pokemon1.secondary_type = pokemon1_general["secondaryType"]
        pokemon1.defense = pokemon1_general["defense"]
        pokemon1.health = pokemon1_general["hp"]
        # Adicionar habilidades (considerando que elas existam no modelo geral)
        pokemon1.ability1 = pokemon1_general.get("hability1", "Tackle")
        pokemon1.ability2 = pokemon1_general.get("hability2", None)
    
    if pokemon2_general:
        pokemon2.name = pokemon2_general["name"]
        pokemon2.primary_type = pokemon2_general["primaryType"]
        pokemon2.secondary_type = pokemon2_general["secondaryType"]
        pokemon2.defense = pokemon2_general["defense"]
        pokemon2.health = pokemon2_general["hp"]
        # Adicionar habilidades (considerando que elas existam no modelo geral)
        pokemon2.ability1 = pokemon2_general.get("hability1", "Tackle")
        pokemon2.ability2 = pokemon2_general.get("hability2", None)
    
    # Calcula as fraquezas de cada Pokémon contra o outro usando a função existente
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
        winner = None
        result = "A batalha terminou em empate!"
    
    # Preparar o contexto para o template
    context = {
        'pokemon1': {
            'name': pokemon1.name,
            'attack': pokemon1.attack,
            'defense': pokemon1.defense,
            'hp': pokemon1.health,
            'current_hp': health_left_pokemon1,
            'primary_type': pokemon1.primary_type,
            'secondary_type': pokemon1.secondary_type if pokemon1.secondary_type != 'None' else None,
            'ability1': pokemon1.ability1,
            'ability2': pokemon1.ability2,
            'sprite_url': f"http://img.pokemondb.net/sprites/black-white/anim/back-normal/{pokemon1.name.lower()}.gif"
        },
        'pokemon2': {
            'name': pokemon2.name,
            'attack': pokemon2.attack,
            'defense': pokemon2.defense,
            'hp': pokemon2.health,
            'current_hp': health_left_pokemon2,
            'primary_type': pokemon2.primary_type,
            'secondary_type': pokemon2.secondary_type if pokemon2.secondary_type != 'None' else None,
            'ability1': pokemon2.ability1,
            'ability2': pokemon2.ability2,
            'sprite_url': f"http://img.pokemondb.net/sprites/black-white/anim/normal/{pokemon2.name.lower()}.gif"
        },
        'battle_result': result,
        'winner': winner
    }
    
    # Renderizar o template com o contexto
    return render(request, 'pokemon_battle.html', context)