from app.sparql_client import run_query
import re

class Pokemon:

    def __init__(self, uri, name, number=None, primary_type=None, secondary_type=None, exp=None,is_mega=False, height=None, weight=None):
        self.uri = uri
        self.name = name
        self.number = number  # Pokedex number
        self.id = self._extract_id_from_uri(uri) # Add id attribute
        self.primary_type = primary_type
        self.secondary_type = secondary_type
        self.exp = exp
        self.is_mega = is_mega
        self.height = height
        self.weight = weight

        name_parts = self.name.strip().lower().split()
        if number:
            if is_mega:
               if name_parts[-1] == "x":
                suffix = "-mega-x"
               elif name_parts[-1] == "y":
                suffix = "-mega-y"
               else:
                    suffix = "-mega"
               self.image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/52427d467f3e3b22af3c9cefc807a7452196ccd7/sprites/pokemon/{self.number}{suffix}.png"
            else:
                self.image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/52427d467f3e3b22af3c9cefc807a7452196ccd7/sprites/pokemon/{self.number}.png"

    def _extract_id_from_uri(self, uri):
        """Helper method to extract numeric ID from Pokémon URI."""
        # Adjust regex if your URI structure is different, e.g., ends in /ID or #ID
        match = re.search(r'/(\d+)$', uri)
        return int(match.group(1)) if match else None

    def __str__(self):
        return self.name

