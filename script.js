// Banco de dados dos pontos turísticos de Manaus
const manausLocations = {
  1: {
    name: "Teatro Amazonas",
    category: "História & Arquitetura",
    description: "Inaugurado em 1896 durante o Ciclo da Borracha, é o principal símbolo cultural do Amazonas e famoso por sua cúpula com as cores da bandeira do Brasil.",
    challenge: "Identifique as peças da cúpula do Teatro e responda qual estilo arquitetônico predominante marca sua construção!"
  },
  2: {
    name: "Mercado Municipal Adolpho Lisboa",
    category: "Gastronomia & Tradição",
    description: "Inspirado no antigo mercado Les Halles de Paris e às margens do Rio Negro, é o centro de sabores, ervas medicinais e artesanato de Manaus.",
    challenge: "Encontre os ingredientes tradicionais para preparar um autêntico Tacacá e um peixe assado na brasa!"
  },
  3: {
    name: "Praia da Ponta Negra",
    category: "Lazer & Natureza",
    description: "Complexo turístico às margens do Rio Negro, famoso pelo seu calçadão de pedras portuguesas, pôr do sol inesquecível e eventos culturais.",
    challenge: "Caminhe pelo calçadão ao pôr do sol e registre a foto perfeita do horizonte sobre as águas escuras do Rio Negro."
  },
  4: {
    name: "Encontro das Águas",
    category: "Fenômeno Natural",
    description: "Fenômeno onde as águas escuras do Rio Negro e as águas barrentas do Rio Solimões correm lado a lado por quilômetros sem se misturar.",
    challenge: "Análise a temperatura e densidade das águas para explicar o motivo de elas não se misturarem imediatamente."
  },
  5: {
    name: "MUSA - Museu da Amazônia",
    category: "Ecoturismo & Ciência",
    description: "Localizado na Reserva Florestal Adolpho Ducke, possui uma torre de observação de 42 metros de altura acima da copa das árvores.",
    challenge: "Suba os 242 degraus da torre do MUSA para avistar a imensidão da floresta amazônica de cima!"
  },
  6: {
    name: "Ponte Rio Negro",
    category: "Engenharia & Cartão Postal",
    description: "Com mais de 3,5 km de extensão, conecta Manaus ao município de Iranduba, sendo uma das maiores pontes estaiadas do Brasil.",
    challenge: "Atravesse a ponte ao anoitecer para apreciar a iluminação especial e a vista panorâmica do Rio Negro."
  }
};

// Estado do jogador
const gameState = {
  currentLevel: 1,
  completedLevels: 0,
  xp: 0,
  level: 1
};

// Função de navegação entre telas
function navigateTo(screenId) {
  const screens = document.querySelectorAll('.screen');
  screens.forEach(screen => screen.classList.remove('active'));

  const target = document.getElementById(screenId);
  if (target) {
    target.classList.add('active');
  }
}

// Carregar detalhes da fase selecionada
function openLevel(levelNumber) {
  gameState.currentLevel = levelNumber;
  const location = manausLocations[levelNumber];

  if (location) {
    document.getElementById('level-title').innerText = `Fase ${levelNumber}`;
    document.getElementById('location-category').innerText = location.category;
    document.getElementById('location-name').innerText = location.name;
    document.getElementById('location-description').innerText = location.description;
    document.getElementById('location-challenge').innerText = location.challenge;
  }

  navigateTo('screen-level');
}

// Concluir desafio e atualizar pontuação
function completeLevel() {
  gameState.xp += 50;
  
  if (gameState.completedLevels < gameState.currentLevel) {
    gameState.completedLevels = gameState.currentLevel;
  }

  gameState.level = Math.floor(gameState.xp / 100) + 1;

  updateProfileUI();
  navigateTo('screen-map');
}

// Atualizar interface do Perfil do Jogador
function updateProfileUI() {
  document.getElementById('completed-levels').innerText = `${gameState.completedLevels} / 6`;
  document.getElementById('player-xp').innerText = `${gameState.xp} XP`;
  document.getElementById('player-level').innerText = gameState.level;

  const statusElement = document.getElementById('player-status');
  if (gameState.completedLevels === 0) {
    statusElement.innerText = "Iniciante";
  } else if (gameState.completedLevels < 3) {
    statusElement.innerText = "Turista Atento";
  } else if (gameState.completedLevels < 6) {
    statusElement.innerText = "Guia Local";
  } else {
    statusElement.innerText = "Mestre Manauara 🏆";
  }
}