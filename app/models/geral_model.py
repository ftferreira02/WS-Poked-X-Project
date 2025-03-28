# app/models.py
from app.sparql_client import run_query

class Pokemon:
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name

    def __str__(self):
        return self.name

class PokemonManager:
    @staticmethod
    def get_all_pokemons():
        query = """
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name WHERE {
          ?pokemon a ex:Pokemon .
          ?pokemon sc:name ?name .
        }
        """
        results = run_query(query)
        
        # Criar uma lista de objetos Pokemon a partir dos resultados da consulta
        pokemons = [Pokemon(binding["pokemon"]["value"], binding["name"]["value"]) for binding in results["results"]["bindings"]]
        
        return pokemons

    @staticmethod
    def search_by_name(name_filter):
        query = f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name WHERE {{
          ?pokemon a ex:Pokemon .
          ?pokemon sc:name ?name .
          FILTER CONTAINS(LCASE(?name), LCASE("{name_filter}"))
        }}
        """
        results = run_query(query)
        
        # Criar uma lista de objetos Pokemon a partir dos resultados da consulta
        pokemons = [Pokemon(binding["pokemon"]["value"], binding["name"]["value"]) for binding in results["results"]["bindings"]]
        
        return pokemons
