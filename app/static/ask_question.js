document.addEventListener('DOMContentLoaded', function() {
    const propertyValues = {
      'pdx:type': [
        { label: 'Fire', uri: 'pdx:Type/fire' },
        { label: 'Water', uri: 'pdx:Type/water' },
        { label: 'Grass', uri: 'pdx:Type/grass' },
        { label: 'Poison', uri: 'pdx:Type/poison' },
        { label: 'Psychic', uri: 'pdx:Type/psychic' },
        { label: 'Electric', uri: 'pdx:Type/electric' },
        { label: 'Ground', uri: 'pdx:Type/ground' },
        { label: 'Fighting', uri: 'pdx:Type/fighting' },
        { label: 'Normal', uri: 'pdx:Type/normal' },
        { label: 'Flying', uri: 'pdx:Type/flying' },
        { label: 'Rock', uri: 'pdx:Type/rock' },
        { label: 'Bug', uri: 'pdx:Type/bug' },
        { label: 'Ghost', uri: 'pdx:Type/ghost' },
        { label: 'Ice', uri: 'pdx:Type/ice' },
        { label: 'Dragon', uri: 'pdx:Type/dragon' },
        { label: 'Dark', uri: 'pdx:Type/dark' },
        { label: 'Steel', uri: 'pdx:Type/steel' },
        { label: 'Fairy', uri: 'pdx:Type/fairy' }
      ],
      'pdx:generation': [
        { label: 'Generation 1', uri: '1' },
        { label: 'Generation 2', uri: '2' },
        { label: 'Generation 3', uri: '3' },
        { label: 'Generation 4', uri: '4' },
        { label: 'Generation 5', uri: '5' },
        { label: 'Generation 6', uri: '6' },
        { label: 'Generation 7', uri: '7' },
        { label: 'Generation 8', uri: '8' }
      ],
      'pdx:isLegendary': [
        { label: 'Yes', uri: 'true' },
        { label: 'No', uri: 'false' }
      ],
      'pdx:habitat': [
        { label: 'Cave', uri: 'pdx:Habitat/cave' },
        { label: 'Forest', uri: 'pdx:Habitat/forest' },
        { label: 'Grassland', uri: 'pdx:Habitat/grassland' },
        { label: 'Mountain', uri: 'pdx:Habitat/mountain' },
        { label: 'Rare', uri: 'pdx:Habitat/rare' },
        { label: 'Rough Terrain', uri: 'pdx:Habitat/roughterrain' },
        { label: 'Sea', uri: 'pdx:Habitat/sea' },
        { label: 'Urban', uri: 'pdx:Habitat/urban' },
        { label: 'Waters Edge', uri: 'pdx:Habitat/watersedge' }
      ],
      'pdx:ability': [
        { label: 'Overgrow', uri: 'pdx:Ability/overgrow' },
        { label: 'Blaze', uri: 'pdx:Ability/blaze' },
        { label: 'Torrent', uri: 'pdx:Ability/torrent' },
        { label: 'Chlorophyll', uri: 'pdx:Ability/chlorophyll' },
        { label: 'Levitate', uri: 'pdx:Ability/levitate' },
        { label: 'Lightning Rod', uri: 'pdx:Ability/lightningrod' },
        { label: 'Run Away', uri: 'pdx:Ability/run_away' },
        { label: 'Pastel Veil', uri: 'pdx:Ability/pastel_veil' },
        { label: 'Intimidate', uri: 'pdx:Ability/intimidate' },
        { label: 'Shield Dust', uri: 'pdx:Ability/shielddust' },
        { label: 'Static', uri: 'pdx:Ability/static' },
        { label: 'Sand Veil', uri: 'pdx:Ability/sand_veil' },
        { label: 'Keen Eye', uri: 'pdx:Ability/keen_eye' },
        { label: 'Inner Focus', uri: 'pdx:Ability/inner_focus' },
        { label: 'Synchronize', uri: 'pdx:Ability/synchronize' },
        { label: 'Clear Body', uri: 'pdx:Ability/clear_body' },
        { label: 'Rock Head', uri: 'pdx:Ability/rock_head' },
        { label: 'Sturdy', uri: 'pdx:Ability/sturdy' },
        { label: 'Swift Swim', uri: 'pdx:Ability/swift_swim' },
        { label: 'Battle Armor', uri: 'pdx:Ability/battle_armor' }
      ],
      'pdx:weakAgainst': [
        { label: 'Fire', uri: 'pdx:Type/fire' },
        { label: 'Water', uri: 'pdx:Type/water' },
        { label: 'Grass', uri: 'pdx:Type/grass' },
        { label: 'Poison', uri: 'pdx:Type/poison' },
        { label: 'Psychic', uri: 'pdx:Type/psychic' },
        { label: 'Electric', uri: 'pdx:Type/electric' },
        { label: 'Ground', uri: 'pdx:Type/ground' },
        { label: 'Fighting', uri: 'pdx:Type/fighting' },
        { label: 'Normal', uri: 'pdx:Type/normal' },
        { label: 'Flying', uri: 'pdx:Type/flying' },
        { label: 'Rock', uri: 'pdx:Type/rock' },
        { label: 'Bug', uri: 'pdx:Type/bug' },
        { label: 'Ghost', uri: 'pdx:Type/ghost' },
        { label: 'Ice', uri: 'pdx:Type/ice' },
        { label: 'Dragon', uri: 'pdx:Type/dragon' },
        { label: 'Dark', uri: 'pdx:Type/dark' },
        { label: 'Steel', uri: 'pdx:Type/steel' },
        { label: 'Fairy', uri: 'pdx:Type/fairy' }
      ]
    };
  
    const pokemonInput = document.getElementById('pokemon');
    const valueSelect = document.getElementById('value');
    const valueContainer = document.getElementById('value-container');
    const propertyLabel = document.getElementById('property-label');
    const valueLabel = document.getElementById('value-label');
    const autocompleteList = document.getElementById('autocomplete-list');
    const allPokemonNamesSet = new Set(allPokemonNames);
  
    // Property selection
    document.querySelectorAll('.property-item').forEach(item => {
      item.addEventListener('click', function() {
        // Remove active class from all items
        document.querySelectorAll('.property-item').forEach(i => i.classList.remove('active'));
        
        // Add active class to clicked item
        this.classList.add('active');
        
        // Get the property URI and update the hidden input
        const propertyUri = this.getAttribute('data-uri');
        document.getElementById('property').value = propertyUri;
        
        // Update the property label in the question
        propertyLabel.textContent = this.textContent.trim();
        
        // Show value selection and populate options
        valueContainer.style.display = 'block';
        populateValueSelect(propertyUri);
      });
    });
  
    valueSelect.addEventListener('change', function() {
      valueLabel.textContent = valueSelect.options[valueSelect.selectedIndex].text;
    });
  
    function populateValueSelect(uri) {
      console.log('Populating values for URI:', uri);
      valueSelect.innerHTML = '<option value="">Select a value</option>';
      const possibleOptions = propertyValues[uri] || [];
      console.log('Available options:', possibleOptions);
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
  