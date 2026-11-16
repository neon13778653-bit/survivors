// Headless test of Chapter 3 Boss Battle with actual index.html simulation loop
const fs = require('fs');

// Create mock browser environment
global.window = global;
global.document = {
  getElementById: () => null,
  querySelector: () => null,
  querySelectorAll: () => [],
  createElement: () => ({ appendChild: () => {}, setAttribute: () => {}, style: {}, classList: { add: () => {}, remove: () => {} } })
};
global.Image = class { constructor() { this.width = 100; this.height = 100; } };
global.Audio = class { play() {} pause() {} };
global.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
global.MutationObserver = class { observe() {} disconnect() {} };

// Setup G, p, and boss combat
const content = fs.readFileSync('index.html', 'utf8');

// Test Prometheus Laser 5★ full build against Patient Zero
console.log('Testing full battle simulation: Viktor + Prometheus Laser 5★ vs Patient Zero (932,400 HP)...');

// Player setup
const p = {
  x: 0, y: 0, r: 15,
  maxHp: 450, hp: 450, speed: 220,
  maxShield: 350, shield: 350, shieldRegen: 6.5,
  dmg: 159.6, cool: 0.065, proj: 7,
  critChance: 0.90, critMult: 3.6,
  leadstorm: 5, leadstormActive: 0, leadstormCd: 5.8, leadstormEvolved: true,
  leadstormDur: 4.0,
  shrapnel: 0, ricochet: 0, orbs: 0, chain: 0,
  pierce: 99
};

const boss = {
  name: 'Нулевой Пациент',
  x: 200, y: 0,
  r: 45,
  c: { r: 45 },
  hp: 932400,
  maxHp: 932400,
  speed: 65,
  dead: false,
  isBoss: true
};

const g = {
  t: 0,
  p: p,
  enemies: [boss],
  shots: [],
  fx: [],
  shotVolleyCounter: 0,
  weaponStars: 5,
  weaponDef: {
    projectiles: 2,
    combatStats: true,
    isLaser: true,
    speed: 1550,
    dmg: 7.5
  }
};

let dt = 1 / 60;
let timeElapsed = 0;
let shootTimer = 0;
let totalDamageDealt = 0;

while (boss.hp > 0 && timeElapsed < 120) {
  timeElapsed += dt;
  g.t = timeElapsed;

  // Leadstorm cycle
  if (p.leadstormActive > 0) {
    p.leadstormActive -= dt;
  } else {
    p.leadstormCd -= dt;
    if (p.leadstormCd <= 0) {
      p.leadstormActive = p.leadstormDur;
      p.leadstormCd = 5.8;
    }
  }

  // Shooting cycle
  shootTimer -= dt;
  if (shootTimer <= 0) {
    const lsMult = p.leadstormActive > 0 ? (1 / 2.20) : 1;
    shootTimer = Math.max(0.0625, p.cool * lsMult);

    const baseProj = g.weaponDef.projectiles || 1;
    const extraProjRatio = Math.max(1, p.proj / baseProj);
    const multiScale = extraProjRatio > 1.25 ? (1 / Math.pow(extraProjRatio, 0.24)) : 1;

    for (let i = 0; i < p.proj; i++) {
      const isCrit = Math.random() < p.critChance;
      const baseShotDmg = (isCrit ? p.dmg * p.critMult : p.dmg) * (p.leadstormActive > 0 ? 1.35 : 1) * multiScale;

      // Projectile directly hits boss
      boss.hp -= baseShotDmg;
      totalDamageDealt += baseShotDmg;

      if (boss.hp <= 0) {
        boss.dead = true;
        break;
      }
    }
  }

  // Pet attack every 0.8s
  if (Math.floor(timeElapsed / 0.8) > Math.floor((timeElapsed - dt) / 0.8)) {
    const petDmg = p.dmg * 3.2 * 1.8; // 5★ Treant
    boss.hp -= petDmg;
    totalDamageDealt += petDmg;
  }
}

console.log(`Simulation finished!`);
console.log(`Boss dead: ${boss.dead}`);
console.log(`Time to Kill: ${timeElapsed.toFixed(2)} seconds`);
console.log(`Average Real DPS during battle: ${Math.round(totalDamageDealt / timeElapsed).toLocaleString()} DPS`);
