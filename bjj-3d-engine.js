/**
 * BJJ 3D Engine - Motor 3D com Integração GrappleMap (bjjcortex-hub/3d-puzzle)
 * Gerador de Poses Anatômicas de Jiu-Jitsu 3D (Guarda, Montada, Passagem, Escapada, Finalização).
 */

// ── Joint Index Reference (GrappleMap Standard) ──────────────────────────────
// 0:LeftToe   1:RightToe   2:LeftHeel   3:RightHeel
// 4:LeftAnkle 5:RightAnkle 6:LeftKnee  7:RightKnee
// 8:LeftHip   9:RightHip  10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist
// 16:LeftHand 17:RightHand 18:LeftFingers 19:RightFingers
// 20:Core  21:Neck  22:Head

class BJJPoseBuilder {
  /**
   * Generates explicit 23-joint 3D coordinates for Tori & Uke based on BJJ technique pose key
   */
  static getPoseJoints(poseKey, toriFallbackPos, ukeFallbackPos) {
    switch (poseKey) {
      // 1. GUARDA FECHADA - PASSO 1: Domínio & Quebra de Postura
      case "closed_guard_bottom":
      case "closed_guard_top_broken":
        return {
          toriJoints: BJJPoseBuilder.createClosedGuardBottom(0, 0, 0),
          ukeJoints: BJJPoseBuilder.createClosedGuardTopBroken(0, 0, 0)
        };

      // 1. GUARDA FECHADA - PASSO 2: Fuga de Quadril
      case "hip_escape_guard":
      case "closed_guard_top_low":
        return {
          toriJoints: BJJPoseBuilder.createHipEscapeGuard(-0.15, 0, 0),
          ukeJoints: BJJPoseBuilder.createClosedGuardTopLow(0.08, 0, 0.05)
        };

      // 1. GUARDA FECHADA - PASSO 3: Canela no Escudo & Desbalanço
      case "scissor_loaded":
      case "off_balance_tilted":
        return {
          toriJoints: BJJPoseBuilder.createScissorLoaded(-0.2, 0, 0),
          ukeJoints: BJJPoseBuilder.createOffBalanceTilted(0.15, 0, 0.08)
        };

      // 1. GUARDA FECHADA - PASSO 4 / MONTADA: Estabilização
      case "mounted_top":
      case "mounted_bottom":
        return {
          toriJoints: BJJPoseBuilder.createMountedTop(0, 0, 0),
          ukeJoints: BJJPoseBuilder.createMountedBottom(0, 0, 0)
        };

      // 2. PASSAGEM DE GUARDA: Knee Slice / Toreando
      case "knee_slice_pass":
      case "toreando_pass":
      case "side_control_top":
      case "side_control_bottom":
        return {
          toriJoints: BJJPoseBuilder.createSideControlTop(0, 0, 0),
          ukeJoints: BJJPoseBuilder.createSideControlBottom(0, 0, 0)
        };

      // DEFAULT: Posição de Combate em Pé (Standing Tie-up)
      default:
        const tPos = toriFallbackPos || [-0.38, 0, 0];
        const uPos = ukeFallbackPos || [0.38, 0, 0];
        return {
          toriJoints: BJJPoseBuilder.createStandingJoints(tPos[0], tPos[2] || 0, false),
          ukeJoints: BJJPoseBuilder.createStandingJoints(uPos[0], uPos[2] || 3.14, true)
        };
    }
  }

