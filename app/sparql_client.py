from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings 


def run_query(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
