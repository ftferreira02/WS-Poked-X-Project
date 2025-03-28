
from django.shortcuts import render
from app.forms import PokemonSearchForm
from app.sparql_client import run_query
from app.models.geral_model import PokemonManager

def search_pokemon(request):
    pokemons = []
    name_filter = ''
    
    # Instanciando o formulário
    form = PokemonSearchForm(request.GET)
    
    if form.is_valid():
        name_filter = form.cleaned_data['name']
        
        if name_filter:
            pokemons = PokemonManager.search_by_name(name_filter)
        else:
            pokemons = PokemonManager.get_all_pokemons()
        
    
    # Passa o formulário e os Pokémon encontrados para o template
    return render(request, 'pokemon_search_form.html', {'form': form, 'pokemons': pokemons})