  // ── 1. Guarda Fechada Por Baixo (Tori de costas no solo com guarda fechada)
  static createClosedGuardBottom(ox, oy, oz) {
    return [
      [-0.08, 0.42, oz + 0.42], // 0:LeftToe (Ganchado atrás das costas)
      [ 0.08, 0.42, oz + 0.42], // 1:RightToe
      [-0.08, 0.40, oz + 0.38], // 2:LeftHeel
      [ 0.08, 0.40, oz + 0.38], // 3:RightHeel
      [-0.10, 0.40, oz + 0.35], // 4:LeftAnkle
      [ 0.10, 0.40, oz + 0.35], // 5:RightAnkle
      [-0.32, 0.46, oz + 0.18], // 6:LeftKnee (Aberto envolvendo o quadril)
      [ 0.32, 0.46, oz + 0.18], // 7:RightKnee
      [-0.15, 0.12, oz],        // 8:LeftHip
      [ 0.15, 0.12, oz],        // 9:RightHip
      [-0.24, 0.12, oz - 0.35], // 10:LeftShoulder
      [ 0.24, 0.12, oz - 0.35], // 11:RightShoulder
      [-0.28, 0.35, oz - 0.15], // 12:LeftElbow (Puxando a gola/manga)
      [ 0.28, 0.35, oz - 0.15], // 13:RightElbow
      [-0.12, 0.52, oz + 0.05], // 14:LeftWrist
      [ 0.12, 0.52, oz + 0.05], // 15:RightWrist
      [-0.12, 0.50, oz + 0.08], // 16:LeftHand
      [ 0.12, 0.50, oz + 0.08], // 17:RightHand
      [-0.12, 0.48, oz + 0.10], // 18:LeftFingers
      [ 0.12, 0.48, oz + 0.10], // 19:RightFingers
      [ 0.0,  0.12, oz - 0.05], // 20:Core (No chão)
      [ 0.0,  0.12, oz - 0.42], // 21:Neck
      [ 0.0,  0.14, oz - 0.55]  // 22:Head
    ];
  }

  // ── 1. Guarda Fechada Por Cima (Uke de joelhos dentro da guarda com postura quebrada)
  static createClosedGuardTopBroken(ox, oy, oz) {
    return [
      [-0.22, 0.02, oz + 0.48], // 0:LeftToe
      [ 0.22, 0.02, oz + 0.48], // 1:RightToe
      [-0.22, 0.02, oz + 0.42], // 2:LeftHeel
      [ 0.22, 0.02, oz + 0.42], // 3:RightHeel
      [-0.24, 0.04, oz + 0.38], // 4:LeftAnkle
      [ 0.24, 0.04, oz + 0.38], // 5:RightAnkle
      [-0.28, 0.05, oz + 0.18], // 6:LeftKnee (No solo)
      [ 0.28, 0.05, oz + 0.18], // 7:RightKnee
      [-0.16, 0.38, oz + 0.28], // 8:LeftHip
      [ 0.16, 0.38, oz + 0.28], // 9:RightHip
      [-0.22, 0.58, oz - 0.15], // 10:LeftShoulder (Projetado à frente)
      [ 0.22, 0.58, oz - 0.15], // 11:RightShoulder
      [-0.25, 0.32, oz - 0.08], // 12:LeftElbow
      [ 0.25, 0.32, oz - 0.08], // 13:RightElbow
      [-0.14, 0.22, oz - 0.25], // 14:LeftWrist (Apoiado na costela do Tori)
      [ 0.14, 0.22, oz - 0.25], // 15:RightWrist
      [-0.14, 0.20, oz - 0.28], // 16:LeftHand
      [ 0.14, 0.20, oz - 0.28], // 17:RightHand
      [-0.14, 0.18, oz - 0.30], // 18:LeftFingers
      [ 0.14, 0.18, oz - 0.30], // 19:RightFingers
      [ 0.0,  0.45, oz + 0.05], // 20:Core
      [ 0.0,  0.62, oz - 0.25], // 21:Neck (Inclinado para frente)
      [ 0.0,  0.68, oz - 0.38]  // 22:Head
    ];
  }

