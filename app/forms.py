# app/forms.py
from django import forms

class PokemonSearchForm(forms.Form):
    name = forms.CharField(label='Pesquisar por nome', max_length=100, required=False)

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