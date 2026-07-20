// ERA — live web client. Each visitor runs their own copy: the deterministic Rust
// engine is compiled to WebAssembly and ticks here, in this browser tab, and this
// renderer reads its live behaviour state every frame. Same artifact runs on
// localhost and on any static web host.
import init, { WasmEngine } from './pkg/era_first_breath.js';

let WORLD, eng, prev = null, cur = null;
const NODES = {}, ROSTER = {};
const placeName = id => (NODES[id] && NODES[id].name) || id;
const humanize = t => t.replace(/loc_[a-z_]+/g, m => placeName(m));

const c = document.getElementById('c'), ctx = c.getContext('2d');
const VW = 1000, VH = 760;
let baseScale = 1;
const cam = { zoom: 1, tx: VW / 2, ty: VH / 2, follow: null };

function resize() {
  const w = c.parentElement.clientWidth, h = c.parentElement.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  c.width = w * dpr; c.height = h * dpr;
  baseScale = Math.min(w / VW, h / VH);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener('resize', resize);
function S(x, y) {
  const w = c.clientWidth, h = c.clientHeight, s = baseScale * cam.zoom;
  return [(x - cam.tx) * s + w / 2, (y - cam.ty) * s + h / 2];
}

// ---- live clock ----
let playing = true, speed = 1, acc = 0, last = null, selected = null, _pn = 0;
let lastPanelTick = -1;
const BASE_TPS = 7 / 6; // ~1.17 five-minute ticks/sec

document.getElementById('play').onclick = e => {
  playing = !playing; e.target.textContent = playing ? 'Pause' : 'Play';
};
document.querySelectorAll('[data-mul]').forEach(b => b.onclick = () => { speed = +b.dataset.mul; });
document.getElementById('newworld').onclick = () => {
  const seed = (+document.getElementById('seed').value) >>> 0;
  eng = new WasmEngine(seed);
  cur = JSON.parse(eng.snapshot_json()); prev = cur; acc = 0; selected = null; cam.follow = null;
  renderPanels(cur); lastPanelTick = cur.tick;
};

c.addEventListener('click', ev => {
  const r = c.getBoundingClientRect();
  const mx = ev.clientX - r.left, my = ev.clientY - r.top;
  let best = null, bd = 24;
  cur.entities.forEach(e => {
    const [sx, sy] = S(e.x, e.y);
    const d = Math.hypot(sx - mx, sy - my);
    if (d < bd) { bd = d; best = e.id; }
  });
  selected = best; cam.follow = best;
});
c.addEventListener('dblclick', () => { selected = null; cam.follow = null; });

// interpolate positions between the previous and current live snapshot
function lerpEntities(a, b, f) {
  const bmap = {}; b.entities.forEach(e => bmap[e.id] = e);
  return a.entities.map(e => {
    const e2 = bmap[e.id] || e;
    return { ...e, x: e.x + (e2.x - e.x) * f, y: e.y + (e2.y - e.y) * f };
  });
}

const pad = n => String(n).padStart(2, '0');
function clockLabel(fr) { return pad(fr.hour) + ':' + pad(fr.minute); }

function draw(ents, fr) {
  const w = c.clientWidth, h = c.clientHeight;
  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = '#222c38'; ctx.lineWidth = 2;
  WORLD.edges.forEach(([a, b]) => {
    const A = NODES[a], B = NODES[b]; if (!A || !B) return;
    const [x1, y1] = S(A.x, A.y), [x2, y2] = S(B.x, B.y);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  });

  const busiest = fr.busiest ? fr.busiest.place : null;
  WORLD.locations.forEach(l => {
    const [x, y] = S(l.x, l.y);
    const open = l.hours ? (fr.hour >= l.hours[0] && fr.hour < l.hours[1]) : true;
    const occ = fr.occupancy[l.id] || 0;
    if (l.id === busiest) { ctx.beginPath(); ctx.arc(x, y, 26, 0, 7); ctx.fillStyle = 'rgba(230,184,0,.14)'; ctx.fill(); }
    ctx.beginPath(); ctx.arc(x, y, l.home ? 8 : 11, 0, 7);
    ctx.fillStyle = l.home ? '#2a3441' : (open ? '#34435a' : '#232c38'); ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = l.id === busiest ? '#e6b800' : '#3a4759'; ctx.stroke();
    ctx.fillStyle = '#7d8b99'; ctx.font = '11px system-ui'; ctx.textAlign = 'center';
    ctx.fillText(l.name, x, y + (l.home ? 20 : 24));
    if (occ > 0) {
      ctx.beginPath(); ctx.arc(x + 13, y - 11, 8, 0, 7);
      ctx.fillStyle = l.id === busiest ? '#e6b800' : '#3d84a8'; ctx.fill();
      ctx.fillStyle = l.id === busiest ? '#1a1200' : '#eaf1f6';
      ctx.font = 'bold 11px system-ui'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(occ, x + 13, y - 11); ctx.textBaseline = 'alphabetic';
    }
  });

  const R = {}; const handled = new Set();
  ents.forEach(e => {
    if (e.pose === 'talk' && e.partner && !handled.has(e.id)) {
      const p = ents.find(o => o.id === e.partner);
      if (p) {
        const cx = (e.x + p.x) / 2, cy = (e.y + p.y) / 2;
        const ang = hashAngle(e.id < p.id ? e.id + p.id : p.id + e.id);
        const ax = Math.cos(ang) * 9, ay = Math.sin(ang) * 9;
        R[e.id] = { x: cx - ax, y: cy - ay, heading: Math.atan2(ay, ax) };
        R[p.id] = { x: cx + ax, y: cy + ay, heading: Math.atan2(-ay, -ax) };
        handled.add(e.id); handled.add(p.id);
      }
    }
  });
  const groups = {};
  ents.forEach(e => { if (!handled.has(e.id) && !e.moving) (groups[e.place] ||= []).push(e); });
  Object.values(groups).forEach(g => g.forEach((e, i) => {
    if (g.length === 1) { R[e.id] = { x: e.x, y: e.y, heading: e.h }; }
    else {
      const ang = (i / g.length) * Math.PI * 2 + hashAngle(e.place);
      const rad = 10 + g.length * 1.4;
      R[e.id] = { x: e.x + Math.cos(ang) * rad, y: e.y + Math.sin(ang) * rad, heading: e.h };
    }
    handled.add(e.id);
  }));
  ents.forEach(e => { if (!handled.has(e.id)) R[e.id] = { x: e.x, y: e.y, heading: e.h }; });

  ents.forEach(e => {
    if (e.pose === 'talk' && e.partner && e.id < e.partner) {
      const p = ents.find(o => o.id === e.partner); if (!p || !R[p.id]) return;
      drawConversation(S(R[e.id].x, R[e.id].y), S(R[p.id].x, R[p.id].y), e.gest, p.gest);
    }
  });
  ents.forEach(e => {
    const meta = ROSTER[e.id] || { color: '#888', kind: 'resident', name: e.id };
    const r = R[e.id]; const [x, y] = S(r.x, r.y);
    drawEntity(x, y, r.heading, e, meta, e.id === selected);
  });
}

function hashAngle(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return (h % 360) * Math.PI / 180; }
function seedOf(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return ((h >>> 0) % 1000) / 1000; }

function animateState(e, T, sd) {
  const s = e.pose; let dx = 0, dy = 0, dh = 0, breathe = 1;
  const c2 = Math.cos(e.h), si = Math.sin(e.h);
  if (s === 'walk') { const b = Math.sin(T * 9 + sd * 6) * (0.7 + (e.spd || 0.3) * 2.5); dy = -Math.abs(b) * 0.6; dx = b * 0.15; }
  else if (s === 'stand' || s === 'alert') { dh = Math.sin(T * 0.5 + sd * 6) * 0.5; dx = Math.sin(T * 0.8 + sd) * 1.3; dy = Math.cos(T * 0.7 + sd) * 1.1; }
  else if (s === 'work') { const w = Math.sin(T * 3 + sd * 6); dx = c2 * w * 2.2; dy = si * w * 2.2; }
  else if (s === 'talk') { const lean = 1.5 + Math.sin(T * 2.2 + sd * 6) * 1.6; dx = c2 * lean; dy = si * lean; if (e.gest === 'laugh') dy -= Math.abs(Math.sin(T * 11)) * 2.4; }
  else if (s === 'sit') { dx = Math.sin(T * 0.6 + sd) * 0.8; }
  else if (s === 'sniff') { dh = Math.sin(T * 3 + sd) * 0.7; dy = Math.abs(Math.sin(T * 4.5)) * 1.6; }
  else if (s === 'forage') { dy = Math.abs(Math.sin(T * 3.2 + sd * 6)) * 2.6; dx = Math.sin(T * 0.4 + sd) * 2.2; }
  else if (s === 'groom') { dx = Math.sin(T * 4 + sd) * 1.3; dy = Math.cos(T * 4 + sd) * 1.3; }
  else if (s === 'perch') { const cyc = (T * 0.4 + sd) % 4; dy = cyc < 0.28 ? -Math.sin(cyc / 0.28 * Math.PI) * 4 : 0; }
  else if (s === 'lie') { breathe = 1 + Math.sin(T * 1.3 + sd * 6) * 0.09; }
  else if (s === 'play') { dx = (Math.sin(T * 2.1 + sd * 6) + Math.sin(T * 3.7 + sd * 3)) * 7; dy = (Math.cos(T * 1.9 + sd * 4) + Math.sin(T * 3.1 + sd)) * 6; }
  return { dx, dy, dh, breathe };
}

function drawEntity(x0, y0, heading0, e, meta, sel) {
  const kind = meta.kind, color = meta.color;
  const bird = kind === 'crow' || kind === 'owl' || kind === 'heron';
  const small = kind === 'fox' || kind === 'cat' || kind === 'hedgehog';
  const dog = kind === 'dog';
  const rad = bird ? 3.6 : small ? 4.5 : dog ? 5 : 6.5;
  const T = _pn / 1000, sd = seedOf(e.id);
  const a = animateState(e, T, sd);
  const x = x0 + a.dx * (baseScale * cam.zoom) * 0.5, y = y0 + a.dy * (baseScale * cam.zoom) * 0.5;
  const heading = heading0 + a.dh;
  const cos = Math.cos(heading), sin = Math.sin(heading);

  if (sel) { ctx.beginPath(); ctx.arc(x, y, rad + 7, 0, 7); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke(); }

  if (e.pose === 'perch') {
    ctx.beginPath(); ctx.moveTo(x - 5, y + 2); ctx.lineTo(x, y - 4); ctx.lineTo(x + 5, y + 2);
    ctx.strokeStyle = color; ctx.lineWidth = 2.4; ctx.stroke();
    if (kind === 'resident') label(x, y - 10, meta.name);
    return;
  }
  if (e.pose === 'lie') {
    ctx.save(); ctx.translate(x, y); ctx.rotate(heading); ctx.scale(1, a.breathe);
    ctx.beginPath(); ctx.ellipse(0, 0, rad + 3, rad - 1.5, 0, 0, 7);
    ctx.fillStyle = color; ctx.fill(); ctx.lineWidth = 1.3; ctx.strokeStyle = 'rgba(0,0,0,.5)'; ctx.stroke(); ctx.restore();
    return;
  }
  if (e.pose === 'play') {
    const bx = x + Math.sin(T * 1.3 + sd) * 15, by = y + 9 - Math.abs(Math.sin(T * 3.2)) * 9;
    ctx.beginPath(); ctx.arc(bx, by, 2.6, 0, 7); ctx.fillStyle = '#eee'; ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,.4)'; ctx.lineWidth = 1; ctx.stroke();
  }

  const sit = e.pose === 'sit';
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + cos * (rad + 5), y + sin * (rad + 5));
  ctx.strokeStyle = 'rgba(200,211,222,.5)'; ctx.lineWidth = 1.5; ctx.stroke();
  ctx.beginPath(); ctx.arc(x, y, sit ? rad - 1 : rad, 0, 7);
  ctx.fillStyle = color; ctx.fill(); ctx.lineWidth = 1.3; ctx.strokeStyle = 'rgba(0,0,0,.55)'; ctx.stroke();

  if (e.pose === 'work') { const w = 0.5 + 0.5 * Math.sin(T * 3 + sd * 6); ctx.globalAlpha = w; ctx.fillStyle = 'rgba(230,184,0,.95)'; ctx.fillRect(x + cos * (rad + 3) - 1.5, y + sin * (rad + 3) - 1.5, 3, 3); ctx.globalAlpha = 1; }
  if (e.pose === 'sniff') { ctx.beginPath(); ctx.arc(x + cos * (rad + 4), y + sin * (rad + 4) + 1, 1.6, 0, 7); ctx.fillStyle = '#cbb28c'; ctx.fill(); }
  if (e.pose === 'forage') { ctx.beginPath(); ctx.arc(x + cos * (rad + 3), y + sin * (rad + 3), 1.5, 0, 7); ctx.fillStyle = '#9c8'; ctx.fill(); }
  if (e.pose === 'talk') {
    const g = 3 + Math.sin(T * 4 + sd * 6) * 1.4;
    ctx.beginPath(); ctx.arc(x, y - rad - 3, g, Math.PI * 0.1, Math.PI * 0.9); ctx.strokeStyle = 'rgba(230,214,180,.85)'; ctx.lineWidth = 1.3; ctx.stroke();
    if (e.gest === 'laugh') sparkle(x, y - rad - 6);
  } else if (e.pose === 'groom') { ctx.beginPath(); ctx.arc(x + Math.sin(T * 4 + sd) * 3, y - rad, 1.2, 0, 7); ctx.fillStyle = 'rgba(220,220,220,.8)'; ctx.fill(); }
  else if (e.gest === 'glance') { ctx.beginPath(); ctx.arc(x + Math.sin(T * 2 + sd) * 4, y - rad - 3, 1.2, 0, 7); ctx.fillStyle = 'rgba(200,211,222,.9)'; ctx.fill(); }

  if (kind === 'resident') label(x, y - rad - 6, meta.name);
}

