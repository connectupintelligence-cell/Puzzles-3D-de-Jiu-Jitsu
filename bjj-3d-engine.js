/**
 * BJJ 3D Engine - Motor 3D com Three.js (Versão PBR & Anatomia Aprimorada)
 * Renderizador de alta fidelidade visual com materiais PBR, iluminação de estúdio e anatomia realista de Jiu-Jitsu.
 */

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

    // Textures & Shared Materials
    this.canvasGiTexture = null;

    // 3D Objects
    this.matGroup = null;
    this.toriGroup = null; // Lutador Atacante (Kimono Azul Real)
    this.ukeGroup = null;  // Lutador Defensor (Kimono Preto Carbono)

    // Animation & State
    this.autoRotate = false;
    this.animationId = null;
    this.targetToriTransform = { pos: [0, 0, 0], rot: [0, 0, 0] };
    this.targetUkeTransform = { pos: [0, 0, 0], rot: [0, 0, 0] };

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

    // 5. Procedural Canvas Weave Texture for BJJ Gi
    this.canvasGiTexture = this.generateGiWeaveTexture();

    // 6. Lighting Studio
    this.setupLighting();

    // 7. Build Tatame (BJJ Mat)
    this.buildMat();

    // 8. Build 3D Humanoid Fighters
    this.buildFighters();

    // 9. Resize Handling
    window.addEventListener("resize", () => this.onWindowResize());
    if (window.ResizeObserver && this.container) {
      const resizeObserver = new ResizeObserver(() => this.onWindowResize());
      resizeObserver.observe(this.container);
    }
    setTimeout(() => this.onWindowResize(), 50);

    // 10. Start Render Loop
    this.animate();
  }

  // Generates a procedural 2D weave texture canvas for realistic BJJ Gi fabric
  generateGiWeaveTexture() {
    const canvas = document.createElement("canvas");
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "#888888";
    ctx.fillRect(0, 0, 128, 128);

    // Draw weave grid pattern
    ctx.fillStyle = "#bbbbbb";
    for (let x = 0; x < 128; x += 4) {
      for (let y = 0; y < 128; y += 4) {
        if ((x + y) % 8 === 0) {
          ctx.fillRect(x, y, 3, 3);
        }
      }
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(6, 6);
    return texture;
  }

  setupLighting() {
    // Hemisphere Light (Sky Warmth + Dark Slate Ground)
    const hemiLight = new THREE.HemisphereLight(0xfff8ee, 0x0f172a, 1.1);
    hemiLight.position.set(0, 10, 0);
    this.scene.add(hemiLight);

    // Studio Key Light (Main Soft Sun Spotlight)
    const keyLight = new THREE.DirectionalLight(0xfffaed, 1.6);
    keyLight.position.set(4.5, 6.5, 4.5);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.bias = -0.0008;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 15;
    this.scene.add(keyLight);

    // Cyan Rim Light (Combat Sports Accent Highlight)
    const cyanRim = new THREE.DirectionalLight(0x38bdf8, 1.4);
    cyanRim.position.set(-4.5, 3.5, -3.5);
    this.scene.add(cyanRim);

    // Gold Fill Point Light (Tatame Center Warmth)
    const goldPoint = new THREE.PointLight(0xf59e0b, 1.8, 7);
    goldPoint.position.set(0, 2.8, 0);
    this.scene.add(goldPoint);

    // Soft Ambient Fill Light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambientLight);
  }

  buildMat() {
    this.matGroup = new THREE.Group();

    // Main BJJ Mat floor (Tatame area)
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

    // Outer Safety Ring (Cyan Neon Line)
    const outerRingGeo = new THREE.RingGeometry(1.5, 1.55, 64);
    const outerRingMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.85
    });
    const outerRingMesh = new THREE.Mesh(outerRingGeo, outerRingMat);
    outerRingMesh.rotation.x = Math.PI / 2;
    outerRingMesh.position.y = 0.002;
    this.matGroup.add(outerRingMesh);

    // Center Tactical Ring (Gold Zone)
    const centerRingGeo = new THREE.RingGeometry(0.55, 0.58, 48);
    const centerRingMat = new THREE.MeshBasicMaterial({
      color: 0xf59e0b,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.75
    });
    const centerRingMesh = new THREE.Mesh(centerRingGeo, centerRingMat);
    centerRingMesh.rotation.x = Math.PI / 2;
    centerRingMesh.position.y = 0.003;
    this.matGroup.add(centerRingMesh);

    // Tatame Grid Helper
    const gridHelper = new THREE.GridHelper(4.4, 16, 0x38bdf8, 0x1f293d);
    gridHelper.position.y = 0.004;
    this.matGroup.add(gridHelper);

    this.scene.add(this.matGroup);
  }

  buildFighters() {
    // Tori: Royal Blue Gi, White Lapels, Black Belt with Red Sleeve
    this.toriGroup = this.createAnatomicalFighter({
      giColor: 0x1d4ed8,
      lapelColor: 0xffffff,
      beltColor: 0x111827,
      rankSleeveColor: 0xd97706, // Red/Gold Rank Sleeve
      skinColor: 0xe0a96d
    });
    this.toriGroup.position.set(0, 0.4, 0);
    this.scene.add(this.toriGroup);

    // Uke: Dark Carbon Gi, Amber Accent, Amber Belt
    this.ukeGroup = this.createAnatomicalFighter({
      giColor: 0x1e293b,
      lapelColor: 0xf59e0b,
      beltColor: 0x111827,
      rankSleeveColor: 0xd97706,
      skinColor: 0xd49b6a
    });
    this.ukeGroup.position.set(0, 0.4, 0.3);
    this.scene.add(this.ukeGroup);
  }

  createAnatomicalFighter(config) {
    const fighterGroup = new THREE.Group();

    // PBR Materials
    const skinMaterial = new THREE.MeshStandardMaterial({
      color: config.skinColor,
      roughness: 0.35,
      metalness: 0.05
    });

    const giMaterial = new THREE.MeshStandardMaterial({
      color: config.giColor,
      roughness: 0.6,
      metalness: 0.05,
      bumpMap: this.canvasGiTexture,
      bumpScale: 0.008
    });

    const lapelMaterial = new THREE.MeshStandardMaterial({
      color: config.lapelColor,
      roughness: 0.4,
      metalness: 0.05
    });

    const beltMaterial = new THREE.MeshStandardMaterial({
      color: config.beltColor,
      roughness: 0.5,
      metalness: 0.1
    });

    const rankSleeveMaterial = new THREE.MeshStandardMaterial({
      color: config.rankSleeveColor,
      roughness: 0.3,
      metalness: 0.1
    });

    // 1. Torso / Gi Jacket (Anatomical V-Taper Shape)
    const chestGroup = new THREE.Group();
    const chestMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.18, 0.46, 16), giMaterial);
    chestMesh.position.y = 0.46;
    chestMesh.scale.set(1.1, 1.0, 0.7);
    chestMesh.castShadow = true;
    chestMesh.receiveShadow = true;
    chestGroup.add(chestMesh);

    // Gi Lapels (V-Cross Lapel Collar)
    const lapelGeo = new THREE.BoxGeometry(0.06, 0.42, 0.05);
    const lapelL = new THREE.Mesh(lapelGeo, lapelMaterial);
    lapelL.position.set(-0.08, 0.48, 0.11);
    lapelL.rotation.z = -0.32;
    chestGroup.add(lapelL);

    const lapelR = new THREE.Mesh(lapelGeo, lapelMaterial);
    lapelR.position.set(0.08, 0.48, 0.11);
    lapelR.rotation.z = 0.32;
    chestGroup.add(lapelR);

    // BJJ Belt (Waistband + Knot + Rank Sleeve)
    const beltRing = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.22, 0.07, 16), beltMaterial);
    beltRing.position.y = 0.27;
    beltRing.scale.set(1.05, 1.0, 0.75);
    beltRing.castShadow = true;
    chestGroup.add(beltRing);

    const beltKnot = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.08, 0.09), beltMaterial);
    beltKnot.position.set(0, 0.27, 0.15);
    chestGroup.add(beltKnot);

    // Belt Hanging Tails
    const beltTail1 = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.22, 0.02), beltMaterial);
    beltTail1.position.set(-0.03, 0.15, 0.16);
    beltTail1.rotation.z = 0.15;
    chestGroup.add(beltTail1);

    // BJJ Rank Sleeve (Ponteira de Faixa de Jiu-Jitsu)
    const rankSleeve = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.07, 0.022), rankSleeveMaterial);
    rankSleeve.position.set(-0.03, 0.08, 0.165);
    rankSleeve.rotation.z = 0.15;
    chestGroup.add(rankSleeve);

    fighterGroup.add(chestGroup);

    // 2. Head & Neck
    const neckMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.1, 12), skinMaterial);
    neckMesh.position.y = 0.69;
    fighterGroup.add(neckMesh);

    const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.125, 20, 20), skinMaterial);
    headMesh.position.y = 0.78;
    headMesh.scale.set(0.95, 1.05, 1.0);
    headMesh.castShadow = true;
    fighterGroup.add(headMesh);

    // Ears
    const earL = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 8), skinMaterial);
    earL.position.set(-0.12, 0.78, 0);
    earL.scale.set(0.4, 0.8, 0.6);
    fighterGroup.add(earL);

    const earR = earL.clone();
    earR.position.x = 0.12;
    fighterGroup.add(earR);

    // 3. Arms (Shoulder Deltoids, Biceps, Forearm & Wrist Tape)
    const createArm = (isLeft) => {
      const armGroup = new THREE.Group();
      const side = isLeft ? -1 : 1;
      armGroup.position.set(side * 0.26, 0.6, 0);

      // Deltoid Shoulder Cap
      const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 14), giMaterial);
      shoulder.castShadow = true;
      armGroup.add(shoulder);

      // Upper Arm (Biceps/Gi Sleeve)
      const bicep = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.065, 0.26, 14), giMaterial);
      bicep.position.set(side * 0.06, -0.14, 0);
      bicep.rotation.z = side * 0.35;
      bicep.castShadow = true;
      armGroup.add(bicep);

      // Elbow Joint
      const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), skinMaterial);
      elbow.position.set(side * 0.11, -0.27, 0.02);
      armGroup.add(elbow);

      // Forearm
      const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.045, 0.24, 14), skinMaterial);
      forearm.position.set(side * 0.16, -0.38, 0.06);
      forearm.rotation.x = -0.4;
      forearm.castShadow = true;
      armGroup.add(forearm);

      // Wrist Tape / Hand
      const hand = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.07, 0.03), skinMaterial);
      hand.position.set(side * 0.2, -0.49, 0.1);
      hand.castShadow = true;
      armGroup.add(hand);

      return armGroup;
    };

    fighterGroup.add(createArm(true));  // Left Arm
    fighterGroup.add(createArm(false)); // Right Arm

    // 4. Legs (Thighs, Knee Joints, Calves & Feet)
    const createLeg = (isLeft) => {
      const legGroup = new THREE.Group();
      const side = isLeft ? -1 : 1;
      legGroup.position.set(side * 0.13, 0.25, 0);

      // Thigh (Gi Pants)
      const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.08, 0.32, 14), giMaterial);
      thigh.position.set(0, -0.16, 0);
      thigh.castShadow = true;
      legGroup.add(thigh);

      // Knee Joint
      const knee = new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 12), giMaterial);
      knee.position.set(0, -0.32, 0.02);
      legGroup.add(knee);

      // Shin / Calf
      const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.055, 0.3, 14), giMaterial);
      shin.position.set(0, -0.46, 0.04);
      shin.rotation.x = 0.18;
      shin.castShadow = true;
      legGroup.add(shin);

      // Bare Foot
      const foot = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.04, 0.14), skinMaterial);
      foot.position.set(0, -0.62, 0.08);
      foot.castShadow = true;
      legGroup.add(foot);

      return legGroup;
    };

    fighterGroup.add(createLeg(true));  // Left Leg
    fighterGroup.add(createLeg(false)); // Right Leg

    return fighterGroup;
  }

  setPose(poseData) {
    if (!poseData) return;

    if (poseData.tori) {
      this.targetToriTransform.pos = poseData.tori.position || [0, 0.4, 0];
      this.targetToriTransform.rot = poseData.tori.rotation || [0, 0, 0];
    }

    if (poseData.uke) {
      this.targetUkeTransform.pos = poseData.uke.position || [0, 0.4, 0.3];
      this.targetUkeTransform.rot = poseData.uke.rotation || [0, 3.14, 0];
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

    // Lerp Tori position & rotation
    if (this.toriGroup && this.targetToriTransform) {
      const tp = this.targetToriTransform.pos;
      const tr = this.targetToriTransform.rot;

      this.toriGroup.position.x += (tp[0] - this.toriGroup.position.x) * 0.1;
      this.toriGroup.position.y += (tp[1] - this.toriGroup.position.y) * 0.1;
      this.toriGroup.position.z += (tp[2] - this.toriGroup.position.z) * 0.1;

      this.toriGroup.rotation.x += (tr[0] - this.toriGroup.rotation.x) * 0.1;
      this.toriGroup.rotation.y += (tr[1] - this.toriGroup.rotation.y) * 0.1;
      this.toriGroup.rotation.z += (tr[2] - this.toriGroup.rotation.z) * 0.1;
    }

    // Lerp Uke position & rotation
    if (this.ukeGroup && this.targetUkeTransform) {
      const up = this.targetUkeTransform.pos;
      const ur = this.targetUkeTransform.rot;

      this.ukeGroup.position.x += (up[0] - this.ukeGroup.position.x) * 0.1;
      this.ukeGroup.position.y += (up[1] - this.ukeGroup.position.y) * 0.1;
      this.ukeGroup.position.z += (up[2] - this.ukeGroup.position.z) * 0.1;

      this.ukeGroup.rotation.x += (ur[0] - this.ukeGroup.rotation.x) * 0.1;
      this.ukeGroup.rotation.y += (ur[1] - this.ukeGroup.rotation.y) * 0.1;
      this.ukeGroup.rotation.z += (ur[2] - this.ukeGroup.rotation.z) * 0.1;
    }

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
