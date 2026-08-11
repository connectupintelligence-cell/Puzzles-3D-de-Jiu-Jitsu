/**
 * BJJ 3D Engine - Motor 3D Baseado no Repositório Oficial GrappleMap (Eelis/GrappleMap)
 * Implementa rigorosamente os 28 segmentos corporais e 23 articulações do padrão GrappleMap (Eelis).
 */

// ── GrappleMap Standard Joint Indices (Eelis/GrappleMap) ─────────────────────
// 0:LeftToe   1:RightToe   2:LeftHeel   3:RightHeel
// 4:LeftAnkle 5:RightAnkle 6:LeftKnee  7:RightKnee
// 8:LeftHip   9:RightHip  10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist
// 16:LeftHand 17:RightHand 18:LeftFingers 19:RightFingers
// 20:Core  21:Neck  22:Head

class BJJPoseBuilder {
  static getPoseJoints(poseKey, toriFallbackPos, ukeFallbackPos) {
    switch (poseKey) {
      // 1. GUARDA FECHADA - PASSO 1: Domínio de Pegadas & Quebra de Postura
      case "closed_guard_bottom":
      case "closed_guard_top_broken":
        return {
          toriJoints: BJJPoseBuilder.createClosedGuardBottom(),
          ukeJoints: BJJPoseBuilder.createClosedGuardTopBroken()
        };

      // 1. GUARDA FECHADA - PASSO 2: Fuga de Quadril
      case "hip_escape_guard":
      case "closed_guard_top_low":
        return {
          toriJoints: BJJPoseBuilder.createHipEscapeGuard(),
          ukeJoints: BJJPoseBuilder.createClosedGuardTopLow()
        };

      // 1. GUARDA FECHADA - PASSO 3: Escala da Canela no Tórax (Tesourinha)
      case "scissor_loaded":
      case "off_balance_tilted":
        return {
          toriJoints: BJJPoseBuilder.createScissorLoaded(),
          ukeJoints: BJJPoseBuilder.createOffBalanceTilted()
        };

      // 1. GUARDA FECHADA - PASSO 4 / MONTADA: Subida na Montada
      case "mounted_top":
      case "mounted_bottom":
        return {
          toriJoints: BJJPoseBuilder.createMountedTop(),
          ukeJoints: BJJPoseBuilder.createMountedBottom()
        };

      // 2. PASSAGEM DE GUARDA / SIDE CONTROL
      case "knee_slice_pass":
      case "toreando_pass":
      case "side_control_top":
      case "side_control_bottom":
        return {
          toriJoints: BJJPoseBuilder.createSideControlTop(),
          ukeJoints: BJJPoseBuilder.createSideControlBottom()
        };

      // DEFAULT: Posição de Combate em Pé
      default:
        return {
          toriJoints: BJJPoseBuilder.createStandingJoints(-0.32, 0, false),
          ukeJoints: BJJPoseBuilder.createStandingJoints(0.32, Math.PI, true)
        };
    }
  }

  // ── 1. Guarda Fechada Por Baixo (GrappleMap Eelis Standard)
  static createClosedGuardBottom() {
    return [
      [-0.06, 0.28, 0.25], // 0:LeftToe
      [ 0.06, 0.28, 0.25], // 1:RightToe
      [-0.06, 0.26, 0.22], // 2:LeftHeel
      [ 0.06, 0.26, 0.22], // 3:RightHeel
      [-0.08, 0.26, 0.20], // 4:LeftAnkle
      [ 0.08, 0.26, 0.20], // 5:RightAnkle
      [-0.26, 0.32, 0.08], // 6:LeftKnee
      [ 0.26, 0.32, 0.08], // 7:RightKnee
      [-0.14, 0.08, -0.08],// 8:LeftHip
      [ 0.14, 0.08, -0.08],// 9:RightHip
      [-0.22, 0.08, -0.42],// 10:LeftShoulder
      [ 0.22, 0.08, -0.42],// 11:RightShoulder
      [-0.25, 0.22, -0.22],// 12:LeftElbow
      [ 0.25, 0.22, -0.22],// 13:RightElbow
      [-0.10, 0.36, -0.05],// 14:LeftWrist
      [ 0.12, 0.36, -0.05],// 15:RightWrist
      [-0.10, 0.34, -0.02],// 16:LeftHand
      [ 0.12, 0.34, -0.02],// 17:RightHand
      [-0.10, 0.32, 0.0],  // 18:LeftFingers
      [ 0.12, 0.32, 0.0],  // 19:RightFingers
      [ 0.0,  0.08, -0.15],// 20:Core
      [ 0.0,  0.08, -0.48],// 21:Neck
      [ 0.0,  0.10, -0.60] // 22:Head
    ];
  }

