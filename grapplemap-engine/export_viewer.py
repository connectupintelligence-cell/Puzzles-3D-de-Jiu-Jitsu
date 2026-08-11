"""
GrappleMap → Standalone 3D Viewer
Gera GrappleMap_viewer.html com Three.js embarcado.
Abre direto no browser, sem servidor.
"""

import requests, json, sys

URL    = "https://raw.githubusercontent.com/Eelis/GrappleMap/master/GrappleMap.txt"
OUTPUT = "GrappleMap_viewer.html"

# ── Decoder base62 ────────────────────────────────────────────────────────────

B62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
B62M = {c: i for i, c in enumerate(B62)}
N_JOINTS = 23  # LeftToe…Head

def decode_frame(lines):
    s = "".join(l.strip() for l in lines)
    if len(s) < 2 * N_JOINTS * 3 * 2:
        return None
    pos = 0
    def g(off):
        nonlocal pos
        v = (B62M.get(s[pos], 0) * 62 + B62M.get(s[pos+1], 0)) / 1000.0 - off
        pos += 2
        return round(v, 4)
    r = {"p0": [], "p1": []}
    for pk in ("p0", "p1"):
        for _ in range(N_JOINTS):
            r[pk].append([g(2.0), g(0.0), g(2.0)])
    return r

# ── Parser ────────────────────────────────────────────────────────────────────

SUB  = {"armbar","kimura","omoplata","triangle","rear_naked_choke","arm_choke",
        "arm_triangle","guillotine","darce","toehold","heel_hook","knee_bar",
        "neck_crank","shoulder_lock","monoplata"}
TD   = {"takedown","double_leg_takedown","single_leg_takedown","throw",
        "sacrifice_throw","te_waza","koshi_waza","ashi_waza","sutemi_waza"}
DOM  = {"mount","side_control","judo_side","north_south","back","turtle",
        "knee_on_belly","crucifix","truck"}

def categorize(ts):
    if ts & SUB:  return "Finalização"
    if ts & TD:   return "Queda"
    if any(t.startswith("pass") for t in ts): return "Passagem"
    if ts & {"sweep","hip_bump"}:  return "Raspagem"
    if ts & {"stand_up","bridge","guard_pull","guard_jump"}: return "Escape"
    if "standing" in ts:  return "Em Pé"
    if any("guard" in t for t in ts): return "Guarda"
    if ts & DOM:  return "Posição Dominante"
    return "Outro"

