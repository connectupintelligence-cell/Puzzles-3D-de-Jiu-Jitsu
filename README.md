# 🥋 BJJ 3D — Puzzles 3D de Jiu-Jitsu & Treino Tático

![BJJ 3D Tech Banner](https://img.shields.io/badge/Three.js-3D_Engine-38bdf8?style=for-the-badge&logo=three.js)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-f59e0b?style=for-the-badge&logo=javascript)
![HTML5](https://img.shields.io/badge/HTML5-Modern_UI-e34f26?style=for-the-badge&logo=html5)
![Status](https://img.shields.io/badge/Status-MVP_Pronto-10b981?style=for-the-badge)

> **Landing Page e plataforma interativa de puzzles 3D para treino de olho tático e leitura de transições em Jiu-Jitsu.**  
> Funciona como um motor de aquisição de audiência de baixo custo (baixo CAC), gerando diagnósticos automatizados de conhecimento técnico com monetização indireta via ofertas low-ticket personalizadas.

---

## 📌 1. Conceito do Produto

Cada puzzle apresenta uma técnica de Jiu-Jitsu (ex: *Raspagem Tesourinha*, *Passagem de Joelho*, *Armbar*, *Triângulo*) desmembrada em **checkpoints-chave 3D**. 

- O usuário examina as posições girando a câmera em **360°** e reordena os checkpoints na sequência biomecânica correta do início ao fim.
- Ao concluir, o sistema calcula a **acurácia** e o **tempo**, alimentando um **Relatório de Análise de Conhecimento Tático**.
- O diagnóstico identifica o **Ponto Forte** e o **Ponto de Atenção** (fraqueza) do praticante, recomendando dinamicamente um produto low-ticket (ex: *Masterclass de Escapadas dos 100kg*).

---

## 🛠️ 2. Funcionalidades do MVP

### 🎨 Motor Gráfico 3D (`bjj-3d-engine.js`)
- Renderização em **Three.js** com tom de cor cinematográfico (`ACESFilmicToneMapping`) e iluminação de estúdio.
- **Lutadores Articulados**:
  - **Tori** (Atacante): Quimono Azul Real com lapela branca e faixa preta com a tradicional **ponteira vermelha/dourada de BJJ**.
  - **Uke** (Defensor): Quimono Preto Carbono com acentos âmbar.
- Textura PBR trançada de tecido de quimono (450g/m²).
- Presets de câmera com um clique: `3D Padrão`, `Visão Superior (Top-Down)`, `Perfil Lateral` e `Zoom Pegada`.

### 🥋 10 Puzzles Técnicos (`puzzles-data.js`)
Divididos em 5 categorias do mapa tático de Jiu-Jitsu:
1. **Guarda & Raspagem**: *Raspagem Tesourinha* e *De La Riva com Gancho Interno*.
2. **Passagem de Guarda**: *Passagem de Joelho no Chão (Knee Slice)* e *Passagem Toreando*.
3. **Quedas & Wrestling**: *Double Leg Takedown (Baiana)* e *Osoto Gari*.
4. **Finalizações**: *Armlock da Guarda Fechada*, *Estrangulamento Triângulo* e *Mata-Leão das Costas*.
5. **Escapadas & Defesa**: *Escapada dos 100kg com Fuga de Quadril*.

### 📊 Relatório de Análise Tática (`app.js`)
- Cálculo automático do **Índice Tático (%)** e graduação correspondente (*Faixa Azul*, *Faixa Roxa*, *Faixa Preta Tático*).
- Gráfico de barras por domínio técnico.
- Oferta low-ticket ajustada dinamicamente à principal fraqueza do usuário.
- Efeitos sonoros sintetizados nativamente via **WebAudio API**.

---

## 📁 3. Estrutura do Projeto

```
.
├── index.html         # Landing Page, Catálogo de Puzzles e Game Arena 3D
├── style.css          # Design System Dark Mode com Glassmorphism
├── bjj-3d-engine.js   # Motor 3D em Three.js com materiais PBR e lutadores BJJ
├── puzzles-data.js    # Base de dados com os 10 Puzzles e poses 3D
├── app.js             # Lógica de ordenação, validação e relatório tático
├── server.js          # Servidor HTTP estático nativo em Node.js (Porta 3000)
└── README.md          # Documentação do repositório
```

---

## 🚀 4. Como Executar Localmente

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/connectupintelligence-cell/Puzzles-3D-de-Jiu-Jitsu.git
   cd Puzzles-3D-de-Jiu-Jitsu
   ```

2. **Iniciar o Servidor**:
   ```bash
   node server.js
   ```

3. **Acessar no Navegador**:
   Abra `http://localhost:3000` em qualquer navegador moderno.

---

## 🗺️ 5. Roadmap Futuro & BJJ Chess

- **Fase 1 (MVP Atual)**: 10 puzzles 3D estáticos com reordenação, relatório automatizado e captura de e-mail.
- **Fase 2**: Retenção e gamificação (streaks de treino, ranking global de faixas, integração com CRM/Checkout).
- **Fase 3 (BJJ Chess 3D)**: Evolução do motor para um jogo estratégico multiplayer de combate biomecânico em tempo real.

---

### 📝 Licença
Desenvolvido para **ConnectUP Intelligence / BJJ 3D Engine**. Todos os direitos reservados.