  // ── 1. Guarda Fechada Por Cima
  static createClosedGuardTopBroken() {
    return [
      [-0.18, 0.02, 0.38], // 0:LeftToe
      [ 0.18, 0.02, 0.38], // 1:RightToe
      [-0.18, 0.02, 0.32], // 2:LeftHeel
      [ 0.18, 0.02, 0.32], // 3:RightHeel
      [-0.18, 0.04, 0.28], // 4:LeftAnkle
      [ 0.18, 0.04, 0.28], // 5:RightAnkle
      [-0.22, 0.05, 0.08], // 6:LeftKnee
      [ 0.22, 0.05, 0.08], // 7:RightKnee
      [-0.14, 0.25, 0.15], // 8:LeftHip
      [ 0.14, 0.25, 0.15], // 9:RightHip
      [-0.20, 0.38, -0.18],// 10:LeftShoulder
      [ 0.20, 0.38, -0.18],// 11:RightShoulder
      [-0.22, 0.22, -0.10],// 12:LeftElbow
      [ 0.22, 0.22, -0.10],// 13:RightElbow
      [-0.12, 0.15, -0.28],// 14:LeftWrist
      [ 0.12, 0.15, -0.28],// 15:RightWrist
      [-0.12, 0.14, -0.30],// 16:LeftHand
      [ 0.12, 0.14, -0.30],// 17:RightHand
      [-0.12, 0.12, -0.32],// 18:LeftFingers
      [ 0.12, 0.12, -0.32],// 19:RightFingers
      [ 0.0,  0.30, 0.0],  // 20:Core
      [ 0.0,  0.42, -0.25],// 21:Neck
      [ 0.0,  0.45, -0.38] // 22:Head
    ];
  }

  // ── 2. Fuga de Quadril & Escudo de Canela
  static createHipEscapeGuard() {
    return [
      [-0.22, 0.02, 0.18], // 0:LeftToe
      [ 0.12, 0.32, 0.05], // 1:RightToe
      [-0.22, 0.02, 0.12], // 2:LeftHeel
      [ 0.12, 0.30, 0.02], // 3:RightHeel
      [-0.22, 0.05, 0.08], // 4:LeftAnkle
      [ 0.12, 0.28, -0.02],// 5:RightAnkle
      [-0.30, 0.25, 0.02], // 6:LeftKnee
      [ 0.02, 0.32, -0.12],// 7:RightKnee
      [-0.20, 0.10, -0.12],// 8:LeftHip
      [-0.02, 0.12, -0.12],// 9:RightHip
      [-0.25, 0.10, -0.44],// 10:LeftShoulder
      [ 0.12, 0.15, -0.42],// 11:RightShoulder
      [-0.28, 0.22, -0.28],// 12:LeftElbow
      [ 0.15, 0.32, -0.22],// 13:RightElbow
      [-0.12, 0.38, -0.10],// 14:LeftWrist
      [ 0.10, 0.38, -0.10],// 15:RightWrist
      [-0.12, 0.36, -0.08],// 16:LeftHand
      [ 0.10, 0.36, -0.08],// 17:RightHand
      [-0.12, 0.34, -0.06],// 18:LeftFingers
      [ 0.10, 0.34, -0.06],// 19:RightFingers
      [-0.12, 0.10, -0.22],// 20:Core
      [-0.08, 0.10, -0.48],// 21:Neck
      [-0.08, 0.10, -0.60] // 22:Head
    ];
  }

  static createClosedGuardTopLow() {
    return BJJPoseBuilder.createClosedGuardTopBroken();
  }

  static createScissorLoaded() {
    return BJJPoseBuilder.createHipEscapeGuard();
  }

  static createOffBalanceTilted() {
    const u = BJJPoseBuilder.createClosedGuardTopBroken();
    return u.map(([x, y, z]) => [x + 0.18, y + 0.05, z]);
  }