def parse_and_decode(text):
    lines = text.split("\n")
    raw_all = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if (ln and
                not ln.startswith("    ") and
                not ln.startswith("tags:") and
                not ln.startswith("properties:") and
                not ln.startswith("ref:") and
                ln.strip() != "..."):
            name_raw = ln.strip()
            j = i + 1
            tags = []
            while j < len(lines) and lines[j].strip() and not lines[j].startswith("    "):
                if lines[j].startswith("tags:"):
                    tags = lines[j].replace("tags:", "").strip().split()
                j += 1
            k = j
            while k < len(lines) and lines[k].startswith("    "):
                k += 1
            n_data = k - j
            if n_data >= 4 and n_data % 4 == 0:
                fkey = "\n".join(lines[j:j+4])
                lkey = "\n".join(lines[k-4:k])
                frames = [decode_frame(lines[j+fi*4:j+(fi+1)*4]) for fi in range(n_data // 4)]
                frames = [f for f in frames if f]
                if frames:
                    raw_all.append({
                        "name":   name_raw.replace("\\n", " / "),
                        "cat":    categorize(set(tags)),
                        "tags":   tags,
                        "frames": frames,
                        "_fkey":  fkey,
                        "_lkey":  lkey,
                    })
            i = k
        else:
            i += 1

    # Classify: 1-frame entries = positions, multi-frame = transitions
    positions   = []
    transitions = []
    frame_to_pos = {}  # fkey -> pos_idx (= absolute index in ENTRIES since positions come first)

    for e in raw_all:
        if len(e["frames"]) == 1:
            idx = len(positions)
            frame_to_pos[e["_fkey"]] = idx
            positions.append({
                "name":   e["name"],
                "cat":    e["cat"],
                "tags":   e["tags"],
                "frames": e["frames"],
            })
        else:
            transitions.append({
                "name":   e["name"],
                "cat":    e["cat"],
                "tags":   e["tags"],
                "frames": e["frames"],
                "_fkey":  e["_fkey"],
                "_lkey":  e["_lkey"],
            })

    # Resolve from/to for transitions; keep only those with known from-position
    n_pos = len(positions)
    kept_trans = []
    graph_out  = {}  # posIdx -> [absolute entry idx of transitions]

    for t in transitions:
        from_idx = frame_to_pos.get(t["_fkey"], -1)
        to_idx   = frame_to_pos.get(t["_lkey"], -1)
        if from_idx < 0:
            continue  # skip — can't place in graph
        abs_idx = n_pos + len(kept_trans)
        kept_trans.append({
            "name":   t["name"],
            "cat":    t["cat"],
            "tags":   t["tags"],
            "frames": t["frames"],
            "from":   from_idx,  # pos idx (= absolute ENTRIES idx)
            "to":     to_idx,    # pos idx or -1
        })
        graph_out.setdefault(from_idx, []).append(abs_idx)

    return {
        "entries":  positions + kept_trans,
        "nPos":     n_pos,
        "graphOut": graph_out,
    }

# ── HTML generator ────────────────────────────────────────────────────────────

def generate_html(data):
    data_json = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>GrappleMap 3D Viewer</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script type="importmap">
{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}}}
</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{display:flex;flex-direction:column;height:100vh;background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;overflow:hidden}}
#app{{display:flex;flex:1;overflow:hidden}}
/* ── sidebar ── */
#sidebar{{width:280px;flex-shrink:0;display:flex;flex-direction:column;border-right:1px solid #21262d;background:#0d1117}}
#sidebar-top{{padding:10px 10px 0}}
h1{{font-size:13px;font-weight:700;color:#58a6ff;margin-bottom:8px;letter-spacing:.5px}}
#search{{width:100%;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:6px 8px;color:#e6edf3;font-size:12px;outline:none}}
#search:focus{{border-color:#58a6ff}}
#cat-filter{{width:100%;margin-top:6px;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:5px 8px;color:#e6edf3;font-size:12px;outline:none;cursor:pointer}}
#count{{font-size:10px;color:#6e7681;margin-top:5px;text-align:right}}
#list{{flex:1;overflow-y:auto;padding:4px 0}}
#list::-webkit-scrollbar{{width:4px}}
#list::-webkit-scrollbar-track{{background:#0d1117}}
#list::-webkit-scrollbar-thumb{{background:#30363d;border-radius:2px}}
.li{{padding:6px 12px;font-size:11px;cursor:pointer;display:flex;align-items:center;gap:6px;border-left:3px solid transparent;color:#8b949e;transition:all .1s}}
.li:hover{{background:#161b22;color:#e6edf3}}
.li.active{{background:#161b22;border-left-color:#58a6ff;color:#e6edf3}}
.dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
#info{{padding:10px 12px;border-top:1px solid #21262d;background:#0d1117;font-size:11px;min-height:90px}}
#info-name{{font-weight:700;color:#e6edf3;margin-bottom:4px;line-height:1.4;font-size:12px}}
#info-cat{{font-size:10px;font-weight:600;padding:1px 6px;border-radius:10px;display:inline-block;margin-bottom:5px}}
#info-tags{{color:#6e7681;font-size:10px;line-height:1.5;max-height:48px;overflow:hidden}}
/* ── canvas ── */
#canvas-wrap{{flex:1;position:relative}}
canvas{{display:block;width:100%!important;height:100%!important}}
/* ── bottom bar ── */
#bar{{height:46px;display:flex;align-items:center;gap:10px;padding:0 16px;border-top:1px solid #21262d;background:#0d1117;flex-shrink:0}}
.btn{{background:#21262d;border:1px solid #30363d;color:#e6edf3;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;transition:background .1s}}
.btn:hover{{background:#30363d}}
.btn:disabled{{opacity:.3;cursor:default}}
#play-btn{{min-width:64px}}
#frame-label{{font-size:11px;color:#6e7681;min-width:70px;text-align:center}}
#speed-wrap{{display:flex;align-items:center;gap:5px;font-size:11px;color:#6e7681}}
input[type=range]{{accent-color:#58a6ff;width:80px}}
#legend{{margin-left:auto;display:flex;gap:12px;font-size:11px;align-items:center}}
.leg-dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:4px}}
#pos-label{{font-size:11px;color:#6e7681}}
/* ── loaders ── */
#loader{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#0d1117;z-index:10;font-size:14px;color:#58a6ff}}
/* ── debug panel ── */
#dbg-panel{{display:none;position:absolute;bottom:54px;right:12px;background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:10px 14px;font-size:11px;z-index:20;min-width:170px;box-shadow:0 4px 16px rgba(0,0,0,.5)}}
#dbg-panel h3{{font-size:9px;font-weight:700;color:#58a6ff;letter-spacing:.6px;text-transform:uppercase;margin-bottom:8px}}
.dbg-row{{display:flex;align-items:center;gap:7px;margin-bottom:5px;cursor:pointer;color:#8b949e;user-select:none}}
.dbg-row:hover{{color:#e6edf3}}
.dbg-row input{{accent-color:#58a6ff;cursor:pointer;margin:0}}
#dbg-panel hr{{border:none;border-top:1px solid #21262d;margin:7px 0}}
#dbg-ab-lbl{{color:#d97706}}
/* ── tabs ── */
#sidebar-tabs{{display:flex;flex-shrink:0;border-bottom:1px solid #21262d}}
.stab{{flex:1;background:none;border:none;border-bottom:2px solid transparent;color:#6e7681;font-size:11px;font-weight:600;padding:8px 4px;cursor:pointer;letter-spacing:.3px}}
.stab.active{{color:#58a6ff;border-bottom-color:#58a6ff}}
#exp-panel{{display:flex;flex-direction:column;flex:1;overflow:hidden}}
/* ── compositor ── */
#cmp-panel{{display:none;flex-direction:column;flex:1;overflow:hidden}}
#cmp-panel.on{{display:flex}}
#cmp-add{{padding:8px 10px;border-bottom:1px solid #21262d;flex-shrink:0}}
#cmp-q{{width:100%;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:5px 8px;color:#e6edf3;font-size:11px;outline:none}}
#cmp-q:focus{{border-color:#58a6ff}}
#cmp-res{{margin-top:4px;background:#161b22;border:1px solid #30363d;border-radius:6px;display:none;max-height:130px;overflow-y:auto}}
#cmp-res.on{{display:block}}
.cr{{padding:5px 10px;font-size:11px;color:#8b949e;cursor:pointer;display:flex;align-items:center;gap:6px}}
.cr:hover{{background:#21262d;color:#e6edf3}}
.cr-add{{margin-left:auto;color:#58a6ff;font-size:10px;white-space:nowrap}}
#cmp-moves{{flex-shrink:0;max-height:180px;overflow-y:auto;border-bottom:1px solid #21262d}}
#cmp-moves::-webkit-scrollbar{{width:4px}}
#cmp-moves::-webkit-scrollbar-thumb{{background:#30363d;border-radius:2px}}
.mv-hdr{{padding:4px 10px;font-size:10px;color:#6e7681;background:#0d1117;position:sticky;top:0}}
.mv{{padding:4px 10px;font-size:11px;color:#8b949e;cursor:pointer;display:flex;align-items:center;gap:6px;border-left:3px solid transparent}}
.mv:hover{{background:#161b22;color:#e6edf3;border-left-color:#d97706}}
.mv-to{{color:#6e7681;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100px}}
#seq-hdr{{padding:5px 12px;font-size:10px;color:#6e7681;flex-shrink:0;display:flex;align-items:center;justify-content:space-between}}
#seq-list{{flex:1;overflow-y:auto;padding:4px 0}}
#seq-list::-webkit-scrollbar{{width:4px}}
#seq-list::-webkit-scrollbar-thumb{{background:#30363d;border-radius:2px}}
.sq{{display:flex;align-items:center;gap:5px;padding:5px 10px;font-size:11px;cursor:pointer;color:#8b949e;border-left:3px solid transparent;transition:all .1s}}
.sq:hover{{background:#161b22;color:#e6edf3}}
.sq.sq-cur{{background:#161b22;border-left-color:#58a6ff;color:#e6edf3}}
.sq-icon{{font-size:9px;flex-shrink:0;width:12px;text-align:center}}
.sq-nm{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.sq-sub{{font-size:10px;color:#6e7681;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.sq-rm{{background:none;border:none;color:#6e7681;cursor:pointer;font-size:13px;padding:0 2px;line-height:1}}
.sq-rm:hover{{color:#ef4444}}
#seq-ctrl{{padding:8px 10px;border-top:1px solid #21262d;display:flex;gap:6px;align-items:center;flex-shrink:0;flex-wrap:wrap}}
#seq-ctrl .btn{{font-size:11px;padding:3px 9px;min-width:auto}}
.seq-lbl{{font-size:10px;color:#6e7681;display:flex;align-items:center;gap:3px}}
#seq-dwell{{width:50px;accent-color:#58a6ff}}
/* ── proportions panel ── */
#props-panel{{display:none;position:absolute;top:10px;right:12px;width:280px;max-height:calc(100% - 70px);background:#0d1117;border:1px solid #30363d;border-radius:8px;z-index:30;box-shadow:0 4px 24px rgba(0,0,0,.6);flex-direction:column;overflow:hidden}}
#props-panel.open{{display:flex}}
#props-panel.minimized .pp-body{{display:none}}
.pp-hdr{{display:flex;align-items:center;gap:6px;padding:8px 10px;border-bottom:1px solid #21262d;flex-shrink:0;background:#161b22;border-radius:8px 8px 0 0}}
.pp-title{{font-weight:700;color:#58a6ff;font-size:11px;flex:1}}
.pp-hdr-btn{{background:none;border:none;color:#6e7681;cursor:pointer;font-size:13px;padding:0 3px;line-height:1}}
.pp-hdr-btn:hover{{color:#e6edf3}}
.pp-body{{overflow-y:auto;flex:1}}
.pp-body::-webkit-scrollbar{{width:3px}}
.pp-body::-webkit-scrollbar-thumb{{background:#30363d;border-radius:2px}}
.pp-preset-bar{{padding:6px 8px;border-bottom:1px solid #21262d;display:flex;align-items:center;gap:4px;flex-shrink:0}}
.pp-preset-sel{{flex:1;background:#161b22;border:1px solid #30363d;border-radius:5px;color:#e6edf3;font-size:11px;padding:3px 5px;outline:none;cursor:pointer;min-width:0}}
.pp-preset-btn{{background:#21262d;border:1px solid #30363d;color:#e6edf3;border-radius:5px;padding:2px 6px;cursor:pointer;font-size:11px;white-space:nowrap}}
.pp-preset-btn:hover{{background:#30363d}}
.pp-name-row{{padding:4px 8px;display:none;align-items:center;gap:4px;border-bottom:1px solid #21262d}}
.pp-name-row.on{{display:flex}}
.pp-name-inp{{flex:1;background:#161b22;border:1px solid #30363d;border-radius:5px;color:#e6edf3;font-size:11px;padding:3px 7px;outline:none}}
.pp-name-inp:focus{{border-color:#58a6ff}}
.pp-compare-bar{{padding:5px 8px;border-bottom:1px solid #21262d;display:flex;gap:4px;flex-shrink:0}}
.pp-cmp-btn{{flex:1;background:#21262d;border:1px solid #30363d;color:#8b949e;border-radius:5px;padding:3px 4px;cursor:pointer;font-size:10px;text-align:center}}
.pp-cmp-btn.active{{background:#1c3f7a;border-color:#58a6ff;color:#e6edf3}}
.pp-ath-tabs{{display:flex;border-bottom:1px solid #21262d;flex-shrink:0}}
.pp-ath-tab{{flex:1;background:none;border:none;border-bottom:2px solid transparent;color:#6e7681;font-size:10px;padding:5px;cursor:pointer}}
.pp-ath-tab.active{{color:#58a6ff;border-bottom-color:#58a6ff}}
.pp-group{{border-bottom:1px solid #21262d}}
.pp-group-hdr{{display:flex;align-items:center;padding:5px 8px;background:#0d1117;user-select:none}}
.pp-group-lbl{{font-size:10px;font-weight:700;letter-spacing:.5px;color:#8b949e;text-transform:uppercase;flex:1}}
.pp-group-mirror{{font-size:12px;cursor:pointer;margin-right:4px}}
.pp-grp-reset{{background:none;border:none;color:#6e7681;cursor:pointer;font-size:11px;padding:0 3px}}
.pp-grp-reset:hover{{color:#e6edf3}}
.pp-grp-rows{{padding:2px 0 4px}}
.pp-row{{display:flex;align-items:center;gap:4px;padding:2px 8px}}
.pp-row-lbl{{width:88px;flex-shrink:0;color:#8b949e;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.pp-row input[type=range]{{flex:1;accent-color:#58a6ff;height:14px;cursor:pointer}}
.pp-val{{width:30px;text-align:right;color:#e6edf3;font-size:10px;font-variant-numeric:tabular-nums;flex-shrink:0}}
.pp-row-reset{{background:none;border:none;color:#30363d;cursor:pointer;font-size:11px;padding:0 2px;flex-shrink:0}}
.pp-row-reset:hover{{color:#6e7681}}
.pp-row-reset.dirty{{color:#d97706}}
.pp-footer{{padding:6px 8px;border-top:1px solid #21262d;display:flex;align-items:center;gap:6px;flex-shrink:0;flex-wrap:wrap;background:#0d1117}}
.pp-link-lbl{{display:flex;align-items:center;gap:4px;cursor:pointer;color:#8b949e;font-size:10px;user-select:none}}
.pp-link-lbl input{{accent-color:#58a6ff;cursor:pointer}}
.pp-status{{margin-left:auto;font-size:10px;color:#27ae60}}
.pp-status.dirty{{color:#d97706}}
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <div id="sidebar-top">
      <h1>⛩ GrappleMap 3D</h1>
    </div>
    <div id="sidebar-tabs">
      <button class="stab active" id="tab-exp">Explorar</button>
      <button class="stab" id="tab-cmp">Compositor</button>
    </div>
    <!-- Explorer panel -->
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
    <!-- Compositor panel -->
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
    <div id="loader">Carregando Three.js…</div>
    <canvas id="c"></canvas>
    <!-- Debug panel (flutuante, fecha ao clicar fora) -->
    <div id="dbg-panel">
      <h3>Debug</h3>
      <label class="dbg-row"><input type="checkbox" id="dbg-segs" checked> Segmentos</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-jsph" checked> Articulações</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-head" checked> Cabeça</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-hair" checked> Cabelo</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-belt" checked> Cinto</label>
      <hr>
      <label class="dbg-row" id="dbg-ab-lbl"><input type="checkbox" id="dbg-ab"> Experimental (B)</label>
      <hr>
      <label class="dbg-row"><input type="checkbox" id="dbg-trunk" checked> Tronco (superfície)</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-trunk-cyls"> Cilin. internos</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-feet" checked> Pés (superfície)</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-feet-pts"> Pts/eixos do pé</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-hands" checked> Mãos (superfície)</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-hands-pts"> Pts da mão</label>
      <label class="dbg-row"><input type="checkbox" id="dbg-hands-axes"> Eixos locais da mão</label>
      <hr>
      <label class="dbg-row"><input type="checkbox" id="hand-flip-l"> Flip mão esquerda</label>
      <label class="dbg-row"><input type="checkbox" id="hand-flip-r"> Flip mão direita</label>
    </div>
    <!-- Proportions panel -->
    <div id="props-panel">
      <div class="pp-hdr">
        <span class="pp-title">⚖ Proporções</span>
        <button class="pp-hdr-btn" id="pp-minimize" title="Minimizar">−</button>
        <button class="pp-hdr-btn" id="pp-close" title="Fechar">×</button>
      </div>
      <div class="pp-body" id="pp-body"></div>
    </div>
  </div>
</div>
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
  <span id="pos-label"></span>
  <button class="btn" id="dbg-btn" style="margin-left:auto;font-size:10px;padding:3px 9px">⚙ Debug</button>
  <button class="btn" id="props-btn" style="font-size:10px;padding:3px 9px">⚖ Props</button>
  <div id="legend">
    <span><span class="leg-dot" style="background:#D4CBC0"></span>Lutador A</span>
    <span><span class="leg-dot" style="background:#1E3A6E"></span>Lutador B</span>
  </div>
</div>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

// ── Data ──────────────────────────────────────────────────────────────────────
const DATA      = {data_json};
const ENTRIES   = DATA.entries;   // [0..N_POS-1] = positions, [N_POS..] = transitions
const N_POS     = DATA.nPos;
const GRAPH_OUT = DATA.graphOut;  // posIdx -> [abs entry idx]
const ALL       = ENTRIES;        // alias for explorer

// ── Joint indices ─────────────────────────────────────────────────────────────
// 0:LeftToe 1:RightToe 2:LeftHeel 3:RightHeel 4:LeftAnkle 5:RightAnkle
// 6:LeftKnee 7:RightKnee 8:LeftHip 9:RightHip 10:LeftShoulder 11:RightShoulder
// 12:LeftElbow 13:RightElbow 14:LeftWrist 15:RightWrist 16:LeftHand 17:RightHand
// 18:LeftFingers 19:RightFingers 20:Core 21:Neck 22:Head

// ── Topologia (FIXO — não alterar joint indices nem conexões) ──────────────────
// JSPH_TOPO: [jidx, type]  — radii vêm de BODY_STYLE.jsph[]
const JSPH_TOPO = [
  [20,'gi'],
  [10,'gi'],   [11,'gi'],
  [12,'sleeve'],[13,'sleeve'],
  [14,'skin'],  [15,'skin'],
  [ 8,'gi'],   [ 9,'gi'],
  [ 6,'leg'],  [ 7,'leg'],
  [ 4,'skin'], [ 5,'skin'],
  [21,'gi'],
];

// SEG_TOPO: [j1, j2, type]  — radii vêm de BODY_STYLE.seg[]
// Ordem dos 20 segmentos mantida exatamente igual ao SEG original.
const SEG_TOPO = [
  // TORSO (0-5)
  [20,10,'gi'],  [20,11,'gi'],
  [20, 8,'gi'],  [20, 9,'gi'],
  [10,11,'gi'],  [ 8, 9,'gi'],
  // SPINE / PESCOÇO (6-7)
  [20,21,'gi'],  [21,22,'skin'],
  // LEFT LEG (8-10)
  [ 8, 6,'leg'], [ 6, 4,'leg'], [ 4, 0,'skin'],
  // RIGHT LEG (11-13)
  [ 9, 7,'leg'], [ 7, 5,'leg'], [ 5, 1,'skin'],
  // LEFT ARM (14-16)
  [10,12,'sleeve'],[12,14,'sleeve'],[14,16,'skin'],
  // RIGHT ARM (17-19)
  [11,13,'sleeve'],[13,15,'sleeve'],[15,17,'skin'],
];

// ── Config visual central ─────────────────────────────────────────────────────
// STYLE_ORIG: valores que reproduzem o visual atual exatamente.
// STYLE_EXP: cópia inicial idêntica; modifique aqui para testes A/B futuros.
// Alterar APENAS raios, materiais e parâmetros geométricos — nunca indices.

const STYLE_ORIG = {{
  // Raios dos segmentos — índice paralelo ao SEG_TOPO (20 entradas)
  // rTop = raio na extremidade j2 | rBot = raio na extremidade j1
  seg: [
    // TORSO
    {{rTop:.076,rBot:.090}},  // 0  Core→LShoulder
    {{rTop:.076,rBot:.090}},  // 1  Core→RShoulder
    {{rTop:.090,rBot:.090}},  // 2  Core→LHip
    {{rTop:.090,rBot:.090}},  // 3  Core→RHip
    {{rTop:.076,rBot:.076}},  // 4  LShoulder↔RShoulder
    {{rTop:.090,rBot:.090}},  // 5  LHip↔RHip
    // SPINE
    {{rTop:.040,rBot:.090}},  // 6  Core→Neck
    {{rTop:.026,rBot:.040}},  // 7  Neck→Head
    // LEFT LEG
    {{rTop:.068,rBot:.090}},  // 8  LHip→LKnee
    {{rTop:.040,rBot:.068}},  // 9  LKnee→LAnkle
    {{rTop:.016,rBot:.040}},  // 10 LAnkle→LToe
    // RIGHT LEG
    {{rTop:.068,rBot:.090}},  // 11 RHip→RKnee
    {{rTop:.040,rBot:.068}},  // 12 RKnee→RAnkle
    {{rTop:.016,rBot:.040}},  // 13 RAnkle→RToe
    // LEFT ARM
    {{rTop:.052,rBot:.076}},  // 14 LShoulder→LElbow
    {{rTop:.028,rBot:.052}},  // 15 LElbow→LWrist
    {{rTop:.018,rBot:.028}},  // 16 LWrist→LHand
    // RIGHT ARM
    {{rTop:.052,rBot:.076}},  // 17 RShoulder→RElbow
    {{rTop:.028,rBot:.052}},  // 18 RElbow→RWrist
    {{rTop:.018,rBot:.028}},  // 19 RWrist→RHand
  ],
  // Raios das esferas de articulação — índice paralelo ao JSPH_TOPO (14 entradas)
  jsph: [.090,.076,.076,.052,.052,.028,.028,.090,.090,.068,.068,.040,.040,.040],
  // Cabeça
  head: {{r:0.128}},
  // Cabelo
  hair: {{r:0.131, capFraction:0.52, color:0x110c06, roughness:0.85}},
  // Cinto
  belt: {{torusR:0.108, tubeR:0.014, knotW:0.05, knotH:0.045, knotD:0.065, knotOffset:0.12}},
  // Materiais
  mat: {{
    gi:     {{roughness:0.90, metalness:0}},
    sleeve: {{roughness:0.88, metalness:0}},
    leg:    {{roughness:0.88, metalness:0}},
    skin:   {{roughness:0.50, metalness:0, color:0xC68642}},
    belt:   {{roughness:0.60, metalness:0.05}},
    hair:   {{roughness:0.85, metalness:0}},
  }},
  // Resolução geométrica
  geo: {{cylSegs:16, sphW:14, sphH:12, headW:18, headH:14}},
  // Iluminação
  lights: {{
    ambCol:0x8898bb, ambInt:1.2,
    keyCol:0xfff5e0, keyInt:2.2, keyPos:[3,7,4],
    fillCol:0x5070c0, fillInt:0.8, fillPos:[-4,3,-3],
    rimCol:0xffffff, rimInt:0.5,  rimPos:[0,-2,-5],
  }},
  // Parâmetros base da geometria procedural do tronco
  trunk: {{
    baseChestDepth:0.22, baseWaistDepth:0.15, basePelvisDepth:0.19, baseRoundness:2.5,
  }},
  // Parâmetros base dos pés procedurais
  foot: {{
    baseWidth:0.058,      // meia-largura lateral no metatarso
    baseThickness:0.036,  // meia-altura vertical no calcanhar
    baseRoundness:1.7,    // expoente base da superelipse
  }},
  // Parâmetros base das mãos procedurais
  hand: {{
    basePalmWidth:0.042,      // meia-largura lateral da palma
    basePalmThick:0.015,      // meia-espessura dorso-palmar
    baseRoundness:3.2,        // expoente alto = seção achatada/retangular
    baseThumbLenScale:1.0,    // escala do comprimento do polegar vs palma
  }},
}};

// Experimental — inicialmente idêntico; modifique aqui nos próximos blocos
const STYLE_EXP = JSON.parse(JSON.stringify(STYLE_ORIG));

let BODY_STYLE = STYLE_ORIG;

const CAT_COLORS = {{
  "Finalização":"#C0392B","Queda":"#8E44AD","Passagem":"#2980B9",
  "Raspagem":"#27AE60","Escape":"#F39C12","Em Pé":"#16A085",
  "Guarda":"#2471A3","Posição Dominante":"#922B21","Outro":"#717D7E",
}};

// ── Scene ─────────────────────────────────────────────────────────────────────
const canvas  = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({{ canvas, antialias:true }});
renderer.setPixelRatio(devicePixelRatio);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d1117);
scene.fog = new THREE.Fog(0x0d1117, 8, 18);

const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 30);
camera.position.set(0, 1.6, 3.8);

const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 0.8, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 0.5;
controls.maxDistance = 10;
controls.update();

// Lights — parâmetros centralizados em STYLE_ORIG.lights
const _li = STYLE_ORIG.lights;
scene.add(new THREE.AmbientLight(_li.ambCol, _li.ambInt));
const key = new THREE.DirectionalLight(_li.keyCol, _li.keyInt);
key.position.set(..._li.keyPos);
key.castShadow = true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.near = 0.1;
key.shadow.camera.far  = 20;
key.shadow.camera.top  = 4;
key.shadow.camera.bottom = -1;
key.shadow.camera.left = -4;
key.shadow.camera.right = 4;
scene.add(key);
const fill = new THREE.DirectionalLight(_li.fillCol, _li.fillInt);
fill.position.set(..._li.fillPos);
scene.add(fill);
const rim = new THREE.DirectionalLight(_li.rimCol, _li.rimInt);
rim.position.set(..._li.rimPos);
scene.add(rim);

// ── Tatame IBJJF ──────────────────────────────────────────────────────────────
const MAT_CFG = {{
  totalSize:   10,   // tapete total (zona de segurança inclusa)
  combatSize:   8,   // área de combate central
  safetyBorder: 1,   // largura da borda de segurança
  combatColor: 0x3373bc,
  safetyColor: 0xecc14b,
}};

// Zona de segurança amarela — 10×10m
const _matOuter = new THREE.Mesh(
  new THREE.PlaneGeometry(MAT_CFG.totalSize, MAT_CFG.totalSize),
  new THREE.MeshStandardMaterial({{ color: MAT_CFG.safetyColor, roughness: 0.88, metalness: 0 }})
);
_matOuter.rotation.x = -Math.PI / 2;
_matOuter.receiveShadow = true;
scene.add(_matOuter);

// Zona de combate azul — 8×8m
const _matInner = new THREE.Mesh(
  new THREE.PlaneGeometry(MAT_CFG.combatSize, MAT_CFG.combatSize),
  new THREE.MeshStandardMaterial({{ color: MAT_CFG.combatColor, roughness: 0.88, metalness: 0 }})
);
_matInner.rotation.x = -Math.PI / 2;
_matInner.position.y = 0.001;
_matInner.receiveShadow = true;
scene.add(_matInner);


// ── Gi fabric texture ─────────────────────────────────────────────────────────
function buildGiTexture(hexColor) {{
  const s = 256;
  const cv = document.createElement('canvas');
  cv.width = cv.height = s;
  const ctx = cv.getContext('2d');
  const r = (hexColor >> 16) & 0xff, g = (hexColor >> 8) & 0xff, b = hexColor & 0xff;
  ctx.fillStyle = `rgb(${{r}},${{g}},${{b}})`;
  ctx.fillRect(0,0,s,s);
  // Pearl-weave pattern (BJJ gi texture)
  const cell = 5;
  for (let x=0; x<s; x+=cell) {{
    for (let y=0; y<s; y+=cell) {{
      const even = ((x/cell + y/cell) % 2 === 0);
      ctx.fillStyle = even ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)';
      ctx.fillRect(x,y,cell,cell);
    }}
  }}
  // Horizontal weft lines
  ctx.strokeStyle = 'rgba(0,0,0,0.05)';
  ctx.lineWidth = 1;
  for (let y=0; y<s; y+=cell*2) {{ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(s,y); ctx.stroke(); }}
  const tex = new THREE.CanvasTexture(cv);
  tex.repeat.set(10,10);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}}

// ── TrunkSurface — geometria procedural do tronco ────────────────────────────
// Duas seções independentes: tórax (Core→ombros) e pelve (quadril→Core).
// Cada seção usa sua própria base ortonormal, permitindo rotações independentes.
const _TR_N  = 10; // segmentos radiais por anel
const _TR_RS = 3;  // anéis por seção

function _makeTrunkSection(mat) {{
  const nV     = _TR_N * _TR_RS;
  const posArr = new Float32Array(nV * 3);
  const uvArr  = new Float32Array(nV * 2);
  const geo    = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
  geo.setAttribute('uv',       new THREE.BufferAttribute(uvArr,  2));
  const idx = [];
  for (let ri = 0; ri < _TR_RS - 1; ri++) {{
    for (let j = 0; j < _TR_N; j++) {{
      const a = ri*_TR_N + j;
      const b = ri*_TR_N + (j+1) % _TR_N;
      const c = (ri+1)*_TR_N + (j+1) % _TR_N;
      const d = (ri+1)*_TR_N + j;
      idx.push(a, d, b, b, d, c);
    }}
  }}
  geo.setIndex(idx);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  return mesh;
}}

class TrunkSurface {{
  constructor(material) {{
    this.mat        = material;
    // Duas malhas independentes, compartilham o mesmo material
    this.chestMesh  = _makeTrunkSection(material);
    this.pelvisMesh = _makeTrunkSection(material);
  }}

  update(pts, cfg) {{
    const LS = pts[10], RS = pts[11];
    const LH = pts[8],  RH = pts[9];
    const core = pts[20], neck = pts[21];

    const midHip = new THREE.Vector3().addVectors(LH, RH).multiplyScalar(0.5);
    const midSh  = new THREE.Vector3().addVectors(LS, RS).multiplyScalar(0.5);

    const st  = STYLE_ORIG.trunk;
    const pow = Math.max(0.5, st.baseRoundness * cfg.roundness);

    // Larguras dos joints reais × multiplicadores
    const chestW  = RS.distanceTo(LS) * 0.5 * cfg.chestWidth;
    const pelvisW = RH.distanceTo(LH) * 0.5 * cfg.pelvisWidth;
    const waistW   = (chestW + pelvisW) * 0.36 * cfg.waistWidth;
    const waistD   = st.baseWaistDepth  * cfg.waistDepth;
    const abdomenW = (chestW + pelvisW) * 0.36 * cfg.abdomenWidth;
    const abdomenD = st.baseWaistDepth  * cfg.abdomenDepth;

    // ── Tórax — frame derivado de LS/RS + Core→Neck ──────────────────────────
    // Rotação do tórax segue o eixo LS↔RS e a direção Core→Neck
    const rC  = new THREE.Vector3().subVectors(RS, LS).normalize();
    const uC  = new THREE.Vector3().subVectors(neck, core).normalize();
    const fC  = new THREE.Vector3().crossVectors(rC, uC).normalize();
    const r2C = new THREE.Vector3().crossVectors(uC, fC).normalize(); // re-ortogonalizado

    const chestD = st.baseChestDepth * cfg.chestDepth;
    const mid24C = new THREE.Vector3().lerpVectors(core, midSh, 0.5);

    this._fillSection([
      {{ ctr: core.clone(),  hw: waistW,              hd: waistD }},
      {{ ctr: mid24C,        hw: (waistW+chestW)*0.5, hd: (waistD+chestD)*0.5 }},
      {{ ctr: midSh.clone(), hw: chestW,              hd: chestD }},
    ], r2C, fC, pow, this.chestMesh);

    // ── Pelve — frame derivado de LH/RH + midHip→Core ────────────────────────
    // Rotação da pelve segue o eixo LH↔RH e a direção midHip→Core
    const rP  = new THREE.Vector3().subVectors(RH, LH).normalize();
    const uP  = new THREE.Vector3().subVectors(core, midHip).normalize();
    const fP  = new THREE.Vector3().crossVectors(rP, uP).normalize();
    const r2P = new THREE.Vector3().crossVectors(uP, fP).normalize();

    const pelvisD = st.basePelvisDepth * cfg.pelvisDepth;
    const hipBot  = new THREE.Vector3().copy(midHip).addScaledVector(uP, -0.045);

    this._fillSection([
      {{ ctr: hipBot,         hw: pelvisW*0.78, hd: pelvisD*0.78 }},
      {{ ctr: midHip.clone(), hw: pelvisW,      hd: pelvisD }},
      {{ ctr: core.clone(),   hw: abdomenW,     hd: abdomenD }},
    ], r2P, fP, pow, this.pelvisMesh);
  }}

  _fillSection(rings, right2, front, pow, mesh) {{
    const pos = mesh.geometry.attributes.position.array;
    const uv  = mesh.geometry.attributes.uv.array;
    const R   = rings.length;
    for (let ri = 0; ri < R; ri++) {{
      const {{ ctr, hw, hd }} = rings[ri];
      const v = ri / (R - 1);
      for (let j = 0; j < _TR_N; j++) {{
        const angle = (j / _TR_N) * Math.PI * 2;
        const ca = Math.cos(angle), sa = Math.sin(angle);
        const ex = Math.sign(ca) * Math.pow(Math.abs(ca), 2 / pow);
        const ez = Math.sign(sa) * Math.pow(Math.abs(sa), 2 / pow);
        const vi = ri * _TR_N + j;
        pos[vi*3]   = ctr.x + right2.x*ex*hw + front.x*ez*hd;
        pos[vi*3+1] = ctr.y + right2.y*ex*hw + front.y*ez*hd;
        pos[vi*3+2] = ctr.z + right2.z*ex*hw + front.z*ez*hd;
        uv[vi*2]    = j / _TR_N;
        uv[vi*2+1]  = v;
      }}
    }}
    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.attributes.uv.needsUpdate = true;
    mesh.geometry.computeVertexNormals();
  }}

  setTransparent(v) {{
    this.mat.opacity     = v ? 0.50 : 1.0;
    this.mat.transparent = v;
    this.mat.depthWrite  = !v;
  }}

  dispose() {{}} // geometrias dispostas pelo traverse do GrappleBody
}}

// ── FootSurface ───────────────────────────────────────────────────────────────
// Pé procedural derivado de Ankle, Heel e Toe (3 joints por lado).
// 5 anéis superelipse ao longo do eixo Heel→Toe; frame local independente.

const _FT_N  = 16;   // segmentos radiais
const _FT_RS = 5;    // anéis por pé (anel 0 e anel 4 são quase-pontos → fechamento natural)

function _makeFootGeo() {{
  // Sem vértices extras de tampa: anéis 0 e 4 são quase-degenerados
  const nV     = _FT_N * _FT_RS;
  const posArr = new Float32Array(nV * 3);
  const uvArr  = new Float32Array(nV * 2);
  const geo    = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
  geo.setAttribute('uv',       new THREE.BufferAttribute(uvArr,  2));
  const idx = [];
  for (let ri = 0; ri < _FT_RS - 1; ri++) {{
    for (let j = 0; j < _FT_N; j++) {{
      const a = ri*_FT_N + j;
      const b = ri*_FT_N + (j+1) % _FT_N;
      const c = (ri+1)*_FT_N + (j+1) % _FT_N;
      const d = (ri+1)*_FT_N + j;
      idx.push(a, d, b, b, d, c);
    }}
  }}
  geo.setIndex(idx);
  return geo;
}}

class FootSurface {{
  constructor(material) {{
    this.mat = material;
    this.leftMesh  = new THREE.Mesh(_makeFootGeo(), material);
    this.rightMesh = new THREE.Mesh(_makeFootGeo(), material);
    this.leftMesh.castShadow  = true;
    this.rightMesh.castShadow = true;

    // Debug: marcadores de joint (heel=vermelho, ankle=verde, toe=azul)
    //        + eixos locais (fwd=branco, lat=amarelo, up=ciano)
    this._dbgMeshes = [];
    const ptGeo  = new THREE.SphereGeometry(0.014, 6, 4);
    const axGeo  = new THREE.CylinderGeometry(0.004, 0.004, 0.09, 4);
    const ptCols = [0xff3333, 0x33cc44, 0x3399ff];
    const axCols = [0xffffff, 0xffee00, 0x00ffcc];
    for (let f = 0; f < 2; f++) {{
      ptCols.forEach(c => {{
        const m = new THREE.Mesh(ptGeo, new THREE.MeshBasicMaterial({{ color:c }}));
        m.visible = false; this._dbgMeshes.push(m);
      }});
      axCols.forEach(c => {{
        const m = new THREE.Mesh(axGeo, new THREE.MeshBasicMaterial({{ color:c }}));
        m.visible = false; this._dbgMeshes.push(m);
      }});
    }}
  }}

  update(pts, cfg) {{
    // Esquerdo: Heel=2, Ankle=4, Toe=0
    this._fillFoot(pts[4], pts[2], pts[0], cfg, this.leftMesh,  0);
    // Direito:  Heel=3, Ankle=5, Toe=1
    this._fillFoot(pts[5], pts[3], pts[1], cfg, this.rightMesh, 6);
  }}

  _fillFoot(ankle, heel, toe, cfg, mesh, dbgOff) {{
    const st = STYLE_ORIG.foot;

    // Frame local: eixo longitudinal = Toe-Heel; eixo lateral por produto vetorial
    const fwd = new THREE.Vector3().subVectors(toe,   heel).normalize();
    const tmp = new THREE.Vector3().subVectors(ankle, heel).normalize();
    const lat = new THREE.Vector3().crossVectors(tmp, fwd).normalize();
    const up  = new THREE.Vector3().crossVectors(fwd, lat).normalize();

    const bW = st.baseWidth;
    const bT = st.baseThickness;

    const heelW = bW * cfg.heelWidth * cfg.footWidth;
    const ballW = bW * cfg.toeWidth  * cfg.footWidth * 1.28;
    const toeW  = bW * cfg.toeWidth  * cfg.footWidth;
    const midW  = (heelW + ballW) * 0.46;
    const heelT = bT * cfg.soleThickness;
    const toeT  = bT * cfg.soleThickness * 0.52;
    const instH = bT * cfg.instepHeight  * 0.90;
    const powH  = Math.max(0.5, st.baseRoundness * cfg.heelRoundness);
    const powT  = Math.max(0.5, st.baseRoundness * cfg.toeRoundness);
    const powM  = (powH + powT) * 0.5;

    // heelProjection desloca o calcanhar para trás do joint Heel
    // (0 = exatamente no joint; valores maiores = mais projeção)
    // heelProjection desloca o extremo posterior para trás do joint Heel
    const heelProj  = 0.020 * cfg.heelProjection;
    const footLen   = heel.distanceTo(toe);
    const tipRadius = Math.min(bW, bT) * 0.022; // raio quase-zero para fechamento natural

    // 5 anéis: extremo-calcanhar (quase-ponto) → sola-calcanhar → arco → metatarso → dedos (quase-ponto)
    // Anéis 0 e 4 são quase-degenerados: a superfície que converge para eles
    // cria o arredondamento (sola→trás no calcanhar; frente dos dedos).
    const rings = [
      // 0 — Extremo posterior do calcanhar (quase-ponto)
      //     heelProjection=0 → ponto no joint Heel; cresce → projeta para trás
      {{ ctr: heel.clone().addScaledVector(fwd, -heelProj),
         hw: tipRadius, hd: tipRadius, pow: powH }},
      // 1 — Corpo do calcanhar: sola + lateral completa
      //     ligeiramente à frente e abaixo do joint para curvar sola→trás
      {{ ctr: heel.clone().addScaledVector(fwd, footLen*0.07).addScaledVector(up, -heelT*0.20),
         hw: heelW, hd: heelT*0.78, pow: powH }},
      // 2 — Arco plantar / peito do pé
      {{ ctr: new THREE.Vector3().lerpVectors(heel, toe, 0.38).addScaledVector(up, instH),
         hw: midW,  hd: (heelT+toeT)*0.55, pow: powM }},
      // 3 — Metatarso (mais largo)
      {{ ctr: new THREE.Vector3().lerpVectors(heel, toe, 0.72).addScaledVector(up, instH*0.28),
         hw: ballW, hd: heelT*0.72, pow: powT }},
      // 4 — Extremo dos dedos (quase-ponto)
      {{ ctr: toe.clone().addScaledVector(up, -bT*0.10),
         hw: tipRadius, hd: tipRadius, pow: powT }},
    ];

    const pos = mesh.geometry.attributes.position.array;
    const uv  = mesh.geometry.attributes.uv.array;

    for (let ri = 0; ri < _FT_RS; ri++) {{
      const {{ ctr, hw, hd, pow }} = rings[ri];
      const v = ri / (_FT_RS - 1);
      for (let j = 0; j < _FT_N; j++) {{
        const angle = (j / _FT_N) * Math.PI * 2;
        const ca = Math.cos(angle), sa = Math.sin(angle);
        const ex = Math.sign(ca) * Math.pow(Math.abs(ca), 2 / pow);
        // Sola mais plana (abaixo), dorso levemente mais arredondado (acima)
        const vPow = sa > 0 ? pow * 0.82 : pow * 1.55;
        const ey   = Math.sign(sa) * Math.pow(Math.abs(sa), 2 / vPow);
        const vi = ri * _FT_N + j;
        pos[vi*3]   = ctr.x + lat.x*ex*hw + up.x*ey*hd;
        pos[vi*3+1] = ctr.y + lat.y*ex*hw + up.y*ey*hd;
        pos[vi*3+2] = ctr.z + lat.z*ex*hw + up.z*ey*hd;
        uv[vi*2]    = j / _FT_N;
        uv[vi*2+1]  = v;
      }}
    }}

    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.attributes.uv.needsUpdate       = true;
    mesh.geometry.computeVertexNormals();

    // Marcadores de debug
    if (this._dbgMeshes[dbgOff].visible) {{
      this._dbgMeshes[dbgOff    ].position.copy(heel);   // vermelho = Heel
      this._dbgMeshes[dbgOff + 1].position.copy(ankle);  // verde    = Ankle
      this._dbgMeshes[dbgOff + 2].position.copy(toe);    // azul     = Toe
      const _Y   = new THREE.Vector3(0,1,0);
      const orig = heel.clone().addScaledVector(up, bT*0.5);
      [fwd, lat, up].forEach((ax, ai) => {{
        const am = this._dbgMeshes[dbgOff + 3 + ai];
        am.position.copy(orig).addScaledVector(ax, 0.045);
        am.quaternion.setFromUnitVectors(_Y, ax.clone().normalize());
      }});
    }}
  }}

  setDebug(v)  {{ this._dbgMeshes.forEach(m => {{ m.visible = v; }}); }}

  setTransparent(v) {{
    this.mat.opacity     = v ? 0.50 : 1.0;
    this.mat.transparent = v;
    this.mat.depthWrite  = !v;
  }}

  dispose() {{ this._dbgMeshes.forEach(m => m.material.dispose()); }}
}}

// ── HandSurface ───────────────────────────────────────────────────────────────
// Mão procedural com frame local estável derivado de Elbow + Wrist + Hand + Fingers.
// Convenção separada por lado para o polegar estar sempre no lado correto.
// Temporal smoothing via sign-consistency + lerp previne flips abruptos entre frames.

const _HND_N  = 12;  // segmentos radiais
const _HND_RS = 3;   // anéis por seção (anel 0=quase-ponto → fechamento natural)

function _makeHandSecGeo() {{
  const nV     = _HND_N * _HND_RS;
  const posArr = new Float32Array(nV * 3);
  const uvArr  = new Float32Array(nV * 2);
  const geo    = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
  geo.setAttribute('uv',       new THREE.BufferAttribute(uvArr,  2));
  const idx = [];
  for (let ri = 0; ri < _HND_RS - 1; ri++) {{
    for (let j = 0; j < _HND_N; j++) {{
      const a = ri*_HND_N + j;
      const b = ri*_HND_N + (j+1) % _HND_N;
      const c = (ri+1)*_HND_N + (j+1) % _HND_N;
      const d = (ri+1)*_HND_N + j;
      idx.push(a, d, b, b, d, c);
    }}
  }}
  geo.setIndex(idx);
  return geo;
}}

class HandSurface {{
  constructor(material) {{
    this.mat = material;
    this.lPalmMesh = new THREE.Mesh(_makeHandSecGeo(), material);
    this.rPalmMesh = new THREE.Mesh(_makeHandSecGeo(), material);
    this.lFingMesh = new THREE.Mesh(_makeHandSecGeo(), material);
    this.rFingMesh = new THREE.Mesh(_makeHandSecGeo(), material);
    const tGeo = new THREE.CylinderGeometry(0.60, 1.0, 1, 8, 1);
    this.lThumbMesh = new THREE.Mesh(tGeo, material);
    this.rThumbMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.60, 1.0, 1, 8, 1), material);
    [this.lPalmMesh, this.rPalmMesh, this.lFingMesh, this.rFingMesh,
     this.lThumbMesh, this.rThumbMesh].forEach(m => {{ m.castShadow = true; }});

    // Debug pts: Wrist=laranja, Hand=roxo, Fingers=amarelo, Elbow=ciano (×2 mãos = 8)
    this._dbgMeshes = [];
    const ptGeo = new THREE.SphereGeometry(0.014, 6, 4);
    [0xff7700,0xcc44ff,0xffee00,0x00ccff, 0xff7700,0xcc44ff,0xffee00,0x00ccff].forEach(c => {{
      const m = new THREE.Mesh(ptGeo, new THREE.MeshBasicMaterial({{ color:c }}));
      m.visible = false; this._dbgMeshes.push(m);
    }});

    // Debug axes: fingerDir=vermelho, palmNormal=verde, thumbAxis=azul (×2 mãos = 6 arrows)
    this._axesMeshes = [];
    const _AX_LEN = 0.09;
    [0xff2222,0x22cc22,0x3366ff, 0xff2222,0x22cc22,0x3366ff].forEach(c => {{
      const arr = new THREE.ArrowHelper(
        new THREE.Vector3(1,0,0), new THREE.Vector3(0,0,0),
        _AX_LEN, c, _AX_LEN*0.28, _AX_LEN*0.18);
      arr.visible = false; this._axesMeshes.push(arr);
    }});

    // Temporal smoothing: palmNormal do frame anterior por lado
    this._prevNormL = null;
    this._prevNormR = null;
  }}

  update(pts, cfg) {{
    // Esquerda: Elbow=12, Wrist=14, Hand=16, Fingers=18
    // Contexto de corpo: lShoulder=10, rShoulder=11, Core=20, Neck=21
    this._build(pts[12], pts[14], pts[16], pts[18],
                pts[10], pts[11], pts[20], pts[21],
                cfg, true,
                this.lPalmMesh, this.lFingMesh, this.lThumbMesh, 0);
    // Direita: Elbow=13, Wrist=15, Hand=17, Fingers=19
    this._build(pts[13], pts[15], pts[17], pts[19],
                pts[10], pts[11], pts[20], pts[21],
                cfg, false,
                this.rPalmMesh, this.rFingMesh, this.rThumbMesh, 4);
  }}

  _build(elbow, wrist, hand, fingers,
         lShoulder, rShoulder, core, neck,
         cfg, isLeft,
         palmMesh, fingMesh, thumbMesh, dbgOff) {{
    const st      = STYLE_ORIG.hand;
    const palmLen = wrist.distanceTo(hand);
    if (palmLen < 0.001) {{
      palmMesh.visible = false; fingMesh.visible = false; thumbMesh.visible = false; return;
    }}
    palmMesh.visible = true; fingMesh.visible = true;

    // ── Eixos primários ──────────────────────────────────────────────────────
    // fingerDir: direção principal dos dedos (Hand→Fingers)
    const fingerDir  = new THREE.Vector3().subVectors(fingers, hand).normalize();
    // forearmDir: direção do antebraço (Elbow→Wrist)
    const forearmDir = new THREE.Vector3().subVectors(wrist, elbow).normalize();

    // ── palmNormal: normal ao plano antebraço×dedos ─────────────────────────
    // Convenção oposta por mão: right = cross(forearm, finger); left = cross(finger, forearm)
    // Isso garante que o polegar fique no lado correto anatomicamente para ambos os lados.
    let palmNormal = isLeft
      ? new THREE.Vector3().crossVectors(fingerDir, forearmDir)
      : new THREE.Vector3().crossVectors(forearmDir, fingerDir);

    // Fallback 1: cross produto degenerado (braço reto) → usa eixo ombro→ombro
    if (palmNormal.lengthSq() < 0.004) {{
      // Para mão esquerda: aponta do ombro esquerdo para direito; para direita: invertido
      const shoulderRef = isLeft
        ? new THREE.Vector3().subVectors(rShoulder, lShoulder).normalize()
        : new THREE.Vector3().subVectors(lShoulder, rShoulder).normalize();
      palmNormal.crossVectors(shoulderRef, fingerDir);
    }}
    // Fallback 2: coluna Core→Neck
    if (palmNormal.lengthSq() < 0.004) {{
      const spineUp = new THREE.Vector3().subVectors(neck, core).normalize();
      palmNormal.crossVectors(spineUp, fingerDir);
    }}
    // Fallback 3: mundo Y
    if (palmNormal.lengthSq() < 0.004) {{
      palmNormal.crossVectors(new THREE.Vector3(0,1,0), fingerDir);
    }}
    // Fallback 4: mundo X (último recurso)
    if (palmNormal.lengthSq() < 0.004) palmNormal.set(isLeft ? -1 : 1, 0, 0);
    palmNormal.normalize();

    // ── Temporal smoothing ───────────────────────────────────────────────────
    // Armazena palmNormal canônico (sem flip) para evitar flips abruptos.
    // O flip do usuário é aplicado DEPOIS do smoothing.
    const prevNorm = isLeft ? this._prevNormL : this._prevNormR;
    if (prevNorm) {{
      // Sign consistency: garante mesma orientação do frame anterior
      if (prevNorm.dot(palmNormal) < 0) palmNormal.negate();
      // Lerp: 70% novo + 30% anterior (suaviza oscilações rápidas)
      palmNormal.lerp(prevNorm, 0.30).normalize();
    }}
    if (isLeft) this._prevNormL = palmNormal.clone();
    else        this._prevNormR = palmNormal.clone();

    // ── Flip manual (aplicado depois do smoothing) ───────────────────────────
    const flip = isLeft ? (cfg.flipL || false) : (cfg.flipR || false);
    if (flip) palmNormal.negate();

    // ── Eixo do polegar (lateral) ─────────────────────────────────────────────
    // thumbAxis = cross(palmNormal, fingerDir) completa o frame ortogonal
    let thumbAxis = new THREE.Vector3().crossVectors(palmNormal, fingerDir).normalize();

    // ── Twist offset ─────────────────────────────────────────────────────────
    // Rotação extra em torno de fingerDir, configurável por mão
    const twistDeg = isLeft ? (cfg.twistL || 0) : (cfg.twistR || 0);
    if (Math.abs(twistDeg) > 0.5) {{
      const qTwist = new THREE.Quaternion().setFromAxisAngle(fingerDir, twistDeg * Math.PI / 180);
      palmNormal.applyQuaternion(qTwist).normalize();
      thumbAxis.applyQuaternion(qTwist).normalize();
    }}

    // ── Dimensões ──────────────────────────────────────────────────────────
    const bW   = st.basePalmWidth  * cfg.palmWidth;
    const bT   = st.basePalmThick  * cfg.palmThickness;
    const bFW  = st.basePalmWidth  * cfg.fingerWidth;
    const bFT  = st.basePalmThick  * cfg.fingerThickness;
    const pow  = Math.max(0.5, st.baseRoundness * cfg.handRoundness);
    const powF = Math.max(0.5, st.baseRoundness * 0.62 * cfg.handRoundness);
    const tip  = Math.min(bW, bT) * 0.024;
    const midT = Math.min(0.90, Math.max(0.15, cfg.palmLengthScale * 0.50));
    // fingerDir é o eixo longo da palma (de Wrist até os dedos)
    const palmFwd = new THREE.Vector3().subVectors(hand, wrist).normalize();

    // ── Palma (Wrist→Hand) ───────────────────────────────────────────────────
    this._fillSec([
      {{ ctr: wrist.clone(),
         hw: tip,       hd: tip,         pow }},
      {{ ctr: new THREE.Vector3().lerpVectors(wrist, hand, midT),
         hw: bW,        hd: bT,          pow }},
      {{ ctr: hand.clone(),
         hw: bW * 0.88, hd: bT * 0.90,  pow }},
    ], thumbAxis, palmNormal, palmMesh);

    // ── Bloco de dedos (Hand→Fingers) ───────────────────────────────────────
    this._fillSec([
      {{ ctr: hand.clone(),
         hw: bFW * 0.90, hd: bFT,          pow: powF }},
      {{ ctr: new THREE.Vector3().lerpVectors(hand, fingers, 0.50),
         hw: bFW * 0.78, hd: bFT * 0.82,  pow: powF }},
      {{ ctr: fingers.clone(),
         hw: tip * 0.8,  hd: tip * 0.8,   pow: powF }},
    ], thumbAxis, palmNormal, fingMesh);

    // ── Polegar ──────────────────────────────────────────────────────────────
    if (cfg.thumbSize > 0.01) {{
      thumbMesh.visible = true;
      const tLen  = palmLen * 0.46 * cfg.thumbSize * st.baseThumbLenScale;
      const tR    = bW * 0.32 * cfg.thumbSize;
      // Base do polegar: lado +thumbAxis da palma
      const tBase = new THREE.Vector3()
        .lerpVectors(wrist, hand, cfg.thumbOffset)
        .addScaledVector(thumbAxis, bW * 0.88);
      // Direção: diverge ligeiramente de thumbAxis em direção aos dedos
      const tDir = new THREE.Vector3().copy(thumbAxis).addScaledVector(palmFwd, 0.48).normalize();
      thumbMesh.scale.set(tR, tLen, tR);
      thumbMesh.position.copy(tBase).addScaledVector(tDir, tLen * 0.5);
      const _Y = new THREE.Vector3(0,1,0);
      if (Math.abs(tDir.dot(_Y)) < 0.9995) thumbMesh.quaternion.setFromUnitVectors(_Y, tDir);
    }} else {{
      thumbMesh.visible = false;
    }}

    // ── Debug: marcadores de joints ────────────────────────────────────────
    if (this._dbgMeshes[dbgOff].visible) {{
      this._dbgMeshes[dbgOff    ].position.copy(wrist);
      this._dbgMeshes[dbgOff + 1].position.copy(hand);
      this._dbgMeshes[dbgOff + 2].position.copy(fingers);
      this._dbgMeshes[dbgOff + 3].position.copy(elbow);
    }}

    // ── Debug: eixos locais da mão ─────────────────────────────────────────
    const axOff = isLeft ? 0 : 3;
    if (this._axesMeshes[axOff].visible) {{
      const origin = hand.clone();
      // vermelho = fingerDir, verde = palmNormal (sem flip nem twist), azul = thumbAxis (com flip/twist)
      this._axesMeshes[axOff    ].position.copy(origin); this._axesMeshes[axOff    ].setDirection(fingerDir);
      this._axesMeshes[axOff + 1].position.copy(origin); this._axesMeshes[axOff + 1].setDirection(palmNormal);
      this._axesMeshes[axOff + 2].position.copy(origin); this._axesMeshes[axOff + 2].setDirection(thumbAxis);
    }}
  }}

  _fillSec(rings, lat, norm, mesh) {{
    const pos = mesh.geometry.attributes.position.array;
    const uv  = mesh.geometry.attributes.uv.array;
    const R   = rings.length;
    for (let ri = 0; ri < R; ri++) {{
      const {{ ctr, hw, hd, pow }} = rings[ri];
      const v = ri / (R - 1);
      for (let j = 0; j < _HND_N; j++) {{
        const angle = (j / _HND_N) * Math.PI * 2;
        const ca = Math.cos(angle), sa = Math.sin(angle);
        const ex = Math.sign(ca) * Math.pow(Math.abs(ca), 2 / pow);
        const ey = Math.sign(sa) * Math.pow(Math.abs(sa), 2 / pow);
        const vi = ri * _HND_N + j;
        pos[vi*3]   = ctr.x + lat.x*ex*hw + norm.x*ey*hd;
        pos[vi*3+1] = ctr.y + lat.y*ex*hw + norm.y*ey*hd;
        pos[vi*3+2] = ctr.z + lat.z*ex*hw + norm.z*ey*hd;
        uv[vi*2]    = j / _HND_N;
        uv[vi*2+1]  = v;
      }}
    }}
    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.attributes.uv.needsUpdate       = true;
    mesh.geometry.computeVertexNormals();
  }}

  setDebug(v)    {{ this._dbgMeshes.forEach(m => {{ m.visible = v; }}); }}
  setHandAxes(v) {{ this._axesMeshes.forEach(m => {{ m.visible = v; }}); }}

  setTransparent(v) {{
    this.mat.opacity     = v ? 0.50 : 1.0;
    this.mat.transparent = v;
    this.mat.depthWrite  = !v;
  }}

  dispose() {{
    this._dbgMeshes.forEach(m => m.material.dispose());
    this._axesMeshes.forEach(m => m.traverse(o => {{
      if (o.geometry) o.geometry.dispose();
      if (o.material) o.material.dispose();
    }}));
  }}
}}

// ── HeadSurface ───────────────────────────────────────────────────────────────
// Cabeça mannequin estilizada: crânio + mandíbula + nariz + orelhas + cabelo.
// Frame local: headUp = Neck→Head, headLat = linha ombros ⊥ headUp, headFwd = cross(lat,up).
// Todos os meshes usam esferas unitárias escaladas para elipsoides — nenhuma geometria
// é recriada por frame; apenas position, quaternion e scale são atualizados.

class HeadSurface {{
  constructor(skinMat, hairMat) {{
    // Crânio: elipsoide principal
    this.craniumMesh = new THREE.Mesh(new THREE.SphereGeometry(1, 22, 16), skinMat);
    // Mandíbula: elipsoide menor abaixo do crânio
    this.jawMesh     = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), skinMat);
    // Nariz: pequeno elipsoide projetando-se da face frontal
    this.noseMesh    = new THREE.Mesh(new THREE.SphereGeometry(1,  8,  6), skinMat);
    // Orelhas: elipsoides achatados nas laterais
    this.lEarMesh    = new THREE.Mesh(new THREE.SphereGeometry(1, 10,  8), skinMat);
    this.rEarMesh    = new THREE.Mesh(new THREE.SphereGeometry(1, 10,  8), skinMat);
    // Cabelo: calota esférica (open bottom = -Y da esfera unitária → -headUp após rotação)
    this.hairMesh    = new THREE.Mesh(
      new THREE.SphereGeometry(1, 20, 14, 0, Math.PI*2, 0, Math.PI*0.62), hairMat);

    this.skinMeshes = [this.craniumMesh, this.jawMesh, this.noseMesh,
                       this.lEarMesh, this.rEarMesh];
    this.skinMeshes.forEach(m => m.castShadow = true);
    this.hairMesh.castShadow = true;
  }}

  update(pts, cfg) {{
    const neck = pts[21], head = pts[22];

    // ── Frame local da cabeça ─────────────────────────────────────────────────
    const headUp = new THREE.Vector3().subVectors(head, neck);
    if (headUp.lengthSq() < 1e-6) return;
    headUp.normalize();

    // Lateral: linha ombro → ombro direito projetada ⊥ headUp
    const shoulderR = new THREE.Vector3().subVectors(pts[11], pts[10]).normalize();
    let headLat = new THREE.Vector3().copy(shoulderR)
      .addScaledVector(headUp, -shoulderR.dot(headUp));
    if (headLat.lengthSq() < 0.01) {{
      // Fallback: linha do quadril
      const hipR = new THREE.Vector3().subVectors(pts[9], pts[8]).normalize();
      headLat.copy(hipR).addScaledVector(headUp, -hipR.dot(headUp));
    }}
    if (headLat.lengthSq() < 0.01) {{
      // Fallback final: eixo X do mundo
      headLat.set(1, 0, 0).addScaledVector(headUp, -headUp.x);
    }}
    headLat.normalize();

    // Frente da face: cross(lateral, up)
    const headFwd = new THREE.Vector3().crossVectors(headLat, headUp).normalize();

    // Quaternion: X=headLat, Y=headUp, Z=headFwd
    const qHead = new THREE.Quaternion().setFromRotationMatrix(
      new THREE.Matrix4().makeBasis(headLat, headUp, headFwd));

    // ── Dimensões (semi-eixos em metros) ──────────────────────────────────────
    const hr  = cfg.r;
    const crW = hr * 0.88 * cfg.headWidth;   // lateral
    const crH = hr * 0.90 * cfg.headHeight;  // vertical
    const crD = hr * 0.76 * cfg.headDepth;   // frente-trás

    // ── Crânio ────────────────────────────────────────────────────────────────
    const craniumCtr = head.clone().addScaledVector(headUp, 0.02 * hr);
    this.craniumMesh.position.copy(craniumCtr);
    this.craniumMesh.quaternion.copy(qHead);
    this.craniumMesh.scale.set(crW, crH, crD);

    // ── Mandíbula ─────────────────────────────────────────────────────────────
    // Levemente mais estreita, mais curta e projetada para frente (queixo)
    const jawW = hr * 0.64 * cfg.jawWidth;
    const jawH = hr * 0.28 * cfg.jawLength;
    const jawD = hr * 0.62 * cfg.headDepth;
    const jawCtr = craniumCtr.clone()
      .addScaledVector(headUp,  -(crH * 0.68 + jawH * 0.52))
      .addScaledVector(headFwd,   0.055 * hr);
    this.jawMesh.position.copy(jawCtr);
    this.jawMesh.quaternion.copy(qHead);
    this.jawMesh.scale.set(jawW, jawH, jawD);

    // ── Nariz ─────────────────────────────────────────────────────────────────
    const nR   = hr * 0.062;
    const nLen = hr * 0.095 * cfg.noseLength;
    // Posicionado na face frontal do crânio, ligeiramente abaixo do centro
    const noseCtr = craniumCtr.clone()
      .addScaledVector(headFwd, crD + nLen * 0.5)
      .addScaledVector(headUp,  -0.17 * hr);
    this.noseMesh.position.copy(noseCtr);
    this.noseMesh.quaternion.copy(qHead);
    this.noseMesh.scale.set(nR * 0.82, nR * 0.68, nLen);

    // ── Orelhas ───────────────────────────────────────────────────────────────
    const eH = hr * 0.17 * cfg.earScale;  // altura da orelha
    const eD = hr * 0.13 * cfg.earScale;  // profundidade frente-trás
    const eT = eH * 0.20;                 // espessura lateral (fina)
    const earCtr = craniumCtr.clone().addScaledVector(headUp, -0.06 * hr);
    this.lEarMesh.position.copy(earCtr).addScaledVector(headLat, -(crW + eT * 0.5));
    this.lEarMesh.quaternion.copy(qHead);
    this.lEarMesh.scale.set(eT, eH, eD);
    this.rEarMesh.position.copy(earCtr).addScaledVector(headLat,  (crW + eT * 0.5));
    this.rEarMesh.quaternion.copy(qHead);
    this.rEarMesh.scale.set(eT, eH, eD);

    // ── Cabelo ────────────────────────────────────────────────────────────────
    // Calota ligeiramente maior que o crânio; hairCoverage escala quanto desce
    const hCov = Math.max(0.1, cfg.hairCoverage);
    this.hairMesh.position.copy(craniumCtr);
    this.hairMesh.quaternion.copy(qHead);
    this.hairMesh.scale.set(crW * 1.025, crH * 1.025 * hCov, crD * 1.025);
  }}

  dispose() {{}} // geometrias descartadas pelo traverse do GrappleBody
}}

// ── GrappleBody ───────────────────────────────────────────────────────────────
class GrappleBody {{
  constructor(giColor, beltColor, style) {{
    this.group = new THREE.Group();
    scene.add(this.group);

    // Sub-grupos para toggle de camada (debug)
    this.grpTrunk = new THREE.Group(); this.group.add(this.grpTrunk); // tronco procedural
    this.grpFeet  = new THREE.Group(); this.group.add(this.grpFeet);  // pés procedurais
    this.grpHands = new THREE.Group(); this.group.add(this.grpHands); // mãos procedurais
    this.grpSegs = new THREE.Group(); this.group.add(this.grpSegs);
    this.grpJsph = new THREE.Group(); this.group.add(this.grpJsph);
    this.grpHead = new THREE.Group(); this.group.add(this.grpHead);
    this.grpHair = new THREE.Group(); this.group.add(this.grpHair);
    this.grpBelt = new THREE.Group(); this.group.add(this.grpBelt);

    const giHex   = parseInt(giColor.replace('#',''), 16);
    const beltHex = parseInt(beltColor.replace('#',''), 16);
    const giTex   = buildGiTexture(giHex);
    const sm      = style.mat;

    this.mats = {{
      gi:     new THREE.MeshStandardMaterial({{color:giHex,   map:giTex, roughness:sm.gi.roughness,     metalness:sm.gi.metalness}}),
      sleeve: new THREE.MeshStandardMaterial({{color:giHex,   map:giTex, roughness:sm.sleeve.roughness, metalness:sm.sleeve.metalness}}),
      leg:    new THREE.MeshStandardMaterial({{color:giHex,   map:giTex, roughness:sm.leg.roughness,    metalness:sm.leg.metalness}}),
      skin:   new THREE.MeshStandardMaterial({{color:sm.skin.color,     roughness:sm.skin.roughness,   metalness:sm.skin.metalness}}),
      belt:   new THREE.MeshStandardMaterial({{color:beltHex,           roughness:sm.belt.roughness,   metalness:sm.belt.metalness}}),
    }};

    // Segmentos cônicos — topologia de SEG_TOPO, radii de style.seg
    // CylinderGeometry(rTop, rBot, 1, cylSegs) — scale.y = comprimento real a cada frame
    this.segs = SEG_TOPO.map(([j1,j2,type], i) => {{
      const sr  = style.seg[i];
      const geo = new THREE.CylinderGeometry(sr.rTop, sr.rBot, 1, style.geo.cylSegs, 1);
      const mesh = new THREE.Mesh(geo, this.mats[type] || this.mats.gi);
      mesh.castShadow = true;
      this.grpSegs.add(mesh);
      return {{mesh, j1, j2}};
    }});

    // Esferas de articulação — topologia de JSPH_TOPO, radii de style.jsph
    this.jsphMeshes = JSPH_TOPO.map(([jidx,type], i) => {{
      const geo  = new THREE.SphereGeometry(style.jsph[i], style.geo.sphW, style.geo.sphH);
      const mesh = new THREE.Mesh(geo, this.mats[type] || this.mats.gi);
      mesh.castShadow = true;
      this.grpJsph.add(mesh);
      return {{mesh, jidx}};
    }});

    // Cabeça
    const headGeo = new THREE.SphereGeometry(style.head.r, style.geo.headW, style.geo.headH);
    this.headMesh = new THREE.Mesh(headGeo, this.mats.skin);
    this.headMesh.castShadow = true;
    this.grpHead.add(this.headMesh);

    // Cabelo
    const h = style.hair;
    const hairGeo = new THREE.SphereGeometry(h.r, 18, 10, 0, Math.PI*2, 0, Math.PI*h.capFraction);
    this.hairMesh = new THREE.Mesh(hairGeo, new THREE.MeshStandardMaterial({{color:h.color, roughness:h.roughness}}));
    this.grpHair.add(this.hairMesh);

    // Cinto
    const b = style.belt;
    const beltGeo = new THREE.TorusGeometry(b.torusR, b.tubeR, 8, 28);
    this.beltMesh = new THREE.Mesh(beltGeo, this.mats.belt);
    this.grpBelt.add(this.beltMesh);
    const knotGeo = new THREE.BoxGeometry(b.knotW, b.knotH, b.knotD);
    this.knotMesh = new THREE.Mesh(knotGeo, this.mats.belt);
    this.grpBelt.add(this.knotMesh);

    this._style = style;

    // Material dedicado ao tronco (instância separada para controle de opacidade)
    this.trunkMat = new THREE.MeshStandardMaterial({{
      color:giHex, map:giTex, roughness:sm.gi.roughness, metalness:sm.gi.metalness,
      side:THREE.DoubleSide,
    }});
    // Superfície procedural
    this.trunkSurf = new TrunkSurface(this.trunkMat);
    this.grpTrunk.add(this.trunkSurf.chestMesh);
    this.grpTrunk.add(this.trunkSurf.pelvisMesh);
    // Cilindros fantasma para debug (visíveis quando "Cilin. internos" ativado)
    // SEG_TOPO [0..6] = tronco: Core→LS, Core→RS, Core→LH, Core→RH, LS↔RS, LH↔RH, Core→Neck
    this.trunkDbgCyls = [0,1,2,3,4,5,6].map(i => {{
      const [j1,j2] = SEG_TOPO[i];
      const sr  = style.seg[i];
      const geo = new THREE.CylinderGeometry(sr.rTop*1.04, sr.rBot*1.04, 1, 8, 1);
      const mat = new THREE.MeshStandardMaterial({{
        color:0x3399ee, roughness:0.7, metalness:0.1,
        transparent:true, opacity:0.72, depthWrite:false,
      }});
      const mesh = new THREE.Mesh(geo, mat);
      mesh.visible = false;
      this.grpTrunk.add(mesh);
      return {{mesh, j1, j2}};
    }});
    this.trunkConfig  = null;  // definido via applyProportions
    this._trunkDebug  = false;

    // Pés procedurais
    this.footMat = new THREE.MeshStandardMaterial({{
      color: sm.skin.color, roughness: sm.skin.roughness, metalness: sm.skin.metalness,
      side: THREE.DoubleSide,
    }});
    this.footSurf = new FootSurface(this.footMat);
    this.grpFeet.add(this.footSurf.leftMesh);
    this.grpFeet.add(this.footSurf.rightMesh);
    this.footSurf._dbgMeshes.forEach(m => this.grpFeet.add(m));
    this.footConfig = null;

    // Mãos procedurais
    this.handMat = new THREE.MeshStandardMaterial({{
      color: sm.skin.color, roughness: sm.skin.roughness, metalness: sm.skin.metalness,
      side: THREE.DoubleSide,
    }});
    this.handSurf = new HandSurface(this.handMat);
    this.grpHands.add(this.handSurf.lPalmMesh);
    this.grpHands.add(this.handSurf.rPalmMesh);
    this.grpHands.add(this.handSurf.lFingMesh);
    this.grpHands.add(this.handSurf.rFingMesh);
    this.grpHands.add(this.handSurf.lThumbMesh);
    this.grpHands.add(this.handSurf.rThumbMesh);
    this.handSurf._dbgMeshes.forEach(m => this.grpHands.add(m));
    this.handSurf._axesMeshes.forEach(m => this.grpHands.add(m));
    this.handConfig = null;
  }}

  update(joints) {{
    const pts  = joints.map(([x,y,z]) => new THREE.Vector3(x,y,z));
    const _up  = new THREE.Vector3(0,1,0);
    const _dir = new THREE.Vector3();

    // Posiciona, escala e orienta cada segmento entre seus dois joints
    this.segs.forEach(({{mesh,j1,j2}}) => {{
      const a = pts[j1], b = pts[j2];
      _dir.subVectors(b,a);
      const len = _dir.length();
      if (len < 0.001) {{ mesh.visible=false; return; }}
      mesh.visible = true;
      mesh.scale.set(1, len, 1);
      mesh.position.addVectors(a,b).multiplyScalar(0.5);
      mesh.quaternion.setFromUnitVectors(_up, _dir.normalize());
    }});
    // Oculta segmentos de pé antigos — substituídos pelo FootSurface
    if (this.footSurf) {{
      this.segs[10].mesh.visible = false;  // LAnkle→LToe
      this.segs[13].mesh.visible = false;  // RAnkle→RToe
    }}

    // Posiciona esferas de articulação
    this.jsphMeshes.forEach(({{mesh,jidx}}) => {{ mesh.position.copy(pts[jidx]); }});

    // Cabeça + cabelo
    this.headMesh.position.copy(pts[22]);
    this.hairMesh.position.copy(pts[22]);
    _dir.subVectors(pts[22], pts[21]).normalize();
    if (_dir.lengthSq() > 0.001) this.hairMesh.quaternion.setFromUnitVectors(_up, _dir);

    // Cinto — anel alinhado ao eixo da coluna, nó na face frontal do corpo
    const core     = pts[20];
    const spineDir = new THREE.Vector3().subVectors(pts[21], pts[20]).normalize();
    const hipDir   = new THREE.Vector3().subVectors(pts[9],  pts[8]).normalize();
    const beltFwd  = new THREE.Vector3().crossVectors(spineDir, hipDir).normalize();
    const _Z       = new THREE.Vector3(0,0,1);
    this.beltMesh.position.copy(core);
    this.beltMesh.quaternion.setFromUnitVectors(_Z, spineDir);
    this.knotMesh.position.copy(core).add(beltFwd.clone().multiplyScalar(this._style.belt.knotOffset));
    this.knotMesh.quaternion.setFromUnitVectors(_Z, beltFwd);

    // Tronco procedural
    if (this.trunkSurf && this.trunkConfig) {{
      this.trunkSurf.update(pts, this.trunkConfig);
    }}
    // Pés procedurais
    if (this.footSurf && this.footConfig) {{
      this.footSurf.update(pts, this.footConfig);
    }}
    // Mãos procedurais
    if (this.handSurf) {{
      this.segs[16].mesh.visible = false;  // LWrist→LHand
      this.segs[19].mesh.visible = false;  // RWrist→RHand
    }}
    if (this.handSurf && this.handConfig) {{
      // flipL/flipR são booleanos globais (não persistidos no config)
      const _hcfg = Object.assign({{}}, this.handConfig, {{ flipL: handFlipL, flipR: handFlipR }});
      this.handSurf.update(pts, _hcfg);
    }}
    // Cilindros de debug do tronco — atualizam posição/orientação mesmo quando ocultos
    this.trunkDbgCyls.forEach(({{mesh, j1, j2}}) => {{
      const a = pts[j1], b = pts[j2];
      _dir.subVectors(b, a);
      const len = _dir.length();
      if (len < 0.001) return;
      mesh.scale.set(1, len, 1);
      mesh.position.addVectors(a, b).multiplyScalar(0.5);
      mesh.quaternion.setFromUnitVectors(_up, _dir.normalize());
    }});
  }}

  // Alterna visibilidade de uma camada (para debug)
  setLayer(layer, v) {{
    const map = {{segs:this.grpSegs, jsph:this.grpJsph, head:this.grpHead,
                  hair:this.grpHair, belt:this.grpBelt, trunk:this.grpTrunk, feet:this.grpFeet, hands:this.grpHands}};
    if (map[layer]) map[layer].visible = v;
  }}

  // Modo debug: superfície semi-transparente + cilindros internos visíveis
  setTrunkDebug(v) {{
    this._trunkDebug = v;
    if (this.trunkSurf) this.trunkSurf.setTransparent(v);
    this.trunkDbgCyls.forEach(({{mesh}}) => {{ mesh.visible = v; }});
  }}

  setVisible(v) {{ this.group.visible = v; }}

  dispose() {{
    this.group.traverse(o => {{ if (o.isMesh) o.geometry.dispose(); }});
    scene.remove(this.group);
    Object.values(this.mats).forEach(m => m.dispose());
    if (this.trunkMat) this.trunkMat.dispose();
    this.trunkDbgCyls.forEach(c => c.mesh.material.dispose());
    if (this.footMat) this.footMat.dispose();
    if (this.footSurf) this.footSurf.dispose();
    if (this.handMat) this.handMat.dispose();
    if (this.handSurf) this.handSurf.dispose();
  }}
}}

// ── Bodies ────────────────────────────────────────────────────────────────────
let bodyA = new GrappleBody('#D8D1C4', '#1C3F7A', BODY_STYLE);
let bodyB = new GrappleBody('#1E3464', '#F0EDE8', BODY_STYLE);

function rebuildBodies() {{
  bodyA.dispose(); bodyB.dispose();
  bodyA = new GrappleBody('#D8D1C4', '#1C3F7A', BODY_STYLE);
  bodyB = new GrappleBody('#1E3464', '#F0EDE8', BODY_STYLE);
  applyAllProportions(); // inclui updateFrame interno
}}

// ── Interpolation ─────────────────────────────────────────────────────────────
function lerp3(a,b,t) {{ return [a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t]; }}

function getFrame(frames, t) {{
  const n = frames.length;
  if (n===1) return frames[0];
  const raw = t * (n-1);
  const i   = Math.min(Math.floor(raw), n-2);
  const f   = raw - i;
  const fa  = frames[i], fb = frames[i+1];
  return {{
    p0: fa.p0.map((j,k) => lerp3(j, fb.p0[k], f)),
    p1: fa.p1.map((j,k) => lerp3(j, fb.p1[k], f)),
  }};
}}

// ── Animation state ───────────────────────────────────────────────────────────
let current  = null;
let animT    = 0;
let playing  = false;
let speed    = 1.0;
let lastTime = 0;

// ── Compositor state ──────────────────────────────────────────────────────────
let seqItems = [];   // absolute entry indices
let seqStep  = -1;
let seqMode  = false;
let seqT     = 0;
let seqDwell = 1.0;

function setEntry(entry, moveCam = true) {{
  current = entry;
  animT   = 0;
  playing = entry.frames.length > 1 && !seqMode;
  updateInfo(entry);
  updateFrame();
  updatePlayBtn();
  if (moveCam) {{
    const f0 = entry.frames[0];
    const allPts = [...f0.p0, ...f0.p1];
    const cx = allPts.reduce((s,p)=>s+p[0],0)/allPts.length;
    const cy = allPts.reduce((s,p)=>s+p[1],0)/allPts.length;
    controls.target.set(cx, cy, 0);
    controls.update();
  }}
}}

function updateFrame() {{
  if (!current) return;
  const fr = getFrame(current.frames, animT);
  bodyA.update(fr.p0);
  bodyB.update(fr.p1);
  const fi = Math.round(animT * (current.frames.length-1)) + 1;
  frameLbl.textContent = current.frames.length > 1
    ? `Frame ${{fi}}/${{current.frames.length}}`
    : 'Posição estática';
}}

// ── Render loop ───────────────────────────────────────────────────────────────
renderer.setAnimationLoop((time) => {{
  const dt = Math.min((time - lastTime) / 1000, 0.1);
  lastTime = time;

  if (seqMode && seqItems.length > 0) {{
    const eIdx = seqItems[seqStep];
    const e    = ENTRIES[eIdx];
    const isAnim = eIdx >= N_POS;  // transitions animate, positions are static
    const dur  = isAnim ? e.frames.length / speed : seqDwell;
    seqT += dt / dur;
    if (seqT >= 1.0) {{
      seqT = 0;
      const next = seqStep + 1;
      if (next >= seqItems.length) {{
        if (document.getElementById('seq-loop').checked) {{
          seqStep = 0;
        }} else {{
          seqMode = false;
          document.getElementById('seq-play-btn').textContent = '▶ Play';
          controls.update(); renderer.render(scene, camera); return;
        }}
      }} else {{ seqStep = next; }}
      setEntry(ENTRIES[seqItems[seqStep]], false);
      renderSeqList();
    }} else {{
      animT = isAnim ? seqT : 0;
      updateFrame();
    }}
  }} else if (playing && current && current.frames.length > 1) {{
    animT = (animT + dt * speed / current.frames.length) % 1;
    updateFrame();
  }}

  controls.update();
  renderer.render(scene, camera);
}});

// ── Resize ────────────────────────────────────────────────────────────────────
const wrap = document.getElementById('canvas-wrap');
const ro = new ResizeObserver(() => {{
  const w = wrap.clientWidth, h = wrap.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}});
ro.observe(wrap);

// ── UI ────────────────────────────────────────────────────────────────────────
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

// Populate category filter
const cats = [...new Set(ALL.map(e=>e.cat))].sort();
cats.forEach(c => {{
  const opt = document.createElement('option');
  opt.value = c; opt.textContent = c;
  catEl.appendChild(opt);
}});

let filtered = [...ALL];
let activeIdx = 0;

function rebuildList() {{
  const q   = searchEl.value.toLowerCase();
  const cat = catEl.value;
  filtered = ALL.filter(e =>
    (!q || e.name.toLowerCase().includes(q)) &&
    (!cat || e.cat === cat)
  );
  countEl.textContent = `${{filtered.length}} / ${{ALL.length}} entradas`;
  listEl.innerHTML = '';
  filtered.forEach((e, i) => {{
    const div = document.createElement('div');
    div.className = 'li' + (i===activeIdx ? ' active' : '');
    const color = CAT_COLORS[e.cat] || '#555';
    div.innerHTML = `<span class="dot" style="background:${{color}}"></span><span>${{e.name}}</span>`;
    div.onclick = () => selectIdx(i);
    listEl.appendChild(div);
  }});
  posLbl.textContent = filtered.length ? `${{activeIdx+1}} / ${{filtered.length}}` : '';
}}

function selectIdx(i) {{
  if (i < 0 || i >= filtered.length) return;
  activeIdx = i;
  const items = listEl.querySelectorAll('.li');
  items.forEach((el,k) => el.classList.toggle('active', k===i));
  items[i]?.scrollIntoView({{block:'nearest'}});
  setEntry(filtered[i]);
  posLbl.textContent = `${{i+1}} / ${{filtered.length}}`;
}}

function updateInfo(e) {{
  document.getElementById('info-name').textContent = e.name;
  const catEl2 = document.getElementById('info-cat');
  catEl2.textContent = e.cat;
  catEl2.style.background = (CAT_COLORS[e.cat]||'#555') + '33';
  catEl2.style.color = CAT_COLORS[e.cat] || '#aaa';
  document.getElementById('info-tags').textContent = e.tags.join(' · ');
}}

function updatePlayBtn() {{
  if (!current || current.frames.length <= 1) {{
    playBtn.textContent = '▶ Play';
    playBtn.disabled = true;
  }} else {{
    playBtn.disabled = false;
    playBtn.textContent = playing ? '‖ Pause' : '▶ Play';
  }}
}}

playBtn.onclick = () => {{
  playing = !playing;
  updatePlayBtn();
}};
prevBtn.onclick = () => selectIdx(activeIdx - 1);
nextBtn.onclick = () => selectIdx(activeIdx + 1);

speedEl.oninput = () => {{
  speed = parseFloat(speedEl.value);
  speedVal.textContent = speed.toFixed(1) + '×';
}};

searchEl.oninput = () => {{ activeIdx=0; rebuildList(); if(filtered.length) selectIdx(0); }};
catEl.onchange   = () => {{ activeIdx=0; rebuildList(); if(filtered.length) selectIdx(0); }};

document.addEventListener('keydown', e => {{
  if (e.key==='ArrowRight') selectIdx(activeIdx+1);
  if (e.key==='ArrowLeft')  selectIdx(activeIdx-1);
  if (e.key===' ') {{ e.preventDefault(); playBtn.click(); }}
}});

// ── Tabs ──────────────────────────────────────────────────────────────────────
document.getElementById('tab-exp').onclick = () => {{
  document.getElementById('exp-panel').style.display = 'flex';
  document.getElementById('cmp-panel').classList.remove('on');
  document.getElementById('tab-exp').classList.add('active');
  document.getElementById('tab-cmp').classList.remove('active');
}};
document.getElementById('tab-cmp').onclick = () => {{
  document.getElementById('exp-panel').style.display = 'none';
  document.getElementById('cmp-panel').classList.add('on');
  document.getElementById('tab-exp').classList.remove('active');
  document.getElementById('tab-cmp').classList.add('active');
}};

// ── Compositor ────────────────────────────────────────────────────────────────
const seqListEl   = document.getElementById('seq-list');
const seqCntEl    = document.getElementById('seq-cnt');
const seqPlayBtn  = document.getElementById('seq-play-btn');
const seqClearBtn = document.getElementById('seq-clear-btn');
const cmpQ        = document.getElementById('cmp-q');
const cmpRes      = document.getElementById('cmp-res');
const cmpMovesEl  = document.getElementById('cmp-moves');
const seqDwellEl  = document.getElementById('seq-dwell');
const seqDwellVal = document.getElementById('seq-dwell-val');

seqDwellEl.oninput = () => {{
  seqDwell = parseFloat(seqDwellEl.value);
  seqDwellVal.textContent = seqDwell.toFixed(1) + 's';
}};

// Returns the last position entry-index in seqItems, or -1
function lastSeqPosIdx() {{
  for (let i = seqItems.length - 1; i >= 0; i--) {{
    if (seqItems[i] < N_POS) return seqItems[i];
  }}
  return -1;
}}

function cmpAddPosition(posEIdx) {{
  seqItems.push(posEIdx);
  if (seqStep < 0) seqStep = 0;
  renderSeqList();
  setEntry(ENTRIES[posEIdx], true);
  cmpQ.value = '';
  cmpRes.classList.remove('on');
  cmpRes.innerHTML = '';
}}

function cmpAddTransition(transEIdx) {{
  seqItems.push(transEIdx);
  const t = ENTRIES[transEIdx];
  if (t.to >= 0) seqItems.push(t.to);  // auto-add destination position
  if (seqStep < 0) seqStep = 0;
  renderSeqList();
  setEntry(ENTRIES[transEIdx], false);
}}

function renderMoves() {{
  cmpMovesEl.innerHTML = '';
  const posIdx = lastSeqPosIdx();
  if (posIdx < 0) return;
  const trans = GRAPH_OUT[posIdx] || [];
  if (!trans.length) {{
    const el = document.createElement('div');
    el.className = 'mv-hdr';
    el.textContent = 'Sem transições disponíveis desta posição.';
    cmpMovesEl.appendChild(el);
    return;
  }}
  const hdr = document.createElement('div');
  hdr.className = 'mv-hdr';
  hdr.textContent = 'Transições disponíveis (' + trans.length + '):';
  cmpMovesEl.appendChild(hdr);
  trans.forEach(ti => {{
    const t = ENTRIES[ti];
    const dest = t.to >= 0 ? ENTRIES[t.to] : null;
    const div = document.createElement('div');
    div.className = 'mv';
    const nFrames = t.frames.length;
    div.innerHTML =
      `<span style="color:#d97706;font-size:9px">▶</span>` +
      `<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{t.name}}</span>` +
      (dest ? `<span class="mv-to">→ ${{dest.name}}</span>` : `<span class="mv-to" style="color:#444">→ ?</span>`) +
      `<span class="cr-add">${{nFrames}}f</span>`;
    div.onclick = () => cmpAddTransition(ti);
    cmpMovesEl.appendChild(div);
  }});
}}

function renderSeqList() {{
  seqCntEl.textContent = seqItems.length;
  seqListEl.innerHTML = '';
  seqItems.forEach((eIdx, i) => {{
    const e     = ENTRIES[eIdx];
    const isPos = eIdx < N_POS;
    const isCur = i === seqStep;
    const div   = document.createElement('div');
    div.className = 'sq' + (isCur ? ' sq-cur' : '');
    const color = CAT_COLORS[e.cat] || '#555';
    const icon  = isPos ? '●' : '▶';
    let sub = '';
    if (!isPos) {{
      const dest = e.to >= 0 ? ENTRIES[e.to] : null;
      sub = dest ? ` → ${{dest.name}}` : '';
    }}
    div.innerHTML =
      `<span class="sq-icon" style="color:${{color}}">${{icon}}</span>` +
      `<span class="sq-nm">${{e.name}}${{sub ? '<span class="sq-sub">' + sub + '</span>' : ''}}</span>` +
      `<button class="sq-rm">×</button>`;
    div.querySelector('.sq-rm').addEventListener('click', ev => {{
      ev.stopPropagation();
      seqItems.splice(i, 1);
      if (seqStep >= seqItems.length) seqStep = Math.max(0, seqItems.length - 1);
      renderSeqList();
    }});
    div.addEventListener('click', () => {{
      seqStep = i; seqT = 0;
      setEntry(ENTRIES[seqItems[i]], true);
      renderSeqList();
    }});
    seqListEl.appendChild(div);
  }});
  renderMoves();
  if (seqStep >= 0 && seqStep < seqItems.length)
    seqListEl.querySelectorAll('.sq')[seqStep]?.scrollIntoView({{block:'nearest'}});
}}

seqPlayBtn.onclick = () => {{
  if (!seqItems.length) return;
  seqMode = !seqMode;
  if (seqMode) {{
    if (seqStep < 0 || seqStep >= seqItems.length) seqStep = 0;
    seqT = 0;
    setEntry(ENTRIES[seqItems[seqStep]], false);
    renderSeqList();
  }}
  seqPlayBtn.textContent = seqMode ? '⏹ Stop' : '▶ Play';
}};

seqClearBtn.onclick = () => {{
  seqItems = []; seqStep = -1; seqMode = false; seqT = 0;
  seqPlayBtn.textContent = '▶ Play';
  renderSeqList();
}};

// Compositor search — searches positions only
cmpQ.oninput = () => {{
  const q = cmpQ.value.toLowerCase().trim();
  if (!q) {{ cmpRes.classList.remove('on'); cmpRes.innerHTML = ''; return; }}
  const hits = [];
  for (let i = 0; i < N_POS && hits.length < 12; i++) {{
    if (ENTRIES[i].name.toLowerCase().includes(q)) hits.push({{e: ENTRIES[i], idx: i}});
  }}
  if (!hits.length) {{ cmpRes.classList.remove('on'); return; }}
  cmpRes.classList.add('on');
  cmpRes.innerHTML = '';
  hits.forEach(({{e, idx}}) => {{
    const div = document.createElement('div');
    div.className = 'cr';
    const color = CAT_COLORS[e.cat] || '#555';
    div.innerHTML = `<span style="color:${{color}};font-size:9px">●</span><span style="flex:1">${{e.name}}</span><span class="cr-add">+ iniciar</span>`;
    div.onclick = () => cmpAddPosition(idx);
    cmpRes.appendChild(div);
  }});
}};

cmpQ.addEventListener('blur', () => setTimeout(() => {{
  cmpRes.classList.remove('on');
}}, 150));

// Init
rebuildList();
if (filtered.length) selectIdx(0);

// ── Debug panel ───────────────────────────────────────────────────────────────
const dbgPanel = document.getElementById('dbg-panel');

document.getElementById('dbg-btn').onclick = (e) => {{
  e.stopPropagation();
  dbgPanel.style.display = dbgPanel.style.display === 'none' ? 'block' : 'none';
}};

// Fecha o painel ao clicar fora
document.addEventListener('click', (e) => {{
  if (!dbgPanel.contains(e.target) && e.target.id !== 'dbg-btn')
    dbgPanel.style.display = 'none';
}});

function applyLayer(layer, v) {{
  bodyA.setLayer(layer, v);
  bodyB.setLayer(layer, v);
}}

['segs','jsph','head','hair','belt'].forEach(id => {{
  document.getElementById('dbg-' + id).onchange = e => applyLayer(id, e.target.checked);
}});

document.getElementById('dbg-trunk').onchange = e => applyLayer('trunk', e.target.checked);
document.getElementById('dbg-trunk-cyls').onchange = e => {{
  bodyA.setTrunkDebug(e.target.checked);
  bodyB.setTrunkDebug(e.target.checked);
}};
document.getElementById('dbg-feet').onchange = e => applyLayer('feet', e.target.checked);
document.getElementById('dbg-feet-pts').onchange = e => {{
  bodyA.footSurf?.setDebug(e.target.checked);
  bodyB.footSurf?.setDebug(e.target.checked);
  if (current) updateFrame();
}};
document.getElementById('dbg-hands').onchange = e => applyLayer('hands', e.target.checked);
document.getElementById('dbg-hands-pts').onchange = e => {{
  bodyA.handSurf?.setDebug(e.target.checked);
  bodyB.handSurf?.setDebug(e.target.checked);
  if (current) updateFrame();
}};
document.getElementById('dbg-hands-axes').onchange = e => {{
  bodyA.handSurf?.setHandAxes(e.target.checked);
  bodyB.handSurf?.setHandAxes(e.target.checked);
  if (current) updateFrame();
}};
document.getElementById('hand-flip-l').onchange = e => {{
  handFlipL = e.target.checked;
  // Reseta smoothing para evitar interpolação artificial após flip
  if (bodyA.handSurf) bodyA.handSurf._prevNormL = null;
  if (bodyB.handSurf) bodyB.handSurf._prevNormL = null;
  if (current) updateFrame();
}};
document.getElementById('hand-flip-r').onchange = e => {{
  handFlipR = e.target.checked;
  if (bodyA.handSurf) bodyA.handSurf._prevNormR = null;
  if (bodyB.handSurf) bodyB.handSurf._prevNormR = null;
  if (current) updateFrame();
}};

document.getElementById('dbg-ab').onchange = e => {{
  BODY_STYLE = e.target.checked ? STYLE_EXP : STYLE_ORIG;
  const label = document.getElementById('dbg-ab-lbl');
  label.style.color = e.target.checked ? '#d97706' : '#8b949e';
  rebuildBodies();
  // Re-aplica estados de visibilidade dos toggles de camada
  ['segs','jsph','head','hair','belt'].forEach(id => {{
    applyLayer(id, document.getElementById('dbg-' + id).checked);
  }});
}};

// ── Proportions system ────────────────────────────────────────────────────────

// SEG_MAP[i]: bodyGroup, rBot key, rTop key — parallel to SEG_TOPO (20 entries)
// rBot = radius at j1 end, rTop = radius at j2 end
const SEG_MAP = [
  {{ bg:'upper', b:'torso.coreSize',      t:'torso.shoulderWidth' }}, // 0  Core→LShoulder
  {{ bg:'upper', b:'torso.coreSize',      t:'torso.shoulderWidth' }}, // 1  Core→RShoulder
  {{ bg:'lower', b:'torso.coreSize',      t:'torso.hipWidth'      }}, // 2  Core→LHip
  {{ bg:'lower', b:'torso.coreSize',      t:'torso.hipWidth'      }}, // 3  Core→RHip
  {{ bg:'upper', b:'torso.shoulderWidth', t:'torso.shoulderWidth' }}, // 4  LShoulder↔RShoulder
  {{ bg:'lower', b:'torso.hipWidth',      t:'torso.hipWidth'      }}, // 5  LHip↔RHip
  {{ bg:'upper', b:'torso.coreSize',      t:'torso.neckGirth'     }}, // 6  Core→Neck
  {{ bg:'upper', b:'torso.neckGirth',     t:'torso.neckGirth'     }}, // 7  Neck→Head
  {{ bg:'lower', b:'legs.thighGirth',     t:'legs.thighGirth'     }}, // 8  LHip→LKnee
  {{ bg:'lower', b:'legs.thighGirth',     t:'legs.calfGirth'      }}, // 9  LKnee→LAnkle
  {{ bg:'lower', b:'legs.calfGirth',      t:'legs.footGirth'      }}, // 10 LAnkle→LToe
  {{ bg:'lower', b:'legs.thighGirth',     t:'legs.thighGirth'     }}, // 11 RHip→RKnee
  {{ bg:'lower', b:'legs.thighGirth',     t:'legs.calfGirth'      }}, // 12 RKnee→RAnkle
  {{ bg:'lower', b:'legs.calfGirth',      t:'legs.footGirth'      }}, // 13 RAnkle→RToe
  {{ bg:'upper', b:'arms.upperArmGirth',  t:'arms.upperArmGirth'  }}, // 14 LShoulder→LElbow
  {{ bg:'upper', b:'arms.upperArmGirth',  t:'arms.forearmGirth'   }}, // 15 LElbow→LWrist
  {{ bg:'upper', b:'arms.forearmGirth',   t:'arms.wristGirth'     }}, // 16 LWrist→LHand
  {{ bg:'upper', b:'arms.upperArmGirth',  t:'arms.upperArmGirth'  }}, // 17 RShoulder→RElbow
  {{ bg:'upper', b:'arms.upperArmGirth',  t:'arms.forearmGirth'   }}, // 18 RElbow→RWrist
  {{ bg:'upper', b:'arms.forearmGirth',   t:'arms.wristGirth'     }}, // 19 RWrist→RHand
];

// JSPH_MAP[i]: bodyGroup, config key — parallel to JSPH_TOPO (14 entries)
const JSPH_MAP = [
  {{ bg:'upper', k:'joints.core'     }}, // 0  Core
  {{ bg:'upper', k:'joints.shoulder' }}, // 1  LShoulder
  {{ bg:'upper', k:'joints.shoulder' }}, // 2  RShoulder
  {{ bg:'upper', k:'joints.elbow'    }}, // 3  LElbow
  {{ bg:'upper', k:'joints.elbow'    }}, // 4  RElbow
  {{ bg:'upper', k:'joints.wrist'    }}, // 5  LWrist
  {{ bg:'upper', k:'joints.wrist'    }}, // 6  RWrist
  {{ bg:'lower', k:'joints.hip'      }}, // 7  LHip
  {{ bg:'lower', k:'joints.hip'      }}, // 8  RHip
  {{ bg:'lower', k:'joints.knee'     }}, // 9  LKnee
  {{ bg:'lower', k:'joints.knee'     }}, // 10 RKnee
  {{ bg:'lower', k:'joints.ankle'    }}, // 11 LAnkle
  {{ bg:'lower', k:'joints.ankle'    }}, // 12 RAnkle
  {{ bg:'upper', k:'joints.neck'     }}, // 13 Neck
];

function deepClone(o) {{ return JSON.parse(JSON.stringify(o)); }}

const DEFAULT_PROPORTIONS = {{
  global: {{ bodyRadius:1, upperBody:1, lowerBody:1 }},
  torso:  {{ coreSize:1, shoulderWidth:1, hipWidth:1, neckGirth:1 }},
  arms:   {{ upperArmGirth:1, forearmGirth:1, wristGirth:1 }},
  legs:   {{ thighGirth:1, calfGirth:1, footGirth:1 }},
  joints: {{ core:1, shoulder:1, elbow:1, wrist:1, hip:1, knee:1, ankle:1, neck:1, head:1 }},
  trunk:  {{ chestDepth:1, waistDepth:1, abdomenDepth:1, pelvisDepth:1, chestWidth:1, waistWidth:1, abdomenWidth:1, pelvisWidth:1, roundness:1 }},
  feet:   {{ footWidth:1, heelWidth:1, toeWidth:1, soleThickness:1, instepHeight:1, toeRoundness:1, heelRoundness:1, heelProjection:0.00 }},
  hands:  {{ palmWidth:1, palmThickness:1, palmLengthScale:1, fingerWidth:1, fingerThickness:1, thumbSize:0.70, thumbOffset:0.30, handRoundness:1, twistL:0, twistR:0 }},
}};

const BUILTIN_PRESETS = [
  {{ name:'Original', values: deepClone(DEFAULT_PROPORTIONS) }},
  {{
    name:'Técnico',
    values: {{
      global: {{ bodyRadius:0.92, upperBody:0.95, lowerBody:1.00 }},
      torso:  {{ coreSize:0.90, shoulderWidth:0.92, hipWidth:0.90, neckGirth:0.92 }},
      arms:   {{ upperArmGirth:0.85, forearmGirth:0.88, wristGirth:0.85 }},
      legs:   {{ thighGirth:0.95, calfGirth:0.95, footGirth:0.90 }},
      joints: {{ core:0.90, shoulder:0.90, elbow:0.88, wrist:0.85, hip:0.90, knee:0.90, ankle:0.88, neck:0.90, head:0.95 }},
    }},
  }},
  {{
    name:'Atlético',
    values: {{
      global: {{ bodyRadius:1.10, upperBody:1.12, lowerBody:1.06 }},
      torso:  {{ coreSize:1.10, shoulderWidth:1.18, hipWidth:1.05, neckGirth:1.12 }},
      arms:   {{ upperArmGirth:1.22, forearmGirth:1.16, wristGirth:1.05 }},
      legs:   {{ thighGirth:1.15, calfGirth:1.10, footGirth:1.00 }},
      joints: {{ core:1.12, shoulder:1.12, elbow:1.10, wrist:1.05, hip:1.10, knee:1.10, ankle:1.05, neck:1.08, head:1.05 }},
    }},
  }},
];

const SLIDER_GROUPS = [
  {{
    id:'global', label:'Global',
    sliders:[
      {{ key:'bodyRadius',  label:'Corpo global',   min:0.70, max:1.35, step:0.01 }},
      {{ key:'upperBody',   label:'Parte superior', min:0.50, max:1.60, step:0.01 }},
      {{ key:'lowerBody',   label:'Parte inferior', min:0.50, max:1.60, step:0.01 }},
    ],
  }},
  {{
    id:'torso', label:'Torso',
    sliders:[
      {{ key:'coreSize',      label:'Core',    min:0.50, max:1.60, step:0.01 }},
      {{ key:'shoulderWidth', label:'Ombros',  min:0.50, max:1.60, step:0.01 }},
      {{ key:'hipWidth',      label:'Quadril', min:0.50, max:1.60, step:0.01 }},
      {{ key:'neckGirth',     label:'Pescoço', min:0.50, max:1.60, step:0.01 }},
    ],
  }},
  {{
    id:'arms', label:'Braços', mirror:'mirrorArms',
    sliders:[
      {{ key:'upperArmGirth', label:'Bíceps',    min:0.50, max:1.60, step:0.01 }},
      {{ key:'forearmGirth',  label:'Antebraço', min:0.50, max:1.60, step:0.01 }},
      {{ key:'wristGirth',    label:'Pulso',     min:0.50, max:1.60, step:0.01 }},
    ],
  }},
  {{
    id:'legs', label:'Pernas', mirror:'mirrorLegs',
    sliders:[
      {{ key:'thighGirth', label:'Coxa',        min:0.50, max:1.60, step:0.01 }},
      {{ key:'calfGirth',  label:'Panturrilha', min:0.50, max:1.60, step:0.01 }},
      {{ key:'footGirth',  label:'Pé',          min:0.50, max:1.60, step:0.01 }},
    ],
  }},
  {{
    id:'joints', label:'Articulações',
    sliders:[
      {{ key:'core',     label:'Core',           min:0.50, max:1.60, step:0.01 }},
      {{ key:'shoulder', label:'Ombro',          min:0.50, max:1.60, step:0.01 }},
      {{ key:'elbow',    label:'Cotovelo',       min:0.50, max:1.60, step:0.01 }},
      {{ key:'wrist',    label:'Pulso (art.)',   min:0.50, max:1.60, step:0.01 }},
      {{ key:'hip',      label:'Quadril (art.)', min:0.50, max:1.60, step:0.01 }},
      {{ key:'knee',     label:'Joelho',         min:0.50, max:1.60, step:0.01 }},
      {{ key:'ankle',    label:'Tornozelo',      min:0.50, max:1.60, step:0.01 }},
      {{ key:'neck',     label:'Pescoço (art.)', min:0.50, max:1.60, step:0.01 }},
      {{ key:'head',     label:'Cabeça',         min:0.50, max:1.60, step:0.01 }},
    ],
  }},
  {{
    id:'trunk', label:'Tronco 3D',
    sliders:[
      {{ key:'chestDepth',   label:'Prof. peito',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'waistDepth',   label:'Prof. cintura',  min:0.30, max:2.50, step:0.05 }},
      {{ key:'abdomenDepth', label:'Prof. abdômen',  min:0.30, max:2.50, step:0.05 }},
      {{ key:'pelvisDepth',  label:'Prof. pelve',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'chestWidth',   label:'Larg. peito',    min:0.50, max:2.00, step:0.05 }},
      {{ key:'waistWidth',   label:'Larg. cintura',  min:0.20, max:2.00, step:0.05 }},
      {{ key:'abdomenWidth', label:'Larg. abdômen',  min:0.20, max:2.00, step:0.05 }},
      {{ key:'pelvisWidth',  label:'Larg. pelve',    min:0.50, max:2.00, step:0.05 }},
      {{ key:'roundness',   label:'Arredondamento', min:0.50, max:4.00, step:0.10 }},
    ],
  }},
  {{
    id:'feet', label:'Pés 3D',
    sliders:[
      {{ key:'footWidth',     label:'Largura geral',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'heelWidth',     label:'Largura calcanhar',min:0.30, max:2.50, step:0.05 }},
      {{ key:'toeWidth',      label:'Largura dedos',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'soleThickness', label:'Espessura sola',   min:0.20, max:3.00, step:0.05 }},
      {{ key:'instepHeight',  label:'Peito do pé',      min:0.10, max:3.00, step:0.05 }},
      {{ key:'heelProjection', label:'Projeção calcanhar', min:0.00, max:3.00, step:0.05 }},
      {{ key:'toeRoundness',   label:'Arred. dedos',      min:0.50, max:4.00, step:0.10 }},
      {{ key:'heelRoundness',  label:'Arred. calcanhar',  min:0.50, max:4.00, step:0.10 }},
    ],
  }},
  {{
    id:'hands', label:'Mãos 3D',
    sliders:[
      {{ key:'palmWidth',       label:'Largura palma',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'palmThickness',   label:'Espessura palma',  min:0.20, max:3.00, step:0.05 }},
      {{ key:'palmLengthScale', label:'Comprimento palma',min:0.30, max:2.00, step:0.05 }},
      {{ key:'fingerWidth',     label:'Largura dedos',    min:0.30, max:2.50, step:0.05 }},
      {{ key:'fingerThickness', label:'Espessura dedos',  min:0.20, max:3.00, step:0.05 }},
      {{ key:'thumbSize',       label:'Tamanho polegar',  min:0.00, max:2.00, step:0.05 }},
      {{ key:'thumbOffset',     label:'Posição polegar',  min:0.10, max:0.90, step:0.05 }},
      {{ key:'handRoundness',   label:'Arred. mão',       min:0.50, max:4.00, step:0.10 }},
      {{ key:'twistL',          label:'Twist esq. (°)',   min:-180, max:180,  step:5    }},
      {{ key:'twistR',          label:'Twist dir. (°)',   min:-180, max:180,  step:5    }},
    ],
  }},
];

const LS_KEY = 'grappleMap.bodyStylePresets.v1';

let customPresets   = [];
let configA         = deepClone(DEFAULT_PROPORTIONS);
let configB         = deepClone(DEFAULT_PROPORTIONS);
let linkAthletes    = true;
let mirrorArms      = true;
let mirrorLegs      = true;
let activeAthlete   = 'A';
let activePresetName = 'Original';
let isDirty         = false;
let compareMode     = 'current'; // 'current' | 'original' | 'compareAB'
let propsPanelOpen  = false;
let ppMinimized     = false;
// Controles globais de mão (não persistidos no config de proporções)
let handFlipL = false;
let handFlipR = false;

function getActiveConfig() {{
  return (linkAthletes || activeAthlete === 'A') ? configA : configB;
}}

function getConfigForBody(which) {{
  if (compareMode === 'original') return DEFAULT_PROPORTIONS;
  if (compareMode === 'compareAB' && which === 'B') return DEFAULT_PROPORTIONS;
  return which === 'A' ? configA : (linkAthletes ? configA : configB);
}}

function getNested(cfg, keyPath) {{
  const [cat, key] = keyPath.split('.');
  return cfg[cat][key];
}}

function setNested(cfg, keyPath, val) {{
  const [cat, key] = keyPath.split('.');
  cfg[cat][key] = val;
}}

function computeSegRadii(segIdx, config) {{
  const m  = SEG_MAP[segIdx];
  const bs = STYLE_ORIG.seg[segIdx];
  const g  = config.global.bodyRadius;
  const gr = m.bg === 'upper' ? config.global.upperBody : config.global.lowerBody;
  return {{
    rTop: bs.rTop * g * gr * getNested(config, m.t),
    rBot: bs.rBot * g * gr * getNested(config, m.b),
  }};
}}

function computeJsphRadius(jsphIdx, config) {{
  const m  = JSPH_MAP[jsphIdx];
  const g  = config.global.bodyRadius;
  const gr = m.bg === 'upper' ? config.global.upperBody : config.global.lowerBody;
  return STYLE_ORIG.jsph[jsphIdx] * g * gr * getNested(config, m.k);
}}

function computeHeadRadius(config) {{
  return STYLE_ORIG.head.r * config.global.bodyRadius * config.global.upperBody * config.joints.head;
}}

function applyProportions(body, config) {{
  body.trunkConfig = config.trunk;
  body.footConfig  = config.feet;
  body.handConfig  = config.hands;
  const s = BODY_STYLE;
  body.segs.forEach(({{mesh}}, i) => {{
    const {{rTop, rBot}} = computeSegRadii(i, config);
    mesh.geometry.dispose();
    mesh.geometry = new THREE.CylinderGeometry(rTop, rBot, 1, s.geo.cylSegs, 1);
  }});
  body.jsphMeshes.forEach(({{mesh}}, i) => {{
    const r = computeJsphRadius(i, config);
    mesh.geometry.dispose();
    mesh.geometry = new THREE.SphereGeometry(r, s.geo.sphW, s.geo.sphH);
  }});
  const hr = computeHeadRadius(config);
  body.headMesh.geometry.dispose();
  body.headMesh.geometry = new THREE.SphereGeometry(hr, s.geo.headW, s.geo.headH);
  const hairR = hr * (STYLE_ORIG.hair.r / STYLE_ORIG.head.r);
  body.hairMesh.geometry.dispose();
  body.hairMesh.geometry = new THREE.SphereGeometry(
    hairR, 18, 10, 0, Math.PI*2, 0, Math.PI*STYLE_ORIG.hair.capFraction);
}}

function applyAllProportions() {{
  applyProportions(bodyA, getConfigForBody('A'));
  applyProportions(bodyB, getConfigForBody('B'));
  // Reconstrói a superfície do tronco com os joints do frame atual
  // (necessário quando parado em posição estática — o render loop não chama update())
  if (current) updateFrame();
}}

// ── Preset storage ────────────────────────────────────────────────────────────

// Preenche seções/chaves ausentes em cfg a partir dos defaults — compatibilidade com configs antigas
function migrateConfig(cfg) {{
  const def = DEFAULT_PROPORTIONS;
  Object.keys(def).forEach(cat => {{
    if (!cfg[cat]) cfg[cat] = JSON.parse(JSON.stringify(def[cat]));
    else Object.keys(def[cat]).forEach(k => {{
      if (cfg[cat][k] === undefined) cfg[cat][k] = def[cat][k];
    }});
  }});
  return cfg;
}}

const UD_KEY = 'grappleMap.userDefault.v1';

function loadPresetsFromStorage() {{
  try {{
    const s = localStorage.getItem(LS_KEY);
    if (s) customPresets = JSON.parse(s).presets || [];
  }} catch(e) {{ customPresets = []; }}
  // Carrega config padrão do usuário, se existir
  try {{
    const d = localStorage.getItem(UD_KEY);
    if (d) {{
      const ud = migrateConfig(JSON.parse(d));
      configA = JSON.parse(JSON.stringify(ud));
      configB = JSON.parse(JSON.stringify(ud));
    }}
  }} catch(e) {{}}
}}

function saveAsDefault() {{
  try {{
    localStorage.setItem(UD_KEY, JSON.stringify(deepClone(getActiveConfig())));
    const btn = document.getElementById('pp-default-btn');
    if (btn) {{ btn.textContent = '★✓'; setTimeout(() => {{ btn.textContent = '★'; }}, 1500); }}
  }} catch(e) {{ alert('Não foi possível salvar o padrão: ' + e.message); }}
}}

function savePresetsToStorage() {{
  try {{ localStorage.setItem(LS_KEY, JSON.stringify({{presets:customPresets}})); }} catch(e) {{}}
}}

function loadPreset(name) {{
  const preset = [...BUILTIN_PRESETS, ...customPresets].find(p => p.name === name);
  if (!preset) return;
  activePresetName = name;
  configA = migrateConfig(deepClone(preset.values));
  configB = migrateConfig(deepClone(preset.values));
  isDirty = false;
  applyAllProportions();
  buildPropsPanel();
}}

function saveCurrentPreset() {{
  const isBuiltin = BUILTIN_PRESETS.some(p => p.name === activePresetName);
  if (isBuiltin) {{ showNameInput(); return; }}
  const idx = customPresets.findIndex(p => p.name === activePresetName);
  const values = deepClone(getActiveConfig());
  if (idx >= 0) customPresets[idx].values = values;
  else customPresets.push({{name:activePresetName, values}});
  isDirty = false;
  savePresetsToStorage();
  buildPropsPanel();
}}

function showNameInput() {{
  const row = document.getElementById('pp-name-row');
  row.classList.add('on');
  const inp = document.getElementById('pp-name-inp');
  const suffix = BUILTIN_PRESETS.some(p => p.name === activePresetName) ? '' : ' (cópia)';
  inp.value = activePresetName + suffix;
  inp.focus();
}}

function confirmSaveAs() {{
  const name = document.getElementById('pp-name-inp').value.trim();
  if (!name) return;
  if (BUILTIN_PRESETS.some(p => p.name === name)) {{ alert('Não é possível sobrescrever presets embutidos.'); return; }}
  const values = deepClone(getActiveConfig());
  const idx = customPresets.findIndex(p => p.name === name);
  if (idx >= 0) customPresets[idx].values = values;
  else customPresets.push({{name, values}});
  activePresetName = name;
  isDirty = false;
  savePresetsToStorage();
  buildPropsPanel();
}}

function markDirty() {{
  isDirty = true;
  const el = document.getElementById('pp-save-status');
  if (el) {{ el.className = 'pp-status dirty'; el.textContent = '● Não salvo'; }}
}}

function exportJSON() {{
  const data = {{
    schemaVersion: 1,
    name: activePresetName,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    values: deepClone(getActiveConfig()),
  }};
  const blob = new Blob([JSON.stringify(data, null, 2)], {{type:'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `proporções-${{activePresetName.replace(/[^a-z0-9]/gi,'_')}}.json`;
  a.click();
  URL.revokeObjectURL(url);
}}

function importJSON() {{
  const inp = document.createElement('input');
  inp.type = 'file';
  inp.accept = '.json';
  inp.onchange = (e) => {{
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {{
      try {{
        const data = JSON.parse(ev.target.result);
        if (data.schemaVersion !== 1 || !data.values) throw new Error('Formato inválido');
        const v = data.values;
        const clamp = (x, lo, hi) => isNaN(x) ? 1 : Math.max(lo, Math.min(hi, x));
        const validateCat = (cat, def) => {{
          if (!v[cat]) v[cat] = {{}};
          Object.keys(def).forEach(k => {{
            const lo = (cat === 'global' && k === 'bodyRadius') ? 0.70 : 0.50;
            const hi = (cat === 'global' && k === 'bodyRadius') ? 1.35 : 1.60;
            v[cat][k] = clamp(parseFloat(v[cat][k] ?? 1), lo, hi);
          }});
        }};
        ['global','torso','arms','legs','joints'].forEach(c => validateCat(c, DEFAULT_PROPORTIONS[c]));
        migrateConfig(v);  // preenche trunk/feet ausentes
        configA = v;
        configB = deepClone(v);
        activePresetName = data.name || 'Importado';
        isDirty = true;
        applyAllProportions();
        buildPropsPanel();
      }} catch(err) {{ alert('Erro ao importar: ' + err.message); }}
    }};
    reader.readAsText(file);
  }};
  inp.click();
}}

// ── Panel UI builder ──────────────────────────────────────────────────────────

function buildPropsPanel() {{
  const body = document.getElementById('pp-body');
  body.innerHTML = '';

  // Compare mode bar
  const cmpBar = document.createElement('div');
  cmpBar.className = 'pp-compare-bar';
  [['current','Atual'], ['original','Original'], ['compareAB','A vs B']].forEach(([m, lbl]) => {{
    const btn = document.createElement('button');
    btn.className = 'pp-cmp-btn' + (compareMode === m ? ' active' : '');
    btn.textContent = lbl;
    btn.onclick = () => {{ compareMode = m; applyAllProportions(); buildPropsPanel(); }};
    cmpBar.appendChild(btn);
  }});
  body.appendChild(cmpBar);

  // Preset bar
  const presetBar = document.createElement('div');
  presetBar.className = 'pp-preset-bar';
  const sel = document.createElement('select');
  sel.className = 'pp-preset-sel';
  [...BUILTIN_PRESETS, ...customPresets].forEach(p => {{
    const opt = document.createElement('option');
    opt.value = p.name;
    opt.textContent = (isDirty && p.name === activePresetName) ? p.name + ' *' : p.name;
    opt.selected = p.name === activePresetName;
    sel.appendChild(opt);
  }});
  sel.onchange = () => loadPreset(sel.value);
  presetBar.appendChild(sel);

  const mkBtn = (txt, title, fn) => {{
    const b = document.createElement('button');
    b.className = 'pp-preset-btn';
    b.textContent = txt;
    b.title = title;
    b.onclick = fn;
    return b;
  }};
  presetBar.appendChild(mkBtn('💾', 'Salvar', saveCurrentPreset));
  presetBar.appendChild(mkBtn('＋', 'Salvar como…', showNameInput));
  presetBar.appendChild(mkBtn('↓', 'Exportar JSON', exportJSON));
  presetBar.appendChild(mkBtn('↑', 'Importar JSON', importJSON));
  const defBtn = mkBtn('★', 'Salvar como padrão de inicialização', saveAsDefault);
  defBtn.id = 'pp-default-btn';
  defBtn.title = 'Salvar como padrão — carregado automaticamente ao abrir';
  presetBar.appendChild(defBtn);
  body.appendChild(presetBar);

  // Name input row
  const nameRow = document.createElement('div');
  nameRow.className = 'pp-name-row';
  nameRow.id = 'pp-name-row';
  const nameInp = document.createElement('input');
  nameInp.className = 'pp-name-inp';
  nameInp.id = 'pp-name-inp';
  nameInp.placeholder = 'Nome do preset…';
  nameRow.appendChild(nameInp);
  nameRow.appendChild(mkBtn('✓', 'Confirmar', confirmSaveAs));
  nameRow.appendChild(mkBtn('✕', 'Cancelar', () => nameRow.classList.remove('on')));
  body.appendChild(nameRow);

  // Athlete tabs (only when unlinked)
  if (!linkAthletes) {{
    const tabs = document.createElement('div');
    tabs.className = 'pp-ath-tabs';
    ['A', 'B'].forEach(ath => {{
      const tab = document.createElement('button');
      tab.className = 'pp-ath-tab' + (activeAthlete === ath ? ' active' : '');
      tab.textContent = `Atleta ${{ath}}`;
      tab.onclick = () => {{ activeAthlete = ath; buildPropsPanel(); }};
      tabs.appendChild(tab);
    }});
    body.appendChild(tabs);
  }}

  // Slider groups
  const cfg = getActiveConfig();
  SLIDER_GROUPS.forEach(grp => {{
    const groupDiv = document.createElement('div');
    groupDiv.className = 'pp-group';

    const hdr = document.createElement('div');
    hdr.className = 'pp-group-hdr';
    const lbl = document.createElement('span');
    lbl.className = 'pp-group-lbl';
    lbl.textContent = grp.label;
    hdr.appendChild(lbl);

    if (grp.mirror) {{
      const active = grp.mirror === 'mirrorArms' ? mirrorArms : mirrorLegs;
      const ms = document.createElement('span');
      ms.className = 'pp-group-mirror';
      ms.title = 'Mirror esq/dir';
      ms.textContent = active ? '🔗' : '⛓';
      ms.onclick = (e) => {{
        e.stopPropagation();
        if (grp.mirror === 'mirrorArms') mirrorArms = !mirrorArms;
        else mirrorLegs = !mirrorLegs;
        buildPropsPanel();
      }};
      hdr.appendChild(ms);
    }}

    const grpRst = document.createElement('button');
    grpRst.className = 'pp-grp-reset';
    grpRst.title = `Reset ${{grp.label}}`;
    grpRst.textContent = '↺';
    grpRst.onclick = (e) => {{
      e.stopPropagation();
      grp.sliders.forEach(sd => {{
        const defVal = getNested(DEFAULT_PROPORTIONS, grp.id + '.' + sd.key);
        setNested(configA, grp.id + '.' + sd.key, defVal);
        setNested(configB, grp.id + '.' + sd.key, defVal);
      }});
      markDirty();
      applyAllProportions();
      buildPropsPanel();
    }};
    hdr.appendChild(grpRst);
    groupDiv.appendChild(hdr);

    const rows = document.createElement('div');
    rows.className = 'pp-grp-rows';

    grp.sliders.forEach(sd => {{
      const keyPath = grp.id + '.' + sd.key;
      const curVal  = getNested(cfg, keyPath);
      const defVal  = getNested(DEFAULT_PROPORTIONS, keyPath);

      const row = document.createElement('div');
      row.className = 'pp-row';

      const rowLbl = document.createElement('span');
      rowLbl.className = 'pp-row-lbl';
      rowLbl.textContent = sd.label;
      rowLbl.title = sd.label;

      const inp = document.createElement('input');
      inp.type = 'range';
      inp.min = sd.min; inp.max = sd.max; inp.step = sd.step;
      inp.value = curVal;

      const valSpan = document.createElement('span');
      valSpan.className = 'pp-val';
      valSpan.textContent = curVal.toFixed(2);

      const rst = document.createElement('button');
      rst.className = 'pp-row-reset' + (Math.abs(curVal - defVal) > 0.001 ? ' dirty' : '');
      rst.textContent = '↺';
      rst.title = 'Reset';
      rst.onclick = () => {{
        setNested(configA, keyPath, defVal);
        setNested(configB, keyPath, defVal);
        inp.value = defVal;
        valSpan.textContent = defVal.toFixed(2);
        rst.classList.remove('dirty');
        markDirty();
        applyAllProportions();
      }};

      inp.oninput = () => {{
        const v = parseFloat(inp.value);
        valSpan.textContent = v.toFixed(2);
        rst.classList.toggle('dirty', Math.abs(v - defVal) > 0.001);
        setNested(getActiveConfig(), keyPath, v);
        if (linkAthletes) {{
          setNested(configA, keyPath, v);
          setNested(configB, keyPath, v);
        }}
        markDirty();
        applyAllProportions();
      }};

      row.appendChild(rowLbl);
      row.appendChild(inp);
      row.appendChild(valSpan);
      row.appendChild(rst);
      rows.appendChild(row);
    }});

    groupDiv.appendChild(rows);
    body.appendChild(groupDiv);
  }});

  // Footer
  const footer = document.createElement('div');
  footer.className = 'pp-footer';

  const linkLbl = document.createElement('label');
  linkLbl.className = 'pp-link-lbl';
  const linkChk = document.createElement('input');
  linkChk.type = 'checkbox';
  linkChk.checked = linkAthletes;
  linkChk.onchange = () => {{
    linkAthletes = linkChk.checked;
    if (linkAthletes) configB = deepClone(configA);
    buildPropsPanel();
    applyAllProportions();
  }};
  linkLbl.appendChild(linkChk);
  linkLbl.append(' Link atletas');
  footer.appendChild(linkLbl);

  const rstAll = document.createElement('button');
  rstAll.className = 'pp-preset-btn';
  rstAll.textContent = '↺ Reset';
  rstAll.onclick = () => {{
    if (!confirm('Resetar todas as proporções?')) return;
    configA = deepClone(DEFAULT_PROPORTIONS);
    configB = deepClone(DEFAULT_PROPORTIONS);
    activePresetName = 'Original';
    isDirty = false;
    applyAllProportions();
    buildPropsPanel();
  }};
  footer.appendChild(rstAll);

  const statusEl = document.createElement('span');
  statusEl.className = 'pp-status' + (isDirty ? ' dirty' : '');
  statusEl.id = 'pp-save-status';
  statusEl.textContent = isDirty ? '● Não salvo' : '✓ Salvo';
  footer.appendChild(statusEl);

  body.appendChild(footer);
}}

// ── Panel toggle ──────────────────────────────────────────────────────────────

const propsPanelEl = document.getElementById('props-panel');

document.getElementById('props-btn').onclick = (e) => {{
  e.stopPropagation();
  propsPanelOpen = !propsPanelOpen;
  propsPanelEl.classList.toggle('open', propsPanelOpen);
  if (propsPanelOpen) buildPropsPanel();
}};

document.getElementById('pp-minimize').onclick = () => {{
  ppMinimized = !ppMinimized;
  propsPanelEl.classList.toggle('minimized', ppMinimized);
  document.getElementById('pp-minimize').textContent = ppMinimized ? '+' : '−';
}};

document.getElementById('pp-close').onclick = () => {{
  propsPanelOpen = false;
  propsPanelEl.classList.remove('open');
}};

// Close props panel when clicking outside (but not inside it or its button)
document.addEventListener('click', (e) => {{
  if (propsPanelOpen &&
      !propsPanelEl.contains(e.target) &&
      e.target.id !== 'props-btn') {{
    propsPanelOpen = false;
    propsPanelEl.classList.remove('open');
  }}
}});

// ── Keyboard shortcuts (proportions) ─────────────────────────────────────────

document.addEventListener('keydown', ev => {{
  if (ev.target.tagName === 'INPUT' || ev.target.tagName === 'SELECT' || ev.target.tagName === 'TEXTAREA') return;
  switch (ev.key.toLowerCase()) {{
    case 'p':
      ev.preventDefault();
      propsPanelOpen = !propsPanelOpen;
      propsPanelEl.classList.toggle('open', propsPanelOpen);
      if (propsPanelOpen) buildPropsPanel();
      break;
    case 'o':
      ev.preventDefault();
      compareMode = compareMode === 'original' ? 'current' : 'original';
      applyAllProportions();
      if (propsPanelOpen) buildPropsPanel();
      break;
    case 'r':
      if (!propsPanelOpen) break;
      ev.preventDefault();
      if (confirm('Resetar todas as proporções?')) {{
        configA = deepClone(DEFAULT_PROPORTIONS);
        configB = deepClone(DEFAULT_PROPORTIONS);
        activePresetName = 'Original';
        isDirty = false;
        applyAllProportions();
        buildPropsPanel();
      }}
      break;
    case 's':
      if (!propsPanelOpen) break;
      ev.preventDefault();
      saveCurrentPreset();
      break;
  }}
}});

// ── Init ──────────────────────────────────────────────────────────────────────
loadPresetsFromStorage();
applyAllProportions();      // garante trunkConfig nos bodies antes do primeiro updateFrame
if (current) updateFrame(); // reconstrói tronco com joints do frame atual
</script>
</body>
</html>"""

def main():
    print("Baixando GrappleMap.txt…")
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    print(f"  {len(r.text):,} bytes")

    print("Parseando e decodificando…")
    data = parse_and_decode(r.text)
    n_pos   = data["nPos"]
    n_trans = len(data["entries"]) - n_pos
    n_conn  = sum(1 for v in data["graphOut"].values() if v)
    print(f"  {n_pos} posições  |  {n_trans} transições (com origem conhecida)  |  {n_conn} posições com saídas")

    from collections import Counter
    cats = Counter(e['cat'] for e in data["entries"][:n_pos])
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {cat:<22} {n:>3}")

    print(f"\nGerando {OUTPUT}…")
    html = generate_html(data)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) / 1024
    print(f"  Tamanho: {size_kb:.0f} KB")
    print(f"  Abrir: {OUTPUT}")

if __name__ == "__main__":
    main()
