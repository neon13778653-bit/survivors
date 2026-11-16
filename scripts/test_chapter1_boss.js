const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
const code = scriptMatch[1];

const listeners = {};
const mockCv = {
  getContext: () => ({
    save: () => {}, restore: () => {}, translate: () => {}, rotate: () => {}, scale: () => {},
    setTransform: () => {}, beginPath: () => {}, arc: () => {}, fill: () => {}, stroke: () => {}, closePath: () => {},
    rect: () => {}, fillRect: () => {}, strokeRect: () => {}, clearRect: () => {}, clip: () => {}, roundRect: () => {}, ellipse: () => {},
    createRadialGradient: () => ({ addColorStop: () => {} }), createLinearGradient: () => ({ addColorStop: () => {} }),
    createPattern: () => ({}), drawImage: () => {}, measureText: () => ({ width: 50 }), fillText: () => {}, strokeText: () => {},
    setLineDash: () => {}, lineTo: () => {}, moveTo: () => {}, quadraticCurveTo: () => {}, bezierCurveTo: () => {}
  }),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  addEventListener: () => {}
};

const mockEl = {
  style: {}, classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
  textContent: '', innerHTML: '', addEventListener: () => {},
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  focus: () => {}, blur: () => {}, remove: () => {}, querySelectorAll: () => [], querySelector: () => mockEl
};

const mockDoc = {
  documentElement: {}, body: mockEl, createElement: () => mockCv, createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => (id === 'c' ? mockCv : mockEl), querySelector: () => mockEl, querySelectorAll: () => [],
  addEventListener: (evt, fn) => { listeners[evt] = fn; }
};

const mockWindow = {
  addEventListener: (evt, fn) => { listeners[evt] = fn; },
  SafeStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  Audio: function () { return { play: () => {}, pause: () => {} }; },
  Image: function () { return { src: '', onload: null, complete: true, naturalWidth: 100, naturalHeight: 100 }; },
  requestAnimationFrame: () => {}, cancelAnimationFrame: () => {},
  innerWidth: 1920, innerHeight: 1080
};

class CanvasRenderingContext2D {}
CanvasRenderingContext2D.prototype = { fillText: () => {}, strokeText: () => {}, measureText: () => ({ width: 50 }) };

const fn = new Function('window', 'document', 'Image', 'Audio', 'addEventListener', 'CanvasRenderingContext2D', 'NodeFilter', 'MutationObserver', 'requestAnimationFrame', `
  window.SafeStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  ${code}
  return {
    save, startGame, update, warpToWave, keys,
    setSelectedLvlIdx: (idx) => { selectedLvlIdx = idx; },
    getG: () => (typeof G !== 'undefined' ? G : null)
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, { SHOW_TEXT: 4 }, class { observe() {} disconnect() {} }, mockWindow.requestAnimationFrame);

env.setSelectedLvlIdx(0);
env.save.selectedChar = 'marcus';
env.save.equip = { weapon: 'w_rebel', armor: 'sh_riot', pet: 'pet_slime' };
env.save.hpLv = 3; env.save.dmgLv = 3; env.save.spdLv = 2;
env.startGame();
const g = env.getG();
env.warpToWave(10);

const boss = g.enemies.find(e => e.isBoss);
console.log(`Gravedigger spawned: HP=${boss.hp}, pos=(${boss.x.toFixed(0)}, ${boss.y.toFixed(0)}) Player pos=(${g.p.x.toFixed(0)}, ${g.p.y.toFixed(0)})`);

let hitsTaken = 0;
let lastHp = g.p.hp;

for (let step = 0; step < 2500; step++) {
  if (!g.run || boss.dead) break;

  // Dodge logic
  const dx = g.p.x - boss.x;
  const dy = g.p.y - boss.y;
  const d = Math.hypot(dx, dy);

  let moveX = 0, moveY = 0;
  if (d < 180) {
    moveX = dx / d;
    moveY = dy / d;
  } else if (d > 250) {
    moveX = -dx / d * 0.5;
    moveY = -dy / d * 0.5;
  } else {
    // Circling
    moveX = -dy / d;
    moveY = dx / d;
  }

  // Arena Center Orbiting (keeps player in the safe central ring)
  if (g.bossArena) {
    const cx = g.bossArena.x + g.bossArena.size / 2;
    const cy = g.bossArena.y + g.bossArena.size / 2;
    const toCenterDist = Math.hypot(g.p.x - cx, g.p.y - cy);
    if (toCenterDist > 250) {
      // Pull strongly back towards center ring
      moveX += (cx - g.p.x) / toCenterDist * 2.5;
      moveY += (cy - g.p.y) / toCenterDist * 2.5;
    }
  }

  const mLen = Math.hypot(moveX, moveY);
  if (mLen > 0.1) { moveX /= mLen; moveY /= mLen; }
  env.keys.KeyD = moveX > 0.15;
  env.keys.KeyA = moveX < -0.15;
  env.keys.KeyS = moveY > 0.15;
  env.keys.KeyW = moveY < -0.15;

  if (step >= 1700 && step <= 1720) {
    console.log(`step ${step}: p=(${g.p.x.toFixed(1)}, ${g.p.y.toFixed(1)}) b=(${boss.x.toFixed(1)}, ${boss.y.toFixed(1)}) d=${d.toFixed(1)} arena_x=[${g.bossArena.x.toFixed(0)}, ${(g.bossArena.x+g.bossArena.size).toFixed(0)}] arena_y=[${g.bossArena.y.toFixed(0)}, ${(g.bossArena.y+g.bossArena.size).toFixed(0)}]`);
  }

  env.update(0.05);

  if (g.p.hp < lastHp) {
    hitsTaken++;
    console.log(`  [step ${step}, t=${g.t.toFixed(1)}s] Player took hit! HP: ${lastHp.toFixed(0)} -> ${g.p.hp.toFixed(0)} (Boss action: ${boss.action}, Boss HP: ${boss.hp})`);
    lastHp = g.p.hp;
  }
}

console.log(`Result: Boss dead=${boss.dead} (HP remaining: ${boss.hp}), Player HP=${g.p.hp.toFixed(0)}, Hits taken=${hitsTaken}`);
