from app.sparql_client import run_query

def analyze_team_roles(team_pokemon_ids):
    """Analyze the roles of Pokemon in a team based on their stats and types."""
    roles = {
        'Physical Attackers': [],
        'Special Attackers': [],
        'Tanks': [],
        'Glass Cannons': [],
        'Fast Pokemon': [],
        'Mixed Attackers': [],
        'Balanced Pokemon': []
    }
    
    for pokemon_id in team_pokemon_ids:
        query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        SELECT ?name ?attack ?spAttack ?defense ?spDefense ?speed ?hp
        WHERE {{
            <http://poked-x.org/pokemon/Pokemon/{pokemon_id}>
                sc:name ?name ;
                pdx:attack ?attack ;
                pdx:spAttack ?spAttack ;
                pdx:defense ?defense ;
                pdx:spDefense ?spDefense ;
                pdx:speed ?speed ;
                pdx:hp ?hp .
        }}
        """
        results = run_query(query)
        if not results["results"]["bindings"]:
            continue
            
        pokemon = results["results"]["bindings"][0]
        name = pokemon["name"]["value"]
        stats = {
            "attack": int(float(pokemon["attack"]["value"])),
            "spAttack": int(float(pokemon["spAttack"]["value"])),
            "defense": int(float(pokemon["defense"]["value"])),
            "spDefense": int(float(pokemon["spDefense"]["value"])),
            "speed": int(float(pokemon["speed"]["value"])),
            "hp": int(float(pokemon["hp"]["value"]))
        }
        
        # Determine roles based on stats
        if stats["attack"] > 100:
            roles["Physical Attackers"].append(name)
        if stats["spAttack"] > 100:
            roles["Special Attackers"].append(name)
        if stats["defense"] + stats["spDefense"] + stats["hp"] > 300:
            roles["Tanks"].append(name)
        if (stats["attack"] > 100 or stats["spAttack"] > 100) and stats["defense"] + stats["spDefense"] < 160:
            roles["Glass Cannons"].append(name)
        if stats["speed"] > 100:
            roles["Fast Pokemon"].append(name)
        if stats["attack"] > 80 and stats["spAttack"] > 80:
            roles["Mixed Attackers"].append(name)
        if all(60 <= stat <= 100 for stat in stats.values()):
            roles["Balanced Pokemon"].append(name)
            
    return roles

def analyze_type_coverage(team_pokemon_ids):
    """Analyze the type coverage of a team."""
    coverage = {
        'offensive': [],  # Using list instead of set
        'defensive': [],  # Using list instead of set
        'team_types': []  # Using list instead of set
    }
    
    for pokemon_id in team_pokemon_ids:
        query = """
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        SELECT ?type ?strongAgainst ?resistantTo
        WHERE {
            <http://poked-x.org/pokemon/Pokemon/%d> 
                pdx:type ?type ;
                pdx:strongAgainst ?strongAgainst ;
                pdx:resistantTo ?resistantTo .
        }
        """ % pokemon_id
        
        results = run_query(query)
        
        # Handle SPARQL results properly
        if results and "results" in results and "bindings" in results["results"]:
            for binding in results["results"]["bindings"]:
                # Extract values from bindings
                pokemon_type = binding.get("type", {}).get("value", "").split("/")[-1]
                strong_against = binding.get("strongAgainst", {}).get("value", "").split("/")[-1]
                resistant_to = binding.get("resistantTo", {}).get("value", "").split("/")[-1]
                
                # Add unique types to coverage
                if pokemon_type and pokemon_type not in coverage['team_types']:
                    coverage['team_types'].append(pokemon_type)
                if strong_against and strong_against not in coverage['offensive']:
                    coverage['offensive'].append(strong_against)
                if resistant_to and resistant_to not in coverage['defensive']:
                    coverage['defensive'].append(resistant_to)
    
    return coverage

def calculate_team_balance_score(team_pokemon_ids):
    """Calculate a balance score for the team based on type coverage and roles."""
    type_coverage = analyze_type_coverage(team_pokemon_ids)
    roles = analyze_team_roles(team_pokemon_ids)
    
    # Calculate scores
    offensive_coverage_score = len(type_coverage['offensive']) / 18.0  # Total number of types
    defensive_coverage_score = len(type_coverage['defensive']) / 18.0
    type_diversity_score = len(type_coverage['team_types']) / 6.0  # Max team size
    
    # Calculate role diversity score
    role_counts = {role: len(pokemon_list) for role, pokemon_list in roles.items()}
    total_roles = sum(1 for count in role_counts.values() if count > 0)
    role_diversity_score = total_roles / len(roles)
    
    # Calculate final score (weighted average)
    final_score = (
        offensive_coverage_score * 0.3 +
        defensive_coverage_score * 0.3 +
        type_diversity_score * 0.2 +
        role_diversity_score * 0.2
    ) * 100
    
    return round(final_score, 1) 