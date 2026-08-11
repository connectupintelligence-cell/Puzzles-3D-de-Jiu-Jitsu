/**
 * BJJ 3D Engine - Motor 3D com Integração GrappleMap (bjjcortex-hub/3d-puzzle)
 * Suporte a 23 articulações anatômicas (Joint Reference), extração de poses GrappleMap e avatares Humanoides.
 */

// ── Joint Index Reference (GrappleMap Standard) ──────────────────────────────
// 0:LeftToe   1:RightToe   2:LeftHeel   3:RightHeel
// 4:LeftAnkle 5:RightAnkle 6:LeftKnee  7:RightKnee
// 8:LeftHip   9:RightHip  10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist
// 16:LeftHand 17:RightHand 18:LeftFingers 19:RightFingers
// 20:Core  21:Neck  22:Head

class GrapplePoseExtractor {
  static extractFromJoints(joints) {
    if (!joints || joints.length < 23) return null;
    const P = (i) => new THREE.Vector3(joints[i][0], joints[i][1], joints[i][2]);
    const mid = (a, b) => a.clone().add(b).multiplyScalar(0.5);

    const lHip = P(8), rHip = P(9);
    const lShoulder = P(10), rShoulder = P(11);
    const core = P(20), neck = P(21);

    const root = mid(lHip, rHip);
    const chest = mid(lShoulder, rShoulder);

    let hipRight = rHip.clone().sub(lHip);
    const spineVec = neck.clone().sub(core);
    let hipFwd = hipRight.clone().cross(spineVec);
    if (hipFwd.lengthSq() < 0.0001) hipFwd.set(0, 0, 1);
    let hipUp = hipFwd.clone().cross(hipRight);
    if (hipUp.lengthSq() < 0.0001) hipUp.set(0, 1, 0);

    hipRight.normalize();
    hipFwd.normalize();
    hipUp.normalize();

    return {
      root, chest, neck: P(21), head: P(22),
      lShoulder, lElbow: P(12), lWrist: P(14),
      rShoulder, rElbow: P(13), rWrist: P(15),
      lHip, lKnee: P(6), lAnkle: P(4),
      rHip, rKnee: P(7), rAnkle: P(5),
      hipRight, hipUp, hipFwd
    };
  }
}

class GrappleHumanoidRig {
  constructor(scene, colorHex, giColorHex, isTori = true) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.scene.add(this.group);