class PokemonManager:
    @staticmethod
    def _parse_results(results):
        """Helper function to parse SPARQL results into Pokemon objects."""
        pokemons = []
        if results and "results" in results and "bindings" in results["results"]:
            for binding in results["results"]["bindings"]:
                uri = binding.get("pokemon", {}).get("value")
                name = binding.get("name", {}).get("value")
                number = int(binding["number"]["value"])
                primary_type = binding["primaryType"]["value"].split("/")[-1]  # Extract 'grass' from URI
                secondary_type = binding.get("secondaryType", {}).get("value")
                if secondary_type:
                    secondary_type = secondary_type.split("/")[-1]
                    
                exp = int(binding.get("totalPoints", {}).get("value", 0))
                
                is_mega = "megaOf" in binding


                if uri and name: # Ensure we have the essential data
                    pokemon_obj = Pokemon(uri, name,number, primary_type, secondary_type, exp,is_mega)
                    # Add the Pokémon object to the list
                    if pokemon_obj.id is not None: # Only add if ID extraction was successful
                       pokemons.append(pokemon_obj)
        return pokemons

    @staticmethod
    def get_all_pokemons():
        query = """
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {
        ?pokemon a ex:Pokemon ;
                sc:name ?name ;
                ex:pokedexNumber ?number ;
                ex:primaryType ?primaryType ;
                ex:totalPoints ?totalPoints .
          OPTIONAL { ?pokemon ex:secondaryType ?secondaryType }
          OPTIONAL { ?pokemon ex:megaEvolutionOf ?megaOf }

        }
        ORDER BY ?number
        """
        results = run_query(query)
        return PokemonManager._parse_results(results) # Use the parser

    @staticmethod
    def search_by_name(name_filter):
        escaped_filter = name_filter.replace('"', '\\"')

        query = f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:primaryType ?primaryType ;
                    ex:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon ex:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon ex:megaEvolutionOf ?megaOf }}

            FILTER CONTAINS(LCASE(?name), LCASE("{escaped_filter}"))
        }} ORDER BY ?name
        """
        results = run_query(query)
        return PokemonManager._parse_results(results)
    
    @staticmethod
    def search_by_type(type_filter):
        query = f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:primaryType ?primaryType ;
                    ex:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon ex:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon ex:megaEvolutionOf ?megaOf }}

            FILTER (
                LCASE(STR(?primaryType)) = "http://example.org/pokemon/type/{type_filter}" ||
                LCASE(STR(?secondaryType)) = "http://example.org/pokemon/type/{type_filter}"
            )
        }} ORDER BY ?number
        """
        results = run_query(query)
        return PokemonManager._parse_results(results)
    
    @staticmethod
    def search_by_name_and_type(name_filter, type_filter):
        escaped_name = name_filter.replace('"', '\\"')

        query = f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:primaryType ?primaryType ;
                    ex:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon ex:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon ex:megaEvolutionOf ?megaOf }}

            FILTER (
                CONTAINS(LCASE(?name), LCASE("{escaped_name}")) &&
                (
                    LCASE(STR(?primaryType)) = "http://example.org/pokemon/type/{type_filter}" ||
                    LCASE(STR(?secondaryType)) = "http://example.org/pokemon/type/{type_filter}"
                )
            )
        }} ORDER BY ?number
        """
        results = run_query(query)
        return PokemonManager._parse_results(results)
    
    @staticmethod
    def get_pokemon_with_physical_info(pokemon_ids):
        if not pokemon_ids:
            return []

        filter_conditions = " || ".join(f"?number = {pid}" for pid in pokemon_ids)

        query = f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?height ?weight ?megaOf WHERE {{
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:height ?height ;
                    ex:weight ?weight .
            OPTIONAL {{ ?pokemon ex:megaEvolutionOf ?megaOf }}
            FILTER ({filter_conditions})
        }}
        """

        results = run_query(query)
        pokemons = []
        if results and "results" in results and "bindings" in results["results"]:
            for binding in results["results"]["bindings"]:
                uri = binding.get("pokemon", {}).get("value")
                name = binding.get("name", {}).get("value")
                number = int(binding["number"]["value"])
                height = float(binding["height"]["value"]) if "height" in binding else None
                print("height", height)
                weight = float(binding["weight"]["value"]) if "weight" in binding else None
                print("weight", weight)
                is_mega = "megaOf" in binding

                pokemon_obj = Pokemon( uri=uri, name=name, number=number, is_mega=is_mega, height=height, weight= weight)
                if pokemon_obj.id is not None:
                    pokemons.append(pokemon_obj)

        return pokemons
    
    @staticmethod
    def get_construct_rdf_query_by_id(pokemon_id):
        uri = f"<http://example.org/pokemon/Pokemon/{pokemon_id}>"
        return f"""
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        CONSTRUCT {{
        {uri} a ex:Pokemon ;
                sc:name ?name ;
                ex:pokedexNumber ?number ;
                ex:height ?height ;
                ex:weight ?weight ;
                ex:primaryType ?primaryType ;
                ex:secondaryType ?secondaryType ;
                ex:hp ?hp ;
                ex:attack ?attack ;
                ex:defense ?defense ;
                ex:spAttack ?spAttack ;
                ex:spDefense ?spDefense ;
                ex:speed ?speed ;
                ex:isLegendary ?isLegendary ;
                ex:generation ?generation ;
                ex:totalPoints ?totalPoints ;
                ex:megaEvolutionOf ?megaOf ;
                ex:ability1 ?ability1 ;
                ex:ability2 ?ability2 ;
                ex:abilityHidden ?abilityHidden ;
                ex:effectiveness ?effNode .

        ?effNode
            ex:againstBug ?againstBug ;
            ex:againstDark ?againstDark ;
            ex:againstDragon ?againstDragon ;
            ex:againstElectric ?againstElectric ;
            ex:againstFairy ?againstFairy ;
            ex:againstFight ?againstFight ;
            ex:againstFire ?againstFire ;
            ex:againstFlying ?againstFlying ;
            ex:againstGhost ?againstGhost ;
            ex:againstGrass ?againstGrass ;
            ex:againstGround ?againstGround ;
            ex:againstIce ?againstIce ;
            ex:againstNormal ?againstNormal ;
            ex:againstPoison ?againstPoison ;
            ex:againstPsychic ?againstPsychic ;
            ex:againstRock ?againstRock ;
            ex:againstSteel ?againstSteel ;
            ex:againstWater ?againstWater .
        }}
        WHERE {{
        BIND ({uri} AS ?pokemon)
        ?pokemon a ex:Pokemon ;
                sc:name ?name ;
                ex:pokedexNumber ?number ;
                ex:height ?height ;
                ex:weight ?weight ;
                ex:primaryType ?primaryType .

        OPTIONAL {{ ?pokemon ex:secondaryType ?secondaryType }}
        OPTIONAL {{ ?pokemon ex:hp ?hp }}
        OPTIONAL {{ ?pokemon ex:attack ?attack }}
        OPTIONAL {{ ?pokemon ex:defense ?defense }}
        OPTIONAL {{ ?pokemon ex:spAttack ?spAttack }}
        OPTIONAL {{ ?pokemon ex:spDefense ?spDefense }}
        OPTIONAL {{ ?pokemon ex:speed ?speed }}
        OPTIONAL {{ ?pokemon ex:isLegendary ?isLegendary }}
        OPTIONAL {{ ?pokemon ex:generation ?generation }}
        OPTIONAL {{ ?pokemon ex:totalPoints ?totalPoints }}
        OPTIONAL {{ ?pokemon ex:megaEvolutionOf ?megaOf }}
        OPTIONAL {{ ?pokemon ex:ability1 ?ability1 }}
        OPTIONAL {{ ?pokemon ex:ability2 ?ability2 }}
        OPTIONAL {{ ?pokemon ex:abilityHidden ?abilityHidden }}

        OPTIONAL {{
            ?pokemon ex:effectiveness ?effNode .
            OPTIONAL {{ ?effNode ex:againstBug ?againstBug }}
            OPTIONAL {{ ?effNode ex:againstDark ?againstDark }}
            OPTIONAL {{ ?effNode ex:againstDragon ?againstDragon }}
            OPTIONAL {{ ?effNode ex:againstElectric ?againstElectric }}
            OPTIONAL {{ ?effNode ex:againstFairy ?againstFairy }}
            OPTIONAL {{ ?effNode ex:againstFight ?againstFight }}
            OPTIONAL {{ ?effNode ex:againstFire ?againstFire }}
            OPTIONAL {{ ?effNode ex:againstFlying ?againstFlying }}
            OPTIONAL {{ ?effNode ex:againstGhost ?againstGhost }}
            OPTIONAL {{ ?effNode ex:againstGrass ?againstGrass }}
            OPTIONAL {{ ?effNode ex:againstGround ?againstGround }}
            OPTIONAL {{ ?effNode ex:againstIce ?againstIce }}
            OPTIONAL {{ ?effNode ex:againstNormal ?againstNormal }}
            OPTIONAL {{ ?effNode ex:againstPoison ?againstPoison }}
            OPTIONAL {{ ?effNode ex:againstPsychic ?againstPsychic }}
            OPTIONAL {{ ?effNode ex:againstRock ?againstRock }}
            OPTIONAL {{ ?effNode ex:againstSteel ?againstSteel }}
            OPTIONAL {{ ?effNode ex:againstWater ?againstWater }}
        }}
        }}
        """


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
    def get_all_evolution_chains():
        query = """
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?evolvesTo ?primaryType WHERE {
        {
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:primaryType ?primaryType ;
                    ex:evolvesTo ?evolvesTo .
        }
        UNION
        {
            ?pokemon a ex:Pokemon ;
                    sc:name ?name ;
                    ex:pokedexNumber ?number ;
                    ex:primaryType ?primaryType .
            ?other ex:evolvesTo ?pokemon .
            OPTIONAL { ?pokemon ex:evolvesTo ?evolvesTo }
        }
        }
        """
        results = run_query(query)
        
        chains = {}
        for binding in results["results"]["bindings"]:
            uri = binding["pokemon"]["value"]
            name = binding["name"]["value"]
            number = int(binding["number"]["value"])
            evolves_to = binding.get("evolvesTo", {}).get("value")
            id = int(uri.split("/")[-1])
            
            primary_type = binding.get("primaryType", {}).get("value", "").split("/")[-1]

            chains.setdefault(uri, {
                "id": id,
                "name": name,
                "number": number,
                "evolves_to": evolves_to,
                "primary_type": primary_type
            })

        # Build chain sequences
        visited = set()
        evolution_chains = []

        for uri, data in chains.items():
            if uri in visited:
                continue
            chain = [data]
            visited.add(uri)

            next_uri = data["evolves_to"]
            while next_uri and next_uri in chains:
                next_data = chains[next_uri]
                chain.append(next_data)
                visited.add(next_uri)
                next_uri = next_data["evolves_to"]

            evolution_chains.append(chain)

        return evolution_chains


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
    
    @staticmethod
    def get_pokemon_by_id(pokemon_id):
        try:
            all_pokemons = PokemonManager.get_all_pokemons()
            return next((p for p in all_pokemons if str(p.id) == str(pokemon_id)), None)
        except Exception as e:
            print(f"Erro ao obter Pokémon com id {pokemon_id}: {e}")
            return None