function label(x, y, name) { ctx.fillStyle = 'rgba(200,211,222,.85)'; ctx.font = '10px system-ui'; ctx.textAlign = 'center'; ctx.fillText(name, x, y); }

function sparkle(x, y) {
  ctx.strokeStyle = 'rgba(255,220,120,.95)'; ctx.lineWidth = 1.2;
  for (let a = 0; a < 6; a++) { const ang = a * Math.PI / 3; ctx.beginPath(); ctx.moveTo(x + Math.cos(ang) * 2, y + Math.sin(ang) * 2); ctx.lineTo(x + Math.cos(ang) * 4.5, y + Math.sin(ang) * 4.5); ctx.stroke(); }
}

function drawConversation([ax, ay], [bx, by]) {
  ctx.save(); ctx.setLineDash([2, 3]); ctx.strokeStyle = 'rgba(230,220,190,.5)'; ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke(); ctx.restore();
  const mx = (ax + bx) / 2, my = (ay + by) / 2 - 6;
  const t = (_pn / 320) % 3;
  for (let i = 0; i < 3; i++) { const p = (t + i) % 3; ctx.globalAlpha = 0.35 + 0.25 * (2 - p); ctx.beginPath(); ctx.arc(mx + (i - 1) * 3, my - p * 3, 1.3, 0, 7); ctx.fillStyle = '#f0e6cf'; ctx.fill(); }
  ctx.globalAlpha = 1;
}

