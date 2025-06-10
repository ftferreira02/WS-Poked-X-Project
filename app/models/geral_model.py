from SPARQLWrapper import SPARQLWrapper, JSON
from app.sparql_client import run_query, get_dbpedia_info
from app.sparql_client import get_full_dbpedia_info_turtle, insert_turtle_to_graphdb, dbpedia_data_already_loaded
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
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {
        ?pokemon a pdx:Pokemon ;
                sc:name ?name ;
                pdx:pokedexNumber ?number ;
                pdx:primaryType ?primaryType ;
                pdx:totalPoints ?totalPoints .
          OPTIONAL { ?pokemon pdx:secondaryType ?secondaryType }
          OPTIONAL { ?pokemon pdx:megaEvolutionOf ?megaOf }

        }
        ORDER BY ?number
        """
        results = run_query(query)
        return PokemonManager._parse_results(results) # Use the parser

    @staticmethod
    def search_by_name(name_filter):
        escaped_filter = name_filter.replace('"', '\\"')

        query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:primaryType ?primaryType ;
                    pdx:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon pdx:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon pdx:megaEvolutionOf ?megaOf }}

            FILTER CONTAINS(LCASE(?name), LCASE("{escaped_filter}"))
        }} ORDER BY ?name
        """
        results = run_query(query)
        return PokemonManager._parse_results(results)
    
    @staticmethod
    def search_by_type(type_filter):
        query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:primaryType ?primaryType ;
                    pdx:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon pdx:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon pdx:megaEvolutionOf ?megaOf }}

            FILTER (
                LCASE(STR(?primaryType)) = "http://poked-x.org/pokemon/type/{type_filter}" ||
                LCASE(STR(?secondaryType)) = "http://poked-x.org/pokemon/type/{type_filter}"
            )
        }} ORDER BY ?number
        """
        results = run_query(query)
        return PokemonManager._parse_results(results)
    
    @staticmethod
    def search_by_name_and_type(name_filter, type_filter):
        escaped_name = name_filter.replace('"', '\\"')

        query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?primaryType ?secondaryType ?totalPoints ?megaOf  WHERE {{
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:primaryType ?primaryType ;
                    pdx:totalPoints ?totalPoints .
            OPTIONAL {{ ?pokemon pdx:secondaryType ?secondaryType }}
            OPTIONAL {{ ?pokemon pdx:megaEvolutionOf ?megaOf }}

            FILTER (
                CONTAINS(LCASE(?name), LCASE("{escaped_name}")) &&
                (
                    LCASE(STR(?primaryType)) = "http://poked-x.org/pokemon/type/{type_filter}" ||
                    LCASE(STR(?secondaryType)) = "http://poked-x.org/pokemon/type/{type_filter}"
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
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?height ?weight ?megaOf WHERE {{
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:height ?height ;
                    pdx:weight ?weight .
            OPTIONAL {{ ?pokemon pdx:megaEvolutionOf ?megaOf }}
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
        uri = f"<http://poked-x.org/pokemon/Pokemon/{pokemon_id}>"
        return f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        CONSTRUCT {{
            {uri} a pdx:Pokemon ;
                sc:name ?name ;
                pdx:pokedexNumber ?number ;
                pdx:height ?height ;
                pdx:weight ?weight ;
                pdx:primaryType ?primaryType ;
                pdx:secondaryType ?secondaryType ;
                pdx:hp ?hp ;
                pdx:attack ?attack ;
                pdx:defense ?defense ;
                pdx:spAttack ?spAttack ;
                pdx:spDefense ?spDefense ;
                pdx:speed ?speed ;
                pdx:isLegendary ?isLegendary ;
                pdx:generation ?generation ;
                pdx:totalPoints ?totalPoints ;
                pdx:megaEvolutionOf ?megaOf ;
                pdx:ability1 ?ability1 ;
                pdx:ability2 ?ability2 ;
                pdx:abilityHidden ?abilityHidden ;
                pdx:effectiveness ?effNode .

            ?effNode
                pdx:againstBug ?againstBug ;
                pdx:againstDark ?againstDark ;
                pdx:againstDragon ?againstDragon ;
                pdx:againstElectric ?againstElectric ;
                pdx:againstFairy ?againstFairy ;
                pdx:againstFight ?againstFight ;
                pdx:againstFire ?againstFire ;
                pdx:againstFlying ?againstFlying ;
                pdx:againstGhost ?againstGhost ;
                pdx:againstGrass ?againstGrass ;
                pdx:againstGround ?againstGround ;
                pdx:againstIce ?againstIce ;
                pdx:againstNormal ?againstNormal ;
                pdx:againstPoison ?againstPoison ;
                pdx:againstPsychic ?againstPsychic ;
                pdx:againstRock ?againstRock ;
                pdx:againstSteel ?againstSteel ;
                pdx:againstWater ?againstWater .
        }}
        WHERE {{
            {uri} a pdx:Pokemon ;
                sc:name ?name ;
                pdx:pokedexNumber ?number ;
                pdx:height ?height ;
                pdx:weight ?weight ;
                pdx:primaryType ?primaryType .

            OPTIONAL {{ {uri} pdx:secondaryType ?secondaryType }}
            OPTIONAL {{ {uri} pdx:hp ?hp }}
            OPTIONAL {{ {uri} pdx:attack ?attack }}
            OPTIONAL {{ {uri} pdx:defense ?defense }}
            OPTIONAL {{ {uri} pdx:spAttack ?spAttack }}
            OPTIONAL {{ {uri} pdx:spDefense ?spDefense }}
            OPTIONAL {{ {uri} pdx:speed ?speed }}
            OPTIONAL {{ {uri} pdx:isLegendary ?isLegendary }}
            OPTIONAL {{ {uri} pdx:generation ?generation }}
            OPTIONAL {{ {uri} pdx:totalPoints ?totalPoints }}
            OPTIONAL {{ {uri} pdx:megaEvolutionOf ?megaOf }}
            OPTIONAL {{ {uri} pdx:ability1 ?ability1 }}
            OPTIONAL {{ {uri} pdx:ability2 ?ability2 }}
            OPTIONAL {{ {uri} pdx:abilityHidden ?abilityHidden }}

            OPTIONAL {{
                {uri} pdx:effectiveness ?effNode .
                OPTIONAL {{ ?effNode pdx:againstBug ?againstBug }}
                OPTIONAL {{ ?effNode pdx:againstDark ?againstDark }}
                OPTIONAL {{ ?effNode pdx:againstDragon ?againstDragon }}
                OPTIONAL {{ ?effNode pdx:againstElectric ?againstElectric }}
                OPTIONAL {{ ?effNode pdx:againstFairy ?againstFairy }}
                OPTIONAL {{ ?effNode pdx:againstFight ?againstFight }}
                OPTIONAL {{ ?effNode pdx:againstFire ?againstFire }}
                OPTIONAL {{ ?effNode pdx:againstFlying ?againstFlying }}
                OPTIONAL {{ ?effNode pdx:againstGhost ?againstGhost }}
                OPTIONAL {{ ?effNode pdx:againstGrass ?againstGrass }}
                OPTIONAL {{ ?effNode pdx:againstGround ?againstGround }}
                OPTIONAL {{ ?effNode pdx:againstIce ?againstIce }}
                OPTIONAL {{ ?effNode pdx:againstNormal ?againstNormal }}
                OPTIONAL {{ ?effNode pdx:againstPoison ?againstPoison }}
                OPTIONAL {{ ?effNode pdx:againstPsychic ?againstPsychic }}
                OPTIONAL {{ ?effNode pdx:againstRock ?againstRock }}
                OPTIONAL {{ ?effNode pdx:againstSteel ?againstSteel }}
                OPTIONAL {{ ?effNode pdx:againstWater ?againstWater }}
            }}
        }}
        """

    @staticmethod
    def get_stats_by_id(pokemon_id):
        query = f"""
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        SELECT ?name ?attack ?defense ?hp ?spAttack ?spDefense ?speed ?totalPoints
            ?height ?weight ?isLegendary ?generation ?baseFriendship
            ?primaryType ?secondaryType ?pokedexNumber
            ?againstType ?value
        WHERE {{
            <http://poked-x.org/pokemon/Pokemon/{pokemon_id}>
                sc:name ?name ;
                pdx:attack ?attack ;
                pdx:defense ?defense ;
                pdx:hp ?hp ;
                pdx:spAttack ?spAttack ;
                pdx:spDefense ?spDefense ;
                pdx:speed ?speed ;
                pdx:totalPoints ?totalPoints ;
                pdx:height ?height ;
                pdx:weight ?weight ;
                pdx:isLegendary ?isLegendary ;
                pdx:generation ?generation ;
                pdx:baseFriendship ?baseFriendship ;
                pdx:primaryType ?primaryType ;
                pdx:pokedexNumber ?pokedexNumber ;
                pdx:hasEffectiveness ?effNode .
            OPTIONAL {{ <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:secondaryType ?secondaryType }}
            ?effNode ?againstType ?value .
            FILTER(CONTAINS(STR(?againstType), "against"))
        }}
        """
        results = run_query(query)
        bindings = results["results"]["bindings"]
        if not bindings:
            return None

        stats = {
            "id": int(pokemon_id),
            "name": None,
            "description": "",
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
            "designer": "",
            "firstAppearance": "",
            "sameTypePokemon": None
        }

        # Process the main stats
        for binding in bindings:
            name_value = binding["name"]["value"]
            if not stats["name"]:
                print(f"✅ Verificado DBpedia para {name_value} | Já existe? {dbpedia_data_already_loaded(name_value)}")
                if not dbpedia_data_already_loaded(name_value):
                    full_info = get_full_dbpedia_info_turtle(name_value)
                    if full_info:
                        insert_turtle_to_graphdb(full_info)

                # Get DBpedia info
                dbpedia_data = get_dbpedia_info(name_value, lang="en")
                stats["description"] = dbpedia_data["description"]
                stats["designer"] = dbpedia_data["designer"]
                stats["firstAppearance"] = dbpedia_data["firstAppearance"]

            stats["name"] = name_value

            for key in ["attack", "defense", "hp", "spAttack", "spDefense", "speed", "totalPoints", 
                       "generation", "baseFriendship", "pokedexNumber"]:
                if key in binding:
                    stats[key] = int(float(binding[key]["value"]))

            for key in ["height", "weight"]:
                if key in binding:
                    stats[key] = float(binding[key]["value"])

            if "isLegendary" in binding:
                stats["isLegendary"] = binding["isLegendary"]["value"].lower() == "true"

            if "primaryType" in binding:
                stats["primaryType"] = binding["primaryType"]["value"].split("/")[-1]

            if "secondaryType" in binding:
                stats["secondaryType"] = binding["secondaryType"]["value"].split("/")[-1]

            # Process effectiveness data
            if "againstType" in binding and "value" in binding:
                type_uri = binding["againstType"]["value"]
                if "against" in type_uri:
                    type_name = type_uri.split("/")[-1].replace("against", "").lower()
                    val = float(binding["value"]["value"])
                    if val > 1.0:
                        stats["strongAgainst"].append(type_name)
                    elif 0.0 < val < 1.0:
                        stats["weakAgainst"].append(type_name)

        stats["strongAgainst"] = list(dict.fromkeys(stats["strongAgainst"]))
        stats["weakAgainst"] = list(dict.fromkeys(stats["weakAgainst"]))

        # Get same type Pokemon
        from app.sparql_client import get_same_type_pokemons
        same_type_pokemon = get_same_type_pokemons(pokemon_id)
        stats["sameTypePokemon"] = same_type_pokemon

        return stats

    
    @staticmethod
    def get_all_evolution_chains():
        query = """
        PREFIX pdx: <http://poked-x.org/pokemon/>
        PREFIX sc: <http://schema.org/>

        SELECT ?pokemon ?name ?number ?evolvesTo ?primaryType WHERE {
        {
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:primaryType ?primaryType ;
                    pdx:evolvesTo ?evolvesTo .
        }
        UNION
        {
            ?pokemon a pdx:Pokemon ;
                    sc:name ?name ;
                    pdx:pokedexNumber ?number ;
                    pdx:primaryType ?primaryType .
            ?other pdx:evolvesTo ?pokemon .
            OPTIONAL { ?pokemon pdx:evolvesTo ?evolvesTo }
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
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" ;
                       pdx:generation {value_uri} .
            }}
            """
        elif property_uri.endswith("isLegendary"):
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" ;
                       pdx:isLegendary {value_uri} .
            }}
            """
        elif property_uri.endswith("type"):
            # Convert pdx:Type/fire to <http://poked-x.org/pokemon/Type/fire>
            full_uri = f"<http://poked-x.org/pokemon/{value_uri.replace('pdx:', '')}>"
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" .
              {{
                FILTER EXISTS {{
                  ?pokemon pdx:primaryType {full_uri} .
                }}
              }}
              UNION
              {{
                FILTER EXISTS {{
                  ?pokemon pdx:secondaryType {full_uri} .
                }}
              }}
            }}
            """
        elif property_uri.endswith("ability"):
            # Convert pdx:Ability/overgrow to <http://poked-x.org/pokemon/Ability/overgrow>
            full_uri = f"<http://poked-x.org/pokemon/{value_uri.replace('pdx:', '')}>"
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" .
              {{
                FILTER EXISTS {{
                  ?pokemon pdx:ability1 {full_uri} .
                }}
              }}
              UNION
              {{
                FILTER EXISTS {{
                  ?pokemon pdx:ability2 {full_uri} .
                }}
              }}
            }}
            """
        elif property_uri.endswith("habitat"):
            # Convert pdx:Habitat/cave to <http://poked-x.org/pokemon/Habitat/cave>
            full_uri = f"<http://poked-x.org/pokemon/{value_uri.replace('pdx:', '')}>"
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" ;
                       pdx:habitat {full_uri} .
            }}
            """
        elif property_uri.endswith("weakAgainst"):
            # Extract type name from the URI and handle it appropriately
            type_name = value_uri.split('/')[-1]
            p = f"against{type_name.capitalize()}"
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" ;
                       pdx:effectiveness ?eff .
              ?eff pdx:{p} ?val .
              FILTER(?val > 1.0)
            }}
            """
        else:
            # Convert prefixed URIs to full URIs
            prop = property_uri.replace('pdx:', '')
            val = value_uri.replace('pdx:', '')
            full_val_uri = f"<http://poked-x.org/pokemon/{val}>"
            query = f"""
            PREFIX pdx: <http://poked-x.org/pokemon/>
            PREFIX sc: <http://schema.org/>
            ASK {{
              ?pokemon a pdx:Pokemon ;
                       sc:name "{n}" ;
                       pdx:{prop} {full_val_uri} .
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
