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

    @staticmethod
    def get_stats_by_id(pokemon_id):
        query = f"""
        PREFIX ns1: <http://example.org/pokemon/>
        PREFIX schema1: <http://schema.org/>

        SELECT ?name ?attack ?defense ?hp ?spAttack ?spDefense ?speed ?totalPoints
              ?height ?weight ?isLegendary ?generation ?baseFriendship
              ?primaryType ?secondaryType
        WHERE {{
          <http://example.org/pokemon/Pokemon/{pokemon_id}> schema1:name ?name ;
                                                          ns1:attack ?attack ;
                                                          ns1:defense ?defense ;
                                                          ns1:hp ?hp ;
                                                          ns1:spAttack ?spAttack ;
                                                          ns1:spDefense ?spDefense ;
                                                          ns1:speed ?speed ;
                                                          ns1:totalPoints ?totalPoints ;
                                                          ns1:height ?height ;
                                                          ns1:weight ?weight ;
                                                          ns1:isLegendary ?isLegendary ;
                                                          ns1:generation ?generation ;
                                                          ns1:baseFriendship ?baseFriendship ;
                                                          ns1:primaryType ?primaryType ;
                                                          ns1:secondaryType ?secondaryType .
        }}
        """

        results = run_query(query)
        bindings = results["results"]["bindings"]
        
        if not bindings:
            return None

        data = bindings[0]

        stats = {
            "name": data["name"]["value"],
            "attack": int(data["attack"]["value"]),
            "defense": int(data["defense"]["value"]),
            "hp": int(data["hp"]["value"]),
            "spAttack": int(data["spAttack"]["value"]),
            "spDefense": int(data["spDefense"]["value"]),
            "speed": int(data["speed"]["value"]),
            "totalPoints": int(data["totalPoints"]["value"]),
            "height": float(data["height"]["value"]),
            "weight": float(data["weight"]["value"]),
            "isLegendary": data["isLegendary"]["value"] == "true",
            "generation": int(data["generation"]["value"]),
            "baseFriendship": int(data["baseFriendship"]["value"]),
            "primaryType": data["primaryType"]["value"].split("/")[-1],
            "secondaryType": data["secondaryType"]["value"].split("/")[-1],
        }

        return stats
