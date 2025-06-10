from app.sparql_client import run_query, run_update
from datetime import datetime
import uuid

def save_battle_result(pokemon1, pokemon2, winner):
    """Save the battle result to the RDF database"""
    battle_id = str(uuid.uuid4())
    battle_uri = f"http://poked-x.org/pokemon/Battle/{battle_id}"

    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>

    INSERT DATA {{
        <{battle_uri}> a pdx:Battle ;
            pdx:pokemon1 <http://poked-x.org/pokemon/Pokemon/{pokemon1['id']}> ;
            pdx:pokemon2 <http://poked-x.org/pokemon/Pokemon/{pokemon2['id']}> ;
            pdx:winner <http://poked-x.org/pokemon/Pokemon/{winner['id']}> ;
            pdx:timestamp "{datetime.now().isoformat()}"^^xsd:dateTime .
    }}
    """
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
    results = run_query(query)
    battles = []

    if results and "results" in results and "bindings" in results["results"]:
        for binding in results["results"]["bindings"]:
            battle_uri = binding["battle"]["value"]
            battle_id = battle_uri.split("/")[-1]
            pokemon1_name = binding["name1"]["value"]
            pokemon2_name = binding["name2"]["value"]
            winner_name = binding["nameWinner"]["value"]
            timestamp = binding["timestamp"]["value"]

            # Convert timestamp to a more readable format
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            battles.append({
                "battle_id": battle_id,
                "pokemon1_name": pokemon1_name,
                "pokemon2_name": pokemon2_name,
                "winner_name": winner_name,
                "date": dt
            })

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
