from SPARQLWrapper import POST, SPARQLWrapper, JSON, TURTLE
from django.conf import settings
from urllib.parse import quote

def run_query(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def run_query_describe(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat('n3')
    return sparql.query().convert().decode("utf-8")


def run_construct_query(query):
    sparql = SPARQLWrapper(settings.GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)
    return sparql.query().convert().decode("utf-8")


def run_update(update_string):
    sparql = SPARQLWrapper(settings.SPARQL_UPDATE_ENDPOINT)
    sparql.setQuery(update_string)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def normalize_dbpedia_resource(name):
    return [quote(name.strip().replace(" ", "_"))]



def get_dbpedia_info(pokemon_name, lang="pt"):
    dbpedia_sparql = SPARQLWrapper("https://dbpedia.org/sparql")

    for candidate in normalize_dbpedia_resource(pokemon_name):
        encoded_name = quote(candidate)
        dbpedia_sparql.setQuery(f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbr: <http://dbpedia.org/resource/>

            SELECT ?abstract ?designer ?firstAppearance WHERE {{
                dbr:{encoded_name} dbo:abstract ?abstract .
                OPTIONAL {{ dbr:{encoded_name} dbo:designer ?designer . }}
                OPTIONAL {{ dbr:{encoded_name} dbo:firstAppearance ?firstAppearance . }}
                FILTER (lang(?abstract) = '{lang}')
            }}
            LIMIT 1
        """)
        dbpedia_sparql.setReturnFormat(JSON)

        try:
            results = dbpedia_sparql.query().convert()
            bindings = results["results"]["bindings"]
            if not bindings:
                continue

            binding = bindings[0]
            description = binding.get("abstract", {}).get("value", "")
            designer_uri = binding.get("designer", {}).get("value", "")
            first_app_uri = binding.get("firstAppearance", {}).get("value", "")

            if "\n\n" in description:
                description = description.split("\n\n")[0]
            elif ". " in description:
                description = description.split(". ")[0] + "."

            return {
                "description": description,
                "designer": designer_uri.split("/")[-1].replace("_", " ") if designer_uri else "",
                "firstAppearance": first_app_uri.split("/")[-1].replace("_", " ") if first_app_uri else ""
            }
        except Exception as e:
            print(f"Erro ao obter info parcial da DBpedia para {candidate}: {e}")
            continue

    return {
        "description": f"Description of {pokemon_name} not found on DBpedia.",
        "designer": "",
        "firstAppearance": ""
    }


def get_full_dbpedia_info_turtle(pokemon_name):
    for candidate in normalize_dbpedia_resource(pokemon_name):
        encoded = quote(candidate)
        dbpedia_sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        dbpedia_sparql.setQuery(f"DESCRIBE dbr:{encoded}")
        dbpedia_sparql.setReturnFormat(TURTLE)

        try:
            data = dbpedia_sparql.query().convert().decode("utf-8")
            if data.strip():
                print(f"✅ Obtido DESCRIBE para dbr:{candidate}")
                return data
        except Exception as e:
            print(f"Erro ao obter DESCRIBE dbr:{candidate}: {e}")
            continue

    print(f"⚠️ Nenhum dado DESCRIBE encontrado para {pokemon_name}")
    return ""


def insert_turtle_to_graphdb(turtle_data):
    try:
        update_query = f"""
        INSERT DATA {{
            {turtle_data}
        }}
        """
        run_update(update_query)
        print("✅ Dados da DBpedia inseridos no GraphDB.")
    except Exception as e:
        print(f"❌ Erro ao inserir dados no GraphDB: {e}")


def dbpedia_data_already_loaded(pokemon_name):
    for candidate in normalize_dbpedia_resource(pokemon_name):
        ask_query = f"""
        ASK {{
            <http://dbpedia.org/resource/{candidate}> ?p ?o .
        }}
        """
        try:
            result = run_query(ask_query)
            if result.get("boolean", False):
                print(f"🔍 Dados já existem no GraphDB para {candidate}")
                return True
        except Exception as e:
            print(f"Erro na verificação para {candidate}: {e}")
            continue

    print(f"📂 Nenhum dado existente no GraphDB para '{pokemon_name}'")
    return False

@staticmethod
def get_same_type_pokemons(pokemon_id):
    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?otherName WHERE {{
        <http://poked-x.org/pokemon/Pokemon/{pokemon_id}> pdx:primaryType ?type .
        ?other pdx:primaryType ?type ;
               sc:name ?otherName .
        FILTER(<http://poked-x.org/pokemon/Pokemon/{pokemon_id}> != ?other)
    }}
    ORDER BY RAND()
    LIMIT 1
    """
    results = run_query(query)
    if results["results"]["bindings"]:
        return results["results"]["bindings"][0]["otherName"]["value"]
    return None

def get_pokemon_role(pokemon_id):
    query = """
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?role WHERE {
        <http://poked-x.org/pokemon/Pokemon/""" + str(pokemon_id) + """> pdx:stats ?stats .
        ?stats pdx:hp ?hp ;
               pdx:attack ?atk ;
               pdx:defense ?def ;
               pdx:spAttack ?spAtk ;
               pdx:spDefense ?spDef ;
               pdx:speed ?spd .
        
        BIND(
            IF(?hp > 80 && ?def > 70 && ?spDef > 70, "Tank",
            IF(?spd > 90 && (?atk > 80 || ?spAtk > 80), "Speedster",
            IF((?atk > 90 || ?spAtk > 90) && ?spd > 70, "Sweeper",
            IF(?def > 90 && ?spDef > 90, "Wall",
            IF((?atk + ?spAtk + ?spd + ?def + ?spDef + ?hp) > 500, "All-Rounder",
            "Support"))))) as ?role
        )
    }
    """
    results = run_query(query)
    if results["results"]["bindings"]:
        return results["results"]["bindings"][0]["role"]["value"]
    return "Unknown"

def get_team_coverage(pokemon_ids):
    ids_list = ", ".join(f"<http://poked-x.org/pokemon/Pokemon/{id}>" for id in pokemon_ids)
    query = f"""
    PREFIX pdx: <http://poked-x.org/pokemon/>
    PREFIX sc: <http://schema.org/>

    SELECT DISTINCT ?type (COUNT(DISTINCT ?pokemon) as ?count) WHERE {{
        VALUES ?pokemon {{ {ids_list} }}
        {{
            ?pokemon pdx:strongAgainst ?type .
        }} UNION {{
            ?pokemon pdx:weakAgainst ?type .
        }}
    }}
    GROUP BY ?type
    """
    results = run_query(query)
    coverage = {
        "offensive": set(),
        "defensive": set()
    }
    
    for binding in results["results"]["bindings"]:
        type_name = binding["type"]["value"].split("/")[-1]
        count = int(binding["count"]["value"])
        if count > 0:
            coverage["offensive"].add(type_name)
            if count >= 2:  # If multiple Pokémon can handle this type
                coverage["defensive"].add(type_name)
    
    return coverage

def analyze_team_roles(pokemon_ids):
    roles = {}
    for pid in pokemon_ids:
        role = get_pokemon_role(pid)
        roles[role] = roles.get(role, 0) + 1
    return roles
