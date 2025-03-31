// fight.js
let battleLogs = window.battleLogs || [];
let hpProgress = window.hpProgress || [];
let winner = window.winner || "";
let turn = 0;

function nextTurn() {
  const battleMessage = document.getElementById('battle-message');
  const hp1 = document.getElementById('hp1');
  const hp2 = document.getElementById('hp2');

  if (turn < battleLogs.length) {
    const message = battleLogs[turn];
    typeText(battleMessage, message);
    
    const index = Math.floor(turn / 2);
    if (hpProgress[index]) {
      hp1.textContent = hpProgress[index].hp1;
      hp2.textContent = hpProgress[index].hp2;
    }
    turn++;
  } else {
    const last = hpProgress[hpProgress.length - 1];
    hp1.textContent = last.hp1;
    hp2.textContent = last.hp2;

    battleMessage.textContent = "🏆 " + winner + " won the battle!";
    document.getElementById("next-btn").disabled = true;
  }
}

function typeText(element, text, speed = 20, callback = null) {
  element.textContent = "";
  let i = 0;
  const interval = setInterval(() => {
    element.textContent += text.charAt(i);
    i++;
    if (i >= text.length) {
      clearInterval(interval);
      if (callback) callback();
    }
  }, speed);
}

function typeColor(type) {
  const colors = {
    fire: "#F08030", water: "#6890F0", grass: "#78C850", electric: "#F8D030",
    flying: "#A890F0", normal: "#A8A878", fighting: "#C03028", ground: "#E0C068",
    rock: "#B8A038", psychic: "#F85888", ghost: "#705898", dark: "#705848",
    steel: "#B8B8D0", fairy: "#EE99AC", dragon: "#7038F8", ice: "#98D8D8",
    bug: "#A8B820", poison: "#A040A0"
  };
  return colors[type.toLowerCase()] || "#444";
}

document.addEventListener('DOMContentLoaded', function () {
  // Aplica cores aos tipos
  document.querySelectorAll('[data-type]').forEach(button => {
    const type = button.getAttribute('data-type');
    button.style.backgroundColor = typeColor(type);
  });

  // Escala dos Pokémon
  const height1 = parseFloat(document.getElementById('player-img').dataset.height || "1");
  const height2 = parseFloat(document.getElementById('opponent-img').dataset.height || "1");

  const averageHeight = (height1 + height2) / 2;
  let maxVisualHeight = 400;

  if (averageHeight < 1.0) {
    maxVisualHeight = 280;
  } else if (averageHeight < 1.5) {
    maxVisualHeight = 340;
  }

  const playerRatio = height1 / Math.max(height1, height2);
  const opponentRatio = height2 / Math.max(height1, height2);

  const scale1 = playerRatio * maxVisualHeight;
  const scale2 = opponentRatio * maxVisualHeight * 0.85;

  const playerImg = document.getElementById('player-img');
  const opponentImg = document.getElementById('opponent-img');

  if (playerImg) {
    animatePokemonEntry(playerImg, scale1);
  }
  if (opponentImg) {
    animatePokemonEntry(opponentImg, scale2);
  }
  


  function animatePokemonEntry(pokemonImg, targetHeight) {
  pokemonImg.style.height = '0px';
  pokemonImg.style.opacity = '0';

  pokemonImg.style.setProperty('--target-height', `${targetHeight}px`);

  // Adiciona a classe animada um pouco depois (força reflow)
  setTimeout(() => {
    pokemonImg.style.animation = 'growIn 1.5s forwards';
  }, 100); // pequeno delay para garantir renderização inicial
}

  

  // Começa com a primeira mensagem
  nextTurn();
});

function animatePokemonEntry(pokemonImg, targetHeight) {
  pokemonImg.style.height = '0px';
  pokemonImg.style.opacity = '0';

  pokemonImg.style.setProperty('--target-height', `${targetHeight}px`);

  // Adiciona a classe animada um pouco depois (força reflow)
  setTimeout(() => {
    pokemonImg.style.animation = 'growIn 1.5s forwards';
  }, 100); // pequeno delay para garantir renderização inicial
}
