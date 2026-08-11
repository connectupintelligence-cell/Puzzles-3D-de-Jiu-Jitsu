/**
 * BJJ 3D Engine - Motor 3D com Integração GrappleMap (bjjcortex-hub/3d-puzzle)
 * Renderizador de bonecos 3D anatômicos de Jiu-Jitsu com articulações GrappleMap.
 */

// ── Joint Index Reference (GrappleMap Standard) ──────────────────────────────
// 0:LeftToe   1:RightToe   2:LeftHeel   3:RightHeel
// 4:LeftAnkle 5:RightAnkle 6:LeftKnee  7:RightKnee
// 8:LeftHip   9:RightHip  10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist
// 16:LeftHand 17:RightHand 18:LeftFingers 19:RightFingers
// 20:Core  21:Neck  22:Head

class GrappleHumanoidRig {
  constructor(scene, skinColorHex, giColorHex, isTori = true) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.scene.add(this.group);

    // High quality materials
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
      color: 0xd97706, // Red/Gold Rank Sleeve
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

    // Current & Target Joints for Lerp Animation
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

    // Forward direction from hip line
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
    this.camera.position.set(2.4, 2.0, 3.4);

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
      this.controls.minDistance = 1.0;
      this.controls.maxDistance = 7.0;
      this.controls.target.set(0, 0.45, 0);
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

    // Set initial clean grappling engagement pose where both feet rest properly on tatami floor (y=0)
    const toriJoints = this.generateStandingJoints(-0.35, 0, false);
    const ukeJoints = this.generateStandingJoints(0.35, 3.14, true);

    this.toriRig.updateJoints(toriJoints, true);
    this.ukeRig.updateJoints(ukeJoints, true);
  }

  generateStandingJoints(offsetX, angleRad, isOpponent = false) {
    const cos = Math.cos(angleRad);
    const sin = Math.sin(angleRad);

    const transformPoint = (x, y, z) => {
      const rx = x * cos - z * sin;
      const rz = x * sin + z * cos;
      return [rx + offsetX, y, rz];
    };

    // Realistic BJJ 23-joint anatomical posture where feet touch y=0
    return [
      transformPoint(-0.14, 0.02, 0.16),  // 0:LeftToe
      transformPoint(0.14, 0.02, 0.16),   // 1:RightToe
      transformPoint(-0.14, 0.02, -0.06), // 2:LeftHeel
      transformPoint(0.14, 0.02, -0.06),  // 3:RightHeel
      transformPoint(-0.14, 0.06, 0.0),   // 4:LeftAnkle
      transformPoint(0.14, 0.06, 0.0),    // 5:RightAnkle
      transformPoint(-0.15, 0.42, 0.08),  // 6:LeftKnee (BJJ combat bend)
      transformPoint(0.15, 0.42, 0.08),   // 7:RightKnee
      transformPoint(-0.14, 0.78, 0.0),   // 8:LeftHip
      transformPoint(0.14, 0.78, 0.0),    // 9:RightHip
      transformPoint(-0.22, 1.28, -0.02), // 10:LeftShoulder
      transformPoint(0.22, 1.28, -0.02),  // 11:RightShoulder
      transformPoint(-0.26, 1.05, 0.18),  // 12:LeftElbow (Ready grip posture)
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

  setPose(poseData) {
    if (!poseData) return;

    if (poseData.toriJoints && this.toriRig) {
      this.toriRig.updateJoints(poseData.toriJoints);
    } else if (poseData.tori && this.toriRig) {
      const pos = poseData.tori.position || [-0.35, 0, 0];
      const joints = this.generateStandingJoints(pos[0], pos[2] || 0, false);
      this.toriRig.updateJoints(joints);
    }

    if (poseData.ukeJoints && this.ukeRig) {
      this.ukeRig.updateJoints(poseData.ukeJoints);
    } else if (poseData.uke && this.ukeRig) {
      const pos = poseData.uke.position || [0.35, 0, 0];
      const joints = this.generateStandingJoints(pos[0], pos[2] || 3.14, true);
      this.ukeRig.updateJoints(joints);
    }
  }

  updateCameraPreset(presetName) {
    if (!this.camera || !this.controls) return;

    switch (presetName) {
      case "top": // Top-Down View
        this.animateCameraPosition(0, 4.2, 0.1, 0, 0.4, 0);
        break;
      case "side": // Side Profile Angle
        this.animateCameraPosition(3.2, 1.3, 0, 0, 0.45, 0);
        break;
      case "tight": // Close Grip Angle
        this.animateCameraPosition(1.2, 1.1, 1.4, 0, 0.5, 0);
        break;
      case "default":
      default: // 3/4 Isometric Perspective
        this.animateCameraPosition(2.4, 2.0, 3.4, 0, 0.45, 0);
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
