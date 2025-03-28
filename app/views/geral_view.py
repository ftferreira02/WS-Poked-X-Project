from django.shortcuts import render
from app.sparql_client import run_query

def search_pokemon(request):
    # Obter o parâmetro 'name' do formulário (filtro de pesquisa)
    name_filter = request.GET.get('name', '').strip()  # Remover espaços extras

    # Definir a consulta base SPARQL
    query = """
    PREFIX ex: <http://example.org/pokemon/>
    PREFIX sc: <http://schema.org/>

    SELECT ?pokemon ?name WHERE {
      ?pokemon a ex:Pokemon .
      ?pokemon sc:name ?name .
    """
    
    # Se o filtro 'name' estiver presente, adicionar um filtro à consulta
    if name_filter:
        query += f"""
        FILTER CONTAINS(LCASE(?name), LCASE("{name_filter}"))
        """

    # Fechar a query
    query += "}"

    # Passar o nome do filtro como parâmetro da consulta SPARQL
    results = run_query(query)

    # Processar os resultados e pegar o nome do Pokémon
    pokemons = [binding["name"]["value"] for binding in results["results"]["bindings"]]

    # Retornar o template com os resultados e o filtro atual
    return render(request, 'pokemon_search_form.html', {'pokemons': pokemons, 'name_filter': name_filter})
