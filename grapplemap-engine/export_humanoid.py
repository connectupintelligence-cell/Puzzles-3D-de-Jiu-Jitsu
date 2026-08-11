"""
GrappleMap → Humanoid 3D Viewer
Marco 1: carrega avatar GLB rigado, valida SkinnedMesh+Skeleton, exibe SkeletonHelper.

Arquitetura (módulos JS inline — projeto é single-file HTML):
  grapplePoseExtractor  → class GrapplePoseExtractor
  poseDebugHelper       → class DebugSourceRig + class PoseDebugHelper
  humanoidLoader        → class HumanoidLoader

Marco 2+: HumanoidBoneMap, RestPoseCapture, HumanoidRetargeter, LimbSolver
Marco 5+: SkeletonUtils.clone() para segundo atleta
Marco 6+: ContactSolver
"""

import json
import requests
from export_viewer import parse_and_decode

URL    = "https://raw.githubusercontent.com/Eelis/GrappleMap/master/GrappleMap.txt"
OUTPUT = "GrappleMap_humanoid.html"

# Plain r-string — chaves JS são literais; __DATA_JSON__ substituído em generate_html().
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>GrappleMap 3D — Humanoid</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<!-- Three.js r127 — UMD global builds (funcionam em file:// sem servidor) -->
<script src="https://cdn.jsdelivr.net/npm/three@0.127.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.127.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.127.0/examples/js/loaders/GLTFLoader.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{display:flex;flex-direction:column;height:100vh;background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;overflow:hidden}
#app{display:flex;flex:1;overflow:hidden}
#sidebar{width:280px;flex-shrink:0;display:flex;flex-direction:column;border-right:1px solid #21262d;background:#0d1117}
#sidebar-top{padding:10px 10px 0}
h1{font-size:13px;font-weight:700;color:#58a6ff;margin-bottom:8px;letter-spacing:.5px}
#search{width:100%;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:6px 8px;color:#e6edf3;font-size:12px;outline:none}
#search:focus{border-color:#58a6ff}
#cat-filter{width:100%;margin-top:6px;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:5px 8px;color:#e6edf3;font-size:12px;outline:none;cursor:pointer}
#count{font-size:10px;color:#6e7681;margin-top:5px;text-align:right}
#list{flex:1;overflow-y:auto;padding:4px 0}
#list::-webkit-scrollbar{width:4px}
#list::-webkit-scrollbar-track{background:#0d1117}
#list::-webkit-scrollbar-thumb{background:#30363d;border-radius:2px}
.li{padding:6px 12px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:6px;border-left:3px solid transparent;color:#8b949e;transition:all .1s}
.li:hover{background:#161b22;color:#e6edf3}
.li.active{background:#161b22;border-left-color:#58a6ff;color:#e6edf3}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
#info{padding:10px 12px;border-top:1px solid #21262d;background:#0d1117;font-size:11px;min-height:90px}
#info-name{font-weight:700;color:#e6edf3;margin-bottom:4px;line-height:1.4;font-size:12px}
#info-cat{font-size:10px;font-weight:600;padding:1px 6px;border-radius:10px;display:inline-block;margin-bottom:5px}
#info-tags{color:#6e7681;font-size:10px;line-height:1.5;max-height:48px;overflow:hidden}
#canvas-wrap{flex:1;position:relative}
canvas{display:block;width:100%!important;height:100%!important}
/* bottom bar */
#bar{height:46px;display:flex;align-items:center;gap:8px;padding:0 12px;border-top:1px solid #21262d;background:#0d1117;flex-shrink:0;flex-wrap:nowrap;overflow:hidden}
.btn{background:#21262d;border:1px solid #30363d;color:#e6edf3;padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px;transition:background .1s;white-space:nowrap}
.btn:hover{background:#30363d}
.btn:disabled{opacity:.3;cursor:default}
#play-btn{min-width:60px}
#frame-label{font-size:11px;color:#6e7681;min-width:80px;text-align:center}
#speed-wrap{display:flex;align-items:center;gap:4px;font-size:11px;color:#6e7681}
input[type=range]{accent-color:#58a6ff;width:70px}
#debug-sep{width:1px;height:20px;background:#21262d;flex-shrink:0;margin:0 2px}
.dbg-lbl{font-size:10px;color:#6e7681;display:flex;align-items:center;gap:3px;cursor:pointer;white-space:nowrap}
.dbg-lbl input{accent-color:#58a6ff}
#avatar-status{font-size:10px;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0}
#legend{margin-left:auto;display:flex;gap:10px;font-size:11px;align-items:center;flex-shrink:0}
.leg-dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:3px}
#pos-label{font-size:11px;color:#6e7681;flex-shrink:0}
/* loader */
#loader{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0d1117;z-index:10;gap:8px;font-size:14px;color:#58a6ff}
#loader-sub{font-size:11px;color:#6e7681}
/* sidebar tabs */
#sidebar-tabs{display:flex;flex-shrink:0;border-bottom:1px solid #21262d}
.stab{flex:1;background:none;border:none;border-bottom:2px solid transparent;color:#6e7681;font-size:11px;font-weight:600;padding:8px 4px;cursor:pointer;letter-spacing:.3px}
.stab.active{color:#58a6ff;border-bottom-color:#58a6ff}
#exp-panel{display:flex;flex-direction:column;flex:1;overflow:hidden}
/* compositor */
#cmp-panel{display:none;flex-direction:column;flex:1;overflow:hidden}
#cmp-panel.on{display:flex}
#cmp-add{padding:8px 10px;border-bottom:1px solid #21262d;flex-shrink:0}
#cmp-q{width:100%;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:5px 8px;color:#e6edf3;font-size:11px;outline:none}
#cmp-q:focus{border-color:#58a6ff}
#cmp-res{margin-top:4px;background:#161b22;border:1px solid #30363d;border-radius:6px;display:none;max-height:130px;overflow-y:auto}
#cmp-res.on{display:block}
.cr{padding:5px 10px;font-size:11px;color:#8b949e;cursor:pointer;display:flex;align-items:center;gap:6px}
.cr:hover{background:#21262d;color:#e6edf3}
.cr-add{margin-left:auto;color:#58a6ff;font-size:10px;white-space:nowrap}
#cmp-moves{flex-shrink:0;max-height:180px;overflow-y:auto;border-bottom:1px solid #21262d}
#cmp-moves::-webkit-scrollbar{width:4px}
#cmp-moves::-webkit-scrollbar-thumb{background:#30363d;border-radius:2px}
.mv-hdr{padding:4px 10px;font-size:10px;color:#6e7681;background:#0d1117;position:sticky;top:0}
.mv{padding:4px 10px;font-size:11px;color:#8b949e;cursor:pointer;display:flex;align-items:center;gap:6px;border-left:3px solid transparent}
.mv:hover{background:#161b22;color:#e6edf3;border-left-color:#d97706}
.mv-to{color:#6e7681;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100px}
#seq-hdr{padding:5px 12px;font-size:10px;color:#6e7681;flex-shrink:0;display:flex;align-items:center;justify-content:space-between}
#seq-list{flex:1;overflow-y:auto;padding:4px 0}
#seq-list::-webkit-scrollbar{width:4px}
#seq-list::-webkit-scrollbar-thumb{background:#30363d;border-radius:2px}
.sq{display:flex;align-items:center;gap:5px;padding:5px 10px;font-size:11px;cursor:pointer;color:#8b949e;border-left:3px solid transparent;transition:all .1s}
.sq:hover{background:#161b22;color:#e6edf3}
.sq.sq-cur{background:#161b22;border-left-color:#58a6ff;color:#e6edf3}
.sq-icon{font-size:9px;flex-shrink:0;width:12px;text-align:center}
.sq-nm{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sq-sub{font-size:10px;color:#6e7681;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sq-rm{background:none;border:none;color:#6e7681;cursor:pointer;font-size:13px;padding:0 2px;line-height:1}
.sq-rm:hover{color:#ef4444}
#seq-ctrl{padding:8px 10px;border-top:1px solid #21262d;display:flex;gap:6px;align-items:center;flex-shrink:0;flex-wrap:wrap}
#seq-ctrl .btn{font-size:11px;padding:3px 8px;min-width:auto}
.seq-lbl{font-size:10px;color:#6e7681;display:flex;align-items:center;gap:3px}
#seq-dwell{width:50px;accent-color:#58a6ff}
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <div id="sidebar-top">
      <h1>⛩ GrappleMap · Humanoid</h1>
    </div>
    <div id="sidebar-tabs">
      <button class="stab active" id="tab-exp">Explorar</button>
      <button class="stab" id="tab-cmp">Compositor</button>
    </div>
    <div id="exp-panel">
      <div style="padding:8px 10px 0">
        <input id="search" placeholder="Buscar posição…" autocomplete="off">
        <select id="cat-filter"><option value="">Todas as categorias</option></select>
        <div id="count"></div>
      </div>
      <div id="list"></div>
      <div id="info">
        <div id="info-name">—</div>
        <span id="info-cat"></span>
        <div id="info-tags"></div>
      </div>
    </div>
    <div id="cmp-panel">
      <div id="cmp-add">
        <input id="cmp-q" placeholder="Buscar posição para iniciar…" autocomplete="off">
        <div id="cmp-res"></div>
      </div>
      <div id="cmp-moves"></div>
      <div id="seq-hdr">
        <span>Sequência · <b id="seq-cnt">0</b> itens</span>
        <label class="seq-lbl"><input type="checkbox" id="seq-loop"> Loop</label>
      </div>
      <div id="seq-list"></div>
      <div id="seq-ctrl">
        <button class="btn" id="seq-play-btn">▶ Play</button>
        <button class="btn" id="seq-clear-btn">✕ Limpar</button>
        <div class="seq-lbl" style="margin-left:auto">
          Pausa <input type="range" id="seq-dwell" min="0.3" max="4" step="0.1" value="1">
          <span id="seq-dwell-val">1s</span>
        </div>
      </div>
    </div>
  </div>
  <div id="canvas-wrap">
    <div id="loader">
      <span>Carregando dados GrappleMap…</span>
      <span id="loader-sub"></span>
    </div>
    <canvas id="c"></canvas>
  </div>
</div>

<!-- bottom bar -->
<div id="bar">
  <button class="btn" id="prev-btn">◀</button>
  <button class="btn" id="play-btn">▶ Play</button>
  <button class="btn" id="next-btn">▶</button>
  <span id="frame-label">—</span>
  <div id="speed-wrap">
    <span>Vel.</span>
    <input type="range" id="speed" min="0.1" max="3" step="0.1" value="1">
    <span id="speed-val">1×</span>
  </div>

  <div id="debug-sep"></div>

  <!-- Debug toggles -->
  <label class="dbg-lbl" title="Bonecos GrappleMap (source rig)">
    <input type="checkbox" id="dbg-source" checked> Boneco
  </label>
  <label class="dbg-lbl" title="SkeletonHelper do avatar GLB">
    <input type="checkbox" id="dbg-skeleton" checked> Esqueleto
  </label>
  <label class="dbg-lbl" title="Avatar GLB">
    <input type="checkbox" id="dbg-avatar" checked> Avatar
  </label>

  <!-- Avatar load -->
  <span id="avatar-status" style="color:#6e7681">sem GLB</span>
  <button class="btn" id="load-glb-btn" title="Carregar modelo .glb / .gltf do disco">📂 GLB</button>
  <input type="file" id="glb-file" accept=".glb,.gltf" style="display:none">

  <span id="pos-label"></span>
  <div id="legend">
    <span><span class="leg-dot" style="background:#D4CBC0"></span>A</span>
    <span><span class="leg-dot" style="background:#1E3A6E"></span>B</span>
  </div>
</div>

<script>
// THREE, THREE.OrbitControls, THREE.GLTFLoader disponíveis como globals (r127 UMD)

// ── Data (GrappleMap) ─────────────────────────────────────────────────────────
const DATA      = __DATA_JSON__;
const ENTRIES   = DATA.entries;
const N_POS     = DATA.nPos;
const GRAPH_OUT = DATA.graphOut;
const ALL       = ENTRIES;

// ── Joint index reference ─────────────────────────────────────────────────────
// 0:LeftToe   1:RightToe   2:LeftHeel   3:RightHeel
// 4:LeftAnkle 5:RightAnkle 6:LeftKnee  7:RightKnee
// 8:LeftHip   9:RightHip  10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist
// 16:LeftHand 17:RightHand 18:LeftFingers 19:RightFingers
// 20:Core  21:Neck  22:Head
// Coordinate system: Y-up, Z-toward-camera, X-right. Units: meters.

const CAT_COLORS = {
  "Finalização":"#C0392B","Queda":"#8E44AD","Passagem":"#2980B9",
  "Raspagem":"#27AE60","Escape":"#F39C12","Em Pé":"#16A085",
  "Guarda":"#2471A3","Posição Dominante":"#922B21","Outro":"#717D7E",
};

// ── Scene ─────────────────────────────────────────────────────────────────────
const canvas   = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(devicePixelRatio);
renderer.outputEncoding = THREE.sRGBEncoding;  // r127 API (r152+ usa outputColorSpace)
renderer.shadowMap.enabled = true;
renderer.shadowMap.type    = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.Fog(0x0d1117, 8, 18);

const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 30);
camera.position.set(0, 1.6, 3.8);

const controls = new THREE.OrbitControls(camera, canvas);
controls.target.set(0, 0.8, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance   = 0.5;
controls.maxDistance   = 10;
controls.update();

// Lighting
scene.add(new THREE.AmbientLight(0x8898bb, 1.2));
const key = new THREE.DirectionalLight(0xfff5e0, 2.2);
key.position.set(3, 7, 4);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.near   = 0.1; key.shadow.camera.far    = 20;
key.shadow.camera.top    = 4;   key.shadow.camera.bottom = -1;
key.shadow.camera.left   = -4;  key.shadow.camera.right  = 4;
scene.add(key);
const fill = new THREE.DirectionalLight(0x5070c0, 0.8);
fill.position.set(-4, 3, -3);
scene.add(fill);
const rim = new THREE.DirectionalLight(0xffffff, 0.5);
rim.position.set(0, -2, -5);
scene.add(rim);

// Tatami mat
(function buildMat() {
  const cv = document.createElement('canvas');
  cv.width = cv.height = 256;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#1a4a28'; ctx.fillRect(0, 0, 256, 256);
  ctx.strokeStyle = '#226035'; ctx.lineWidth = 1;
  for (let x = 0; x <= 256; x += 32) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,256); ctx.stroke(); }
  for (let y = 0; y <= 256; y += 32) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(256,y); ctx.stroke(); }
  const tex = new THREE.CanvasTexture(cv);
  tex.repeat.set(3, 3); tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(6, 6), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.9 }));
  mesh.rotation.x = -Math.PI / 2; mesh.receiveShadow = true;
  scene.add(mesh);
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.45, 0.50, 32), new THREE.MeshBasicMaterial({ color: 0x2d7a44, side: THREE.DoubleSide }));
  ring.rotation.x = -Math.PI / 2; ring.position.y = 0.001;
  scene.add(ring);
})();

// ═══════════════════════════════════════════════════════════════════════════════
//  grapplePoseExtractor  (src/pose/grapplePoseExtractor.ts)
// ───────────────────────────────────────────────────────────────────────────────
//  GrapplePose type:
//  {
//    root: Vector3, chest: Vector3, neck: Vector3, head: Vector3,
//    lShoulder, lElbow, lWrist, rShoulder, rElbow, rWrist,
//    lHip, lKnee, lAnkle, rHip, rKnee, rAnkle: Vector3,
//    hipRight, hipUp, hipFwd: Vector3   ← ortogonalizado (body frame)
//  }
// ═══════════════════════════════════════════════════════════════════════════════
class GrapplePoseExtractor {
  static extract(joints) {
    const P   = (i) => new THREE.Vector3(joints[i][0], joints[i][1], joints[i][2]);
    const mid = (a, b) => a.clone().add(b).multiplyScalar(0.5);

    const lHip = P(8), rHip = P(9);
    const lShoulder = P(10), rShoulder = P(11);
    const core = P(20), neck = P(21);

    const root  = mid(lHip, rHip);
    const chest = mid(lShoulder, rShoulder);

    // Body frame — Gram-Schmidt sobre os eixos do quadril
    // right: de quadril esquerdo para direito
    // forward: cross(right, coluna) — aponta para frente do atleta
    // up: cross(forward, right) — não depende de quaternion externo
    let hipRight = rHip.clone().sub(lHip);
    const spineVec = neck.clone().sub(core);
    let hipFwd = hipRight.clone().cross(spineVec);
    if (hipFwd.lengthSq() < 0.0001) hipFwd.set(0, 0, 1);
    let hipUp  = hipFwd.clone().cross(hipRight);
    if (hipUp.lengthSq() < 0.0001) hipUp.set(0, 1, 0);
    hipRight.normalize(); hipFwd.normalize(); hipUp.normalize();

    return {
      root, chest,
      neck: P(21), head: P(22),
      lShoulder, lElbow: P(12), lWrist: P(14),
      rShoulder, rElbow: P(13), rWrist: P(15),
      lHip, lKnee: P(6), lAnkle: P(4),
      rHip, rKnee: P(7), rAnkle: P(5),
      hipRight, hipUp, hipFwd,
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  debug/poseDebugHelper — DebugSourceRig
//  Visualização do source rig GrappleMap via cilindros.
//  Permanece disponível como referência de pose (invisível no modo final).
// ═══════════════════════════════════════════════════════════════════════════════
class DebugSourceRig {
  constructor(color) {
    this.group = new THREE.Group();
    scene.add(this.group);

    const hex  = parseInt(color.replace('#', ''), 16);
    const matA = new THREE.MeshStandardMaterial({ color: hex,      roughness: 0.88 });
    const matS = new THREE.MeshStandardMaterial({ color: 0xC68642, roughness: 0.50 });

    // [j1, j2, radius, useSkin]
    const defs = [
      // Torso
      [20, 10, 0.040, false], [20, 11, 0.040, false],
      [20,  8, 0.048, false], [20,  9, 0.048, false],
      [10, 11, 0.036, false], [ 8,  9, 0.042, false],
      // Spine / neck
      [20, 21, 0.024, false], [21, 22, 0.018, true],
      // Left leg
      [ 8,  6, 0.038, false], [ 6,  4, 0.028, false], [ 4,  0, 0.014, true],
      // Right leg
      [ 9,  7, 0.038, false], [ 7,  5, 0.028, false], [ 5,  1, 0.014, true],
      // Left arm
      [10, 12, 0.028, false], [12, 14, 0.020, false], [14, 16, 0.013, true],
      // Right arm
      [11, 13, 0.028, false], [13, 15, 0.020, false], [15, 17, 0.013, true],
    ];

    this._segs = defs.map(([j1, j2, r, skin]) => {
      const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 10, 1), skin ? matS : matA);
      m.castShadow = true;
      this.group.add(m);
      return { m, j1, j2 };
    });

    this._head = new THREE.Mesh(new THREE.SphereGeometry(0.10, 12, 8), matS);
    this._head.castShadow = true;
    this.group.add(this._head);
  }

  update(joints) {
    const P  = (i) => new THREE.Vector3(joints[i][0], joints[i][1], joints[i][2]);
    const UP = new THREE.Vector3(0, 1, 0);
    const D  = new THREE.Vector3();

    this._segs.forEach(({ m, j1, j2 }) => {
      const a = P(j1), b = P(j2);
      D.subVectors(b, a);
      const len = D.length();
      if (len < 0.001) { m.visible = false; return; }
      m.visible = true;
      m.scale.set(1, len, 1);
      m.position.addVectors(a, b).multiplyScalar(0.5);
      m.quaternion.setFromUnitVectors(UP, D.normalize());
    });
    this._head.position.copy(P(22));
  }

  setVisible(v) { this.group.visible = v; }

  dispose() {
    this.group.traverse(o => { if (o.isMesh) o.geometry.dispose(); });
    scene.remove(this.group);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  debug/poseDebugHelper — PoseDebugHelper
//  Gerencia SkeletonHelpers e as opções de visibilidade de debug.
// ═══════════════════════════════════════════════════════════════════════════════
class PoseDebugHelper {
  constructor() {
    this._helpers = [];
  }

  // Adiciona SkeletonHelper para o objeto raiz do avatar (gltf.scene ou SkinnedMesh).
  addSkeletonHelper(root) {
    const h = new THREE.SkeletonHelper(root);
    scene.add(h);
    this._helpers.push(h);
    return h;
  }

  clearSkeletonHelpers() {
    this._helpers.forEach(h => scene.remove(h));
    this._helpers = [];
  }

  setSkeletonVisible(v) {
    this._helpers.forEach(h => { h.visible = v; });
  }

  // Stub — Marco 4: joint markers para IK targets
  setJointsVisible(_v) {}

  dispose() {
    this.clearSkeletonHelpers();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  models/humanoidLoader  (src/models/humanoidLoader.ts)
// ───────────────────────────────────────────────────────────────────────────────
//  Regras de validação obrigatórias (spec §MODELO HUMANO):
//  1. Ao menos um THREE.SkinnedMesh
//  2. SkinnedMesh possui .skeleton
//  3. Geometria possui skinIndex e skinWeight
//  4. Skeleton contém bones
// ═══════════════════════════════════════════════════════════════════════════════
class HumanoidLoader {
  // Retorna Promise<LoadResult | null>
  // LoadResult: { valid, gltf, skinnedMesh, allMeshes, skeleton }
  static load(url) {
    return new Promise((resolve) => {
      const loader = new THREE.GLTFLoader();
      loader.load(
        url,
        (gltf) => resolve(HumanoidLoader._validate(gltf)),
        (xhr)  => {
          if (xhr.lengthComputable) {
            const pct = Math.round(xhr.loaded / xhr.total * 100);
            document.getElementById('loader-sub').textContent = `GLB ${pct}%`;
          }
        },
        (err) => {
          const msg = err?.message || String(err) || url;
          console.warn('[HumanoidLoader] Falha ao carregar GLB:', msg);
          resolve(null);
        }
      );
    });
  }

  static _validate(gltf) {
    const allMeshes = [];
    gltf.scene.traverse(o => { if (o.isSkinnedMesh) allMeshes.push(o); });

    if (!allMeshes.length) {
      console.error('[HumanoidLoader] ❌ Nenhum THREE.SkinnedMesh encontrado no GLB');
      return { valid: false };
    }

    const sm = allMeshes[0];

    if (!sm.skeleton) {
      console.error('[HumanoidLoader] ❌ SkinnedMesh não possui skeleton');
      return { valid: false };
    }
    if (!sm.geometry.attributes.skinIndex) {
      console.error('[HumanoidLoader] ❌ SkinnedMesh sem atributo skinIndex');
      return { valid: false };
    }
    if (!sm.geometry.attributes.skinWeight) {
      console.error('[HumanoidLoader] ❌ SkinnedMesh sem atributo skinWeight');
      return { valid: false };
    }
    if (!sm.skeleton.bones?.length) {
      console.error('[HumanoidLoader] ❌ Skeleton sem bones');
      return { valid: false };
    }

    // Bounding box — detecta escala (centímetros vs metros)
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const sz  = box.getSize(new THREE.Vector3());
    console.log(`[HumanoidLoader] ✅ ${allMeshes.length} SkinnedMesh(es) | ${sm.skeleton.bones.length} bones`);
    console.log(`[HumanoidLoader]    Bounding box: ${sz.x.toFixed(3)} × ${sz.y.toFixed(3)} × ${sz.z.toFixed(3)} m`);
    if (sz.y > 10)
      console.warn('[HumanoidLoader] ⚠ Modelo possivelmente em centímetros (height > 10). Ajuste: gltf.scene.scale.setScalar(0.01)');
    if (sz.y < 0.5)
      console.warn('[HumanoidLoader] ⚠ Modelo muito pequeno (height < 0.5). Verifique unidade ou escala.');

    HumanoidLoader.logSkeletonBones(sm);

    return { valid: true, gltf, skinnedMesh: sm, allMeshes, skeleton: sm.skeleton };
  }

  // Imprime todos os bones no console — não colapsa para garantir visibilidade.
  static logSkeletonBones(skinnedMesh) {
    const bones = skinnedMesh.skeleton.bones;
    const lines = bones.map((b, i) => {
      const parent = b.parent && b.parent.isBone ? b.parent.name : '(root)';
      return '  [' + String(i).padStart(3) + '] "' + b.name + '"  parent: "' + parent + '"';
    });
    console.log('[HumanoidLoader] Skeleton bones (' + bones.length + '):\n' + lines.join('\n'));
  }
}

// ── HumanoidBoneMap (módulo: humanoidBoneMap.ts) ──────────────────────────────
// Mapeia nomes lógicos → Bone objects para o rig mixamorig2.
class HumanoidBoneMap {
  constructor(skeleton) {
    const idx = {};
    skeleton.bones.forEach(b => { idx[b.name] = b; });
    const P = 'mixamorig2';
    this.hips      = idx[P+'Hips'];
    this.spine     = idx[P+'Spine'];
    this.spine1    = idx[P+'Spine1'];
    this.spine2    = idx[P+'Spine2'];
    this.neck      = idx[P+'Neck'];
    this.head      = idx[P+'Head'];
    this.lShoulder = idx[P+'LeftShoulder'];
    this.lArm      = idx[P+'LeftArm'];
    this.lForeArm  = idx[P+'LeftForeArm'];
    this.lHand     = idx[P+'LeftHand'];
    this.rShoulder = idx[P+'RightShoulder'];
    this.rArm      = idx[P+'RightArm'];
    this.rForeArm  = idx[P+'RightForeArm'];
    this.rHand     = idx[P+'RightHand'];
    this.lUpLeg    = idx[P+'LeftUpLeg'];
    this.lLeg      = idx[P+'LeftLeg'];
    this.lFoot     = idx[P+'LeftFoot'];
    this.rUpLeg    = idx[P+'RightUpLeg'];
    this.rLeg      = idx[P+'RightLeg'];
    this.rFoot     = idx[P+'RightFoot'];
    const critical = ['hips','spine','spine2','neck','head',
                      'lArm','lForeArm','rArm','rForeArm',
                      'lUpLeg','lLeg','rUpLeg','rLeg'];
    const missing = critical.filter(k => !this[k]);
    if (missing.length)
      console.warn('[HumanoidBoneMap] Bones ausentes: ' + missing.join(', '));
    else
      console.log('[HumanoidBoneMap] Todos os bones criticos mapeados.');
  }
}

// ── RestPoseCapture (módulo: restPoseCapture.ts) ──────────────────────────────
// Captura as transformações locais da T-pose antes de qualquer retargeting.
class RestPoseCapture {
  constructor(skeleton) {
    this.data = {};
    skeleton.bones.forEach(b => {
      this.data[b.name] = {
        pos:  b.position.clone(),
        quat: b.quaternion.clone(),
      };
    });
    console.log('[RestPoseCapture] ' + skeleton.bones.length + ' bones capturados na T-pose.');
  }
  restQuat(bone) {
    const d = this.data[bone.name];
    return d ? d.quat.clone() : new THREE.Quaternion();
  }
  restPos(bone) {
    const d = this.data[bone.name];
    return d ? d.pos.clone() : new THREE.Vector3();
  }
  // Reseta um conjunto de bones para a T-pose
  resetBones(bones) {
    bones.forEach(b => {
      if (!b) return;
      const d = this.data[b.name];
      if (d) { b.position.copy(d.pos); b.quaternion.copy(d.quat); }
    });
  }
}

// ── HumanoidRetargeter (módulo: humanoidRetargeter.ts) ────────────────────────
// Marco 2: aplica posição e orientação da pelvis (Hips).
// Marco 3+: torso, cabeça, membros.
const _retargM4 = new THREE.Matrix4();
const _retargQ  = new THREE.Quaternion();

class HumanoidRetargeter {
  // Aplica pelvis: posição (world GrappleMap → local bone) + orientação.
  // invScale = 1 / scaleFactor (converte metros GrappleMap para espaço local do bone).
  static applyPelvis(boneMap, restCapture, pose, invScale) {
    const hips = boneMap.hips;
    if (!hips) return;

    // Posição: o Hips é raiz — sem parent bone.
    // worldPos = boneLocalPos * sceneScale  →  localPos = worldPos / sceneScale
    hips.position.set(
      pose.root.x * invScale,
      pose.root.y * invScale,
      pose.root.z * invScale,
    );

    // Orientação: constrói quaternion a partir dos eixos do quadril (GrappleMap).
    // hipRight → X, hipUp → Y, hipFwd → Z  (THREE.Matrix4.makeBasis define colunas).
    _retargM4.makeBasis(pose.hipRight, pose.hipUp, pose.hipFwd);
    _retargQ.setFromRotationMatrix(_retargM4);

    // Como Hips é raiz (sem parent bone), local = world.
    // Queremos: worldQ = targetQ  →  localQ = invParentWorldQ * targetQ = targetQ
    // (a scene rotation é identidade após auto-escala)
    hips.quaternion.copy(_retargQ);
  }

  // Marco 3: tronco (spine chain)
  // Marco 4: membros
}

// ── Instâncias ────────────────────────────────────────────────────────────────
// Source rigs (debug — mostram a pose GrappleMap via cilindros)
const sourceRigA = new DebugSourceRig('#D8D1C4');  // branco
const sourceRigB = new DebugSourceRig('#1E3464');  // azul

const debugHelper = new PoseDebugHelper();

// Avatar GLB carregado
let avatarModel = null;  // { valid, gltf, skinnedMesh, allMeshes, skeleton, boneMap, restPose, invScale }

// ── Interpolação GrappleMap ───────────────────────────────────────────────────
function lerp3(a, b, t) {
  return [a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t];
}
function getFrame(frames, t) {
  const n = frames.length;
  if (n === 1) return frames[0];
  const raw = t * (n - 1);
  const i   = Math.min(Math.floor(raw), n - 2);
  const f   = raw - i;
  const fa  = frames[i], fb = frames[i + 1];
  return {
    p0: fa.p0.map((j, k) => lerp3(j, fb.p0[k], f)),
    p1: fa.p1.map((j, k) => lerp3(j, fb.p1[k], f)),
  };
}

// ── Animation state ───────────────────────────────────────────────────────────
let current  = null;
let animT    = 0;
let playing  = false;
let speed    = 1.0;
let lastTime = 0;

let seqItems = [];
let seqStep  = -1;
let seqMode  = false;
let seqT     = 0;
let seqDwell = 1.0;

function setEntry(entry, moveCam = true) {
  current = entry;
  animT   = 0;
  playing = entry.frames.length > 1 && !seqMode;
  updateInfo(entry);
  updateFrame();
  updatePlayBtn();
  if (moveCam) {
    const f0  = entry.frames[0];
    const all = [...f0.p0, ...f0.p1];
    const cx  = all.reduce((s, p) => s + p[0], 0) / all.length;
    const cy  = all.reduce((s, p) => s + p[1], 0) / all.length;
    controls.target.set(cx, cy, 0);
    controls.update();
  }
}

function updateFrame() {
  if (!current) return;
  const fr = getFrame(current.frames, animT);

  // Source rig debug (sempre atualizado — pose de referência)
  sourceRigA.update(fr.p0);
  sourceRigB.update(fr.p1);

  // Marco 2: retargeting de pelvis para o avatar A (player 0)
  if (avatarModel && avatarModel.boneMap) {
    const poseA = GrapplePoseExtractor.extract(fr.p0);
    HumanoidRetargeter.applyPelvis(
      avatarModel.boneMap,
      avatarModel.restPose,
      poseA,
      avatarModel.invScale,
    );
  }

  const fi = Math.round(animT * (current.frames.length - 1)) + 1;
  frameLbl.textContent = current.frames.length > 1
    ? `Frame ${fi}/${current.frames.length}`
    : 'Posicao estatica';
}

// ── Render loop ───────────────────────────────────────────────────────────────
renderer.setAnimationLoop((time) => {
  const dt = Math.min((time - lastTime) / 1000, 0.1);
  lastTime = time;

  if (seqMode && seqItems.length > 0) {
    const eIdx   = seqItems[seqStep];
    const e      = ENTRIES[eIdx];
    const isAnim = eIdx >= N_POS;
    const dur    = isAnim ? e.frames.length / speed : seqDwell;
    seqT += dt / dur;
    if (seqT >= 1.0) {
      seqT = 0;
      const next = seqStep + 1;
      if (next >= seqItems.length) {
        if (document.getElementById('seq-loop').checked) { seqStep = 0; }
        else {
          seqMode = false;
          document.getElementById('seq-play-btn').textContent = '▶ Play';
          controls.update(); renderer.render(scene, camera); return;
        }
      } else { seqStep = next; }
      setEntry(ENTRIES[seqItems[seqStep]], false);
      renderSeqList();
    } else {
      animT = isAnim ? seqT : 0;
      updateFrame();
    }
  } else if (playing && current && current.frames.length > 1) {
    animT = (animT + dt * speed / current.frames.length) % 1;
    updateFrame();
  }

  controls.update();
  renderer.render(scene, camera);
});

// ── Resize ────────────────────────────────────────────────────────────────────
const wrap = document.getElementById('canvas-wrap');
new ResizeObserver(() => {
  const w = wrap.clientWidth, h = wrap.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}).observe(wrap);

// ═══════════════════════════════════════════════════════════════════════════════
//  Avatar loading  (Marco 1)
// ═══════════════════════════════════════════════════════════════════════════════
function setAvatarStatus(msg, ok = true) {
  const el = document.getElementById('avatar-status');
  el.textContent = msg;
  el.style.color = ok ? '#3fb950' : '#f85149';
}

async function loadAvatar(url) {
  setAvatarStatus('carregando…');
  document.getElementById('loader').style.display = 'flex';
  document.getElementById('loader-sub').textContent = 'GLB…';

  const result = await HumanoidLoader.load(url);

  document.getElementById('loader').style.display = 'none';
  document.getElementById('loader-sub').textContent = '';

  if (!result || !result.valid) {
    setAvatarStatus('GLB inválido — ver console', false);
    return;
  }

  // Remove instância anterior se houver
  if (avatarModel) {
    scene.remove(avatarModel.gltf.scene);
    debugHelper.clearSkeletonHelpers();
  }

  avatarModel = result;

  // Auto-orient + auto-escala.
  // 1) Detecta eixo "up" real: se Y << max(X,Z), o modelo é Z-up (exportado do Blender/Maya
  //    sem conversão de eixo). Corrige com rotação -90° em X antes de medir escala.
  {
    const _bb0 = new THREE.Box3().setFromObject(result.gltf.scene);
    const _sz0 = _bb0.getSize(new THREE.Vector3());
    const _upIsZ = _sz0.y < Math.max(_sz0.x, _sz0.z) * 0.5;
    if (_upIsZ) {
      result.gltf.scene.rotation.x = -Math.PI / 2;
      console.log('[loadAvatar] Modelo Z-up detectado — aplicando rotation.x = -90 deg');
    }
  }
  // 2) Mede bounding box pós-rotação e escala para altura Y ≈ 1.7 m.
  const rawBox = new THREE.Box3().setFromObject(result.gltf.scene);
  const rawSz  = rawBox.getSize(new THREE.Vector3());
  let scaleFactor = 1;
  if (rawSz.y > 1e-4) {
    scaleFactor = 1.7 / rawSz.y;
    result.gltf.scene.scale.setScalar(scaleFactor);
    console.log('[loadAvatar] auto-escala: Y=' + rawSz.y.toFixed(4) +
      ' m  × ' + scaleFactor.toFixed(2) + '  = 1.70 m');
  }

  // Adicionar à cena na T-pose original
  scene.add(result.gltf.scene);

  // Marco 2: mapear bones e capturar rest pose (ANTES de qualquer retargeting)
  result.boneMap  = new HumanoidBoneMap(result.skeleton);
  result.restPose = new RestPoseCapture(result.skeleton);
  result.invScale = scaleFactor > 0 ? 1 / scaleFactor : 1;

  // SkeletonHelper
  debugHelper.addSkeletonHelper(result.gltf.scene);

  // Sincronizar com os toggles de debug
  result.gltf.scene.visible = document.getElementById('dbg-avatar').checked;
  debugHelper.setSkeletonVisible(document.getElementById('dbg-skeleton').checked);

  const nBones = result.skeleton.bones.length;
  const scaleStr = scaleFactor !== 1 ? ' ×' + scaleFactor.toFixed(3) : '';
  setAvatarStatus('✓ ' + nBones + ' bones' + scaleStr, true);

  // Relatório Marco 2
  console.log('── Marco 2: Avatar pronto para retargeting ────────────────────');
  console.log('  SkinnedMeshes : ' + result.allMeshes.length);
  console.log('  Skeleton bones: ' + nBones);
  console.log('  Scale factor  : ' + scaleFactor.toFixed(4) + '  (invScale=' + result.invScale.toFixed(6) + ')');
  console.log('  Retargeting   : pelvis ativo (Hips posicao + rotacao)');
  console.log('  Proximo passo : Marco 3 — spine chain + head');
  console.log('────────────────────────────────────────────────────────────────');
}

// Tenta carregar automaticamente do path padrão (requer servidor HTTP)
// Para usar localmente sem servidor: botão 📂 GLB
loadAvatar('./models/bjj-fighter.glb').catch(() => {});

// Botão e file input
document.getElementById('load-glb-btn').onclick = () =>
  document.getElementById('glb-file').click();

document.getElementById('glb-file').onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  try {
    await loadAvatar(url);
  } finally {
    // GLB é auto-contido — safe revogar após parse completo
    URL.revokeObjectURL(url);
    e.target.value = '';  // permite re-selecionar o mesmo arquivo
  }
};

// ── Debug toggles ─────────────────────────────────────────────────────────────
document.getElementById('dbg-source').onchange = (e) => {
  sourceRigA.setVisible(e.target.checked);
  sourceRigB.setVisible(e.target.checked);
};
document.getElementById('dbg-skeleton').onchange = (e) => {
  debugHelper.setSkeletonVisible(e.target.checked);
};
document.getElementById('dbg-avatar').onchange = (e) => {
  if (avatarModel) avatarModel.gltf.scene.visible = e.target.checked;
};

// ── UI — Explorer ─────────────────────────────────────────────────────────────
document.getElementById('loader').style.display = 'none';

const listEl   = document.getElementById('list');
const searchEl = document.getElementById('search');
const catEl    = document.getElementById('cat-filter');
const countEl  = document.getElementById('count');
const playBtn  = document.getElementById('play-btn');
const prevBtn  = document.getElementById('prev-btn');
const nextBtn  = document.getElementById('next-btn');
const frameLbl = document.getElementById('frame-label');
const speedEl  = document.getElementById('speed');
const speedVal = document.getElementById('speed-val');
const posLbl   = document.getElementById('pos-label');

const cats = [...new Set(ALL.map(e => e.cat))].sort();
cats.forEach(c => {
  const opt = document.createElement('option');
  opt.value = c; opt.textContent = c;
  catEl.appendChild(opt);
});

let filtered = [...ALL];
let activeIdx = 0;

function rebuildList() {
  const q   = searchEl.value.toLowerCase();
  const cat = catEl.value;
  filtered = ALL.filter(e => (!q || e.name.toLowerCase().includes(q)) && (!cat || e.cat === cat));
  countEl.textContent = `${filtered.length} / ${ALL.length} entradas`;
  listEl.innerHTML = '';
  filtered.forEach((e, i) => {
    const div = document.createElement('div');
    div.className = 'li' + (i === activeIdx ? ' active' : '');
    const color = CAT_COLORS[e.cat] || '#555';
    div.innerHTML = `<span class="dot" style="background:${color}"></span><span>${e.name}</span>`;
    div.onclick = () => selectIdx(i);
    listEl.appendChild(div);
  });
  posLbl.textContent = filtered.length ? `${activeIdx + 1} / ${filtered.length}` : '';
}

function selectIdx(i) {
  if (i < 0 || i >= filtered.length) return;
  activeIdx = i;
  listEl.querySelectorAll('.li').forEach((el, k) => el.classList.toggle('active', k === i));
  listEl.querySelectorAll('.li')[i]?.scrollIntoView({ block: 'nearest' });
  setEntry(filtered[i]);
  posLbl.textContent = `${i + 1} / ${filtered.length}`;
}

function updateInfo(e) {
  document.getElementById('info-name').textContent = e.name;
  const c2 = document.getElementById('info-cat');
  c2.textContent = e.cat;
  c2.style.background = (CAT_COLORS[e.cat] || '#555') + '33';
  c2.style.color = CAT_COLORS[e.cat] || '#aaa';
  document.getElementById('info-tags').textContent = e.tags.join(' · ');
}

function updatePlayBtn() {
  if (!current || current.frames.length <= 1) {
    playBtn.textContent = '▶ Play'; playBtn.disabled = true;
  } else {
    playBtn.disabled = false;
    playBtn.textContent = playing ? '‖ Pause' : '▶ Play';
  }
}

playBtn.onclick = () => { playing = !playing; updatePlayBtn(); };
prevBtn.onclick = () => selectIdx(activeIdx - 1);
nextBtn.onclick = () => selectIdx(activeIdx + 1);
speedEl.oninput = () => { speed = parseFloat(speedEl.value); speedVal.textContent = speed.toFixed(1) + '×'; };
searchEl.oninput = () => { activeIdx = 0; rebuildList(); if (filtered.length) selectIdx(0); };
catEl.onchange   = () => { activeIdx = 0; rebuildList(); if (filtered.length) selectIdx(0); };
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') selectIdx(activeIdx + 1);
  if (e.key === 'ArrowLeft')  selectIdx(activeIdx - 1);
  if (e.key === ' ') { e.preventDefault(); playBtn.click(); }
});

// ── UI — Tabs ─────────────────────────────────────────────────────────────────
document.getElementById('tab-exp').onclick = () => {
  document.getElementById('exp-panel').style.display = 'flex';
  document.getElementById('cmp-panel').classList.remove('on');
  document.getElementById('tab-exp').classList.add('active');
  document.getElementById('tab-cmp').classList.remove('active');
};
document.getElementById('tab-cmp').onclick = () => {
  document.getElementById('exp-panel').style.display = 'none';
  document.getElementById('cmp-panel').classList.add('on');
  document.getElementById('tab-exp').classList.remove('active');
  document.getElementById('tab-cmp').classList.add('active');
};

// ── UI — Compositor ───────────────────────────────────────────────────────────
const seqListEl   = document.getElementById('seq-list');
const seqCntEl    = document.getElementById('seq-cnt');
const seqPlayBtn  = document.getElementById('seq-play-btn');
const seqClearBtn = document.getElementById('seq-clear-btn');
const cmpQ        = document.getElementById('cmp-q');
const cmpRes      = document.getElementById('cmp-res');
const cmpMovesEl  = document.getElementById('cmp-moves');
const seqDwellEl  = document.getElementById('seq-dwell');
const seqDwellVal = document.getElementById('seq-dwell-val');

seqDwellEl.oninput = () => {
  seqDwell = parseFloat(seqDwellEl.value);
  seqDwellVal.textContent = seqDwell.toFixed(1) + 's';
};

function lastSeqPosIdx() {
  for (let i = seqItems.length - 1; i >= 0; i--)
    if (seqItems[i] < N_POS) return seqItems[i];
  return -1;
}

function cmpAddPosition(posEIdx) {
  seqItems.push(posEIdx);
  if (seqStep < 0) seqStep = 0;
  renderSeqList();
  setEntry(ENTRIES[posEIdx], true);
  cmpQ.value = ''; cmpRes.classList.remove('on'); cmpRes.innerHTML = '';
}

function cmpAddTransition(transEIdx) {
  seqItems.push(transEIdx);
  const t = ENTRIES[transEIdx];
  if (t.to >= 0) seqItems.push(t.to);
  if (seqStep < 0) seqStep = 0;
  renderSeqList();
  setEntry(ENTRIES[transEIdx], false);
}

function renderMoves() {
  cmpMovesEl.innerHTML = '';
  const posIdx = lastSeqPosIdx();
  if (posIdx < 0) return;
  const trans = GRAPH_OUT[posIdx] || [];
  if (!trans.length) {
    cmpMovesEl.innerHTML = '<div class="mv-hdr">Sem transições desta posição.</div>';
    return;
  }
  const hdr = document.createElement('div');
  hdr.className = 'mv-hdr';
  hdr.textContent = `Transições disponíveis (${trans.length}):`;
  cmpMovesEl.appendChild(hdr);
  trans.forEach(ti => {
    const t    = ENTRIES[ti];
    const dest = t.to >= 0 ? ENTRIES[t.to] : null;
    const div  = document.createElement('div');
    div.className = 'mv';
    div.innerHTML =
      `<span style="color:#d97706;font-size:9px">▶</span>` +
      `<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${t.name}</span>` +
      (dest ? `<span class="mv-to">→ ${dest.name}</span>` : `<span class="mv-to" style="color:#444">→ ?</span>`) +
      `<span class="cr-add">${t.frames.length}f</span>`;
    div.onclick = () => cmpAddTransition(ti);
    cmpMovesEl.appendChild(div);
  });
}

function renderSeqList() {
  seqCntEl.textContent = seqItems.length;
  seqListEl.innerHTML  = '';
  seqItems.forEach((eIdx, i) => {
    const e     = ENTRIES[eIdx];
    const isPos = eIdx < N_POS;
    const div   = document.createElement('div');
    div.className = 'sq' + (i === seqStep ? ' sq-cur' : '');
    const color = CAT_COLORS[e.cat] || '#555';
    const sub   = (!isPos && e.to >= 0) ? ` → ${ENTRIES[e.to].name}` : '';
    div.innerHTML =
      `<span class="sq-icon" style="color:${color}">${isPos ? '●' : '▶'}</span>` +
      `<span class="sq-nm">${e.name}${sub ? '<span class="sq-sub">' + sub + '</span>' : ''}</span>` +
      `<button class="sq-rm">×</button>`;
    div.querySelector('.sq-rm').addEventListener('click', ev => {
      ev.stopPropagation();
      seqItems.splice(i, 1);
      if (seqStep >= seqItems.length) seqStep = Math.max(0, seqItems.length - 1);
      renderSeqList();
    });
    div.addEventListener('click', () => {
      seqStep = i; seqT = 0;
      setEntry(ENTRIES[seqItems[i]], true);
      renderSeqList();
    });
    seqListEl.appendChild(div);
  });
  renderMoves();
  if (seqStep >= 0 && seqStep < seqItems.length)
    seqListEl.querySelectorAll('.sq')[seqStep]?.scrollIntoView({ block: 'nearest' });
}

seqPlayBtn.onclick = () => {
  if (!seqItems.length) return;
  seqMode = !seqMode;
  if (seqMode) {
    if (seqStep < 0 || seqStep >= seqItems.length) seqStep = 0;
    seqT = 0;
    setEntry(ENTRIES[seqItems[seqStep]], false);
    renderSeqList();
  }
  seqPlayBtn.textContent = seqMode ? '⏹ Stop' : '▶ Play';
};

seqClearBtn.onclick = () => {
  seqItems = []; seqStep = -1; seqMode = false; seqT = 0;
  seqPlayBtn.textContent = '▶ Play';
  renderSeqList();
};

cmpQ.oninput = () => {
  const q = cmpQ.value.toLowerCase().trim();
  if (!q) { cmpRes.classList.remove('on'); cmpRes.innerHTML = ''; return; }
  const hits = [];
  for (let i = 0; i < N_POS && hits.length < 12; i++)
    if (ENTRIES[i].name.toLowerCase().includes(q)) hits.push({ e: ENTRIES[i], idx: i });
  if (!hits.length) { cmpRes.classList.remove('on'); return; }
  cmpRes.classList.add('on'); cmpRes.innerHTML = '';
  hits.forEach(({ e, idx }) => {
    const div = document.createElement('div');
    div.className = 'cr';
    const color = CAT_COLORS[e.cat] || '#555';
    div.innerHTML =
      `<span style="color:${color};font-size:9px">●</span>` +
      `<span style="flex:1">${e.name}</span>` +
      `<span class="cr-add">+ iniciar</span>`;
    div.onclick = () => cmpAddPosition(idx);
    cmpRes.appendChild(div);
  });
};
cmpQ.addEventListener('blur', () => setTimeout(() => cmpRes.classList.remove('on'), 150));

// ── Init ──────────────────────────────────────────────────────────────────────
rebuildList();
if (filtered.length) selectIdx(0);
</script>
</body>
</html>"""


def generate_html(data: dict) -> str:
    data_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return HTML_TEMPLATE.replace("__DATA_JSON__", data_json)


def main():
    print("Baixando GrappleMap.txt…")
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    print(f"  {len(r.text):,} bytes")

    print("Parseando e decodificando…")
    data    = parse_and_decode(r.text)
    n_pos   = data["nPos"]
    n_trans = len(data["entries"]) - n_pos
    n_conn  = sum(1 for v in data["graphOut"].values() if v)
    print(f"  {n_pos} posições  |  {n_trans} transições  |  {n_conn} posições com saídas")

    print(f"\nGerando {OUTPUT}…")
    html = generate_html(data)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) / 1024
    print(f"  Tamanho: {size_kb:.0f} KB")
    print(f"  Abrir: {OUTPUT}")
    print()
    print("Marco 1 -- instrucoes:")
    print("  Para testar com avatar GLB:")
    print("    1. Obtenha um modelo GLB humanoide rigado (Mixamo, ReadyPlayerMe, etc.)")
    print("    2. Opcao A (servidor): copie para ./models/bjj-fighter.glb")
    print("         e sirva com:  python -m http.server 8080")
    print("         abra:  http://localhost:8080/GrappleMap_humanoid.html")
    print("    3. Opcao B (sem servidor): abra o HTML e clique em [GLB]")
    print("         para selecionar o .glb diretamente do disco")
    print("  O console exibira todos os bone names para o Marco 2 (bone map).")


if __name__ == "__main__":
    main()
