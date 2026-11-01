const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
if(!scriptMatch){
  console.error("Script tag not found!");
  process.exit(1);
}
const code = scriptMatch[1];

// Mock minimal browser environment
const listeners = {};
const mockCv = {
  getContext: () => ({
    save: ()=>{}, restore: ()=>{}, translate: ()=>{}, rotate: ()=>{}, scale: ()=>{},
    setTransform: ()=>{},
    beginPath: ()=>{}, arc: ()=>{}, fill: ()=>{}, stroke: ()=>{}, closePath: ()=>{},
    rect: ()=>{}, fillRect: ()=>{}, strokeRect: ()=>{}, clearRect: ()=>{},
    createRadialGradient: () => ({ addColorStop: ()=>{} }),
    createLinearGradient: () => ({ addColorStop: ()=>{} }),
    drawImage: ()=>{}, measureText: () => ({ width: 50 }), fillText: ()=>{},
    setLineDash: ()=>{}, lineTo: ()=>{}, moveTo: ()=>{}, quadraticCurveTo: ()=>{}, bezierCurveTo: ()=>{}
  }),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  addEventListener: ()=>{}
};

const mockDoc = {
  documentElement: {},
  body: {},
  createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => {
    if(id === 'c') return mockCv;
    return {
      style: {},
      classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{}, contains: ()=>false },
      textContent: '',
      innerHTML: '',
      addEventListener: ()=>{},
      getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 })
    };
  },
  querySelector: () => null,
  querySelectorAll: () => [],
  addEventListener: (evt, fn) => { listeners[evt] = fn; }
};

const mockWindow = {
  addEventListener: (evt, fn) => { listeners[evt] = fn; },
  SafeStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  Audio: function(){ return { play: ()=>{}, pause: ()=>{} }; },
  Image: function(){ return { src: '', onload: null }; },
  requestAnimationFrame: () => {},
  cancelAnimationFrame: () => {},
  innerWidth: 1920,
  innerHeight: 1080
};

class CanvasRenderingContext2D {}
CanvasRenderingContext2D.prototype = {
  fillText: ()=>{}, strokeText: ()=>{}, measureText: ()=>({width: 50})
};

const NodeFilter = { SHOW_TEXT: 4 };

class MutationObserver {
  observe() {}
  disconnect() {}
}

