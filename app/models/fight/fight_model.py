from app.sparql_client import run_query

class Pokemon:
    def __init__(self, uri, name, attack, defense, health, primary_type, secondary_type):
        self.uri = uri
        self.name = name
        self.attack = attack
        self.defense = defense
        self.health = health
        self.primary_type = primary_type
        self.secondary_type = secondary_type
    
    def __str__(self):
        return self.name

    def get_weakness(self, opponent_type):
        # Aqui você pode mapear fraquezas com base nos tipos
        # Exemplo de como você pode calcular a fraqueza contra tipos específicos
        type_weakness = {
            "fire": 2,  # Fraco contra fogo
            "water": 0.5,  # Resistente à água
            "grass": 2,  # Fraco contra grama
            "electric": 0.5,  # Resistente à eletricidade
            # Adicione mais tipos conforme necessário
        }
        if opponent_type == self.primary_type or opponent_type == self.secondary_type:
            return type_weakness.get(opponent_type, 1)
        return 1  # Se não for vulnerável, retorna 1

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
        pokemons = [Pokemon(binding["pokemon"]["value"], binding["name"]["value"], 0, 0, 0, "", "") for binding in results["results"]["bindings"]]
        
        return pokemons

    @staticmethod
    def get_stats_by_id(pokemon_id):
        query = f"""
        PREFIX ns1: <http://example.org/pokemon/>
        PREFIX schema1: <http://schema.org/>

        SELECT ?name ?attack ?defense ?hp ?primaryType ?secondaryType
        WHERE {{
          <http://example.org/pokemon/Pokemon/{pokemon_id}> schema1:name ?name ;
                                                          ns1:attack ?attack ;
                                                          ns1:defense ?defense ;
                                                          ns1:hp ?hp ;
                                                          ns1:primaryType ?primaryType ;
                                                          ns1:secondaryType ?secondaryType .
        }}
        """

        results = run_query(query)
        bindings = results["results"]["bindings"]
        
        if not bindings:
            return None

        data = bindings[0]

        pokemon = Pokemon(
            uri=f"http://example.org/pokemon/Pokemon/{pokemon_id}",
            name=data["name"]["value"],
            attack=int(data["attack"]["value"]),
            defense=int(data["defense"]["value"]),
            health=int(data["hp"]["value"]),
            primary_type=data["primaryType"]["value"].split("/")[-1],
            secondary_type=data["secondaryType"]["value"].split("/")[-1] if "secondaryType" in data else ""
        )

        return pokemon