function currentHappening(fr) {
  const notable = fr.events.find(([, , k]) => k === 'match' || k === 'oak' || k === 'social' || k === 'b');
  if (notable) return { who: notable[0], text: notable[1], kind: notable[2] === 'b' ? '' : notable[2] };
  if (fr.busiest && fr.busiest.count >= 3) return { who: '', text: fr.busiest.name + ' is the heart of the district just now', kind: '' };
  const soft = fr.events.find(([, , k]) => k === 'town' || k === 'micro' || k === 'moment' || k === 'wild');
  if (soft) return { who: soft[0], text: soft[1], kind: 'quiet' };
  return { who: '', text: 'A quiet moment in the district — ' + fr.phase + '.', kind: 'quiet' };
}

function renderPanels(fr) {
  document.getElementById('wd').textContent = fr.weekday;
  document.getElementById('day').textContent = fr.day;
  document.getElementById('hh').textContent = clockLabel(fr);
  document.getElementById('phase').textContent = fr.phase;
  document.getElementById('season').textContent = fr.oak.appearance + ' · ' + fr.oak.season;

  const h = currentHappening(fr), hb = document.getElementById('happening');
  hb.className = h.kind || '';
  const body = humanize(h.text).replace(/\s+via\s+.*$/, '');
  hb.innerHTML = h.who ? `<span class="who">${h.who}</span> ${body.startsWith(h.who) ? body.slice(h.who.length).trim() : body}` : body;

  const co = document.getElementById('callouts'); co.innerHTML = '';
  fr.callouts.forEach(k => { const d = document.createElement('div'); d.className = 'callout ' + k.kind; d.textContent = k.text; co.appendChild(d); });

  const sel = document.getElementById('sel');
  if (selected) {
    const e = fr.entities.find(x => x.id === selected);
    const meta = ROSTER[selected] || {};
    if (e) sel.innerHTML =
      `<div class="name"><span class="dot" style="background:${meta.color}"></span>${meta.name}</div>`
      + `<div class="meta">${placeName(e.place)}${e.moving ? ' · on the move' : ''}</div>`
      + `<div class="doing">${e.doing}</div>`
      + `<div class="hint" style="margin-top:7px">following — double-click the map to release</div>`;
  } else { sel.innerHTML = '<span class="hint">Click anyone on the map to follow them.</span>'; }

  document.getElementById('oak').innerHTML =
    `${fr.oak.ageYears} years old, ${fr.oak.appearance} this ${fr.oak.season}.<br>`
    + `${fr.oak.visits} visits · ${fr.oak.scarves} scarves · ${fr.oak.bouquets} bouquets`;

  const bd = document.getElementById('bonds');
  bd.innerHTML = fr.bonds.length ? '' : '<span class="hint">no shared history yet</span>';
  fr.bonds.forEach(b => {
    const row = document.createElement('div'); row.className = 'bond';
    row.innerHTML = `<span class="who">${b.a} &amp; ${b.b}</span>`
      + `<span class="where">${b.place ? 'the ' + b.place : ''}</span>`
      + `<span class="n">${b.meetings}×</span>`;
    bd.appendChild(row);
  });

  const t = document.getElementById('ticker'); t.innerHTML = '';
  fr.events.forEach(([who, text0, kind]) => {
    const text = humanize(text0);
    const li = document.createElement('li'); li.className = kind;
    li.innerHTML = kind === 'b' ? `<span class="who">${who}</span> ${(text.startsWith(who) ? text.slice(who.length).trim() : text)}`
                                 : `<span class="who">${who}</span> — ${text}`;
    t.appendChild(li);
  });
}