const fn = new Function('window', 'document', 'Image', 'Audio', 'addEventListener', 'CanvasRenderingContext2D', 'NodeFilter', 'MutationObserver', 'requestAnimationFrame', `
  window.SafeStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  ${code}
  return {
    LEVELS,
    save,
    spawnCyberCerberusBoss,
    spawnBioButcherBoss,
    spawnChitinReaperBoss,
    spawnNeuroOvermindBoss,
    spawnPatientZeroBoss,
    testSkipWaves,
    warpToWave,
    testSkipBoss,
    getG: () => (typeof G !== 'undefined' ? G : null),
    setG: (val) => { G = val; }
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, NodeFilter, MutationObserver, mockWindow.requestAnimationFrame);
console.log("Environment initialized successfully.");

// Check Levels
console.log("Level 3 check:", env.LEVELS.find(l => l.id === 3)?.name);
if(!env.save.unlockedLvls.includes(3)){
  console.error("FAIL: Chapter 3 is not in save.unlockedLvls!");
  process.exit(1);
}
console.log("save.unlockedLvls:", env.save.unlockedLvls);

// Mock Game object for Chapter 3
function setupGame(){
  const g = {
    run: true,
    pause: false,
    wave: 1,
    lvlConfig: env.LEVELS.find(l => l.id === 3),
    enemies: [],
    bullets: [],
    airdrops: [],
    fx: [],
    p: { x: 500, y: 500, hp: 100, maxHp: 100 },
    activeBoss: null,
    bossArena: null,
    bossWarning: null,
    t: 0
  };
  env.setG(g);
  return g;
}

// Test 1: Cyber Cerberus at Wave 10
let g = setupGame();
env.warpToWave(10);
let boss = g.enemies.find(e => e.isBoss);
console.log("Wave 10 Boss:", boss?.name, "bossId:", boss?.bossId, "HP:", boss?.hp);
if(!boss || boss.bossId !== 'cyber_cerberus'){
  console.error("FAIL: Wave 10 boss is not cyber_cerberus!");
  process.exit(1);
}

// Test 2: Bio Butcher at Wave 20
g = setupGame();
env.warpToWave(20);
boss = g.enemies.find(e => e.isBoss);
console.log("Wave 20 Boss:", boss?.name, "bossId:", boss?.bossId, "HP:", boss?.hp);
if(!boss || boss.bossId !== 'bio_butcher'){
  console.error("FAIL: Wave 20 boss is not bio_butcher!");
  process.exit(1);
}

// Test 3: Chitin Reaper at Wave 30
g = setupGame();
env.warpToWave(30);
boss = g.enemies.find(e => e.isBoss);
console.log("Wave 30 Boss:", boss?.name, "bossId:", boss?.bossId, "HP:", boss?.hp);
if(!boss || boss.bossId !== 'chitin_reaper'){
  console.error("FAIL: Wave 30 boss is not chitin_reaper!");
  process.exit(1);
}

// Test 4: Neuro Overmind at Wave 40
g = setupGame();
env.warpToWave(40);
boss = g.enemies.find(e => e.isBoss);
console.log("Wave 40 Boss:", boss?.name, "bossId:", boss?.bossId, "HP:", boss?.hp);
if(!boss || boss.bossId !== 'neuro_overmind'){
  console.error("FAIL: Wave 40 boss is not neuro_overmind!");
  process.exit(1);
}

// Test 5: Patient Zero at Wave 50
g = setupGame();
env.warpToWave(50);
boss = g.enemies.find(e => e.isBoss);
console.log("Wave 50 Boss:", boss?.name, "bossId:", boss?.bossId, "HP:", boss?.hp);
if(!boss || boss.bossId !== 'patient_zero'){
  console.error("FAIL: Wave 50 boss is not patient_zero!");
  process.exit(1);
}

console.log("Testing testSkipBoss sequentially through all 5 bosses...");
g = setupGame();
// Wave 1 -> skip to Boss 1
env.testSkipBoss();
let active = g.enemies.find(e => e.isBoss && !e.dead);
console.log("Step 1:", g.wave, active?.name, active?.bossId);
if(g.wave !== 10 || active?.bossId !== 'cyber_cerberus') throw new Error("Step 1 failed");

// Defeat Boss 1
env.testSkipBoss();
// Skip to Boss 2
env.testSkipBoss();
active = g.enemies.find(e => e.isBoss && !e.dead);
console.log("Step 2:", g.wave, active?.name, active?.bossId);
if(g.wave !== 20 || active?.bossId !== 'bio_butcher') throw new Error("Step 2 failed");

// Defeat Boss 2
env.testSkipBoss();
// Skip to Boss 3
env.testSkipBoss();
active = g.enemies.find(e => e.isBoss && !e.dead);
console.log("Step 3:", g.wave, active?.name, active?.bossId);
if(g.wave !== 30 || active?.bossId !== 'chitin_reaper') throw new Error("Step 3 failed");

// Defeat Boss 3
env.testSkipBoss();
// Skip to Boss 4
env.testSkipBoss();
active = g.enemies.find(e => e.isBoss && !e.dead);
console.log("Step 4:", g.wave, active?.name, active?.bossId);
if(g.wave !== 40 || active?.bossId !== 'neuro_overmind') throw new Error("Step 4 failed");

// Defeat Boss 4
env.testSkipBoss();
// Skip to Boss 5
env.testSkipBoss();
active = g.enemies.find(e => e.isBoss && !e.dead);
console.log("Step 5:", g.wave, active?.name, active?.bossId);
if(g.wave !== 50 || active?.bossId !== 'patient_zero') throw new Error("Step 5 failed");

console.log("ALL 5 BOSS PIPELINE VERIFICATIONS PASSED 100%!");
