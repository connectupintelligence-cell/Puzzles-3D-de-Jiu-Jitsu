/**
 * BJJ 3D - Base de Dados de Puzzles Técnicos
 * Contém os 10 Puzzles do MVP divididos em 5 categorias táticas.
 */

window.BJJ_PUZZLES_DATA = [
  {
    id: "puzzle-1",
    title: "Raspagem Tesourinha (Scissor Sweep)",
    category: "guarda",
    categoryLabel: "Guarda & Raspagem",
    difficulty: "Iniciante",
    icon: "ph-arrows-clockwise",
    description: "Reconstrua a sequência clássica de raspagem tesourinha partindo da guarda fechada contra um oponente posturado.",
    tacticalTip: "A chave da tesourinha é a quebra de postura aliada ao desbalanço lateral antes de aplicar a tesoura com as pernas.",
    checkpoints: [
      {
        id: "p1-step1",
        stepNumber: 1,
        name: "Domínio de Pegadas & Quebra de Postura",
        detail: "Estabelecer pegada cruzada na gola funda e pegada no tríceps/manga do mesmo lado. Puxar o oponente quebrando a postura frontal.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0, 0], pose: "closed_guard_bottom" },
          uke: { position: [0, 0.5, 0.2], rotation: [0, 3.14, 0], pose: "closed_guard_top_broken" }
        }
      },
      {
        id: "p1-step2",
        stepNumber: 2,
        name: "Abertura de Guarda & Fuga de Quadril",
        detail: "Abrir a guarda fechada, apoiar o pé no solo e fugir o quadril lateralmente para abrir espaço para a canela.",
        pose3d: {
          tori: { position: [-0.2, 0.2, 0], rotation: [0, 0.4, 0.2], pose: "hip_escape_guard" },
          uke: { position: [0.1, 0.5, 0.2], rotation: [0, 3.0, 0], pose: "closed_guard_top_low" }
        }
      },
      {
        id: "p1-step3",
        stepNumber: 3,
        name: "Escala da Canela no Tórax & Desbalanço",
        detail: "Escalar a perna superior cruzando a canela pelo tórax/esternal do oponente enquanto a perna inferior apoia perto do joelho.",
        pose3d: {
          tori: { position: [-0.3, 0.2, 0], rotation: [0, 0.6, 0.3], pose: "scissor_loaded" },
          uke: { position: [0.2, 0.4, 0.1], rotation: [0, 2.8, -0.2], pose: "off_balance_tilted" }
        }
      },
      {
        id: "p1-step4",
        stepNumber: 4,
        name: "Execução da Tesoura & Subida na Montada",
        detail: "Efetuar a tesourada contínua puxando a manga e chutando a perna base para raspar e estabilizar na montada.",
        pose3d: {
          tori: { position: [0, 0.7, 0], rotation: [0, 0, 0], pose: "mounted_top" },
          uke: { position: [0, 0.2, 0], rotation: [3.14, 0, 0], pose: "mounted_bottom" }
        }
      }
    ]
  },
  {
    id: "puzzle-2",
    title: "Raspagem De La Riva com Gancho Interno",
    category: "guarda",
    categoryLabel: "Guarda & Raspagem",
    difficulty: "Intermediário",
    icon: "ph-hook",
    description: "Ordene a sequência da guarda De La Riva para desbalançar e raspar subindo no single leg.",
    tacticalTip: "Manter o calcanhar do oponente preso firmemente impede a rotação e a defesa da passagem de guarda.",
    checkpoints: [
      {
        id: "p2-step1",
        stepNumber: 1,
        name: "Entrada do Gancho DLR & Domínio de Calcanhar",
        detail: "Ganchar a perna externa por fora da coxa do passador e segurar o calcanhar com a mão do mesmo lado.",
        pose3d: {
          tori: { position: [0, 0.2, -0.3], rotation: [0, 0, 0], pose: "dlr_bottom" },
          uke: { position: [0, 0.8, 0.4], rotation: [0, 3.14, 0], pose: "standing_passer" }
        }
      },
      {
        id: "p2-step2",
        stepNumber: 2,
        name: "Chute na Virilha & Troca de Gancho",
        detail: "Usar a perna livre para empurrar o joelho/virilha oposta do passador, criando espaço para mudar o ângulo.",
        pose3d: {
          tori: { position: [-0.1, 0.2, -0.3], rotation: [0, 0.3, 0], pose: "dlr_push" },
          uke: { position: [0.1, 0.8, 0.5], rotation: [0, 2.9, 0.2], pose: "standing_unbalanced" }
        }
      },
      {
        id: "p2-step3",
        stepNumber: 3,
        name: "Tranco de Quadril & Queda Lateral",
        detail: "Projetar o quadril para frente combinando a puxada da gola para projetar o oponente de joelhos no solo.",
        pose3d: {
          tori: { position: [0, 0.3, 0], rotation: [0, 0.5, 0.5], pose: "dlr_sweep_launch" },
          uke: { position: [0.4, 0.3, 0.3], rotation: [0, 2.5, -0.6], pose: "falling_side" }
        }
      },
      {
        id: "p2-step4",
        stepNumber: 4,
        name: "Subida Técnica & Projeção no Single Leg",
        detail: "Fazer a subida técnica mantendo a perna presa e concluir a raspagem por cima acumulando os 2 pontos.",
        pose3d: {
          tori: { position: [0.3, 0.8, 0.2], rotation: [0, 1.2, 0], pose: "single_leg_top" },
          uke: { position: [0.1, 0.3, 0.3], rotation: [0, 3.0, -0.4], pose: "bottom_turtled" }
        }
      }
    ]
  },
  {
    id: "puzzle-3",
    title: "Passagem de Joelho no Chão (Knee Slice)",
    category: "passagem",
    categoryLabel: "Passagem de Guarda",
    difficulty: "Iniciante",
    icon: "ph-arrow-right",
    description: "Reconstrua o passo a passo da tradicional passagem com o joelho cortando pela coxa.",
    tacticalTip: "O underhook (esgrima) profundo é obrigatório para impedir a subida de costas do guardeiro.",
    checkpoints: [
      {
        id: "p3-step1",
        stepNumber: 1,
        name: "Abertura de Guarda & Domínio de Calça/Gola",
        detail: "Posturar no centro da guarda aberta, segurar as calças do oponente e imobilizar a perna.",
        pose3d: {
          tori: { position: [0, 0.6, 0.3], rotation: [0, 0, 0], pose: "open_guard_passer" },
          uke: { position: [0, 0.2, -0.2], rotation: [0, 3.14, 0], pose: "open_guard_bottom" }
        }
      },
      {
        id: "p3-step2",
        stepNumber: 2,
        name: "Esgrima Profunda (Underhook) & Apoio de Cabeça",
        detail: "Mergulhar o braço sob a axila do oponente (esgrima) e colar o ombro/cabeça no peito para anular defesas.",
        pose3d: {
          tori: { position: [0.1, 0.5, 0.1], rotation: [0, -0.2, 0.2], pose: "knee_slice_underhook" },
          uke: { position: [0, 0.2, -0.2], rotation: [0, 3.0, 0.1], pose: "flattened_bottom" }
        }
      },
      {
        id: "p3-step3",
        stepNumber: 3,
        name: "Deslize do Joelho Cruzado no Solo",
        detail: "Deslizar o joelho diagonalmente sobre a coxa do guardeiro raspando o tatame até tocar o chão.",
        pose3d: {
          tori: { position: [0.3, 0.4, 0], rotation: [0, -0.5, 0.3], pose: "knee_slicing" },
          uke: { position: [0, 0.2, -0.1], rotation: [0, 2.9, 0.2], pose: "flattened_pinched" }
        }
      },
      {
        id: "p3-step4",
        stepNumber: 4,
        name: "Chute de Liberação do Pé & Estabilização nos 100kg",
        detail: "Chutar o pé de trás para destravar da meia-guarda e abraçar a cabeça/tronco caindo nos 100kg com peso distribuído.",
        pose3d: {
          tori: { position: [0, 0.4, 0], rotation: [0, 1.57, 0], pose: "side_control_top" },
          uke: { position: [0, 0.2, 0], rotation: [0, 3.14, 0], pose: "side_control_bottom" }
        }
      }
    ]
  },
  {
    id: "puzzle-4",
    title: "Passagem Toreando (Toreando Pass)",
    category: "passagem",
    categoryLabel: "Passagem de Guarda",
    difficulty: "Intermediário",
    icon: "ph-lightning",
    description: "Ordene os movimentos explosivos da passagem Toreando contra a guarda aberta.",
    tacticalTip: "Não tente empurrar o oponente para trás; direcione as pernas dele para um lado enquanto seu corpo avança para o outro.",
    checkpoints: [
      {
        id: "p4-step1",
        stepNumber: 1,
        name: "Pegada Dupla nos Joelhos/Calças",
        detail: "Fazer pegadas firmes na parte externa do tecido da calça na altura dos joelhos.",
        pose3d: {
          tori: { position: [0, 0.7, 0.4], rotation: [0, 0, 0], pose: "toreando_standing" },
          uke: { position: [0, 0.2, -0.2], rotation: [0, 3.14, 0], pose: "open_guard_legs_up" }
        }
      },
      {
        id: "p4-step2",
        stepNumber: 2,
        name: "Empurrão Inicial & Reação de Extensão",
        detail: "Empurrar levemente os joelhos em direção ao peito do oponente para gerar uma reação de resposta e desbalanço.",
        pose3d: {
          tori: { position: [0, 0.6, 0.3], rotation: [0, 0, 0.1], pose: "toreando_push" },
          uke: { position: [0, 0.25, -0.1], rotation: [0, 3.14, -0.1], pose: "open_guard_compressed" }
        }
      },
      {
        id: "p4-step3",
        stepNumber: 3,
        name: "Projeção das Pernas & Passo Lateral em Arco",
        detail: "Jogar as pernas do guardeiro vigorosamente para a esquerda enquanto dá um passo diagonal explosivo para a direita.",
        pose3d: {
          tori: { position: [0.4, 0.5, 0.1], rotation: [0, -0.7, 0.2], pose: "toreando_sidestep" },
          uke: { position: [-0.2, 0.2, -0.2], rotation: [0, 2.5, 0.4], pose: "toreando_swung_legs" }
        }
      },
      {
        id: "p4-step4",
        stepNumber: 4,
        name: "Queda de Quadril & Bloqueio com o Joelho",
        detail: "Soltar a calça, colar o quadril na lateral do oponente e bloquear o quadril dele com o joelho para selar a passagem.",
        pose3d: {
          tori: { position: [0.1, 0.4, -0.1], rotation: [0, -1.4, 0], pose: "side_control_top" },
          uke: { position: [-0.1, 0.2, -0.1], rotation: [0, 3.14, 0], pose: "side_control_bottom" }
        }
      }
    ]
  },
  {
    id: "puzzle-5",
    title: "Double Leg Takedown (Baiana)",
    category: "quedas",
    categoryLabel: "Quedas & Wrestling",
    difficulty: "Iniciante",
    icon: "ph-person-simple-throw",
    description: "Reconstrua o ataque de queda de pernas duplas (Double Leg) do clinch inicial até a queda.",
    tacticalTip: "A mudança de nível deve preceder a penetração. A cabeça deve estar firme na costela para evitar a guilhotina.",
    checkpoints: [
      {
        id: "p5-step1",
        stepNumber: 1,
        name: "Mudança de Nível (Level Change)",
        detail: "Flexionar os joelhos mantendo a coluna ereta para rebaixar o centro de gravidade abaixo dos ombros do oponente.",
        pose3d: {
          tori: { position: [0, 0.6, 0.5], rotation: [0, 0, 0], pose: "level_change_squat" },
          uke: { position: [0, 0.9, 0], rotation: [0, 3.14, 0], pose: "upright_stance" }
        }
      },
      {
        id: "p5-step2",
        stepNumber: 2,
        name: "Passo de Penetração & Joelho no Solo",
        detail: "Dar um passo profundo entre as pernas do oponente colando o joelho da frente no tatame e a cabeça na costela.",
        pose3d: {
          tori: { position: [0, 0.4, 0.2], rotation: [0, 0, 0.2], pose: "penetration_step" },
          uke: { position: [0, 0.85, -0.1], rotation: [0, 3.14, -0.1], pose: "upright_shocked" }
        }
      },
      {
        id: "p5-step3",
        stepNumber: 3,
        name: "Abraço Atrás das Dobras dos Joelhos",
        detail: "Laçar fortemente as duas pernas por trás das dobras dos joelhos tirando o apoio de base.",
        pose3d: {
          tori: { position: [0, 0.4, 0.1], rotation: [0, 0, 0.3], pose: "leg_clinch_grip" },
          uke: { position: [0, 0.8, -0.2], rotation: [0, 3.0, -0.3], pose: "off_balance_backwards" }
        }
      },
      {
        id: "p5-step4",
        stepNumber: 4,
        name: "Empurrão de Cabeça & Projeção Lateral",
        detail: "Dirigir o tronco com a cabeça pressionando a costela e puxando os joelhos para derrubar de costas na guarda aberta.",
        pose3d: {
          tori: { position: [0, 0.5, -0.1], rotation: [0, 0.2, 0.4], pose: "takedown_finish_top" },
          uke: { position: [0, 0.2, -0.4], rotation: [3.0, 0, 0], pose: "takedown_finish_bottom" }
        }
      }
    ]
  },
  {
    id: "puzzle-6",
    title: "Osoto Gari (Varrida de Perna Externa)",
    category: "quedas",
    categoryLabel: "Quedas & Wrestling",
    difficulty: "Intermediário",
    icon: "ph-person-arms-spread",
    description: "Reconstrua o clássico golpe de projeção do Judô adaptado ao BJJ.",
    tacticalTip: "O desbalanço frontal (Kuzushi) deve trazer todo o peso do oponente para o calcanhar do lado que será varrido.",
    checkpoints: [
      {
        id: "p6-step1",
        stepNumber: 1,
        name: "Pegada de Gola/Manga & Kuzushi (Desbalanço)",
        detail: "Erguer o cotovelo da gola e puxar a manga para colocar o peso do oponente sobre o pé direito dele.",
        pose3d: {
          tori: { position: [0, 0.9, 0.3], rotation: [0, 0, 0], pose: "judo_kuzushi_tori" },
          uke: { position: [0, 0.9, -0.1], rotation: [0, 3.14, 0.1], pose: "judo_kuzushi_uke" }
        }
      },
      {
        id: "p6-step2",
        stepNumber: 2,
        name: "Passo de Apoio Lateral Avançado",
        detail: "Avançar o pé esquerdo paralelamente e ao lado do pé do oponente, alinhando o peito com o ombro dele.",
        pose3d: {
          tori: { position: [-0.1, 0.9, 0.1], rotation: [0, 0.1, 0], pose: "osoto_step_in" },
          uke: { position: [0.1, 0.9, -0.1], rotation: [0, 3.1, 0], pose: "osoto_tilted_uke" }
        }
      },
      {
        id: "p6-step3",
        stepNumber: 3,
        name: "Elevação da Perna de Ataque por Trás",
        detail: "Lançar a perna direita alta por trás da coxa do oponente colando os peitos.",
        pose3d: {
          tori: { position: [0, 0.9, 0], rotation: [0, 0.3, 0.3], pose: "osoto_leg_raise" },
          uke: { position: [0.1, 0.85, -0.1], rotation: [0, 2.9, -0.2], pose: "osoto_one_leg_balance" }
        }
      },
      {
        id: "p6-step4",
        stepNumber: 4,
        name: "Varrida de Coxa & Projeção Direta ao Solo",
        detail: "Varrer a coxa vigorosamente para trás inclinando a cabeça para a frente e caindo por cima no controle lateral.",
        pose3d: {
          tori: { position: [0.1, 0.4, 0], rotation: [0, 0.8, 0], pose: "side_control_top" },
          uke: { position: [-0.1, 0.2, 0], rotation: [3.14, 0, 0], pose: "side_control_bottom" }
        }
      }
    ]
  },
  {
    id: "puzzle-7",
    title: "Armlock da Guarda Fechada",
    category: "finalizacao",
    categoryLabel: "Finalizações",
    difficulty: "Iniciante",
    icon: "ph-crosshair",
    description: "Reconstrua o ataque de chave de braço reto (Armbar) a partir da guarda fechada.",
    tacticalTip: "O segredo do armbar de guarda é fazer o giro de quadril perpendicular de 90° em relação ao corpo do oponente.",
    checkpoints: [
      {
        id: "p7-step1",
        stepNumber: 1,
        name: "Domínio Cruzado do Pulso & Gola",
        detail: "Segurar o pulso do oponente com as duas mãos ou domínio cruzado e dominar a gola oposta.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0, 0], pose: "closed_guard_bottom" },
          uke: { position: [0, 0.5, 0.2], rotation: [0, 3.14, 0], pose: "closed_guard_top" }
        }
      },
      {
        id: "p7-step2",
        stepNumber: 2,
        name: "Pé no Quadril & Escalada da Guarda",
        detail: "Colocar o pé do mesmo lado do braço atacado no quadril do oponente e escalar a outra perna alta nas costas.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0.4, 0.2], pose: "high_guard_armbar_prep" },
          uke: { position: [0, 0.45, 0.1], rotation: [0, 2.9, 0], pose: "closed_guard_trapped" }
        }
      },
      {
        id: "p7-step3",
        stepNumber: 3,
        name: "Giro de Quadril Perpendicular (90°)",
        detail: "Girar o tronco perpendicularmente até enxergar o ouvido do oponente, mantendo a perna alta pressionando as costas.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 1.57, 0.2], pose: "armbar_spin_90" },
          uke: { position: [0, 0.4, 0], rotation: [0, 3.0, 0], pose: "armbar_trapped_arm" }
        }
      },
      {
        id: "p7-step4",
        stepNumber: 4,
        name: "Perna sobre a Cabeça & Extensão do Quadril",
        detail: "Passar a perna sobre o rosto, colar os joelhos, segurar o polegar apontado para cima e projetar o quadril.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 1.57, 0.3], pose: "armbar_finish_locked" },
          uke: { position: [0, 0.25, 0], rotation: [3.14, 0, 0], pose: "armbar_victim_tapped" }
        }
      }
    ]
  },
  {
    id: "puzzle-8",
    title: "Estrangulamento Triângulo (Triangle Choke)",
    category: "finalizacao",
    categoryLabel: "Finalizações",
    difficulty: "Intermediário",
    icon: "ph-triangle",
    description: "Ordene o ajuste milimétrico do triângulo de pernas da guarda.",
    tacticalTip: "O braço do oponente deve estar totalmente cruzado sobre o pescoço antes de fechar o cadeado nº 4.",
    checkpoints: [
      {
        id: "p8-step1",
        stepNumber: 1,
        name: "Controle Um Braço Dentro, Um Fora",
        detail: "Empurrar um pulso do oponente contra o peito dele enquanto puxa a cabeça com a outra mão.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0, 0], pose: "closed_guard_bottom" },
          uke: { position: [0, 0.5, 0.2], rotation: [0, 3.14, 0], pose: "one_arm_in_one_out" }
        }
      },
      {
        id: "p8-step2",
        stepNumber: 2,
        name: "Disparo da Perna Alta sobre a Nuca",
        detail: "Lançar a perna por cima do ombro preso e cruzar os tornozelos nas costas com elevamento de quadril.",
        pose3d: {
          tori: { position: [0, 0.25, 0], rotation: [0, 0.2, 0.3], pose: "triangle_stage1" },
          uke: { position: [0, 0.4, 0.1], rotation: [0, 2.9, -0.2], pose: "trapped_in_triangle" }
        }
      },
      {
        id: "p8-step3",
        stepNumber: 3,
        name: "Cruzar o Braço & Ajuste de Ângulo na Canela",
        detail: "Trazer o braço preso do oponente cruzando seu pescoço e dominar a própria canela ajustando o ângulo de lateralidade.",
        pose3d: {
          tori: { position: [0, 0.25, 0], rotation: [0, 0.7, 0.3], pose: "triangle_arm_crossed" },
          uke: { position: [0, 0.35, 0.1], rotation: [0, 2.7, -0.3], pose: "choked_in_triangle" }
        }
      },
      {
        id: "p8-step4",
        stepNumber: 4,
        name: "Fechamento do Cadeado N.º 4 & Compressão",
        detail: "Encaixar a fossa poplítea do joelho sobre o peito do pé oposto, puxar a nuca e elevar o quadril para finalizar.",
        pose3d: {
          tori: { position: [0, 0.3, 0], rotation: [0, 0.8, 0.4], pose: "triangle_locked_finish" },
          uke: { position: [0, 0.3, 0.1], rotation: [0, 2.6, -0.4], pose: "triangle_tapped_uke" }
        }
      }
    ]
  },
  {
    id: "puzzle-9",
    title: "Mata-Leão da Pegada de Costas (RNC)",
    category: "finalizacao",
    categoryLabel: "Finalizações",
    difficulty: "Intermediário",
    icon: "ph-shield-warning",
    description: "Reconstrua o ataque de estrangulamento Mata-Leão partindo do domínio de costas com ganchos.",
    tacticalTip: "Esconda a mão que fecha a trava atrás da cabeça do oponente para evitar que ele consiga segurar os dedos.",
    checkpoints: [
      {
        id: "p9-step1",
        stepNumber: 1,
        name: "Estabilização dos Ganchos & Cinto de Segurança",
        detail: "Manter dois ganchos firmes nas coxas internas e domínio de cinto de segurança (um braço por cima, um por baixo).",
        pose3d: {
          tori: { position: [0, 0.5, -0.2], rotation: [0, 0, 0], pose: "back_control_top" },
          uke: { position: [0, 0.45, 0], rotation: [0, 0, 0], pose: "back_control_victim" }
        }
      },
      {
        id: "p9-step2",
        stepNumber: 2,
        name: "Avanço do Braço de Ataque Sob o Queixo",
        detail: "Deslizar o braço superior sob o queixo do oponente até alinhar o cotovelo com o pomo de adão.",
        pose3d: {
          tori: { position: [0, 0.55, -0.2], rotation: [0, 0.1, 0], pose: "rnc_under_chin" },
          uke: { position: [0, 0.45, 0], rotation: [0, 0, -0.1], pose: "back_control_victim" }
        }
      },
      {
        id: "p9-step3",
        stepNumber: 3,
        name: "Trava da Mão no Bíceps Oposto",
        detail: "Remover a mão de apoio e segurar firmemente no próprio bíceps oposto, dobrando o cotovelo.",
        pose3d: {
          tori: { position: [0, 0.55, -0.2], rotation: [0, 0, 0.1], pose: "rnc_bicep_grip" },
          uke: { position: [0, 0.45, 0], rotation: [0, 0, -0.1], pose: "rnc_choked_head" }
        }
      },
      {
        id: "p9-step4",
        stepNumber: 4,
        name: "Mão Atrás da Nuca & Compressão Isométrica",
        detail: "Esconder a mão livre atrás da nuca do oponente, expandir o peito e aplicar pressão isométrica fechando os cotovelos.",
        pose3d: {
          tori: { position: [0, 0.55, -0.2], rotation: [0, 0, 0.15], pose: "rnc_locked_choke" },
          uke: { position: [0, 0.45, 0], rotation: [0, 0, -0.2], pose: "rnc_tapped" }
        }
      }
    ]
  },
  {
    id: "puzzle-10",
    title: "Escapada dos 100kg com Fuga de Quadril",
    category: "escapada",
    categoryLabel: "Escapadas & Defesa",
    difficulty: "Intermediário",
    icon: "ph-shield-check",
    description: "Reconstrua a saída técnica por baixo nos 100kg para recuperar a guarda fechada ou meia-guarda.",
    tacticalTip: "Nunca fique plano de costas no tatame. A ponte precisa ser forte para criar o espaço necessário para a fuga de quadril.",
    checkpoints: [
      {
        id: "p10-step1",
        stepNumber: 1,
        name: "Proteção de Cúbitas (Frames no Pescoço & Quadril)",
        detail: "Posicionar o antebraço cruzado no pescoço do oponente e a outra mão apoiada na crista ilíaca (quadril).",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0, 0], pose: "side_control_bottom_frames" },
          uke: { position: [0, 0.4, 0], rotation: [0, -1.57, 0], pose: "side_control_top_heavy" }
        }
      },
      {
        id: "p10-step2",
        stepNumber: 2,
        name: "Ponte Explosiva (Bridge) para Criar Espaço",
        detail: "Apoiar os calcanhares perto dos glúteos e dar uma ponte explosiva diagonal direcionada ao ombro do passador.",
        pose3d: {
          tori: { position: [0, 0.35, 0], rotation: [0, 0, 0.4], pose: "bridge_explosive" },
          uke: { position: [0, 0.45, 0.1], rotation: [0, -1.4, 0.2], pose: "side_control_top_lifted" }
        }
      },
      {
        id: "p10-step3",
        stepNumber: 3,
        name: "Fuga de Quadril (Hip Escape) & Reposição do Joelho",
        detail: "No ápice da ponte, jogar o quadril violentamente para trás no solo e introduzir o joelho inferior no peito do oponente.",
        pose3d: {
          tori: { position: [-0.3, 0.25, 0], rotation: [0, 0.5, 0.2], pose: "hip_escape_knee_in" },
          uke: { position: [0.1, 0.4, 0], rotation: [0, -1.5, 0], pose: "side_control_top_pushed" }
        }
      },
      {
        id: "p10-step4",
        stepNumber: 4,
        name: "Recuperação Completa da Guarda Fechada",
        detail: "Usar o joelho introduzido como alavanca para empurrar o oponente e fechar os tornozelos nas costas, redefinindo a luta.",
        pose3d: {
          tori: { position: [0, 0.2, 0], rotation: [0, 0, 0], pose: "closed_guard_bottom" },
          uke: { position: [0, 0.5, 0.2], rotation: [0, 3.14, 0], pose: "closed_guard_top" }
        }
      }
    ]
  }
];
