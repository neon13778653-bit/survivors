const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
const code = scriptMatch[1];

let saveDepth = 0;
let errors = [];

const mockCv = {
  getContext: () => ({
    save: () => {
      saveDepth++;
    },
    restore: () => {
      saveDepth--;
      if(saveDepth < 0) {
        errors.push('Save depth went negative: ' + saveDepth);
      }
    },
    translate: ()=>{}, rotate: ()=>{}, scale: ()=>{}, setTransform: ()=>{},
    beginPath: ()=>{}, arc: ()=>{}, fill: ()=>{}, stroke: ()=>{}, closePath: ()=>{},
    rect: ()=>{}, fillRect: ()=>{}, strokeRect: ()=>{}, clearRect: ()=>{},
    clip: ()=>{}, roundRect: ()=>{}, ellipse: ()=>{},
    createRadialGradient: () => ({ addColorStop: ()=>{} }),
    createLinearGradient: () => ({ addColorStop: ()=>{} }),
    createPattern: () => ({}),
    drawImage: (...args)=>{},
    measureText: () => ({ width: 50 }),
    fillText: ()=>{}, strokeText: ()=>{}, setLineDash: ()=>{},
    lineTo: ()=>{}, moveTo: ()=>{}, quadraticCurveTo: ()=>{}, bezierCurveTo: ()=>{}
  }),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 400, height: 800 }),
  addEventListener: ()=>{}
};

const mockEl = {
  style: {},
  classList: { add: ()=>{}, remove: ()=>{}, toggle: ()=>{}, contains: ()=>false },
  textContent: '', innerHTML: '', addEventListener: ()=>{},
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 400, height: 800 }),
  focus: ()=>{}, blur: ()=>{}, remove: ()=>{}
};

const mockDoc = {
  documentElement: {}, body: mockEl,
  createElement: () => mockCv,
  createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => (id === 'c' ? mockCv : mockEl),
  querySelector: () => mockEl, querySelectorAll: () => [],
  addEventListener: ()=>{}
};

const mockWindow = {
  addEventListener: ()=>{},
  SafeStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  Audio: function(){ return { play: ()=>{}, pause: ()=>{} }; },
  Image: function(){ return { src: '', onload: null, complete: true, naturalWidth: 280, naturalHeight: 280 }; },
  requestAnimationFrame: () => {}, cancelAnimationFrame: () => {},
  innerWidth: 400, innerHeight: 800
};

class CanvasRenderingContext2D {}
const NodeFilter = { SHOW_TEXT: 4 };
class MutationObserver { observe() {} disconnect() {} }

const fn = new Function('window', 'document', 'Image', 'Audio', 'addEventListener', 'CanvasRenderingContext2D', 'NodeFilter', 'MutationObserver', 'requestAnimationFrame', `
  window.SafeStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  ${code}
  return {
    startGame, update, drawGame,
    spawnCyberCerberusBoss, spawnBioButcherBoss, spawnChitinReaperBoss,
    spawnNeuroOvermindBoss, spawnPatientZeroBoss,
    setSelectedLvlIdx: (idx) => { selectedLvlIdx = idx; },
    getG: () => G
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, NodeFilter, MutationObserver, mockWindow.requestAnimationFrame);

env.setSelectedLvlIdx(2);
env.startGame();
const g = env.getG();

const bosses = [
  { name: 'CyberCerberus', spawn: env.spawnCyberCerberusBoss },
  { name: 'BioButcher', spawn: env.spawnBioButcherBoss },
  { name: 'ChitinReaper', spawn: env.spawnChitinReaperBoss },
  { name: 'NeuroOvermind', spawn: env.spawnNeuroOvermindBoss },
  { name: 'PatientZero', spawn: env.spawnPatientZeroBoss }
];

for(const b of bosses){
  saveDepth = 0;
  errors = [];
  g.enemies = [];
  g.activeBoss = null;
  b.spawn();
  console.log(`\nTesting ${b.name}...`);
  for(let f = 0; f < 150; f++){
    saveDepth = 0;
    env.update(0.016);
    env.drawGame();
    if(saveDepth !== 0){
      console.error(`ERROR in ${b.name} at frame ${f}: final saveDepth = ${saveDepth}`);
      break;
    }
  }
  if(errors.length > 0){
    console.error(`Negative depth errors in ${b.name}:`, errors);
  } else if(saveDepth === 0){
    console.log(`PERFECT: ${b.name} maintains 0 stack leak across 150 frames!`);
  }
}
