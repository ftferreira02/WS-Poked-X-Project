from SPARQLWrapper import POST, SPARQLWrapper, JSON , TURTLE
from django.conf import settings 



def run_query(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def run_query_describe(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat('n3')  # ou 'nt' para N-Triples
    return sparql.query().convert().decode("utf-8")

def run_construct_query(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)
    return sparql.query().convert().decode("utf-8")

def run_update(update_string):
    """Execute a SPARQL UPDATE query."""
    sparql = SPARQLWrapper(settings.SPARQL_UPDATE_ENDPOINT)
    sparql.setQuery(update_string)
    sparql.setMethod(POST)  # Use POST instead of URLENCODED
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_description_from_dbpedia(pokemon_name, lang="pt"):
    """
    Obtém a descrição (abstract) de um Pokémon a partir da DBpedia, no idioma especificado.
    """
    dbpedia_sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    dbpedia_sparql.setQuery(f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>

        SELECT ?abstract WHERE {{
            dbr:{pokemon_name} dbo:abstract ?abstract .
            FILTER (lang(?abstract) = '{lang}')
        }}
        LIMIT 1
    """)
    dbpedia_sparql.setReturnFormat(JSON)
    
    try:
            results = dbpedia_sparql.query().convert()
            full_text = results["results"]["bindings"][0]["abstract"]["value"]
            
            if "\n\n" in full_text:
                return full_text.split("\n\n")[0]
            elif ". " in full_text:
                return full_text.split(". ")[0] + "."
            else:
                return full_text
    except Exception:
        return f"Description of {pokemon_name} not found on DBpedia."