  // ── 2. Fuga de Quadril & Escudo de Canela (Tori de lado abrindo espaço)
  static createHipEscapeGuard(ox, oy, oz) {
    return [
      [-0.25, 0.02, oz + 0.25], // 0:LeftToe (Pé de apoio no solo)
      [ 0.18, 0.45, oz + 0.12], // 1:RightToe
      [-0.25, 0.02, oz + 0.18], // 2:LeftHeel
      [ 0.18, 0.42, oz + 0.08], // 3:RightHeel
      [-0.25, 0.05, oz + 0.15], // 4:LeftAnkle
      [ 0.18, 0.40, oz + 0.05], // 5:RightAnkle
      [-0.35, 0.38, oz + 0.05], // 6:LeftKnee (Flexionado para fuga)
      [ 0.05, 0.48, oz - 0.08], // 7:RightKnee (Canela atravessando o peito)
      [-0.25, 0.14, oz - 0.10], // 8:LeftHip (Fugido de lado)
      [-0.05, 0.18, oz - 0.10], // 9:RightHip
      [-0.28, 0.14, oz - 0.42], // 10:LeftShoulder
      [ 0.15, 0.22, oz - 0.40], // 11:RightShoulder
      [-0.32, 0.32, oz - 0.25], // 12:LeftElbow
      [ 0.18, 0.42, oz - 0.20], // 13:RightElbow
      [-0.15, 0.52, oz - 0.05], // 14:LeftWrist (Pegada na gola)
      [ 0.12, 0.52, oz - 0.05], // 15:RightWrist (Pegada no tríceps)
      [-0.15, 0.50, oz - 0.02], // 16:LeftHand
      [ 0.12, 0.50, oz - 0.02], // 17:RightHand
      [-0.15, 0.48, oz + 0.0],  // 18:LeftFingers
      [ 0.12, 0.48, oz + 0.0],  // 19:RightFingers
      [-0.15, 0.14, oz - 0.20], // 20:Core
      [-0.10, 0.14, oz - 0.48], // 21:Neck
      [-0.10, 0.14, oz - 0.60]  // 22:Head
    ];
  }

  static createClosedGuardTopLow(ox, oy, oz) {
    return BJJPoseBuilder.createClosedGuardTopBroken(ox, oy, oz);
  }

  // ── 3. Escala da Tesoura Carregada
  static createScissorLoaded(ox, oy, oz) {
    return BJJPoseBuilder.createHipEscapeGuard(ox, oy, oz);
  }

  static createOffBalanceTilted(ox, oy, oz) {
    const u = BJJPoseBuilder.createClosedGuardTopBroken(ox, oy, oz);
    // Tilt Uke to the right for off-balance
    return u.map(([x, y, z]) => [x + 0.22, y + 0.05, z]);
  }

  // ── 4. Montada Por Cima (Tori montado sobre o abdômen do Uke)
  static createMountedTop(ox, oy, oz) {
    return [
      [-0.28, 0.05, oz - 0.35], // 0:LeftToe (Pés nas virilhas do Uke)
      [ 0.28, 0.05, oz - 0.35], // 1:RightToe
      [-0.28, 0.05, oz - 0.28], // 2:LeftHeel
      [ 0.28, 0.05, oz - 0.28], // 3:RightHeel
      [-0.28, 0.08, oz - 0.22], // 4:LeftAnkle
      [ 0.28, 0.08, oz - 0.22], // 5:RightAnkle
      [-0.32, 0.25, oz + 0.02], // 6:LeftKnee (Joelhos prensados)
      [ 0.32, 0.25, oz + 0.02], // 7:RightKnee
      [-0.14, 0.62, oz - 0.05], // 8:LeftHip (Montado no abdômen)
      [ 0.14, 0.62, oz - 0.05], // 9:RightHip
      [-0.22, 1.02, oz - 0.15], // 10:LeftShoulder
      [ 0.22, 1.02, oz - 0.15], // 11:RightShoulder
      [-0.28, 0.72, oz + 0.10], // 12:LeftElbow (Posturado com pressão)
      [ 0.28, 0.72, oz + 0.10], // 13:RightElbow
      [-0.22, 0.42, oz + 0.20], // 14:LeftWrist (Mãos no peito do Uke)
      [ 0.22, 0.42, oz + 0.20], // 15:RightWrist
      [-0.22, 0.38, oz + 0.22], // 16:LeftHand
      [ 0.22, 0.38, oz + 0.22], // 17:RightHand
      [-0.22, 0.35, oz + 0.25], // 18:LeftFingers
      [ 0.22, 0.35, oz + 0.25], // 19:RightFingers
      [ 0.0,  0.75, oz - 0.08], // 20:Core
      [ 0.0,  1.12, oz - 0.18], // 21:Neck
      [ 0.0,  1.26, oz - 0.20]  // 22:Head
    ];
  }

