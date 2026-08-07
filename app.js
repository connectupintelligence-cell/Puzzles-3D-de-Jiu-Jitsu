/**
 * BJJ 3D - Aplicação Principal & Lógica dos Puzzles
 * Controla os estados dos puzzles 3D, ordenação drag-and-drop, score e relatório de análise tática.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    puzzles: window.BJJ_PUZZLES_DATA || [],
    activeCategory: "all",
    activePuzzle: null,
    shuffledCheckpoints: [],
    activeInspectIndex: 0,
    userScores: {}, // puzzleId -> { score, accuracy, timeSeconds }
    soundEnabled: true,
    timerInterval: null,
    elapsedSeconds: 0
  };

  // 3D Engines instances
  let hero3DEngine = null;
  let arena3DEngine = null;

  // DOM Element References
  const elements = {
    heroCanvas: document.getElementById("hero-3d-canvas"),
    heroCamReset: document.getElementById("hero-cam-reset"),
    heroCamAuto: document.getElementById("hero-cam-auto"),
    heroViewAnalysisBtn: document.getElementById("hero-view-analysis-btn"),
    quickPlayBtn: document.getElementById("quick-play-btn"),
    soundToggleBtn: document.getElementById("sound-toggle-btn"),
    soundIcon: document.getElementById("sound-icon"),

    categoryFilters: document.getElementById("category-filters"),
    puzzlesGrid: document.getElementById("puzzles-grid"),

    // Arena elements
    arenaOverlay: document.getElementById("puzzle-arena-overlay"),
    btnCloseArena: document.getElementById("btn-close-arena"),
    arenaTitle: document.getElementById("arena-title"),
    arenaCategoryBadge: document.getElementById("arena-category-badge"),
    arenaTimer: document.getElementById("arena-timer"),
    arenaScoreVal: document.getElementById("arena-score-val"),
    puzzleCanvas: document.getElementById("puzzle-3d-canvas"),

    bannerStepBadge: document.getElementById("banner-step-badge"),
    bannerStepTitle: document.getElementById("banner-step-title"),
    bannerStepDetail: document.getElementById("banner-step-detail"),

    reorderList: document.getElementById("checkpoints-reorder-list"),
    btnShuffle: document.getElementById("btn-shuffle-puzzle"),
    btnVerify: document.getElementById("btn-verify-sequence"),

    feedbackDrawer: document.getElementById("feedback-drawer"),
    feedbackIcon: document.getElementById("feedback-icon"),
    feedbackTitle: document.getElementById("feedback-title"),
    feedbackSubtitle: document.getElementById("feedback-subtitle"),
    feedbackTactical: document.getElementById("feedback-tactical-explanation"),
    btnNextPuzzle: document.getElementById("btn-next-puzzle"),

    // Analysis Modal elements
    analysisOverlay: document.getElementById("analysis-modal-overlay"),
    navAnalysisBtn: document.getElementById("nav-analysis-btn"),
    btnCloseAnalysis: document.getElementById("btn-close-analysis"),
    iqNumberVal: document.getElementById("iq-number-val"),
    iqRankTitle: document.getElementById("iq-rank-title"),
    iqRankDesc: document.getElementById("iq-rank-desc"),
    completedCountText: document.getElementById("completed-count-text"),
    breakdownBarsContainer: document.getElementById("breakdown-bars-container"),
    strengthTitle: document.getElementById("strength-title"),
    strengthDesc: document.getElementById("strength-desc"),
    weaknessTitle: document.getElementById("weakness-title"),
    weaknessDesc: document.getElementById("weakness-desc"),
    offerTitle: document.getElementById("offer-title"),
    offerDescription: document.getElementById("offer-description"),
    leadCaptureForm: document.getElementById("lead-capture-form")
  };

  // WebAudio Synthesizer for Sound Effects
  const soundFX = {
    ctx: null,
    init() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) this.ctx = new AudioCtx();
      }
    },
    playClick() {
      if (!state.soundEnabled) return;
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(600, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(300, this.ctx.currentTime + 0.05);
      gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.05);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.05);
    },
    playSuccess() {
      if (!state.soundEnabled) return;
      this.init();
      if (!this.ctx) return;
      const now = this.ctx.currentTime;
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.frequency.setValueAtTime(freq, now + i * 0.08);
        gain.gain.setValueAtTime(0.2, now + i * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.08 + 0.25);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + i * 0.08);
        osc.stop(now + i * 0.08 + 0.25);
      });
    },
    playError() {
      if (!state.soundEnabled) return;
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(180, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(110, this.ctx.currentTime + 0.2);
      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.2);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.2);
    }
  };

  // Initialize Hero 3D Engine
  function initHero3D() {
    if (elements.heroCanvas && window.BJJ3DEngine) {
      hero3DEngine = new BJJ3DEngine("hero-3d-canvas");
      hero3DEngine.toggleAutoRotate(true);

      // Set initial demo pose (e.g. Scissor sweep pose)
      if (state.puzzles.length > 0 && state.puzzles[0].checkpoints[2]) {
        hero3DEngine.setPose(state.puzzles[0].checkpoints[2].pose3d);
      }
    }
  }

  // Render Catalog Grid Cards
  function renderCatalog() {
    if (!elements.puzzlesGrid) return;
    elements.puzzlesGrid.innerHTML = "";

    const filtered = state.activeCategory === "all"
      ? state.puzzles
      : state.puzzles.filter(p => p.category === state.activeCategory);

    filtered.forEach(puzzle => {
      const isCompleted = !!state.userScores[puzzle.id];
      const scoreObj = state.userScores[puzzle.id];

      const card = document.createElement("div");
      card.className = "puzzle-card";

      card.innerHTML = `
        <div class="puzzle-card-header">
          <span class="card-category-tag">${puzzle.categoryLabel}</span>
          <span class="card-difficulty-tag">
            <i class="ph-bold ph-gauge"></i> ${puzzle.difficulty}
          </span>
        </div>
        <h3 class="puzzle-card-title">${puzzle.title}</h3>
        <p class="puzzle-card-desc">${puzzle.description}</p>
        <div class="puzzle-card-meta">
          <span class="checkpoint-count-badge">
            <i class="ph-bold ph-steps"></i> ${puzzle.checkpoints.length} Checkpoints 3D
          </span>
          <button type="button" class="btn-play-puzzle" data-id="${puzzle.id}">
            ${isCompleted ? `<i class="ph-bold ph-check"></i> Refazer (${scoreObj.accuracy}%)` : `<i class="ph-bold ph-play"></i> Resolver`}
          </button>
        </div>
      `;

      card.querySelector(".btn-play-puzzle").addEventListener("click", () => {
        soundFX.playClick();
        openPuzzleArena(puzzle.id);
      });

      elements.puzzlesGrid.appendChild(card);
    });
  }

  // Launch Active Puzzle Arena
  function openPuzzleArena(puzzleId) {
    const puzzle = state.puzzles.find(p => p.id === puzzleId);
    if (!puzzle) return;

    state.activePuzzle = puzzle;
    state.shuffledCheckpoints = shuffleArray([...puzzle.checkpoints]);
    state.activeInspectIndex = 0;
    state.elapsedSeconds = 0;

    elements.arenaTitle.textContent = puzzle.title;
    elements.arenaCategoryBadge.textContent = puzzle.categoryLabel;
    elements.arenaScoreVal.textContent = state.userScores[puzzleId] ? state.userScores[puzzleId].score : "0";

    elements.feedbackDrawer.classList.add("hidden");
    elements.arenaOverlay.classList.remove("hidden");

    // Initialize or reset Arena 3D Engine
    if (!arena3DEngine && window.BJJ3DEngine) {
      arena3DEngine = new BJJ3DEngine("puzzle-3d-canvas");
    }

    // Render Reorder list and update initial 3D pose
    renderReorderList();
    inspectCheckpoint(0);

    // Start timer
    startTimer();
  }

  function startTimer() {
    clearInterval(state.timerInterval);
    state.timerInterval = setInterval(() => {
      state.elapsedSeconds++;
      const mins = String(Math.floor(state.elapsedSeconds / 60)).padStart(2, "0");
      const secs = String(state.elapsedSeconds % 60).padStart(2, "0");
      elements.arenaTimer.textContent = `${mins}:${secs}`;
    }, 1000);
  }

  function stopTimer() {
    clearInterval(state.timerInterval);
  }

  function closePuzzleArena() {
    stopTimer();
    elements.arenaOverlay.classList.add("hidden");
  }

  // Shuffle Array Helper
  function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // Render Reorder Dock List
  function renderReorderList() {
    elements.reorderList.innerHTML = "";

    state.shuffledCheckpoints.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "checkpoint-card-item";
      card.draggable = true;
      card.dataset.index = index;

      card.innerHTML = `
        <i class="ph-bold ph-dots-six-vertical drag-handle"></i>
        <div class="item-step-num">${index + 1}</div>
        <div class="item-content">
          <h4 class="item-title">${item.name}</h4>
          <p class="item-detail">${item.detail}</p>
        </div>
        <div class="item-controls">
          <button class="btn-move-step btn-up" title="Mover para cima"><i class="ph-bold ph-caret-up"></i></button>
          <button class="btn-move-step btn-down" title="Mover para baixo"><i class="ph-bold ph-caret-down"></i></button>
        </div>
      `;

      // Click card to inspect 3D pose
      card.addEventListener("click", (e) => {
        if (!e.target.closest(".btn-move-step")) {
          soundFX.playClick();
          inspectCheckpoint(index);
        }
      });

      // Up / Down Button Handlers for touch screens
      card.querySelector(".btn-up").addEventListener("click", (e) => {
        e.stopPropagation();
        if (index > 0) {
          soundFX.playClick();
          swapCheckpoints(index, index - 1);
        }
      });

      card.querySelector(".btn-down").addEventListener("click", (e) => {
        e.stopPropagation();
        if (index < state.shuffledCheckpoints.length - 1) {
          soundFX.playClick();
          swapCheckpoints(index, index + 1);
        }
      });

      // HTML5 Drag & Drop handlers
      card.addEventListener("dragstart", (e) => {
        card.classList.add("dragging");
        e.dataTransfer.setData("text/plain", index);
      });

      card.addEventListener("dragover", (e) => {
        e.preventDefault();
        card.style.borderColor = "var(--accent-cyan)";
      });

      card.addEventListener("dragleave", () => {
        card.style.borderColor = "var(--border-glass)";
      });

      card.addEventListener("drop", (e) => {
        e.preventDefault();
        card.style.borderColor = "var(--border-glass)";
        const fromIndex = parseInt(e.dataTransfer.getData("text/plain"), 10);
        const toIndex = index;
        if (fromIndex !== toIndex) {
          soundFX.playClick();
          swapCheckpoints(fromIndex, toIndex);
        }
      });

      card.addEventListener("dragend", () => {
        card.classList.remove("dragging");
      });

      elements.reorderList.appendChild(card);
    });
  }

  function swapCheckpoints(fromIndex, toIndex) {
    const item = state.shuffledCheckpoints.splice(fromIndex, 1)[0];
    state.shuffledCheckpoints.splice(toIndex, 0, item);
    renderReorderList();
    inspectCheckpoint(toIndex);
  }

  // Update 3D Mannequin Viewport with Inspect Pose
  function inspectCheckpoint(index) {
    state.activeInspectIndex = index;
    const cp = state.shuffledCheckpoints[index];
    if (!cp) return;

    elements.bannerStepBadge.textContent = `Posição ${index + 1}`;
    elements.bannerStepTitle.textContent = cp.name;
    elements.bannerStepDetail.textContent = cp.detail;

    if (arena3DEngine) {
      arena3DEngine.setPose(cp.pose3d);
    }
  }

  // Validate Sequence Mechanics
  function verifySequence() {
    stopTimer();
    const puzzle = state.activePuzzle;
    if (!puzzle) return;

    let correctCount = 0;
    const total = puzzle.checkpoints.length;
    const itemCards = elements.reorderList.children;

    state.shuffledCheckpoints.forEach((cp, index) => {
      const isCorrectSlot = cp.stepNumber === (index + 1);
      if (isCorrectSlot) correctCount++;

      if (itemCards[index]) {
        itemCards[index].classList.remove("correct-slot", "incorrect-slot");
        itemCards[index].classList.add(isCorrectSlot ? "correct-slot" : "incorrect-slot");
      }
    });

    const accuracy = Math.round((correctCount / total) * 100);
    const speedBonus = Math.max(0, 500 - state.elapsedSeconds * 5);
    const calculatedScore = (correctCount * 250) + speedBonus;

    // Save score to user state
    state.userScores[puzzle.id] = {
      score: calculatedScore,
      accuracy: accuracy,
      timeSeconds: state.elapsedSeconds,
      category: puzzle.category
    };

    elements.arenaScoreVal.textContent = calculatedScore;

    // Show Feedback Drawer
    elements.feedbackDrawer.classList.remove("hidden");
    if (accuracy === 100) {
      soundFX.playSuccess();
      elements.feedbackDrawer.className = "feedback-drawer correct";
      elements.feedbackIcon.className = "ph-bold ph-check-circle";
      elements.feedbackTitle.textContent = "Sequência 100% Perfeita!";
      elements.feedbackSubtitle.textContent = `Você dominou os ${total} checkpoints em ${state.elapsedSeconds} segundos!`;
    } else {
      soundFX.playError();
      elements.feedbackDrawer.className = "feedback-drawer incorrect";
      elements.feedbackIcon.className = "ph-bold ph-warning-circle";
      elements.feedbackTitle.textContent = `Precisão: ${accuracy}%`;
      elements.feedbackSubtitle.textContent = `Você acertou ${correctCount} de ${total} checkpoints. Veja o destaque de transição abaixo:`;
    }

    elements.feedbackTactical.textContent = puzzle.tacticalTip;
    renderCatalog();
  }

  // Open Knowledge Analysis & Tailored Upsell Report Modal
  function openKnowledgeAnalysis() {
    soundFX.playClick();
    const completedIds = Object.keys(state.userScores);
    const completedCount = completedIds.length;

    // Calculate scores per category
    const categories = [
      { key: "guarda", label: "Guarda & Raspagem", score: 85 },
      { key: "passagem", label: "Passagem de Guarda", score: 90 },
      { key: "quedas", label: "Quedas & Wrestling", score: 70 },
      { key: "finalizacao", label: "Finalizações", score: 80 },
      { key: "escapada", label: "Escapadas & Defesa", score: 60 }
    ];

    // Recalculate based on real user scores if played
    if (completedCount > 0) {
      categories.forEach(cat => {
        const catScores = Object.values(state.userScores).filter(s => s.category === cat.key);
        if (catScores.length > 0) {
          const avgAcc = catScores.reduce((acc, curr) => acc + curr.accuracy, 0) / catScores.length;
          cat.score = Math.round(avgAcc);
        }
      });
    }

    // Overall IQ Calculation
    const overallIQ = Math.round(categories.reduce((a, b) => a + b.score, 0) / categories.length);
    elements.iqNumberVal.textContent = `${overallIQ}%`;

    // Dynamic Rank Title
    let rankTitle = "Faixa Azul Estratégico";
    if (overallIQ >= 90) rankTitle = "Faixa Preta Tático";
    else if (overallIQ >= 80) rankTitle = "Faixa Roxa Estratégico";
    else if (overallIQ >= 70) rankTitle = "Faixa Azul Avançado";
    elements.iqRankTitle.textContent = rankTitle;

    elements.completedCountText.textContent = `${completedCount} de 10 puzzles concluídos`;

    // Render Progress Bars
    elements.breakdownBarsContainer.innerHTML = "";
    categories.forEach(cat => {
      const row = document.createElement("div");
      row.className = "breakdown-row";
      row.innerHTML = `
        <div class="row-meta">
          <span>${cat.label}</span>
          <span style="color: var(--accent-cyan);">${cat.score}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${cat.score}%;"></div>
        </div>
      `;
      elements.breakdownBarsContainer.appendChild(row);
    });

    // Determine Strength & Weakness
    categories.sort((a, b) => b.score - a.score);
    const strongest = categories[0];
    const weakest = categories[categories.length - 1];

    elements.strengthTitle.textContent = strongest.label;
    elements.strengthDesc.textContent = `Desempenho excelente com ${strongest.score}% de acurácia. Suas entradas de alavancagem nesta área são instintivas.`;

    elements.weaknessTitle.textContent = weakest.label;
    elements.weaknessDesc.textContent = `Acurácia em ${weakest.score}%. Foi detectada hesitação na leitura de tempo e transições biomecânicas nesta área.`;

    // Dynamically Tailor Low-Ticket Upsell Offer based on Weakness
    updateUpsellOffer(weakest.key);

    elements.analysisOverlay.classList.remove("hidden");
  }

  function updateUpsellOffer(weakCategoryKey) {
    const offerMap = {
      escapada: {
        title: "Masterclass: Escapadas de Elite & Defesa Pós-Passagem",
        desc: "Elimine o ponto fraco detectado. Um guia acelerado passo a passo para nunca mais ficar travado sob os 100kg, montada ou pegada de costas."
      },
      finalizacao: {
        title: "Manual de Ajuste Fino de Finalizações & Chaves de Braço",
        desc: "Transforme suas tentativas de submission em pegadas fatais. Ajustes de ângulo e rotação de quadril testados em competição."
      },
      passagem: {
        title: "Guia Definitivo de Passagem de Guarda sem Pano e com Pano",
        desc: "Domine o passe de joelho, toreando e pressão por cima anulando guardas modernas como De La Riva e Guarda Aranha."
      },
      guarda: {
        title: "Manual de Raspagens Inoxidáveis & Guarda Fechada",
        desc: "Construa uma guarda impenetrável. Aprenda a quebrar a postura do passador e conectar raspagens em cadeia."
      },
      quedas: {
        title: "Curso Quedas para Jiu-Jitsu sem Risco de Lesão",
        desc: "Desenvolva um jogo de wrestling e Judô prático adaptado para a realidade do tatame de BJJ."
      }
    };

    const offer = offerMap[weakCategoryKey] || offerMap.escapada;
    elements.offerTitle.textContent = offer.title;
    elements.offerDescription.textContent = offer.desc;
  }

  function closeKnowledgeAnalysis() {
    elements.analysisOverlay.classList.add("hidden");
  }

  // Event Listeners Registration
  function registerEventListeners() {
    // Sound Toggle
    if (elements.soundToggleBtn) {
      elements.soundToggleBtn.addEventListener("click", () => {
        state.soundEnabled = !state.soundEnabled;
        elements.soundIcon.className = state.soundEnabled ? "ph-bold ph-speaker-high" : "ph-bold ph-speaker-slash";
      });
    }

    // Quick Play Button
    if (elements.quickPlayBtn) {
      elements.quickPlayBtn.addEventListener("click", () => {
        soundFX.playClick();
        openPuzzleArena("puzzle-1");
      });
    }

    // Category Filters
    if (elements.categoryFilters) {
      elements.categoryFilters.addEventListener("click", (e) => {
        const filterBtn = e.target.closest(".filter-btn");
        if (!filterBtn) return;

        soundFX.playClick();
        document.querySelectorAll(".filter-btn").forEach(btn => btn.classList.remove("active"));
        filterBtn.classList.add("active");

        state.activeCategory = filterBtn.dataset.category;
        renderCatalog();
      });
    }

    // Hero controls
    if (elements.heroCamReset) {
      elements.heroCamReset.addEventListener("click", () => {
        if (hero3DEngine) hero3DEngine.resetCamera();
      });
    }

    if (elements.heroCamAuto) {
      elements.heroCamAuto.addEventListener("click", () => {
        if (hero3DEngine) hero3DEngine.toggleAutoRotate();
      });
    }

    if (elements.heroViewAnalysisBtn) {
      elements.heroViewAnalysisBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openKnowledgeAnalysis();
      });
    }

    // Navigation Analysis Link
    if (elements.navAnalysisBtn) {
      elements.navAnalysisBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openKnowledgeAnalysis();
      });
    }

    if (elements.btnCloseAnalysis) {
      elements.btnCloseAnalysis.addEventListener("click", closeKnowledgeAnalysis);
    }

    // Arena controls
    if (elements.btnCloseArena) {
      elements.btnCloseArena.addEventListener("click", closePuzzleArena);
    }

    if (elements.btnShuffle) {
      elements.btnShuffle.addEventListener("click", () => {
        soundFX.playClick();
        state.shuffledCheckpoints = shuffleArray([...state.activePuzzle.checkpoints]);
        renderReorderList();
        inspectCheckpoint(0);
      });
    }

    if (elements.btnVerify) {
      elements.btnVerify.addEventListener("click", () => {
        soundFX.playClick();
        verifySequence();
      });
    }

    if (elements.btnNextPuzzle) {
      elements.btnNextPuzzle.addEventListener("click", () => {
        soundFX.playClick();
        const currIndex = state.puzzles.findIndex(p => p.id === state.activePuzzle.id);
        const nextPuzzle = state.puzzles[(currIndex + 1) % state.puzzles.length];
        openPuzzleArena(nextPuzzle.id);
      });
    }

    // Camera preset buttons in Arena
    document.querySelectorAll(".camera-presets-group .preset-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        soundFX.playClick();
        document.querySelectorAll(".camera-presets-group .preset-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        if (arena3DEngine) arena3DEngine.updateCameraPreset(btn.dataset.preset);
      });
    });

    const arenaCamAuto = document.getElementById("arena-cam-auto");
    if (arenaCamAuto) {
      arenaCamAuto.addEventListener("click", () => {
        if (arena3DEngine) arena3DEngine.toggleAutoRotate();
      });
    }

    const arenaCamReset = document.getElementById("arena-cam-reset");
    if (arenaCamReset) {
      arenaCamReset.addEventListener("click", () => {
        if (arena3DEngine) arena3DEngine.resetCamera();
      });
    }

    // Lead Capture Form
    if (elements.leadCaptureForm) {
      elements.leadCaptureForm.addEventListener("submit", (e) => {
        e.preventDefault();
        soundFX.playSuccess();
        alert("🎉 Diagnóstico salvo com sucesso! Você será redirecionado para a oferta especial.");
        closeKnowledgeAnalysis();
      });
    }
  }

  // App Initialization Sequence
  function initApp() {
    initHero3D();
    renderCatalog();
    registerEventListeners();
  }

  initApp();
});
