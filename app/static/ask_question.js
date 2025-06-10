document.addEventListener('DOMContentLoaded', function() {
    const propertyValues = {
      'http://poked-x.org/pokemon/type': [
        { label: 'Fire', uri: 'http://poked-x.org/pokemon/Type/fire' },
        { label: 'Water', uri: 'http://poked-x.org/pokemon/Type/water' },
        { label: 'Grass', uri: 'http://poked-x.org/pokemon/Type/grass' },
        { label: 'Poison', uri: 'http://poked-x.org/pokemon/Type/poison' },
        { label: 'Psychic', uri: 'http://poked-x.org/pokemon/Type/psychic' },
        { label: 'Electric', uri: 'http://poked-x.org/pokemon/Type/electric' },
        { label: 'Ground', uri: 'http://poked-x.org/pokemon/Type/ground' },
        { label: 'Fighting', uri: 'http://poked-x.org/pokemon/Type/fighting' },
        { label: 'Normal', uri: 'http://poked-x.org/pokemon/Type/normal' },
        { label: 'Flying', uri: 'http://poked-x.org/pokemon/Type/flying' },
        { label: 'Rock', uri: 'http://poked-x.org/pokemon/Type/rock' },
        { label: 'Bug', uri: 'http://poked-x.org/pokemon/Type/bug' },
        { label: 'Ghost', uri: 'http://poked-x.org/pokemon/Type/ghost' },
        { label: 'Ice', uri: 'http://poked-x.org/pokemon/Type/ice' },
        { label: 'Dragon', uri: 'http://poked-x.org/pokemon/Type/dragon' },
        { label: 'Dark', uri: 'http://poked-x.org/pokemon/Type/dark' },
        { label: 'Steel', uri: 'http://poked-x.org/pokemon/Type/steel' },
        { label: 'Fairy', uri: 'http://poked-x.org/pokemon/Type/fairy' }
      ],
      'http://poked-x.org/pokemon/generation': [
        { label: 'Generation 1', uri: '1' },
        { label: 'Generation 2', uri: '2' },
        { label: 'Generation 3', uri: '3' },
        { label: 'Generation 4', uri: '4' },
        { label: 'Generation 5', uri: '5' },
        { label: 'Generation 6', uri: '6' },
        { label: 'Generation 7', uri: '7' },
        { label: 'Generation 8', uri: '8' }
      ],
      'http://poked-x.org/pokemon/isLegendary': [
        { label: 'Yes', uri: 'true' },
        { label: 'No', uri: 'false' }
      ],
      'http://poked-x.org/pokemon/habitat': [
        { label: 'Cave', uri: 'http://poked-x.org/pokemon/habitat/cave' },
        { label: 'Forest', uri: 'http://poked-x.org/pokemon/habitat/forest' },
        { label: 'Grassland', uri: 'http://poked-x.org/pokemon/habitat/grassland' },
        { label: 'Mountain', uri: 'http://poked-x.org/pokemon/habitat/mountain' },
        { label: 'Rare', uri: 'http://poked-x.org/pokemon/habitat/rare' },
        { label: 'Rough Terrain', uri: 'http://poked-x.org/pokemon/habitat/roughterrain' },
        { label: 'Sea', uri: 'http://poked-x.org/pokemon/habitat/sea' },
        { label: 'Urban', uri: 'http://poked-x.org/pokemon/habitat/urban' },
        { label: 'Waters Edge', uri: 'http://poked-x.org/pokemon/habitat/watersedge' }
      ],
      'http://poked-x.org/pokemon/ability': [
        { label: 'Overgrow', uri: 'http://poked-x.org/pokemon/Ability/overgrow' },
        { label: 'Blaze', uri: 'http://poked-x.org/pokemon/Ability/blaze' },
        { label: 'Torrent', uri: 'http://poked-x.org/pokemon/Ability/torrent' },
        { label: 'Chlorophyll', uri: 'http://poked-x.org/pokemon/Ability/chlorophyll' },
        { label: 'Levitate', uri: 'http://poked-x.org/pokemon/Ability/levitate' },
        { label: 'Lightning Rod', uri: 'http://poked-x.org/pokemon/Ability/lightningrod' },
        { label: 'Run Away', uri: 'http://poked-x.org/pokemon/Ability/run_away' },
        { label: 'Pastel Veil', uri: 'http://poked-x.org/pokemon/Ability/pastel_veil' },
        { label: 'Intimidate', uri: 'http://poked-x.org/pokemon/Ability/intimidate' },
        { label: 'Shield Dust', uri: 'http://poked-x.org/pokemon/Ability/shielddust' }
      ],
      'http://poked-x.org/pokemon/weakAgainst': [
        { label: 'Fire', uri: 'http://poked-x.org/pokemon/Type/fire' },
        { label: 'Water', uri: 'http://poked-x.org/pokemon/Type/water' },
        { label: 'Electric', uri: 'http://poked-x.org/pokemon/Type/electric' },
        { label: 'Ground', uri: 'http://poked-x.org/pokemon/Type/ground' },
        { label: 'Psychic', uri: 'http://poked-x.org/pokemon/Type/psychic' },
        { label: 'Rock', uri: 'http://poked-x.org/pokemon/Type/rock' },
        { label: 'Flying', uri: 'http://poked-x.org/pokemon/Type/flying' },
        { label: 'Steel', uri: 'http://poked-x.org/pokemon/Type/steel' },
        { label: 'Grass', uri: 'http://poked-x.org/pokemon/Type/grass' }
      ]
    };
  
    const propertyItems = document.querySelectorAll('.property-item');
    const propertyInput = document.getElementById('property');
    const valueContainer = document.getElementById('value-container');
    const valueSelect = document.getElementById('value');
    const propertyLabel = document.getElementById('property-label');
    const valueLabel = document.getElementById('value-label');
    const pokemonInput = document.getElementById('pokemon');
    const autocompleteList = document.getElementById('autocomplete-list');
    const allPokemonNamesSet = new Set(allPokemonNames || []);
  
    const currentProperty = propertyInput.value;
    if (currentProperty && propertyValues[currentProperty]) {
      populateValueSelect(currentProperty);
      valueContainer.style.display = 'block';
    }
  
    propertyItems.forEach(item => {
      item.addEventListener('click', function() {
        propertyItems.forEach(i => i.classList.remove('selected'));
        this.classList.add('selected');
        const uri = this.getAttribute('data-uri');
        propertyInput.value = uri;
        propertyLabel.textContent = this.innerText.trim();
        populateValueSelect(uri);
        valueContainer.style.display = 'block';
      });
    });
  
    valueSelect.addEventListener('change', function() {
      valueLabel.textContent = valueSelect.options[valueSelect.selectedIndex].text;
    });
  
    function populateValueSelect(uri) {
      valueSelect.innerHTML = '<option value="">Select a value</option>';
      const possibleOptions = propertyValues[uri] || [];
      possibleOptions.forEach(optObj => {
        const option = document.createElement('option');
        option.value = optObj.uri;
        option.textContent = optObj.label;
        valueSelect.appendChild(option);
      });
      valueLabel.textContent = '...';
    }
  
    pokemonInput.addEventListener('input', function() {
      const val = pokemonInput.value.trim().toLowerCase();
      autocompleteList.innerHTML = '';
      if (!val) {
        autocompleteList.style.display = 'none';
        return;
      }
      const matches = [...allPokemonNamesSet].filter(name =>
        name.toLowerCase().includes(val)
      );
      if (!matches.length) {
        autocompleteList.style.display = 'none';
        return;
      }
      matches.forEach(name => {
        const item = document.createElement('div');
        item.classList.add('autocomplete-item');
        item.textContent = name;
        item.addEventListener('click', function() {
          pokemonInput.value = name;
          autocompleteList.innerHTML = '';
          autocompleteList.style.display = 'none';
        });
        autocompleteList.appendChild(item);
      });
      autocompleteList.style.display = 'block';
    });
  
    document.addEventListener('click', function(e) {
      if (e.target !== pokemonInput) {
        autocompleteList.innerHTML = '';
        autocompleteList.style.display = 'none';
      }
    });
  });
  