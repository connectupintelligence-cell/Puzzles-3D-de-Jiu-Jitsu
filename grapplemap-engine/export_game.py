"""
GrappleMap → BJJ Position Game
Gera GrappleMap_game.html — explorador de posições para 2 jogadores.
Os jogadores escolhem movimentações alternadamente (branco primeiro) a partir
de uma posição inicial; cada escolha avança a posição de ambos os atletas.
"""

import requests, json

URL    = "https://raw.githubusercontent.com/Eelis/GrappleMap/master/GrappleMap.txt"
OUTPUT = "GrappleMap_game.html"

# ── Decoder base62 ─────────────────────────────────────────────────────────────

B62  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
B62M = {c: i for i, c in enumerate(B62)}
N_JOINTS = 23

def decode_frame(lines):
    s = "".join(l.strip() for l in lines)
    if len(s) < 2 * N_JOINTS * 3 * 2:
        return None
    idx = 0
    def g(off):
        nonlocal idx
        v = (B62M.get(s[idx], 0) * 62 + B62M.get(s[idx+1], 0)) / 1000.0 - off
        idx += 2
        return round(v, 3)
    r = {"p0": [], "p1": []}
    for pk in ("p0", "p1"):
        for _ in range(N_JOINTS):
            r[pk].append([g(2.0), g(0.0), g(2.0)])
    return r

# ── Parser ─────────────────────────────────────────────────────────────────────

def parse_grapplemap(text):
    lines = text.split("\n")
    positions    = []
    trans_raw    = []
    frame_to_pos = {}

    i = 0
    while i < len(lines):
        ln = lines[i]
        if (ln and
                not ln.startswith("    ") and
                not ln.startswith("tags:") and
                not ln.startswith("properties:") and
                not ln.startswith("ref:") and
                ln.strip() != "..."):
            name = ln.strip().replace("\\n", " / ")
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith("    "):
                j += 1
            k = j
            while k < len(lines) and lines[k].startswith("    "):
                k += 1
            n = k - j
            if n >= 4 and n % 4 == 0:
                fkey = "\n".join(lines[j:j+4])
                lkey = "\n".join(lines[k-4:k])
                f0   = decode_frame(lines[j:j+4])
                if f0:
                    if n == 4:   # posição nomeada
                        pos_idx = len(positions)
                        frame_to_pos[fkey] = pos_idx
                        positions.append({"name": name, "frame": f0, "virtual": False})
                    else:        # transição
                        trans_raw.append({"name": name, "fkey": fkey, "lkey": lkey})
            i = k
        else:
            i += 1

    # Cria posições virtuais para endpoints de transições sem posição nomeada.
    # Isso amplia o grafo: 221 → ~689 transições navegáveis.
    for t in trans_raw:
        fp = frame_to_pos.get(t["fkey"])
        if fp is None:
            continue                    # origem desconhecida — ignora
        if t["lkey"] in frame_to_pos:
            continue                    # destino já mapeado
        # Decodifica o último frame da transição como nova posição
        f_last = decode_frame(t["lkey"].split("\n"))
        if f_last:
            vpos_idx = len(positions)
            frame_to_pos[t["lkey"]] = vpos_idx
            positions.append({"name": t["name"], "frame": f_last, "virtual": True})

    # Monta adjacência com todos os endpoints agora resolvidos
    adj = [[] for _ in range(len(positions))]
    for t in trans_raw:
        fp = frame_to_pos.get(t["fkey"])
        lp = frame_to_pos.get(t["lkey"])
        if fp is not None and lp is not None and fp != lp:
            adj[fp].append({"name": t["name"], "to": lp})

    return positions, adj

def find_start(positions, keyword="staggered"):
    kw = keyword.lower()
    for i, p in enumerate(positions):
        if kw in p["name"].lower():
            return i
    # fallback: qualquer posição em pé
    for i, p in enumerate(positions):
        if "standing" in p["name"].lower():
            return i
    return 0