  // ── 4. Montada Por Baixo (Uke de costas sob a montada do Tori)
  static createMountedBottom(ox, oy, oz) {
    return [
      [-0.18, 0.02, oz + 0.65], // 0:LeftToe
      [ 0.18, 0.02, oz + 0.65], // 1:RightToe
      [-0.18, 0.02, oz + 0.58], // 2:LeftHeel
      [ 0.18, 0.02, oz + 0.58], // 3:RightHeel
      [-0.18, 0.05, oz + 0.52], // 4:LeftAnkle
      [ 0.18, 0.05, oz + 0.52], // 5:RightAnkle
      [-0.22, 0.18, oz + 0.30], // 6:LeftKnee (Pernas estendidas no chão)
      [ 0.22, 0.18, oz + 0.30], // 7:RightKnee
      [-0.15, 0.10, oz - 0.05], // 8:LeftHip
      [ 0.15, 0.10, oz - 0.05], // 9:RightHip
      [-0.24, 0.10, oz - 0.45], // 10:LeftShoulder
      [ 0.24, 0.10, oz - 0.45], // 11:RightShoulder
      [-0.28, 0.32, oz - 0.20], // 12:LeftElbow (Defendendo o pescoço)
      [ 0.28, 0.32, oz - 0.20], // 13:RightElbow
      [-0.14, 0.48, oz - 0.05], // 14:LeftWrist
      [ 0.14, 0.48, oz - 0.05], // 15:RightWrist
      [-0.14, 0.45, oz - 0.02], // 16:LeftHand
      [ 0.14, 0.45, oz - 0.02], // 17:RightHand
      [-0.14, 0.42, oz + 0.0],  // 18:LeftFingers
      [ 0.14, 0.42, oz + 0.0],  // 19:RightFingers
      [ 0.0,  0.10, oz - 0.20], // 20:Core (De costas no tatame)
      [ 0.0,  0.10, oz - 0.52], // 21:Neck
      [ 0.0,  0.10, oz - 0.65]  // 22:Head
    ];
  }

  // ── 5. Passagem de Guarda / Imobilização Lateral (Side Control)
  static createSideControlTop(ox, oy, oz) {
    return [
      [-0.35, 0.02, oz + 0.20], // 0:LeftToe
      [ 0.35, 0.02, oz + 0.20], // 1:RightToe
      [-0.35, 0.02, oz + 0.12], // 2:LeftHeel
      [ 0.35, 0.02, oz + 0.12], // 3:RightHeel
      [-0.35, 0.05, oz + 0.08], // 4:LeftAnkle
      [ 0.35, 0.05, oz + 0.08], // 5:RightAnkle
      [-0.38, 0.18, oz - 0.10], // 6:LeftKnee (Base esparramada de 100kg)
      [ 0.38, 0.18, oz - 0.10], // 7:RightKnee
      [-0.15, 0.32, oz - 0.10], // 8:LeftHip
      [ 0.15, 0.32, oz - 0.10], // 9:RightHip
      [-0.22, 0.38, oz - 0.42], // 10:LeftShoulder (Pressão de ombro no queixo)
      [ 0.22, 0.38, oz - 0.42], // 11:RightShoulder
      [-0.35, 0.18, oz - 0.25], // 12:LeftElbow (Esgrima sob a cabeça)
      [ 0.35, 0.18, oz - 0.25], // 13:RightElbow
      [-0.25, 0.12, oz - 0.05], // 14:LeftWrist
      [ 0.25, 0.12, oz - 0.05], // 15:RightWrist
      [-0.25, 0.10, oz - 0.02], // 16:LeftHand
      [ 0.25, 0.10, oz - 0.02], // 17:RightHand
      [-0.25, 0.08, oz + 0.0],  // 18:LeftFingers
      [ 0.25, 0.08, oz + 0.0],  // 19:RightFingers
      [ 0.0,  0.35, oz - 0.22], // 20:Core
      [ 0.0,  0.38, oz - 0.48], // 21:Neck
      [ 0.0,  0.38, oz - 0.60]  // 22:Head
    ];
  }

  static createSideControlBottom(ox, oy, oz) {
    return BJJPoseBuilder.createMountedBottom(ox, oy, oz);
  }