function tick(ts) {
  if (last === null) last = ts;
  _pn = ts;
  const dt = (ts - last) / 1000; last = ts;
  if (playing) {
    acc += dt * BASE_TPS * speed;
    let guard = 0;
    while (acc >= 1 && guard < 240) { eng.tick(); prev = cur; cur = JSON.parse(eng.snapshot_json()); acc -= 1; guard++; }
  }
  const f = playing ? Math.min(acc, 1) : 0;
  const ents = lerpEntities(prev, cur, f);

  let tx = VW / 2, ty = VH / 2, tz = 1;
  if (cam.follow) { const fe = ents.find(e => e.id === cam.follow); if (fe) { tx = fe.x; ty = fe.y; tz = 3.2; } }
  cam.tx += (tx - cam.tx) * 0.12; cam.ty += (ty - cam.ty) * 0.12; cam.zoom += (tz - cam.zoom) * 0.1;

  draw(ents, cur);
  if (cur.tick !== lastPanelTick) { renderPanels(cur); lastPanelTick = cur.tick; }
  requestAnimationFrame(tick);
}

async function main() {
  await init();
  eng = new WasmEngine(0);
  WORLD = JSON.parse(eng.world_json());
  WORLD.locations.forEach(l => NODES[l.id] = l);
  WORLD.entities.forEach(e => ROSTER[e.id] = e);
  cur = JSON.parse(eng.snapshot_json()); prev = cur;
  resize();
  renderPanels(cur); lastPanelTick = cur.tick;
  document.getElementById('loading').remove();
  requestAnimationFrame(tick);
}

main().catch(err => {
  const l = document.getElementById('loading');
  if (l) l.textContent = 'Failed to start: ' + err;
  console.error(err);
});
