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
from django.http import JsonResponse

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
    
    # Get strong Pokemon data using spAttack > 120
    strong_pokemon_query = """
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    SELECT ?pokemon ?name WHERE {
        ?pokemon pdx:spAttack ?spAttack ;
                 sc:name ?name .
        FILTER(?spAttack > 120)
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

def get_strongest_match(request):
    """AJAX endpoint to get the strongest match for a given Pokemon"""
    if request.method == 'GET':
        pokemon_id = request.GET.get('pokemon_id')
        
        if not pokemon_id:
            return JsonResponse({'error': 'Pokemon ID is required'}, status=400)
        
        # Query for the strongest match using the inferred data from SPIN rules
        strongest_match_query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        
        SELECT ?strongestMatch ?name ?strength ?pokedexNumber
        WHERE {{
            ?strongestMatch pdx:strongestMatchAgainst <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> ;
                           pdx:matchStrength ?strength ;
                           sc:name ?name ;
                           pdx:pokedexNumber ?pokedexNumber .
        }}
        ORDER BY DESC(?strength)
        LIMIT 1
        """
        
        # Fallback query if no inferred matches exist
        fallback_query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        
        SELECT ?strongestMatch ?name ?totalAttack ?pokedexNumber
        WHERE {{
            # Get target Pokemon types
            <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:primaryType ?targetType1 .
            OPTIONAL {{ <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:secondaryType ?targetType2 . }}
            
            # Find attackers with good matchup
            ?strongestMatch pdx:primaryType ?attackerType ;
                          pdx:attack ?attack ;
                          pdx:spAttack ?spAttack ;
                          sc:name ?name ;
                          pdx:pokedexNumber ?pokedexNumber .
            
            # Ensure it's not the same Pokemon
            FILTER(?strongestMatch != <http://poked-x.org/pokemon/Pokemon/{pokemon_id}>)
            
            # Look for type advantages
            ?effectiveness pdx:attackingType ?attackerType ;
                          pdx:defendingType ?targetType1 ;
                          pdx:effectiveness ?effValue .
            
            FILTER(?effValue > 1.0)
            
            BIND((?attack + ?spAttack) as ?totalAttack)
        }}
        ORDER BY DESC(?effValue) DESC(?totalAttack)
        LIMIT 1
        """
        
        try:
            # Try the main query first
            result = run_query(strongest_match_query)
            
            if not result or not result.get("results", {}).get("bindings"):
                # Fall back to simpler query
                result = run_query(fallback_query)
            
            if result and result.get("results", {}).get("bindings"):
                binding = result["results"]["bindings"][0]
                
                # Extract Pokemon ID from URI
                match_uri = binding["strongestMatch"]["value"]
                match_id = match_uri.split("/")[-1]
                
                return JsonResponse({
                    'success': True,
                    'match': {
                        'id': match_id,
                        'name': binding["name"]["value"],
                        'number': binding.get("pokedexNumber", {}).get("value", "Unknown"),
                        'strength': binding.get("strength", {}).get("value", "N/A")
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No suitable strongest match found'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Query failed: {str(e)}'
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_weakest_match(request):
    """AJAX endpoint to get the weakest match for a given Pokemon"""
    if request.method == 'GET':
        pokemon_id = request.GET.get('pokemon_id')
        
        if not pokemon_id:
            return JsonResponse({'error': 'Pokemon ID is required'}, status=400)
        
        # Query for the weakest match using the inferred data from SPIN rules
        weakest_match_query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        
        SELECT ?weakestMatch ?name ?weakness ?pokedexNumber
        WHERE {{
            ?weakestMatch pdx:weakestMatchAgainst <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> ;
                         pdx:matchWeakness ?weakness ;
                         sc:name ?name ;
                         pdx:pokedexNumber ?pokedexNumber .
        }}
        ORDER BY ASC(?weakness)
        LIMIT 1
        """
        
        # Fallback query if no inferred matches exist
        fallback_query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        
        SELECT ?weakestMatch ?name ?totalAttack ?pokedexNumber
        WHERE {{
            # Get target Pokemon types
            <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:primaryType ?targetType1 .
            OPTIONAL {{ <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:secondaryType ?targetType2 . }}
            
            # Find attackers with poor matchup
            ?weakestMatch pdx:primaryType ?attackerType ;
                         pdx:attack ?attack ;
                         pdx:spAttack ?spAttack ;
                         sc:name ?name ;
                         pdx:pokedexNumber ?pokedexNumber .
            
            # Ensure it's not the same Pokemon
            FILTER(?weakestMatch != <http://poked-x.org/pokemon/Pokemon/{pokemon_id}>)
            
            # Look for type disadvantages
            ?effectiveness pdx:attackingType ?attackerType ;
                          pdx:defendingType ?targetType1 ;
                          pdx:effectiveness ?effValue .
            
            FILTER(?effValue < 1.0)
            
            BIND((?attack + ?spAttack) as ?totalAttack)
        }}
        ORDER BY ASC(?effValue) ASC(?totalAttack)
        LIMIT 1
        """
        
        try:
            # Try the main query first
            result = run_query(weakest_match_query)
            
            if not result or not result.get("results", {}).get("bindings"):
                # Fall back to simpler query
                result = run_query(fallback_query)
            
            if result and result.get("results", {}).get("bindings"):
                binding = result["results"]["bindings"][0]
                
                # Extract Pokemon ID from URI
                match_uri = binding["weakestMatch"]["value"]
                match_id = match_uri.split("/")[-1]
                
                return JsonResponse({
                    'success': True,
                    'match': {
                        'id': match_id,
                        'name': binding["name"]["value"],
                        'number': binding.get("pokedexNumber", {}).get("value", "Unknown"),
                        'strength': binding.get("weakness", {}).get("value", "N/A")
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No suitable weakest match found'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Query failed: {str(e)}'
            })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def pokemon_battle_view(request, pokemon1_id, pokemon2_id):
    """Existing battle view - unchanged"""
    # Your existing battle logic here
    pass

def delete_battle_view(request, battle_id):
    """Existing delete battle view - unchanged"""
    # Your existing delete logic here
    pass