  // ── Em Pé (Combate Frontal)
  static createStandingJoints(offsetX, angleRad, isOpponent = false) {
    const cos = Math.cos(angleRad);
    const sin = Math.sin(angleRad);

    const transformPoint = (x, y, z) => {
      const rx = x * cos - z * sin;
      const rz = x * sin + z * cos;
      return [rx + offsetX, y, rz];
    };

    return [
      transformPoint(-0.14, 0.02, 0.16),  // 0:LeftToe
      transformPoint(0.14, 0.02, 0.16),   // 1:RightToe
      transformPoint(-0.14, 0.02, -0.06), // 2:LeftHeel
      transformPoint(0.14, 0.02, -0.06),  // 3:RightHeel
      transformPoint(-0.14, 0.06, 0.0),   // 4:LeftAnkle
      transformPoint(0.14, 0.06, 0.0),    // 5:RightAnkle
      transformPoint(-0.15, 0.42, 0.08),  // 6:LeftKnee
      transformPoint(0.15, 0.42, 0.08),   // 7:RightKnee
      transformPoint(-0.14, 0.78, 0.0),   // 8:LeftHip
      transformPoint(0.14, 0.78, 0.0),    // 9:RightHip
      transformPoint(-0.22, 1.28, -0.02), // 10:LeftShoulder
      transformPoint(0.22, 1.28, -0.02),  // 11:RightShoulder
      transformPoint(-0.26, 1.05, 0.18),  // 12:LeftElbow
      transformPoint(0.26, 1.05, 0.18),   // 13:RightElbow
      transformPoint(-0.22, 0.95, 0.35),  // 14:LeftWrist
      transformPoint(0.22, 0.95, 0.35),   // 15:RightWrist
      transformPoint(-0.22, 0.92, 0.38),  // 16:LeftHand
      transformPoint(0.22, 0.92, 0.38),   // 17:RightHand
      transformPoint(-0.22, 0.89, 0.40),  // 18:LeftFingers
      transformPoint(0.22, 0.89, 0.40),   // 19:RightFingers
      transformPoint(0.0, 0.80, 0.0),     // 20:Core
      transformPoint(0.0, 1.32, -0.02),   // 21:Neck
      transformPoint(0.0, 1.48, -0.02)    // 22:Head
    ];
  }
}

class GrappleHumanoidRig {
  constructor(scene, skinColorHex, giColorHex, isTori = true) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.scene.add(this.group);

    // Materials
    this.skinMat = new THREE.MeshStandardMaterial({
      color: skinColorHex,
      roughness: 0.40,
      metalness: 0.05
    });

    this.giMat = new THREE.MeshStandardMaterial({
      color: giColorHex,
      roughness: 0.65,
      metalness: 0.05
    });

