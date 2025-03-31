# app/forms.py
from django import forms
from app.models.geral_model import PokemonManager


class PokemonSearchForm(forms.Form):
    name = forms.CharField(label='Pesquisar por nome', max_length=100, required=False)


class PokemonSelectionForm(forms.Form):
    pokemon1 = forms.CharField(
        label='Enter first Pokémon name', 
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'pokemon-input', 'placeholder': 'Type to search...'})
    )
    
    pokemon2 = forms.CharField(
        label='Enter second Pokémon name', 
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'pokemon-input', 'placeholder': 'Type to search...'})
    )
    
    # Hidden fields to store the selected Pokemon IDs
    pokemon1_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    pokemon2_id = forms.CharField(widget=forms.HiddenInput(), required=True)