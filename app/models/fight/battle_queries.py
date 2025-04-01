from app.sparql_client import run_query, run_update
from datetime import datetime

def save_battle_result(pokemon1, pokemon2, winner):
    """Salva o resultado da batalha no banco de dados RDF usando SPARQL INSERT."""
    battle_id = f"battle_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    battle_uri = f"http://example.org/pokemon/Battle/{battle_id}"
    
    # Debug print
    print(f"Saving battle: {pokemon1['name']} vs {pokemon2['name']}, Winner: {winner['name']}")
    
    insert_query = f"""
    PREFIX poke: <http://example.org/pokemon/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        <{battle_uri}> rdf:type poke:Battle ;
            poke:date "{datetime.now().isoformat()}"^^xsd:dateTime ;
            poke:pokemon1 <http://example.org/pokemon/Pokemon/{pokemon1['id']}> ;
            poke:pokemon2 <http://example.org/pokemon/Pokemon/{pokemon2['id']}> ;
            poke:winner <http://example.org/pokemon/Pokemon/{winner['id']}> ;
            poke:pokemon1Name "{pokemon1['name']}" ;
            poke:pokemon2Name "{pokemon2['name']}" ;
            poke:winnerName "{winner['name']}" .
    }}
    """

    try:
        result = run_update(insert_query)
        print(f"Insert result: {result}")
        return True
    except Exception as e:
        print(f"Error saving battle result: {e}")
        return False

def get_battle_history(limit=10):
    """Recupera o histórico de batalhas do banco de dados RDF usando SPARQL."""
    print("Fetching battle history...")
    
    query = f"""
    PREFIX poke: <http://example.org/pokemon/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?battle ?date ?pokemon1Name ?pokemon2Name ?winnerName
    WHERE {{
        ?battle rdf:type poke:Battle ;
                poke:date ?date ;
                poke:pokemon1Name ?pokemon1Name ;
                poke:pokemon2Name ?pokemon2Name ;
                poke:winnerName ?winnerName .
    }}
    ORDER BY DESC(?date)
    LIMIT {limit}
    """

    try:
        results = run_query(query)
        print("Battle query results:", results)
        
        battle_history = []

        for result in results.get('results', {}).get('bindings', []):
            # Get the date string from the result
            date_str = result.get('date', {}).get('value', '')
            
            # Try to parse the date string into a datetime object
            try:
                # Try parsing ISO format date
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Fallback to a more flexible parser if needed
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    # If all parsing fails, use the current date as a fallback
                    print(f"Could not parse date: {date_str}")
                    date_obj = datetime.now()
            
            entry = {
                'battle_id': result.get('battle', {}).get('value', '').split('/')[-1],
                'date': date_obj,  # Now a datetime object
                'pokemon1_name': result.get('pokemon1Name', {}).get('value', ''),
                'pokemon2_name': result.get('pokemon2Name', {}).get('value', ''),
                'winner_name': result.get('winnerName', {}).get('value', '')
            }
            battle_history.append(entry)

        print(f"Returning {len(battle_history)} battles")
        return battle_history
    except Exception as e:
        print(f"Error retrieving battle history: {e}")
        import traceback
        traceback.print_exc()
        return []
    
def delete_battle(battle_id):
    """Remove uma batalha específica do RDF."""
    battle_uri = f"http://example.org/pokemon/Battle/{battle_id}"
    
    delete_query = f"""
    PREFIX poke: <http://example.org/pokemon/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    DELETE WHERE {{
        <{battle_uri}> ?p ?o .
    }}
    """

    try:
        result = run_update(delete_query)
        print(f"Deleted battle {battle_id}: {result}")
        return True
    except Exception as e:
        print(f"Error deleting battle {battle_id}: {e}")
        return False