    this.beltMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.50,
      metalness: 0.10
    });

    this.rankSleeveMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      roughness: 0.30,
      metalness: 0.10
    });

    // 23-joint Segment Definitions: [jointStart, jointEnd, radiusStart, radiusEnd, isSkin]
    const segmentDefs = [
      // Spine / Torso
      [20, 21, 0.070, 0.055, false], // Spine Core to Neck
      [21, 22, 0.035, 0.030, true],  // Neck to Head
      [20, 10, 0.065, 0.050, false], // Core to L Shoulder
      [20, 11, 0.065, 0.050, false], // Core to R Shoulder
      [10, 11, 0.055, 0.055, false], // Shoulder Collar
      [20,  8, 0.070, 0.055, false], // Core to L Hip
      [20,  9, 0.070, 0.055, false], // Core to R Hip
      [ 8,  9, 0.060, 0.060, false], // Pelvis / Hip Line
      // Left Leg
      [ 8,  6, 0.060, 0.048, false], // L Thigh
      [ 6,  4, 0.045, 0.036, false], // L Calf
      [ 4,  0, 0.024, 0.016, true],  // L Foot
      // Right Leg
      [ 9,  7, 0.060, 0.048, false], // R Thigh
      [ 7,  5, 0.045, 0.036, false], // R Calf
      [ 5,  1, 0.024, 0.016, true],  // R Foot
      // Left Arm
      [10, 12, 0.042, 0.034, false], // L Upper Arm
      [12, 14, 0.032, 0.026, false], // L Forearm
      [14, 16, 0.022, 0.016, true],  // L Hand
      // Right Arm
      [11, 13, 0.042, 0.034, false], // R Upper Arm
      [13, 15, 0.032, 0.026, false], // R Forearm
      [15, 17, 0.022, 0.016, true]   // R Hand
    ];

    this.segments = segmentDefs.map(([j1, j2, r1, r2, isSkin]) => {
      const geo = new THREE.CylinderGeometry(r2, r1, 1, 12, 1);
      const mesh = new THREE.Mesh(geo, isSkin ? this.skinMat : this.giMat);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.group.add(mesh);
      return { mesh, j1, j2 };
    });

    // Head Sphere
    this.head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 18, 18), this.skinMat);
    this.head.castShadow = true;
    this.group.add(this.head);

    // Belt Ring on Waist
    this.beltRing = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.09, 0.06, 14), this.beltMat);
    this.beltRing.castShadow = true;
    this.group.add(this.beltRing);

    // Belt Knot & Rank Sleeve
    this.beltKnot = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, 0.06), this.beltMat);
    this.rankSleeve = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.07, 0.02), this.rankSleeveMat);
    this.group.add(this.beltKnot);
    this.group.add(this.rankSleeve);

    this.currentJoints = null;
    this.targetJoints = null;
  }

  updateJoints(joints, immediate = false) {
    if (!joints || joints.length < 23) return;

    if (immediate || !this.currentJoints) {
      this.currentJoints = joints.map(j => [...j]);
      this.targetJoints = joints.map(j => [...j]);
      this.applyJoints(this.currentJoints);
    } else {
      this.targetJoints = joints.map(j => [...j]);
    }
  }

  animateLerp(lerpFactor = 0.12) {
    if (!this.currentJoints || !this.targetJoints) return;

    let needsUpdate = false;
    for (let i = 0; i < 23; i++) {
      for (let k = 0; k < 3; k++) {
        const diff = this.targetJoints[i][k] - this.currentJoints[i][k];
        if (Math.abs(diff) > 0.0001) {
          this.currentJoints[i][k] += diff * lerpFactor;
          needsUpdate = true;
        }
      }
    }

    if (needsUpdate) {
      this.applyJoints(this.currentJoints);
    }
  }

  applyJoints(joints) {
    const P = (i) => new THREE.Vector3(joints[i][0], joints[i][1], joints[i][2]);
    const UP = new THREE.Vector3(0, 1, 0);
    const D = new THREE.Vector3();

    this.segments.forEach(({ mesh, j1, j2 }) => {
      const a = P(j1), b = P(j2);
      D.subVectors(b, a);
      const len = D.length();
      if (len < 0.001) {
        mesh.visible = false;
        return;
      }
      mesh.visible = true;
      mesh.scale.set(1, len, 1);
      mesh.position.addVectors(a, b).multiplyScalar(0.5);
      mesh.quaternion.setFromUnitVectors(UP, D.normalize());
    });

    // Head Position
    const headPos = P(22);
    this.head.position.copy(headPos);

    // Belt Position & Orientation at Core / Hip level
    const corePos = P(20);
    const lHipPos = P(8);
    const rHipPos = P(9);
    const hipCenter = lHipPos.clone().add(rHipPos).multiplyScalar(0.5);
    const waistPos = corePos.clone().add(hipCenter).multiplyScalar(0.5);

    this.beltRing.position.copy(waistPos);

    const hipRight = rHipPos.clone().sub(lHipPos);
    const neckPos = P(21);
    const spine = neckPos.clone().sub(corePos);
    const fwd = hipRight.clone().cross(spine).normalize();

    this.beltKnot.position.copy(waistPos.clone().add(fwd.clone().multiplyScalar(0.09)));
    this.rankSleeve.position.copy(waistPos.clone().add(fwd.clone().multiplyScalar(0.10)).sub(new THREE.Vector3(0, 0.04, 0)));
  }

  setVisible(visible) {
    this.group.visible = visible;
  }
}

class BJJ3DEngine {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.width = this.container.clientWidth || this.container.offsetWidth || 600;
    this.height = this.container.clientHeight || this.container.offsetHeight || 420;

    // Three.js Core components
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;

    // 3D Humanoid Rigs (GrappleMap 23-Joint System)
    this.toriRig = null; // Tori (Royal Blue Gi)
    this.ukeRig = null;  // Uke (Dark Carbon Gi)
    this.matGroup = null;

    // Animation & State
    this.autoRotate = false;
    this.animationId = null;