# ── HTML template ──────────────────────────────────────────────────────────────
# Usa /*DATA*/ como placeholder — Python injeta os dados ali.
# Nenhuma brace-doubling necessária pois não é f-string.

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BJJ Position Game</title>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#0d0d0d;color:#ddd;font-family:system-ui,sans-serif;font-size:13px}

/* ── header ── */
#header{display:flex;align-items:center;gap:10px;padding:7px 14px;background:#141414;border-bottom:1px solid #252525;flex-shrink:0;height:46px}
#pos-name{flex:1;text-align:center;font-weight:700;font-size:13px;color:#f0f0f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 8px}
#turn-badge{padding:3px 13px;border-radius:20px;font-weight:800;font-size:11px;letter-spacing:.06em;flex-shrink:0}
#turn-badge.w{background:#e8ddc8;color:#1a1a1a}
#turn-badge.b{background:#162d62;color:#7aaeff}
.hbtn{padding:4px 11px;border-radius:6px;border:1px solid #2e2e2e;background:#1a1a1a;color:#888;cursor:pointer;font-size:12px;transition:background .1s}
.hbtn:hover{background:#252525;color:#ccc}
.hbtn:disabled{opacity:.3;cursor:default}

/* ── layout ── */
#app{display:flex;height:calc(100vh - 46px - 30px);overflow:hidden}

/* ── panels ── */
.panel{width:265px;flex-shrink:0;display:flex;flex-direction:column;overflow:hidden}
#wp{background:#0e0d0b;border-right:1px solid #222}
#bp{background:#0a0c12;border-left:1px solid #222}
.ph{padding:9px 14px;font-weight:700;font-size:11px;letter-spacing:.07em;border-bottom:1px solid #1e1e1e;display:flex;align-items:center;gap:6px}
#wp .ph{color:#c8b888;background:#141208}
#bp .ph{color:#7aaeff;background:#0c1020}
.ph .cnt{margin-left:auto;font-size:10px;font-weight:400;opacity:.55}
.pm{flex:1;overflow-y:auto;padding:6px}
.pm::-webkit-scrollbar{width:3px}
.pm::-webkit-scrollbar-thumb{background:#2a2a2a;border-radius:2px}

/* ── move items ── */
.mi{padding:8px 11px;border-radius:7px;margin-bottom:4px;cursor:pointer;border:1px solid #1e1e1e;transition:background .11s,border-color .11s;user-select:none}
.mi:hover{background:#1c1c1c;border-color:#333}
.mi:active{background:#222}
.mn{font-weight:600;color:#eee;line-height:1.35;font-size:12px}
.md{font-size:10px;color:#555;margin-top:2px}
.mi.preview{border-color:#444;background:#1a1a1a}

/* inactive panel */
.inactive .mi{pointer-events:none;opacity:.2}
.inactive .ph{opacity:.45}

/* empty/waiting */
.emsg{padding:24px 14px;color:#3a3a3a;font-size:12px;text-align:center;line-height:1.6}
.emsg b{display:block;font-size:18px;margin-bottom:6px;color:#2a2a2a}

/* ── canvas ── */
#cw{flex:1;position:relative;min-width:0}
canvas{width:100%;height:100%;display:block}

/* ── history bar ── */
#hbar{height:30px;display:flex;align-items:center;padding:0 14px;background:#0a0a0a;border-top:1px solid #1a1a1a;overflow-x:auto;white-space:nowrap;flex-shrink:0;gap:0}
#hbar::-webkit-scrollbar{height:3px}
#hbar::-webkit-scrollbar-thumb{background:#222}
.hi{display:inline-flex;align-items:center;color:#3a3a3a;font-size:10px;cursor:pointer;padding:2px 5px;border-radius:4px;transition:color .1s}
.hi:hover{color:#888;background:#181818}
.hi.cur{color:#aaa;cursor:default}
.hi.cur:hover{background:none}
.hs{color:#222;font-size:11px;margin:0 1px;flex-shrink:0}
</style>
</head>
<body>
<div id="header">
  <div id="pos-name">…</div>
  <div id="turn-badge" class="w">BRANCO</div>
  <button class="hbtn" id="ubtn" onclick="undoMove()" disabled>↩ Desfazer</button>
  <button class="hbtn" onclick="resetGame()">↺ Reiniciar</button>
</div>
<div id="app">
  <div id="wp" class="panel">
    <div class="ph">⬜ BRANCO <span class="cnt" id="wcnt"></span></div>
    <div class="pm" id="wm"></div>
  </div>
  <div id="cw"><canvas id="cvs"></canvas></div>
  <div id="bp" class="panel inactive">
    <div class="ph">🟦 AZUL <span class="cnt" id="bcnt"></span></div>
    <div class="pm" id="bm"></div>
  </div>
</div>
<div id="hbar"><span id="hi"></span></div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/*DATA*/

// ── Three.js setup ────────────────────────────────────────────────────────────
const cw  = document.getElementById('cw');
const cvs = document.getElementById('cvs');
const renderer = new THREE.WebGLRenderer({ canvas:cvs, antialias:true });
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

const scene  = new THREE.Scene();
scene.background = new THREE.Color(0x0d0d0d);
scene.fog = new THREE.Fog(0x0d0d0d, 8, 20);

const camera = new THREE.PerspectiveCamera(52, 1, 0.05, 30);
camera.position.set(0, 2.0, 3.8);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.85, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.12;
controls.minDistance = 0.6;
controls.maxDistance = 12;
controls.update();

// Luzes
scene.add(new THREE.AmbientLight(0x3a3f55, 2.2));
const sun = new THREE.DirectionalLight(0xfff5e0, 2.6);
sun.position.set(3, 7, 2);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = sun.shadow.camera.bottom = -5;
sun.shadow.camera.right = sun.shadow.camera.top = 5;
sun.shadow.camera.far = 25;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x6080c0, 0.7);
fill.position.set(-3, 2, -3);
scene.add(fill);

// Tatame IBJJF: amarelo fora, azul dentro
const mkPlane = (w, color, y=0) => {
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(w, w),
    new THREE.MeshStandardMaterial({ color, roughness:0.92, metalness:0 })
  );
  m.rotation.x = -Math.PI/2;
  m.position.y = y;
  m.receiveShadow = true;
  scene.add(m);
};
mkPlane(10, 0xecc14b);
mkPlane(8,  0x3373bc, 0.001);

// ── Stick bodies ──────────────────────────────────────────────────────────────
const SEG_TOPO = [
  [0,2],[1,3],[2,4],[3,5],[4,6],[5,7],[6,8],[7,9],
  [8,20],[9,20],[8,9],[20,10],[20,11],[10,11],
  [10,12],[11,13],[12,14],[13,15],
  [14,16],[15,17],[16,18],[17,19],
  [20,21],[21,22]
];
const _up  = new THREE.Vector3(0,1,0);
const _dir = new THREE.Vector3();
const _pa  = new THREE.Vector3();
const _pb  = new THREE.Vector3();

function makeStickBody(color, opacity) {
  const solid = opacity >= 1;
  const mat = new THREE.MeshStandardMaterial({
    color, roughness:0.72,
    transparent: !solid, opacity,
    depthWrite: solid,
  });
  const joints = Array.from({length:23}, (_, i) => {
    const r   = i === 22 ? 0.070 : 0.034;
    const geo = new THREE.SphereGeometry(r, 10, 8);
    const msh = new THREE.Mesh(geo, mat);
    msh.castShadow = solid;
    return msh;
  });
  const segs = SEG_TOPO.map(([a,b]) => {
    const geo = new THREE.CylinderGeometry(0.021, 0.021, 1, 8, 1);
    const msh = new THREE.Mesh(geo, mat);
    msh.castShadow = solid;
    return { msh, a, b };
  });
  const group = new THREE.Group();
  joints.forEach(m => group.add(m));
  segs.forEach(({msh}) => group.add(msh));
  return { group, joints, segs };
}

function applyPts(body, pts) {
  for (let i = 0; i < 23; i++) {
    body.joints[i].position.set(pts[i][0], pts[i][1], pts[i][2]);
  }
  for (const {msh, a, b} of body.segs) {
    _pa.set(pts[a][0], pts[a][1], pts[a][2]);
    _pb.set(pts[b][0], pts[b][1], pts[b][2]);
    _dir.subVectors(_pb, _pa);
    const len = _dir.length();
    if (len < 0.001) { msh.visible = false; continue; }
    msh.visible = true;
    msh.scale.y = len;
    msh.position.addVectors(_pa, _pb).multiplyScalar(0.5);
    msh.quaternion.setFromUnitVectors(_up, _dir.divideScalar(len));
  }
}

// Corpo principal
const bW = makeStickBody(0xd4c49a, 1.0);
const bB = makeStickBody(0x1a3470, 1.0);
scene.add(bW.group);
scene.add(bB.group);

// Ghost (pré-visualização ao passar o mouse na lista)
const gW = makeStickBody(0xd4c49a, 0.25);
const gB = makeStickBody(0x1a3470, 0.25);
scene.add(gW.group);
scene.add(gB.group);
gW.group.visible = false;
gB.group.visible = false;

function showPos(posIdx) {
  const d = POS_DATA[posIdx];
  applyPts(bW, d.p0);
  applyPts(bB, d.p1);
}

function showGhost(posIdx) {
  const d = POS_DATA[posIdx];
  applyPts(gW, d.p0);
  applyPts(gB, d.p1);
  gW.group.visible = true;
  gB.group.visible = true;
}

function clearGhost() {
  gW.group.visible = false;
  gB.group.visible = false;
}

// ── Estado do jogo ────────────────────────────────────────────────────────────
let curPos    = START_POS;
let curPlayer = 'white';   // 'white' | 'blue'
let history   = [];        // [{pos, player}] — estado ANTES de cada jogada

function pickMove(toPos) {
  history.push({ pos: curPos, player: curPlayer });
  curPos    = toPos;
  curPlayer = curPlayer === 'white' ? 'blue' : 'white';
  clearGhost();
  showPos(curPos);
  refreshUI();
}

function undoMove() {
  if (!history.length) return;
  const prev = history.pop();
  curPos    = prev.pos;
  curPlayer = prev.player;
  clearGhost();
  showPos(curPos);
  refreshUI();
}

function undoTo(idx) {
  if (idx >= history.length) return;
  const target = history[idx];
  history = history.slice(0, idx);
  curPos    = target.pos;
  curPlayer = target.player;
  clearGhost();
  showPos(curPos);
  refreshUI();
}

function resetGame() {
  history   = [];
  curPos    = START_POS;
  curPlayer = 'white';
  clearGhost();
  showPos(curPos);
  refreshUI();
}

// ── UI ────────────────────────────────────────────────────────────────────────
function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function trunc(s, n=26) {
  return s.length > n ? s.slice(0, n) + '…' : s;
}

function buildMoveList(containerId, active) {
  const el  = document.getElementById(containerId);
  const mvs = ADJACENCY[curPos];
  el.innerHTML = '';

  if (!active) {
    el.innerHTML = '<div class="emsg"><b>—</b>Aguardando a jogada do oponente…</div>';
    return mvs.length;
  }
  if (!mvs.length) {
    el.innerHTML = '<div class="emsg"><b>✕</b>Sem movimentações disponíveis.<br>Use ↩ Desfazer para voltar.</div>';
    return 0;
  }

  for (const mv of mvs) {
    const div = document.createElement('div');
    div.className = 'mi';
    div.innerHTML = `<div class="mn">${esc(mv.name)}</div><div class="md">→ ${esc(trunc(POS_NAMES[mv.to]))}</div>`;
    div.addEventListener('mouseenter', () => { showGhost(mv.to); div.classList.add('preview'); });
    div.addEventListener('mouseleave', () => { clearGhost(); div.classList.remove('preview'); });
    div.addEventListener('click', () => pickMove(mv.to));
    el.appendChild(div);
  }
  return mvs.length;
}

function refreshUI() {
  const isW = curPlayer === 'white';

  // Nome da posição
  document.getElementById('pos-name').textContent = POS_NAMES[curPos];

  // Badge de turno
  const badge = document.getElementById('turn-badge');
  badge.textContent = isW ? 'VEZ DO BRANCO' : 'VEZ DO AZUL';
  badge.className   = isW ? 'w' : 'b';

  // Painel esquerdo (branco) / direito (azul)
  const wp = document.getElementById('wp');
  const bp = document.getElementById('bp');
  wp.classList.toggle('inactive', !isW);
  bp.classList.toggle('inactive',  isW);

  const wc = buildMoveList('wm', isW);
  const bc = buildMoveList('bm', !isW);
  document.getElementById('wcnt').textContent = isW ? `${wc} opções` : '';
  document.getElementById('bcnt').textContent = !isW ? `${bc} opções` : '';

  // Botão desfazer
  document.getElementById('ubtn').disabled = history.length === 0;

  // Barra de histórico
  const hc = document.getElementById('hi');
  hc.innerHTML = '';

  // Mostra até 14 passos anteriores
  const show = history.slice(-14);
  const off  = history.length - show.length;

  show.forEach((h, i) => {
    if (i > 0) {
      const sep = document.createElement('span');
      sep.className = 'hs'; sep.textContent = '›';
      hc.appendChild(sep);
    }
    const item = document.createElement('span');
    item.className = 'hi';
    item.title = POS_NAMES[h.pos];
    item.textContent = trunc(POS_NAMES[h.pos], 20);
    const realIdx = off + i;
    item.onclick = () => undoTo(realIdx);
    hc.appendChild(item);
  });

  if (history.length > 0) {
    const sep = document.createElement('span');
    sep.className = 'hs'; sep.textContent = '›';
    hc.appendChild(sep);
  }
  const cur = document.createElement('span');
  cur.className = 'hi cur';
  cur.textContent = '● ' + trunc(POS_NAMES[curPos], 20);
  hc.appendChild(cur);

  // Scroll para o fim do histórico
  const hbar = document.getElementById('hbar');
  hbar.scrollLeft = hbar.scrollWidth;
}

// ── Init ──────────────────────────────────────────────────────────────────────
showPos(curPos);
refreshUI();

// ── Resize + render loop ──────────────────────────────────────────────────────
function onResize() {
  const w = cw.clientWidth, h = cw.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(onResize).observe(cw);
onResize();

(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
</script>
</body>
</html>"""

# ── Build ───────────────────────────────────────────────────────────────────────

def build_html(positions, adj, start_pos):
    names_j = json.dumps(
        [p["name"] for p in positions],
        ensure_ascii=False, separators=(',', ':')
    )
    data_j = json.dumps(
        [{"p0": p["frame"]["p0"], "p1": p["frame"]["p1"]} for p in positions],
        ensure_ascii=False, separators=(',', ':')
    )
    adj_j = json.dumps(adj, ensure_ascii=False, separators=(',', ':'))

    data_js = (
        f"const POS_NAMES={names_j};\n"
        f"const POS_DATA={data_j};\n"
        f"const ADJACENCY={adj_j};\n"
        f"const START_POS={start_pos};\n"
    )
    return HTML_TEMPLATE.replace("/*DATA*/", data_js)

# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print("Baixando GrappleMap.txt…")
    resp = requests.get(URL, timeout=90)
    resp.raise_for_status()
    print(f"  {len(resp.content):,} bytes")

    print("Parseando…")
    positions, adj = parse_grapplemap(resp.text)
    n_trans = sum(len(a) for a in adj)
    print(f"  {len(positions)} posições  |  {n_trans} transições mapeadas")

    start_pos = find_start(positions, "staggered")
    print(f"  Posição inicial: [{start_pos}] {positions[start_pos]['name']!r}")

    print(f"Gerando {OUTPUT}…")
    html = build_html(positions, adj, start_pos)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Tamanho: {len(html.encode())//1024} KB")
    print(f"  Abrir: {OUTPUT}")

if __name__ == "__main__":
    main()
