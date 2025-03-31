
from app.sparql_client import run_query, run_update
from datetime import datetime

def save_battle_result(pokemon1, pokemon2, winner):
    """Salva o resultado da batalha no banco de dados RDF usando SPARQL INSERT."""
    battle_id = f"battle_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    battle_uri = f"http://example.org/pokemon/Battle/{battle_id}"

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
        run_update(insert_query)
        return True
    except Exception as e:
        print(f"Erro ao salvar o resultado da batalha: {e}")
        return False

def get_battle_history(limit=10):
    """Recupera o histórico de batalhas do banco de dados RDF usando SPARQL."""
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
        battle_history = []

        for result in results.get('results', {}).get('bindings', []):
            battle_history.append({
                'battle_id': result.get('battle', {}).get('value', '').split('/')[-1],
                'date': result.get('date', {}).get('value', ''),
                'pokemon1_name': result.get('pokemon1Name', {}).get('value', ''),
                'pokemon2_name': result.get('pokemon2Name', {}).get('value', ''),
                'winner_name': result.get('winnerName', {}).get('value', '')
            })

        return battle_history
    except Exception as e:
        print(f"Erro ao recuperar o histórico de batalhas: {e}")
        return []
