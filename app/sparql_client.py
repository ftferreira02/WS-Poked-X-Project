from SPARQLWrapper import POST, SPARQLWrapper, JSON
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

def run_update(update_string):
    """Execute a SPARQL UPDATE query."""
    sparql = SPARQLWrapper(settings.SPARQL_UPDATE_ENDPOINT)
    sparql.setQuery(update_string)
    sparql.setMethod(POST)  # Use POST instead of URLENCODED
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()