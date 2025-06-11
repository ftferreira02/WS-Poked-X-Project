"""
Aplicador de regras SPIN independente do Django
"""
from SPARQLWrapper import POST, SPARQLWrapper, JSON, TURTLE
import rdflib
from rdflib import Graph, Namespace
from rdflib.namespace import XSD

# Configurações do GraphDB - ajuste conforme necessário
GRAPHDB_ENDPOINT = "http://graphdb:7200/repositories/Poked-X"
SPARQL_UPDATE_ENDPOINT = "http://graphdb:7200/repositories/Poked-X/statements"

def run_query(query):
    """Executa uma query SPARQL SELECT"""
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def run_construct_query(query):
    """Executa uma query SPARQL CONSTRUCT"""
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(TURTLE)
    return sparql.query().convert().decode("utf-8")

def run_update(update_string):
    sparql = SPARQLWrapper(SPARQL_UPDATE_ENDPOINT)
    sparql.setQuery(update_string)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def extract_construct_queries_from_spin(spin_file_path):
    """
    Extrai as consultas CONSTRUCT do arquivo SPIN TTL e adiciona os prefixos necessários
    """
    g = Graph()
    g.parse(spin_file_path, format="turtle")
    
    # Definir namespaces
    SP = Namespace("http://spinrdf.org/sp#")
    
    # Prefixos necessários para as consultas
    prefixes = """PREFIX pdx: <http://poked-x.org/pokemon/>
PREFIX sc: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

"""
    
    # Encontrar todas as consultas CONSTRUCT
    construct_queries = []
    
    for subj, pred, obj in g.triples((None, SP.text, None)):
        query_text = str(obj).strip()
        
        # Adicionar prefixos se não estiverem presentes
        if not query_text.startswith("PREFIX"):
            full_query = prefixes + query_text
        else:
            full_query = query_text
            
        construct_queries.append(full_query)
    
    return construct_queries

