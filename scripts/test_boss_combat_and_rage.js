const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
const code = scriptMatch[1];

const listeners = {};
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
  focus: ()=>{}, blur: ()=>{}, remove: ()=>{},
  querySelectorAll: () => [],
  querySelector: () => null
};

const mockDoc = {
  documentElement: {},
  body: mockEl,
  createElement: () => mockCv,
  createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => (id === 'c' ? mockCv : mockEl),
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
  fillText: ()=>{}, strokeText: ()=>{}, measureText: ()=>({width: 50}), clip: ()=>{}
};

const NodeFilter = { SHOW_TEXT: 4 };
class MutationObserver { observe() {} disconnect() {} }

const fn = new Function('window', 'document', 'Image', 'Audio', 'addEventListener', 'CanvasRenderingContext2D', 'NodeFilter', 'MutationObserver', 'requestAnimationFrame', `
  window.SafeStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  ${code}
  return {
    LEVELS,
    save,
    warpToWave,
    startGame,
    update,
    drawGame,
    hurt,
    setSelectedLvlIdx: (idx) => { selectedLvlIdx = idx; },
    getG: () => (typeof G !== 'undefined' ? G : null)
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, NodeFilter, MutationObserver, mockWindow.requestAnimationFrame);

console.log("=== VERIFYING FULL BOSS COMBAT & RAGE MODE FOR ALL 5 BOSSES ===");

function testFullBossCombat(bossName, waveNum){
  console.log(`\nTesting Boss: ${bossName} (Wave ${waveNum})`);
  env.setSelectedLvlIdx(2);
  env.save.selectedLvl = 3;
  env.startGame();
  const g = env.getG();

  env.warpToWave(waveNum);
  const boss = g.enemies.find(e => e.isBoss);
  console.log(`1. Spawned: ${boss.name} (HP: ${boss.hp})`);

  // Simulate emergence (200 frames ~ 3.2s)
  for(let i = 0; i < 200; i++){
    env.update(0.016);
    env.drawGame();
  }
  console.log(`2. Emergence completed: state = ${boss.spawnState}`);

  // Deal damage to trigger Enrage (< 50% HP)
  boss.phaseGuardT = 0;
  boss.immortal = false;
  boss.hp = boss.maxHp * 0.45;
  env.update(0.016);
  env.drawGame();
  console.log(`3. Enrage triggered: enraged = ${boss.enraged}`);
  if(!boss.enraged) throw new Error(`${bossName} failed to enter enraged mode!`);

  // Run 150 frames in Rage Mode with active abilities and shockwaves
  for(let i = 0; i < 150; i++){
    env.update(0.016);
    env.drawGame();
  }
  console.log(`4. Rage Mode survived 150 frames cleanly (Active shockwaves: ${g.bossShockwaves?.length || 0})`);

  // Defeat boss (boss has 5% single-hit damage cap, so reduce hp first)
  boss.phaseGuardT = 0;
  boss.immortal = false;
  boss.hp = 1;
  env.hurt(boss, 10);
  env.update(0.016);
  env.drawGame();
  console.log(`5. Defeat handled cleanly: boss.dead = ${boss.dead}, arena cleared = ${!g.bossArena}`);
  if(!boss.dead || g.bossArena) throw new Error(`${bossName} defeat failed!`);
}

try {
  testFullBossCombat('CyberCerberus', 10);
  testFullBossCombat('BioButcher', 20);
  testFullBossCombat('ChitinReaper', 30);
  testFullBossCombat('NeuroOvermind', 40);
  testFullBossCombat('PatientZero', 50);
  console.log("\n==============================================");
  console.log("ALL 5 BOSS COMBAT & RAGE CYCLES PASSED 100%!");
  console.log("==============================================");
} catch(e) {
  console.error("FATAL COMBAT ERROR:", e);
  process.exit(1);
}