    this.init();
  }

  init() {
    if (typeof THREE === "undefined") {
      console.error("Three.js library is missing.");
      return;
    }

    // 1. Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x080c14);
    this.scene.fog = new THREE.FogExp2(0x080c14, 0.05);

    // 2. Camera setup
    this.camera = new THREE.PerspectiveCamera(42, this.width / this.height, 0.1, 100);
    this.camera.position.set(2.4, 1.8, 3.2);

    // 3. Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    // Clear container and append canvas
    this.container.innerHTML = "";
    this.container.appendChild(this.renderer.domElement);

    // 4. Orbit Controls
    const OrbitControlsClass = (typeof THREE !== "undefined" && THREE.OrbitControls) ? THREE.OrbitControls : window.OrbitControls;
    if (OrbitControlsClass) {
      this.controls = new OrbitControlsClass(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2 + 0.08;
      this.controls.minDistance = 0.8;
      this.controls.maxDistance = 7.0;
      this.controls.target.set(0, 0.35, 0);
    }

    // 5. Studio Lighting
    this.setupLighting();

    // 6. Build Tatame (BJJ Mat)
    this.buildMat();

    // 7. Build GrappleMap Humanoid Rigs
    this.buildFighters();

    // 8. Resize Handling
    window.addEventListener("resize", () => this.onWindowResize());
    if (window.ResizeObserver && this.container) {
      const resizeObserver = new ResizeObserver(() => this.onWindowResize());
      resizeObserver.observe(this.container);
    }
    setTimeout(() => this.onWindowResize(), 50);

    // 9. Start Render Loop
    this.animate();
  }

  setupLighting() {
    const hemiLight = new THREE.HemisphereLight(0xfff8ee, 0x0f172a, 1.2);
    hemiLight.position.set(0, 10, 0);
    this.scene.add(hemiLight);

    const keyLight = new THREE.DirectionalLight(0xfffaed, 1.8);
    keyLight.position.set(4.0, 6.0, 4.0);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.bias = -0.0008;
    this.scene.add(keyLight);

    const cyanRim = new THREE.DirectionalLight(0x38bdf8, 1.5);
    cyanRim.position.set(-4.0, 3.0, -3.0);
    this.scene.add(cyanRim);

    const goldPoint = new THREE.PointLight(0xf59e0b, 1.6, 6);
    goldPoint.position.set(0, 2.5, 0);
    this.scene.add(goldPoint);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
    this.scene.add(ambientLight);
  }

  buildMat() {
    this.matGroup = new THREE.Group();

    const matGeometry = new THREE.BoxGeometry(4.4, 0.08, 4.4);
    const matMaterial = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.35,
      metalness: 0.15
    });
    const matMesh = new THREE.Mesh(matGeometry, matMaterial);
    matMesh.position.y = -0.04;
    matMesh.receiveShadow = true;
    this.matGroup.add(matMesh);

    const outerRingGeo = new THREE.RingGeometry(1.5, 1.54, 64);
    const outerRingMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, side: THREE.DoubleSide, transparent: true, opacity: 0.85 });
    const outerRingMesh = new THREE.Mesh(outerRingGeo, outerRingMat);
    outerRingMesh.rotation.x = Math.PI / 2;
    outerRingMesh.position.y = 0.002;
    this.matGroup.add(outerRingMesh);

    const centerRingGeo = new THREE.RingGeometry(0.55, 0.58, 48);
    const centerRingMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, side: THREE.DoubleSide, transparent: true, opacity: 0.75 });
    const centerRingMesh = new THREE.Mesh(centerRingGeo, centerRingMat);
    centerRingMesh.rotation.x = Math.PI / 2;
    centerRingMesh.position.y = 0.003;
    this.matGroup.add(centerRingMesh);

    const gridHelper = new THREE.GridHelper(4.4, 16, 0x38bdf8, 0x1f293d);
    gridHelper.position.y = 0.004;
    this.matGroup.add(gridHelper);

    this.scene.add(this.matGroup);
  }

  buildFighters() {
    // Tori: Skin tone 0xe0a96d, Royal Blue Gi 0x1d4ed8
    this.toriRig = new GrappleHumanoidRig(this.scene, 0xe0a96d, 0x1d4ed8, true);
    // Uke: Skin tone 0xd49b6a, Dark Carbon Gi 0x1e293b
    this.ukeRig = new GrappleHumanoidRig(this.scene, 0xd49b6a, 0x1e293b, false);

    // Initial default pose: Closed Guard
    const initialPose = BJJPoseBuilder.getPoseJoints("closed_guard_bottom");
    this.toriRig.updateJoints(initialPose.toriJoints, true);
    this.ukeRig.updateJoints(initialPose.ukeJoints, true);
  }

  setPose(poseData) {
    if (!poseData) return;

    let toriPos = null;
    let ukePos = null;

    if (poseData.toriJoints && poseData.ukeJoints) {
      toriPos = poseData.toriJoints;
      ukePos = poseData.ukeJoints;
    } else {
      const poseKey = (poseData.tori && poseData.tori.pose) ? poseData.tori.pose : "default";
      const toriPosFB = poseData.tori ? poseData.tori.position : [-0.35, 0, 0];
      const ukePosFB = poseData.uke ? poseData.uke.position : [0.35, 0, 0];

      const generated = BJJPoseBuilder.getPoseJoints(poseKey, toriPosFB, ukePosFB);
      toriPos = generated.toriJoints;
      ukePos = generated.ukeJoints;
    }

    if (this.toriRig && toriPos) this.toriRig.updateJoints(toriPos);
    if (this.ukeRig && ukePos) this.ukeRig.updateJoints(ukePos);
  }

  updateCameraPreset(presetName) {
    if (!this.camera || !this.controls) return;

    switch (presetName) {
      case "top": // Top-Down View
        this.animateCameraPosition(0, 3.8, 0.1, 0, 0.25, 0);
        break;
      case "side": // Side Profile Angle
        this.animateCameraPosition(2.8, 1.2, 0, 0, 0.3, 0);
        break;
      case "tight": // Close Grip Angle
        this.animateCameraPosition(1.1, 0.9, 1.2, 0, 0.35, 0);
        break;
      case "default":
      default: // 3/4 Isometric Perspective
        this.animateCameraPosition(2.4, 1.8, 3.2, 0, 0.35, 0);
        break;
    }
  }

  animateCameraPosition(cx, cy, cz, tx, ty, tz) {
    const startCam = { x: this.camera.position.x, y: this.camera.position.y, z: this.camera.position.z };
    const startTarget = { x: this.controls ? this.controls.target.x : 0, y: this.controls ? this.controls.target.y : 0, z: this.controls ? this.controls.target.z : 0 };
    let startTime = null;
    const duration = 600;

    const step = (now) => {
      if (!startTime) startTime = now;
      const progress = Math.min((now - startTime) / duration, 1);
      const ease = 0.5 - Math.cos(progress * Math.PI) / 2;

      this.camera.position.x = startCam.x + (cx - startCam.x) * ease;
      this.camera.position.y = startCam.y + (cy - startCam.y) * ease;
      this.camera.position.z = startCam.z + (cz - startCam.z) * ease;

      if (this.controls) {
        this.controls.target.x = startTarget.x + (tx - startTarget.x) * ease;
        this.controls.target.y = startTarget.y + (ty - startTarget.y) * ease;
        this.controls.target.z = startTarget.z + (tz - startTarget.z) * ease;
        this.controls.update();
      }

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };
    requestAnimationFrame(step);
  }

  toggleAutoRotate(enable) {
    this.autoRotate = enable !== undefined ? enable : !this.autoRotate;
    if (this.controls) {
      this.controls.autoRotate = this.autoRotate;
      this.controls.autoRotateSpeed = 2.0;
    }
    return this.autoRotate;
  }

  resetCamera() {
    this.updateCameraPreset("default");
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());

    // Lerp update joint animations smoothly
    if (this.toriRig) this.toriRig.animateLerp(0.12);
    if (this.ukeRig) this.ukeRig.animateLerp(0.12);

    if (this.controls) {
      this.controls.update();
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;

    const w = this.container.clientWidth || this.container.offsetWidth || 600;
    const h = this.container.clientHeight || this.container.offsetHeight || 420;

    if (w === 0 || h === 0) return;

    this.width = w;
    this.height = h;

    this.camera.aspect = this.width / this.height;
    this.camera.updateProjectionMatrix();

    this.renderer.setSize(this.width, this.height);
  }

  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    if (this.renderer && this.renderer.domElement) {
      this.renderer.domElement.remove();
    }
  }
}

window.BJJ3DEngine = BJJ3DEngine;
window.GrappleHumanoidRig = GrappleHumanoidRig;
window.BJJPoseBuilder = BJJPoseBuilder;