    // Materials
    this.skinMat = new THREE.MeshStandardMaterial({ color: 0xe0a96d, roughness: 0.35, metalness: 0.05 });
    this.giMat = new THREE.MeshStandardMaterial({ color: giColorHex, roughness: 0.55, metalness: 0.05 });
    this.lapelMat = new THREE.MeshStandardMaterial({ color: isTori ? 0xffffff : 0xf59e0b, roughness: 0.4 });
    this.beltMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.5 });
    this.rankMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.3 });

    // Segment Defs: [j1, j2, radius, isSkin]
    const defs = [
      // Torso / Spine
      [20, 10, 0.045, false], [20, 11, 0.045, false],
      [20,  8, 0.052, false], [20,  9, 0.052, false],
      [10, 11, 0.040, false], [ 8,  9, 0.046, false],
      [20, 21, 0.030, false], [21, 22, 0.022, true],
      // Left Leg
      [ 8,  6, 0.042, false], [ 6,  4, 0.032, false], [ 4,  0, 0.016, true],
      // Right Leg
      [ 9,  7, 0.042, false], [ 7,  5, 0.032, false], [ 5,  1, 0.016, true],
      // Left Arm
      [10, 12, 0.032, false], [12, 14, 0.024, false], [14, 16, 0.016, true],
      // Right Arm
      [11, 13, 0.032, false], [13, 15, 0.024, false], [15, 17, 0.016, true]
    ];

    this.segments = defs.map(([j1, j2, r, isSkin]) => {
      const mesh = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 12, 1), isSkin ? this.skinMat : this.giMat);
      mesh.castShadow = true;
      this.group.add(mesh);
      return { mesh, j1, j2 };
    });

    // Anatomical Head
    this.head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 16), this.skinMat);
    this.head.castShadow = true;
    this.group.add(this.head);

    // Gi Lapel Chest V
    this.lapelL = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.28, 0.04), this.lapelMat);
    this.lapelR = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.28, 0.04), this.lapelMat);
    this.group.add(this.lapelL);
    this.group.add(this.lapelR);

    // BJJ Belt Knot & Rank Sleeve
    this.beltKnot = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.07, 0.08), this.beltMat);
    this.rankSleeve = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.06, 0.02), this.rankMat);
    this.group.add(this.beltKnot);
    this.group.add(this.rankSleeve);
  }

  updateJoints(joints) {
    if (!joints || joints.length < 23) return;
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

    // Position Head
    this.head.position.copy(P(22));

    // Position Lapels & Belt on Core
    const corePos = P(20);
    const neckPos = P(21);
    const chestPos = corePos.clone().add(neckPos).multiplyScalar(0.5);

    this.lapelL.position.set(chestPos.x - 0.06, chestPos.y + 0.02, chestPos.z + 0.08);
    this.lapelR.position.set(chestPos.x + 0.06, chestPos.y + 0.02, chestPos.z + 0.08);
    this.beltKnot.position.set(corePos.x, corePos.y - 0.02, corePos.z + 0.1);
    this.rankSleeve.position.set(corePos.x - 0.02, corePos.y - 0.08, corePos.z + 0.11);
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
    this.toriRig = null;
    this.ukeRig = null;
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
    this.camera.position.set(2.6, 2.3, 3.9);

    // 3. Renderer setup
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;

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
      this.controls.minDistance = 1.2;
      this.controls.maxDistance = 8.0;
      this.controls.target.set(0, 0.5, 0);
    }

    // 5. Lighting Studio
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
    const hemiLight = new THREE.HemisphereLight(0xfff8ee, 0x0f172a, 1.1);
    hemiLight.position.set(0, 10, 0);
    this.scene.add(hemiLight);

    const keyLight = new THREE.DirectionalLight(0xfffaed, 1.6);
    keyLight.position.set(4.5, 6.5, 4.5);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.bias = -0.0008;
    this.scene.add(keyLight);

    const cyanRim = new THREE.DirectionalLight(0x38bdf8, 1.4);
    cyanRim.position.set(-4.5, 3.5, -3.5);
    this.scene.add(cyanRim);

    const goldPoint = new THREE.PointLight(0xf59e0b, 1.8, 7);
    goldPoint.position.set(0, 2.8, 0);
    this.scene.add(goldPoint);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
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

    const outerRingGeo = new THREE.RingGeometry(1.5, 1.55, 64);
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
    // GrappleMap Humanoid Rig for Tori (Royal Blue Gi) & Uke (Dark Carbon Gi)
    this.toriRig = new GrappleHumanoidRig(this.scene, 0xd4cbc0, 0x1d4ed8, true);
    this.ukeRig = new GrappleHumanoidRig(this.scene, 0x1e3a6e, 0x1e293b, false);

    // Initial default GrappleMap 23-joint standing/guard poses
    const defaultToriJoints = this.createDefaultJoints(0, 0.4, 0);
    const defaultUkeJoints = this.createDefaultJoints(0, 0.4, 0.3, true);

    this.toriRig.updateJoints(defaultToriJoints);
    this.ukeRig.updateJoints(defaultUkeJoints);
  }

  createDefaultJoints(ox, oy, oz, isOpponent = false) {
    const rotZ = isOpponent ? 3.14 : 0;
    // 23 3D Joint positions array matching GrappleMap reference
    return [
      [ox - 0.12, oy + 0.0, oz + 0.18],  // 0:LeftToe
      [ox + 0.12, oy + 0.0, oz + 0.18],  // 1:RightToe
      [ox - 0.12, oy + 0.0, oz - 0.05],  // 2:LeftHeel
      [ox + 0.12, oy + 0.0, oz - 0.05],  // 3:RightHeel
      [ox - 0.12, oy + 0.05, oz],        // 4:LeftAnkle
      [ox + 0.12, oy + 0.05, oz],        // 5:RightAnkle
      [ox - 0.13, oy + 0.28, oz + 0.02], // 6:LeftKnee
      [ox + 0.13, oy + 0.28, oz + 0.02], // 7:RightKnee
      [ox - 0.12, oy + 0.50, oz],        // 8:LeftHip
      [ox + 0.12, oy + 0.50, oz],        // 9:RightHip
      [ox - 0.24, oy + 0.82, oz],        // 10:LeftShoulder
      [ox + 0.24, oy + 0.82, oz],        // 11:RightShoulder
      [ox - 0.32, oy + 0.65, oz + 0.1],  // 12:LeftElbow
      [ox + 0.32, oy + 0.65, oz + 0.1],  // 13:RightElbow
      [ox - 0.28, oy + 0.52, oz + 0.25], // 14:LeftWrist
      [ox + 0.28, oy + 0.52, oz + 0.25], // 15:RightWrist
      [ox - 0.28, oy + 0.48, oz + 0.28], // 16:LeftHand
      [ox + 0.28, oy + 0.48, oz + 0.28], // 17:RightHand
      [ox - 0.28, oy + 0.45, oz + 0.30], // 18:LeftFingers
      [ox + 0.28, oy + 0.45, oz + 0.30], // 19:RightFingers
      [ox,       oy + 0.50, oz],        // 20:Core
      [ox,       oy + 0.85, oz],        // 21:Neck
      [ox,       oy + 0.98, oz]         // 22:Head
    ];
  }

  setPose(poseData) {
    if (!poseData) return;

    // Check if GrappleMap 23-joint arrays are provided
    if (poseData.toriJoints && this.toriRig) {
      this.toriRig.updateJoints(poseData.toriJoints);
    } else if (poseData.tori && this.toriRig) {
      const pos = poseData.tori.position || [0, 0.4, 0];
      const joints = this.createDefaultJoints(pos[0], pos[1], pos[2], false);
      this.toriRig.updateJoints(joints);
    }

    if (poseData.ukeJoints && this.ukeRig) {
      this.ukeRig.updateJoints(poseData.ukeJoints);
    } else if (poseData.uke && this.ukeRig) {
      const pos = poseData.uke.position || [0, 0.4, 0.3];
      const joints = this.createDefaultJoints(pos[0], pos[1], pos[2], true);
      this.ukeRig.updateJoints(joints);
    }
  }

  updateCameraPreset(presetName) {
    if (!this.camera || !this.controls) return;

    switch (presetName) {
      case "top": // Top-Down View
        this.animateCameraPosition(0, 4.5, 0.1, 0, 0.3, 0);
        break;
      case "side": // Side Profile Angle
        this.animateCameraPosition(3.6, 1.2, 0, 0, 0.4, 0);
        break;
      case "tight": // Close Grip Angle
        this.animateCameraPosition(1.4, 1.2, 1.6, 0, 0.45, 0);
        break;
      case "default":
      default: // 3/4 Isometric Perspective
        this.animateCameraPosition(2.6, 2.3, 3.9, 0, 0.5, 0);
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
window.GrapplePoseExtractor = GrapplePoseExtractor;
window.GrappleHumanoidRig = GrappleHumanoidRig;