  // ── 4. Montada Por Cima
  static createMountedTop() {
    return [
      [-0.24, 0.04, -0.30], // 0:LeftToe
      [ 0.24, 0.04, -0.30], // 1:RightToe
      [-0.24, 0.04, -0.24], // 2:LeftHeel
      [ 0.24, 0.04, -0.24], // 3:RightHeel
      [-0.24, 0.06, -0.18], // 4:LeftAnkle
      [ 0.24, 0.06, -0.18], // 5:RightAnkle
      [-0.28, 0.15, 0.02],  // 6:LeftKnee
      [ 0.28, 0.15, 0.02],  // 7:RightKnee
      [-0.14, 0.42, -0.08], // 8:LeftHip
      [ 0.14, 0.42, -0.08], // 9:RightHip
      [-0.20, 0.78, -0.18], // 10:LeftShoulder
      [ 0.20, 0.78, -0.18], // 11:RightShoulder
      [-0.25, 0.52, 0.05],  // 12:LeftElbow
      [ 0.25, 0.52, 0.05],  // 13:RightElbow
      [-0.18, 0.32, 0.15],  // 14:LeftWrist
      [ 0.18, 0.32, 0.15],  // 15:RightWrist
      [-0.18, 0.30, 0.18],  // 16:LeftHand
      [ 0.18, 0.30, 0.18],  // 17:RightHand
      [-0.18, 0.28, 0.20],  // 18:LeftFingers
      [ 0.18, 0.28, 0.20],  // 19:RightFingers
      [ 0.0,  0.55, -0.10], // 20:Core
      [ 0.0,  0.88, -0.20], // 21:Neck
      [ 0.0,  0.98, -0.22]  // 22:Head
    ];
  }

  // ── 4. Montada Por Baixo
  static createMountedBottom() {
    return [
      [-0.16, 0.02, 0.55], // 0:LeftToe
      [ 0.16, 0.02, 0.55], // 1:RightToe
      [-0.16, 0.02, 0.48], // 2:LeftHeel
      [ 0.16, 0.02, 0.48], // 3:RightHeel
      [-0.16, 0.05, 0.42], // 4:LeftAnkle
      [ 0.16, 0.05, 0.42], // 5:RightAnkle
      [-0.20, 0.12, 0.22], // 6:LeftKnee
      [ 0.20, 0.12, 0.22], // 7:RightKnee
      [-0.14, 0.08, -0.08],// 8:LeftHip
      [ 0.14, 0.08, -0.08],// 9:RightHip
      [-0.22, 0.08, -0.42],// 10:LeftShoulder
      [ 0.22, 0.08, -0.42],// 11:RightShoulder
      [-0.25, 0.22, -0.22],// 12:LeftElbow
      [ 0.25, 0.22, -0.22],// 13:RightElbow
      [-0.12, 0.35, -0.08],// 14:LeftWrist
      [ 0.12, 0.35, -0.08],// 15:RightWrist
      [-0.12, 0.32, -0.05],// 16:LeftHand
      [ 0.12, 0.32, -0.05],// 17:RightHand
      [-0.12, 0.30, -0.02],// 18:LeftFingers
      [ 0.12, 0.30, -0.02],// 19:RightFingers
      [ 0.0,  0.08, -0.18],// 20:Core
      [ 0.0,  0.08, -0.48],// 21:Neck
      [ 0.0,  0.08, -0.60] // 22:Head
    ];
  }

  // ── 5. Imobilização Lateral
  static createSideControlTop() {
    return [
      [-0.32, 0.02, 0.15], // 0:LeftToe
      [ 0.32, 0.02, 0.15], // 1:RightToe
      [-0.32, 0.02, 0.08], // 2:LeftHeel
      [ 0.32, 0.02, 0.08], // 3:RightHeel
      [-0.32, 0.05, 0.04], // 4:LeftAnkle
      [ 0.32, 0.05, 0.04], // 5:RightAnkle
      [-0.35, 0.12, -0.15],// 6:LeftKnee
      [ 0.35, 0.12, -0.15],// 7:RightKnee
      [-0.14, 0.22, -0.15],// 8:LeftHip
      [ 0.14, 0.22, -0.15],// 9:RightHip
      [-0.20, 0.28, -0.42],// 10:LeftShoulder
      [ 0.20, 0.28, -0.42],// 11:RightShoulder
      [-0.30, 0.15, -0.28],// 12:LeftElbow
      [ 0.30, 0.15, -0.28],// 13:RightElbow
      [-0.20, 0.10, -0.08],// 14:LeftWrist
      [ 0.20, 0.10, -0.08],// 15:RightWrist
      [-0.20, 0.08, -0.05],// 16:LeftHand
      [ 0.20, 0.08, -0.05],// 17:RightHand
      [-0.20, 0.06, -0.02],// 18:LeftFingers
      [ 0.20, 0.06, -0.02],// 19:RightFingers
      [ 0.0,  0.25, -0.25],// 20:Core
      [ 0.0,  0.28, -0.48],// 21:Neck
      [ 0.0,  0.28, -0.60] // 22:Head
    ];
  }

