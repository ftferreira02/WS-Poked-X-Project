# app/forms.py
from django import forms
from app.models.geral_model import PokemonManager


class PokemonSearchForm(forms.Form):
    name = forms.CharField(label='Pesquisar por nome', max_length=100, required=False)


class PokemonSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get all Pokémon for the dropdown options
        pokemons = PokemonManager.get_all_pokemons()
        pokemon_choices = [(pokemon.id, pokemon.name) for pokemon in pokemons]
        
        # Create the selection fields
        self.fields['pokemon1'] = forms.ChoiceField(
            label='Select first Pokémon',
            choices=pokemon_choices,
            required=True,
            widget=forms.Select(attrs={'class': 'pokemon-select'})
        )
        
        self.fields['pokemon2'] = forms.ChoiceField(
            label='Select second Pokémon',
            choices=pokemon_choices,
            required=True,
            widget=forms.Select(attrs={'class': 'pokemon-select'})
        )