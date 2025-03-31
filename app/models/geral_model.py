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
        return [
            Pokemon(binding["pokemon"]["value"], binding["name"]["value"])
            for binding in results["results"]["bindings"]
        ]

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
        return [
            Pokemon(binding["pokemon"]["value"], binding["name"]["value"])
            for binding in results["results"]["bindings"]
        ]

    @staticmethod
    def get_stats_by_id(pokemon_id):
        query = f"""
        PREFIX ns1: <http://example.org/pokemon/>
        PREFIX schema1: <http://schema.org/>
        SELECT ?name ?attack ?defense ?hp ?spAttack ?spDefense ?speed ?totalPoints
               ?height ?weight ?isLegendary ?generation ?baseFriendship
               ?primaryType ?secondaryType ?pokedexNumber
               ?againstType ?value
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
                                                           ns1:secondaryType ?secondaryType ;
                                                           ns1:pokedexNumber ?pokedexNumber ;
                                                           ns1:effectiveness ?eff .
          ?eff ?againstType ?value .
          FILTER STRSTARTS(STR(?againstType), STR(ns1:against))
        }}
        """
        results = run_query(query)
        bindings = results["results"]["bindings"]
        if not bindings:
            return None

        stats = {
            "id": int(pokemon_id),
            "name": None,
            "attack": 0,
            "defense": 0,
            "hp": 0,
            "spAttack": 0,
            "spDefense": 0,
            "speed": 0,
            "totalPoints": 0,
            "height": 0.0,
            "weight": 0.0,
            "isLegendary": False,
            "generation": 0,
            "baseFriendship": 0,
            "primaryType": "",
            "secondaryType": "",
            "strongAgainst": [],
            "weakAgainst": [],
            "pokedexNumber": 0,
        }

        for binding in bindings:
            if not stats["name"]:
                stats.update({
                    "name": binding["name"]["value"],
                    "attack": int(binding["attack"]["value"]),
                    "defense": int(binding["defense"]["value"]),
                    "hp": int(binding["hp"]["value"]),
                    "spAttack": int(binding["spAttack"]["value"]),
                    "spDefense": int(binding["spDefense"]["value"]),
                    "speed": int(binding["speed"]["value"]),
                    "totalPoints": int(binding["totalPoints"]["value"]),
                    "height": float(binding["height"]["value"]),
                    "weight": float(binding["weight"]["value"]),
                    "isLegendary": (binding["isLegendary"]["value"] == "true"),
                    "generation": int(binding["generation"]["value"]),
                    "baseFriendship": int(binding["baseFriendship"]["value"]),
                    "primaryType": binding["primaryType"]["value"].split("/")[-1],
                    "secondaryType": binding["secondaryType"]["value"].split("/")[-1],
                    "pokedexNumber": int(binding.get("pokedexNumber", {}).get("value", 0)),
                })

            type_name = binding["againstType"]["value"].split("against")[-1].lower()
            val = float(binding["value"]["value"])
            if val > 1.0:
                stats["strongAgainst"].append(type_name)
            elif 0.0 < val < 1.0:
                stats["weakAgainst"].append(type_name)

            stats["strongAgainst"] = list(dict.fromkeys(stats["strongAgainst"]))
            stats["weakAgainst"] = list(dict.fromkeys(stats["weakAgainst"]))

        return stats

    @staticmethod
    def ask_question_about_pokemon(pokemon_name, property_uri, value_uri):
        n = pokemon_name.replace('"', '\\"')
        if property_uri.endswith("generation"):
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" ;
                       ex:generation {value_uri} .
            }}
            """
        elif property_uri.endswith("isLegendary"):
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" ;
                       ex:isLegendary {value_uri} .
            }}
            """
        elif property_uri.endswith("type"):
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" .
              {{
                FILTER EXISTS {{
                  ?pokemon ex:primaryType <{value_uri}> .
                }}
              }}
              UNION
              {{
                FILTER EXISTS {{
                  ?pokemon ex:secondaryType <{value_uri}> .
                }}
              }}
            }}
            """
        elif property_uri.endswith("ability"):
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" .
              {{
                FILTER EXISTS {{
                  ?pokemon ex:ability1 <{value_uri}> .
                }}
              }}
              UNION
              {{
                FILTER EXISTS {{
                  ?pokemon ex:ability2 <{value_uri}> .
                }}
              }}
            }}
            """
        elif property_uri.endswith("habitat"):
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" ;
                       ex:habitat <{value_uri}> .
            }}
            """
        elif property_uri.endswith("weakAgainst"):
            t = value_uri.rsplit('/', 1)[-1]
            p = f"against{t.capitalize()}"
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" ;
                       ex:effectiveness ?eff .
              ?eff ex:{p} ?val .
              FILTER(?val > 1.0)
            }}
            """
        else:
            query = f"""
            PREFIX ex: <http://example.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a ex:Pokemon ;
                       sc:name "{n}" ;
                       <{property_uri}> <{value_uri}> .
            }}
            """
        result = run_query(query)
        return result.get("boolean", False)