  static createSideControlBottom() {
    return BJJPoseBuilder.createMountedBottom();
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

    // Official Eelis/GrappleMap Athlete Colors & Materials
    this.skinMat = new THREE.MeshStandardMaterial({
      color: skinColorHex,
      roughness: 0.38,
      metalness: 0.05
    });

    this.giMat = new THREE.MeshStandardMaterial({
      color: giColorHex,
      roughness: 0.65,
      metalness: 0.05
    });

    this.lapelMat = new THREE.MeshStandardMaterial({
      color: isTori ? 0xffffff : 0xf59e0b,
      roughness: 0.45
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

    // ── Official Eelis/GrappleMap 28 Segment Table ──
    // [j1, j2, radius, isSkin]
    const eelisSegments = [
      [0, 2, 0.025, true],   // LeftToe -> LeftHeel
      [0, 4, 0.025, true],   // LeftToe -> LeftAnkle
      [2, 4, 0.025, true],   // LeftHeel -> LeftAnkle
      [4, 6, 0.055, false],  // LeftAnkle -> LeftKnee (Calf)
      [6, 8, 0.085, false],  // LeftKnee -> LeftHip (Thigh)
      [8, 20, 0.100, false], // LeftHip -> Core
      [20, 10, 0.075, false],// Core -> LeftShoulder
      [10, 12, 0.060, false],// LeftShoulder -> LeftElbow
      [12, 14, 0.030, false],// LeftElbow -> LeftWrist
      [14, 16, 0.020, true], // LeftWrist -> LeftHand
      [16, 18, 0.020, true], // LeftHand -> LeftFingers
      [14, 18, 0.020, false],// LeftWrist -> LeftFingers
      [1, 3, 0.025, true],   // RightToe -> RightHeel
      [1, 5, 0.025, true],   // RightToe -> RightAnkle
      [3, 5, 0.025, true],   // RightHeel -> RightAnkle
      [5, 7, 0.055, false],  // RightAnkle -> RightKnee (Calf)
      [7, 9, 0.085, false],  // RightKnee -> RightHip (Thigh)
      [9, 20, 0.100, false], // RightHip -> Core
      [20, 11, 0.075, false],// Core -> RightShoulder
      [11, 13, 0.060, false],// RightShoulder -> RightElbow
      [13, 15, 0.030, false],// RightElbow -> RightWrist
      [15, 17, 0.020, true], // RightWrist -> RightHand
      [17, 19, 0.020, true], // RightHand -> RightFingers
      [15, 19, 0.020, false],// RightWrist -> RightFingers
      [8, 9, 0.100, false],  // LeftHip -> RightHip (Pelvis Line)
      [10, 21, 0.065, false],// LeftShoulder -> Neck
      [11, 21, 0.065, false],// RightShoulder -> Neck
      [21, 22, 0.050, true]  // Neck -> Head
    ];

    this.segments = eelisSegments.map(([j1, j2, r, isSkin]) => {
      const geo = new THREE.CylinderGeometry(r, r, 1, 14, 1);
      const mesh = new THREE.Mesh(geo, isSkin ? this.skinMat : this.giMat);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.group.add(mesh);
      return { mesh, j1, j2 };
    });

    // ── Official Eelis/GrappleMap 23 Joint Spheres ──
    const eelisJoints = [
      [0, 0.025, true],  // 0:LeftToe
      [1, 0.025, true],  // 1:RightToe
      [2, 0.030, true],  // 2:LeftHeel
      [3, 0.030, true],  // 3:RightHeel
      [4, 0.030, true],  // 4:LeftAnkle
      [5, 0.030, true],  // 5:RightAnkle
      [6, 0.050, false], // 6:LeftKnee
      [7, 0.050, false], // 7:RightKnee
      [8, 0.090, false], // 8:LeftHip
      [9, 0.090, false], // 9:RightHip
      [10, 0.080, false],// 10:LeftShoulder
      [11, 0.080, false],// 11:RightShoulder
      [12, 0.045, false],// 12:LeftElbow
      [13, 0.045, false],// 13:RightElbow
      [14, 0.020, true], // 14:LeftWrist
      [15, 0.020, true], // 15:RightWrist
      [16, 0.020, true], // 16:LeftHand
      [17, 0.020, true], // 17:RightHand
      [18, 0.020, true], // 18:LeftFingers
      [19, 0.020, true], // 19:RightFingers
      [20, 0.100, false],// 20:Core
      [21, 0.050, false],// 21:Neck
      [22, 0.110, true]  // 22:Head
    ];

    this.jointSpheres = eelisJoints.map(([jIdx, r, isSkin]) => {
      const sphere = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 14), isSkin ? this.skinMat : this.giMat);
      sphere.castShadow = true;
      this.group.add(sphere);
      return { sphere, jIdx };
    });

    // BJJ Gi Lapel Collar V-Cross
    this.lapelL = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.28, 0.035), this.lapelMat);
    this.lapelR = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.28, 0.035), this.lapelMat);
    this.group.add(this.lapelL);
    this.group.add(this.lapelR);

    // Belt Ring & Rank Sleeve
    this.beltRing = new THREE.Mesh(new THREE.CylinderGeometry(0.092, 0.096, 0.065, 16), this.beltMat);
    this.beltRing.castShadow = true;
    this.group.add(this.beltRing);

    this.beltKnot = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.065, 0.065), this.beltMat);
    this.rankSleeve = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.075, 0.022), this.rankSleeveMat);
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

  animateLerp(lerpFactor = 0.14) {
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

    // 1. Position Eelis 28 Segment Cylinders
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

    // 2. Position Eelis 23 Joint Spheres
    this.jointSpheres.forEach(({ sphere, jIdx }) => {
      sphere.position.copy(P(jIdx));
    });

    // 3. Orient Gi Lapel Collar to Chest Spine Segment
    const corePos = P(20);
    const neckPos = P(21);
    const spine = neckPos.clone().sub(corePos);
    const chestMid = corePos.clone().add(neckPos).multiplyScalar(0.5);

    const lShoulder = P(10);
    const rShoulder = P(11);
    const shoulderLine = rShoulder.clone().sub(lShoulder);
    const chestFwd = shoulderLine.clone().cross(spine).normalize();

    this.lapelL.position.copy(chestMid.clone().add(shoulderLine.clone().multiplyScalar(-0.18)).add(chestFwd.clone().multiplyScalar(0.07)));
    this.lapelR.position.copy(chestMid.clone().add(shoulderLine.clone().multiplyScalar(0.18)).add(chestFwd.clone().multiplyScalar(0.07)));

    this.lapelL.quaternion.setFromUnitVectors(UP, spine.clone().normalize());
    this.lapelR.quaternion.setFromUnitVectors(UP, spine.clone().normalize());

    // 4. Position Belt Ring & Knot on Waist Line
    const lHip = P(8);
    const rHip = P(9);
    const waistPos = corePos.clone().add(lHip.clone().add(rHip).multiplyScalar(0.5)).multiplyScalar(0.5);

    this.beltRing.position.copy(waistPos);
    this.beltRing.quaternion.setFromUnitVectors(UP, spine.clone().normalize());

    const waistFwd = rHip.clone().sub(lHip).cross(spine).normalize();
    this.beltKnot.position.copy(waistPos.clone().add(waistFwd.clone().multiplyScalar(0.09)));
    this.rankSleeve.position.copy(waistPos.clone().add(waistFwd.clone().multiplyScalar(0.10)).sub(new THREE.Vector3(0, 0.04, 0)));
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

    // 3D Humanoid Rigs (Official Eelis/GrappleMap 28-Segment System)
    this.toriRig = null; // Athlete A (Color #D4CBC0 / Royal Blue Gi)
    this.ukeRig = null;  // Athlete B (Color #1E3A6E / Dark Carbon Gi)
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
    this.camera.position.set(2.2, 1.6, 2.8);

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
      this.controls.target.set(0, 0.25, 0);
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
    // Official GrappleMap Athlete Colors: #D4CBC0 (Athlete A) & #1E3A6E (Athlete B)
    this.toriRig = new GrappleHumanoidRig(this.scene, 0xd4cbc0, 0x1d4ed8, true);
    this.ukeRig = new GrappleHumanoidRig(this.scene, 0x1e3a6e, 0x1e293b, false);

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
        this.animateCameraPosition(0, 3.6, 0.1, 0, 0.2, 0);
        break;
      case "side": // Side Profile Angle
        this.animateCameraPosition(2.6, 1.1, 0, 0, 0.25, 0);
        break;
      case "tight": // Close Grip Angle
        this.animateCameraPosition(1.1, 0.8, 1.1, 0, 0.3, 0);
        break;
      case "default":
      default: // 3/4 Isometric Perspective
        this.animateCameraPosition(2.2, 1.6, 2.8, 0, 0.25, 0);
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
    if (this.toriRig) this.toriRig.animateLerp(0.14);
    if (this.ukeRig) this.ukeRig.animateLerp(0.14);

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
