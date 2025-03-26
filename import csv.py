import csv
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

g = Graph()
EX = Namespace("http://example.org/pokemon#")
g.bind("ex", EX)

with open("pokedex.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["name"]
        pokemon_uri = EX[name.replace(" ", "_")]
        g.add((pokemon_uri, RDF.type, EX.Pokemon))
        g.add((pokemon_uri, EX.hasName, Literal(name)))
        g.add((pokemon_uri, EX.pokedexNumber, Literal(row["pokedex_number"], datatype=XSD.integer)))
        g.add((pokemon_uri, EX.hasHeight, Literal(row["height_m"], datatype=XSD.decimal)))
        g.add((pokemon_uri, EX.hasType, EX[row["type_1"]]))
        if row["type_2"]:
            g.add((pokemon_uri, EX.hasType, EX[row["type_2"]]))

g.serialize(destination="pokemon.ttl", format="turtle")
