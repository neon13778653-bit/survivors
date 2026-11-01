const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
if(!scriptMatch){
  console.error("Script tag not found!");
  process.exit(1);
}
const code = scriptMatch[1];

const listeners = {};
const calls = [];
const mockCv = {
  getContext: () => ({
    save: ()=>{}, restore: ()=>{}, translate: ()=>{}, rotate: ()=>{}, scale: ()=>{},
    setTransform: ()=>{},
    beginPath: ()=>{}, arc: ()=>{}, fill: ()=>{}, stroke: ()=>{}, closePath: ()=>{},
    rect: ()=>{}, fillRect: ()=>{}, strokeRect: ()=>{}, clearRect: ()=>{},
    clip: ()=>{},
    roundRect: ()=>{},
    ellipse: ()=>{},
    createRadialGradient: () => ({ addColorStop: ()=>{} }),
    createLinearGradient: () => ({ addColorStop: ()=>{} }),
    createPattern: () => ({}),
    drawImage: (...args)=>{},
    measureText: () => ({ width: 50 }),
    fillText: ()=>{},
    strokeText: ()=>{},
    setLineDash: ()=>{},
    lineTo: ()=>{}, moveTo: ()=>{}, quadraticCurveTo: ()=>{}, bezierCurveTo: ()=>{}
  }),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  addEventListener: ()=>{}
};

const mockEl = {
  style: {},
  classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{}, contains: ()=>false },
  textContent: '',
  innerHTML: '',
  addEventListener: ()=>{},
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  focus: ()=>{}, blur: ()=>{}, remove: ()=>{}
};

const mockDoc = {
  documentElement: {},
  body: mockEl,
  createElement: () => mockCv,
  createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => {
    if(id === 'c') return mockCv;
    return mockEl;
  },
  querySelector: () => mockEl,
  querySelectorAll: () => [],
  addEventListener: (evt, fn) => { listeners[evt] = fn; }
};

const mockWindow = {
  addEventListener: (evt, fn) => { listeners[evt] = fn; },
  SafeStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  Audio: function(){ return { play: ()=>{}, pause: ()=>{} }; },
  Image: function(){ return { src: '', onload: null, complete: true, naturalWidth: 100, naturalHeight: 100 }; },
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
class MutationObserver { observe() {} disconnect() {} }

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
    warpToWave,
    startGame,
    update,
    drawGame,
    setSelectedLvlIdx: (idx) => { selectedLvlIdx = idx; },
    getG: () => (typeof G !== 'undefined' ? G : null),
    setG: (val) => { G = val; }
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, NodeFilter, MutationObserver, mockWindow.requestAnimationFrame);

console.log("Testing full frame simulation for all 5 bosses...");

function runBossSimulation(bossName, waveNum){
  console.log(`\n--- Simulating Boss ${bossName} (Wave ${waveNum}) ---`);
  // Start game using real startGame() logic
  env.setSelectedLvlIdx(2);
  env.save.selectedLvl = 3;
  env.startGame();
  const g = env.getG();
  if(!g) throw new Error("G was not created by startGame()");

  // Warp to wave
  env.warpToWave(waveNum);
  const boss = g.enemies.find(e => e.isBoss);
  console.log(`Spawned: ${boss?.name} (${boss?.bossId})`);

  // Run 300 update steps and draw calls (approx 5 seconds of gameplay)
  for(let i = 0; i < 300; i++){
    try {
      env.update(0.016);
    } catch(err) {
      console.error(`ERROR in update() at step ${i} for ${bossName}:`, err);
      throw err;
    }
    try {
      env.drawGame();
    } catch(err) {
      console.error(`ERROR in drawGame() at step ${i} for ${bossName}:`, err);
      throw err;
    }
  }
  console.log(`SUCCESS: 300 frames simulated cleanly for ${bossName}!`);
}

try {
  runBossSimulation('CyberCerberus', 10);
  runBossSimulation('BioButcher', 20);
  runBossSimulation('ChitinReaper', 30);
  runBossSimulation('NeuroOvermind', 40);
  runBossSimulation('PatientZero', 50);
  console.log("\nALL BOSS SIMULATIONS PASSED WITHOUT ERROR!");
} catch(e) {
  console.error("FATAL ERROR DURING SIMULATION:", e);
}
