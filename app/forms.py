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
    
class ComparePokemonForm(forms.Form):
    pokemons = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'size': 10}),
        label="Select up to 5 Pokémon"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.geral_model import PokemonManager  # avoid circular import
        all_pokemons = PokemonManager.get_all_pokemons()
        self.fields['pokemons'].choices = [
            (str(p.number), f"#{p.number} - {p.name}") for p in all_pokemons
        ]

    def clean_pokemons(self):
        selected = self.cleaned_data['pokemons']
        if len(selected) > 5:
            raise forms.ValidationError("You can only select up to 5 Pokémon.")
        return selected
