# app/forms.py
from django import forms

class PokemonSearchForm(forms.Form):
    name = forms.CharField(label='Pesquisar por nome', max_length=100, required=False)