def apply_spin_rules(spin_file_path="spin-rules.ttl", dry_run=False):
    """
    Aplica as regras SPIN ao GraphDB
    
    Args:
        spin_file_path: Caminho para o arquivo SPIN TTL
        dry_run: Se True, apenas mostra as consultas sem executar
    """
    
    print("🔄 Extraindo regras SPIN...")
    queries = extract_construct_queries_from_spin(spin_file_path)
    
    print(f"📋 Encontradas {len(queries)} regras SPIN")
    
    results = {}
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Executando regra {i}:")
        print("─" * 50)
        print(query)
        print("─" * 50)
        
        if dry_run:
            print("⏸️  Modo dry-run - consulta não executada")
            continue
            
        try:
            # Executar a consulta CONSTRUCT
            turtle_result = run_construct_query(query)
            
            if turtle_result.strip():
                print(f"✅ Regra {i} gerou novos triplos:")
                print(turtle_result[:200] + "..." if len(turtle_result) > 200 else turtle_result)
                
                # Inserir os novos triplos no GraphDB
                insert_query = f"""
                INSERT DATA {{
                    {turtle_result}
                }}
                """
                
                run_update(insert_query)
                print(f"✅ Triplos da regra {i} inseridos no GraphDB")
                
                results[f"rule_{i}"] = {
                    "status": "success",
                    "triples_generated": turtle_result.count('\n'),
                    "query": query
                }
            else:
                print(f"ℹ️  Regra {i} não gerou novos triplos")
                results[f"rule_{i}"] = {
                    "status": "no_results",
                    "query": query
                }
                
        except Exception as e:
            print(f"❌ Erro ao executar regra {i}: {e}")
            results[f"rule_{i}"] = {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    return results

def apply_specific_rule(rule_name, spin_file_path="spin-rules.ttl"):
    """
    Aplica uma regra específica baseada no nome
    """
    
    # Mapear nomes de regras para índices
    rule_mapping = {
        "legendary": 0,      # InferLegendaryPokemon
        "strong_against": 1, # InferStrongAgainst  
        "same_type": 2,      # InferHasSameTypeAs
        "strong": 3,         # InferStrongPokemon
        "old_gen": 4,        # InferOldGeneration
        "shared_type": 5,    # InferSharedPrimaryType
        "fast": 6,           # InferFastPokemon
        "mixed_type": 7      # InferMixedType
    }
    
    if rule_name not in rule_mapping:
        print(f"❌ Regra '{rule_name}' não encontrada. Regras disponíveis: {list(rule_mapping.keys())}")
        return
    
    queries = extract_construct_queries_from_spin(spin_file_path)
    rule_index = rule_mapping[rule_name]
    
    if rule_index >= len(queries):
        print(f"❌ Índice da regra {rule_index} fora do intervalo")
        return
    
    query = queries[rule_index]
    print(f"🔍 Executando regra '{rule_name}':")
    print("─" * 50)
    print(query)
    print("─" * 50)
    
    try:
        turtle_result = run_construct_query(query)
        
        if turtle_result.strip():
            print(f"✅ Regra '{rule_name}' gerou novos triplos")
            
            insert_query = f"""
            INSERT DATA {{
                {turtle_result}
            }}
            """
            
            run_update(insert_query)
            print(f"✅ Triplos inseridos no GraphDB")
            
            return turtle_result
        else:
            print(f"ℹ️  Regra '{rule_name}' não gerou novos triplos")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao executar regra '{rule_name}': {e}")
        return None

def verify_inferred_data():
    """
    Verifica se as inferências foram aplicadas corretamente
    """
    
    verification_queries = {
        "legendary_pokemon": """
            PREFIX pdx: <http://poked-x.org/pokemon/>
            SELECT (COUNT(?p) as ?count) WHERE {
                ?p a pdx:LegendaryPokemon .
            }
        """,
        
        "strong_types": """
            PREFIX pdx: <http://poked-x.org/pokemon/>
            SELECT (COUNT(?relation) as ?count) WHERE {
                ?type1 pdx:strongAgainst ?type2 .
                BIND(CONCAT(STR(?type1), " -> ", STR(?type2)) as ?relation)
            }
        """,
        
        "same_type_relations": """
            PREFIX pdx: <http://poked-x.org/pokemon/>
            SELECT (COUNT(?relation) as ?count) WHERE {
                ?p1 pdx:hasSameTypeAs ?p2 .
                BIND(CONCAT(STR(?p1), " <-> ", STR(?p2)) as ?relation)
            }
        """,
        
        "strong_pokemon": """
            PREFIX pdx: <http://poked-x.org/pokemon/>
            SELECT (COUNT(?p) as ?count) WHERE {
                ?p pdx:isStrong true .
            }
        """,
        
        "fast_pokemon": """
            PREFIX pdx: <http://poked-x.org/pokemon/>
            SELECT (COUNT(?p) as ?count) WHERE {
                ?p pdx:isFast true .
            }
        """
    }
    
    print("🔍 Verificando dados inferidos...")
    
    for name, query in verification_queries.items():
        try:
            result = run_query(query)
            count = result["results"]["bindings"][0]["count"]["value"]
            print(f"📊 {name}: {count} triplos inferidos")
        except Exception as e:
            print(f"❌ Erro ao verificar {name}: {e}")

def configure_endpoints(graphdb_endpoint=None, update_endpoint=None):
    """
    Configura os endpoints do GraphDB
    """
    global GRAPHDB_ENDPOINT, SPARQL_UPDATE_ENDPOINT
    
    if graphdb_endpoint:
        GRAPHDB_ENDPOINT = graphdb_endpoint
    if update_endpoint:
        SPARQL_UPDATE_ENDPOINT = update_endpoint
    
    print(f"🔧 GraphDB Query Endpoint: {GRAPHDB_ENDPOINT}")
    print(f"🔧 GraphDB Update Endpoint: {SPARQL_UPDATE_ENDPOINT}")

# Exemplo de uso
if __name__ == "__main__":
    print("🚀 Aplicador de Regras SPIN (Standalone)")
    print("=" * 50)
    
    # Configurar endpoints se necessário
    # configure_endpoints(
    #     "http://localhost:7200/repositories/Poked-X",
    #     "http://localhost:7200/repositories/Poked-X/statements"
    # )
    
    # Aplicar todas as regras
    print("\n1. Aplicando todas as regras SPIN...")
    results = apply_spin_rules("dataBase/spin-rules.ttl", dry_run=False)
    
    # Verificar resultados
    print("\n2. Verificando dados inferidos...")
    verify_inferred_data()
    
    # Exemplo de aplicação de regra específica
    # apply_specific_rule("legendary", "dataBase/spin-rules.ttl")