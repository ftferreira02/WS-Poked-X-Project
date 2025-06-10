from app.sparql_client import run_query, run_update
from datetime import datetime
import uuid

def save_battle_result(pokemon1, pokemon2, winner):
    """Save the battle result to the RDF database"""
    battle_id = str(uuid.uuid4())
    battle_uri = f"http://poked-x.org/pokemon/Battle/{battle_id}"

    print(f"Debug - Saving battle result:")
    print(f"Debug - Battle ID: {battle_id}")
    print(f"Debug - Battle URI: {battle_uri}")
    print(f"Debug - Pokemon1: {pokemon1}")
    print(f"Debug - Pokemon2: {pokemon2}")
    print(f"Debug - Winner: {winner}")

    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        <{battle_uri}> a pdx:Battle ;
            pdx:pokemon1 <http://poked-x.org/pokemon/Pokemon/{pokemon1['id']}> ;
            pdx:pokemon2 <http://poked-x.org/pokemon/Pokemon/{pokemon2['id']}> ;
            pdx:winner <http://poked-x.org/pokemon/Pokemon/{winner['id']}> ;
            pdx:timestamp "{datetime.now().isoformat()}"^^xsd:dateTime .
    }}
    """
    print(f"Debug - SPARQL Query: {query}")
    run_update(query)
    return battle_id


def get_battle_history():
    """Get the history of all battles"""
    query = """
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>

    SELECT ?battle ?pokemon1 ?pokemon2 ?winner ?timestamp ?name1 ?name2 ?nameWinner
    WHERE {
        ?battle a pdx:Battle ;
                pdx:pokemon1 ?pokemon1 ;
                pdx:pokemon2 ?pokemon2 ;
                pdx:winner ?winner ;
                pdx:timestamp ?timestamp .
        
        ?pokemon1 sc:name ?name1 .
        ?pokemon2 sc:name ?name2 .
        ?winner sc:name ?nameWinner .
    }
    ORDER BY DESC(?timestamp)
    LIMIT 10
    """
    print(f"Debug - Executing battle history query: {query}")
    results = run_query(query)
    print(f"Debug - Query results: {results}")
    battles = []

    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            battle_uri = binding["battle"]["value"]
            battle_id = battle_uri.split("/")[-1]
            pokemon1_name = binding["name1"]["value"]
            pokemon2_name = binding["name2"]["value"]
            winner_name = binding["nameWinner"]["value"]
            timestamp = binding["timestamp"]["value"]

            print(f"Debug - Processing battle:")
            print(f"Debug - Battle URI: {battle_uri}")
            print(f"Debug - Battle ID: {battle_id}")
            print(f"Debug - Pokemon1: {pokemon1_name}")
            print(f"Debug - Pokemon2: {pokemon2_name}")
            print(f"Debug - Winner: {winner_name}")
            print(f"Debug - Timestamp: {timestamp}")

            # Convert timestamp to a more readable format
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            battles.append({
                "battle_id": battle_id,
                "pokemon1_name": pokemon1_name,
                "pokemon2_name": pokemon2_name,
                "winner_name": winner_name,
                "date": dt
            })

    print(f"Debug - Final battle history: {battles}")
    return battles


def delete_battle(battle_id):
    """Delete a battle from the RDF database"""
    battle_uri = f"http://poked-x.org/pokemon/Battle/{battle_id}"

    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>

    DELETE WHERE {{
        <{battle_uri}> ?p ?o .
    }}
    """
    run_update(query)
