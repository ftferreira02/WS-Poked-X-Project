
from django.shortcuts import render
from app.forms import PokemonSearchForm
from app.sparql_client import run_query

def search_pokemon(request):
    pokemons = []
    name_filter = ''
    
    # Instanciando o formulário
    form = PokemonSearchForm(request.GET)
    
    if form.is_valid():
        name_filter = form.cleaned_data['name']
        
        query = """
        PREFIX ex: <http://example.org/pokemon/>
        PREFIX sc: <http://schema.org/>
        
        SELECT ?pokemon ?name WHERE {
          ?pokemon a ex:Pokemon .
          ?pokemon sc:name ?name .
        """
        
        if name_filter:
            query += f"""
            FILTER CONTAINS(LCASE(?name), LCASE("{name_filter}"))
            """
        
        query += "}"
        
        # Executa a consulta SPARQL
        results = run_query(query)
        
        # Processa os resultados
        pokemons = [binding["name"]["value"] for binding in results["results"]["bindings"]]
    
    # Passa o formulário e os Pokémon encontrados para o template
    return render(request, 'pokemon_search_form.html', {'form': form, 'pokemons': pokemons})
