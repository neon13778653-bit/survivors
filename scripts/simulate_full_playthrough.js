const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
  console.error("Script tag not found!");
  process.exit(1);
}
const code = scriptMatch[1];

const listeners = {};
const mockCv = {
  getContext: () => ({
    save: () => {}, restore: () => {}, translate: () => {}, rotate: () => {}, scale: () => {},
    setTransform: () => {},
    beginPath: () => {}, arc: () => {}, fill: () => {}, stroke: () => {}, closePath: () => {},
    rect: () => {}, fillRect: () => {}, strokeRect: () => {}, clearRect: () => {},
    clip: () => {}, roundRect: () => {}, ellipse: () => {},
    createRadialGradient: () => ({ addColorStop: () => {} }),
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createPattern: () => ({}),
    drawImage: () => {},
    measureText: () => ({ width: 50 }),
    fillText: () => {}, strokeText: () => {},
    setLineDash: () => {},
    lineTo: () => {}, moveTo: () => {}, quadraticCurveTo: () => {}, bezierCurveTo: () => {}
  }),
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  addEventListener: () => {}
};

const levelupBox = {
  style: {},
  _buttons: [],
  get innerHTML() { return ''; },
  set innerHTML(htmlStr) {
    this._buttons = [];
    const re = /data-i="(\d+)"/g;
    let match;
    while ((match = re.exec(htmlStr)) !== null) {
      const idx = parseInt(match[1], 10);
      this._buttons.push({
        dataset: { i: idx },
        onclick: null
      });
    }
  },
  querySelectorAll(sel) {
    if (sel === 'button') return this._buttons;
    return [];
  }
};

const mockEl = {
  style: {},
  classList: {
    add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false
  },
  textContent: '',
  innerHTML: '',
  addEventListener: () => {},
  getBoundingClientRect: () => ({ left: 0, top: 0, width: 800, height: 600 }),
  focus: () => {}, blur: () => {}, remove: () => {},
  querySelectorAll: (selector) => {
    if (selector === 'button') return levelupBox._buttons;
    return [];
  },
  querySelector: () => mockEl
};

const mockDoc = {
  documentElement: {},
  body: mockEl,
  createElement: () => mockCv,
  createTreeWalker: () => ({ nextNode: () => null }),
  getElementById: (id) => {
    if (id === 'c') return mockCv;
    if (id === 'levelup-cards-box') {
      return levelupBox;
    }
    return mockEl;
  },
  querySelector: () => mockEl,
  querySelectorAll: () => [],
  addEventListener: (evt, fn) => { listeners[evt] = fn; }
};

const mockWindow = {
  addEventListener: (evt, fn) => { listeners[evt] = fn; },
  SafeStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  Audio: function () { return { play: () => {}, pause: () => {} }; },
  Image: function () { return { src: '', onload: null, complete: true, naturalWidth: 100, naturalHeight: 100 }; },
  requestAnimationFrame: () => {},
  cancelAnimationFrame: () => {},
  innerWidth: 1920,
  innerHeight: 1080
};

class CanvasRenderingContext2D {}
CanvasRenderingContext2D.prototype = {
  fillText: () => {}, strokeText: () => {}, measureText: () => ({ width: 50 })
};

const NodeFilter = { SHOW_TEXT: 4 };
class MutationObserver { observe() {} disconnect() {} }

const fn = new Function('window', 'document', 'Image', 'Audio', 'addEventListener', 'CanvasRenderingContext2D', 'NodeFilter', 'MutationObserver', 'requestAnimationFrame', `
  window.SafeStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  ${code}
  return {
    LEVELS,
    CHARACTERS,
    ITEMS,
    save,
    CONFIG,
    startGame,
    update,
    drawGame,
    die,
    keys,
    joy,
    setSelectedLvlIdx: (idx) => { selectedLvlIdx = idx; },
    getG: () => (typeof G !== 'undefined' ? G : null),
    setG: (val) => { G = val; }
  };
`);

const env = fn(mockWindow, mockDoc, mockWindow.Image, mockWindow.Audio, mockWindow.addEventListener, CanvasRenderingContext2D, NodeFilter, MutationObserver, mockWindow.requestAnimationFrame);

function simulateRun(chapterNum, charId, weaponId, metaUpgrades = {}, botSkill = 'normal') {
  console.log(`\n======================================================`);
  console.log(`RUN: Chapter ${chapterNum} | Hero: ${charId} | Weapon: ${weaponId}`);
  console.log(`Meta:`, JSON.stringify(metaUpgrades), `| Skill: ${botSkill}`);
  console.log(`======================================================`);

  env.save.selectedChar = charId;
  env.save.equip = {
    weapon: weaponId,
    armor: metaUpgrades.shield || null,
    pet: metaUpgrades.pet || null,
    art1: metaUpgrades.art1 || null,
    art2: metaUpgrades.art2 || null
  };
  env.save.unlockedLvls = [1, 2, 3];
  env.save.hpLv = metaUpgrades.hpLv || 0;
  env.save.dmgLv = metaUpgrades.dmgLv || 0;
  env.save.spdLv = metaUpgrades.spdLv || 0;
  env.save.rateLv = metaUpgrades.rateLv || 0;
  env.save.pickLv = metaUpgrades.pickLv || 0;

  env.setSelectedLvlIdx(chapterNum - 1);
  env.startGame();
  const g = env.getG();
  if (!g) throw new Error("Game failed to initialize");

  const dt = 0.05;
  const maxSteps = 50000;
  let step = 0;
  let victory = false;
  let minHp = g.p.hp;
  let maxHpSeen = g.p.maxHp;
  let lastReportWave = 1;
  let bossKillTimes = {};
  let currentBossStart = 0;
  let currentBossName = '';
  let abilitiesPicked = 0;

  while (g.run && step < maxSteps) {
    step++;

    // 1. Handle Level-Up
    if (g.pause) {
      if (levelupBox._buttons.length > 0) {
        // Prioritize first choice
        const choice = 0;
        const b = levelupBox._buttons[choice];
        if (b && typeof b.onclick === 'function') {
          b.onclick();
          abilitiesPicked++;
        } else {
          g.pause = false;
        }
      } else {
        g.pause = false;
      }
    }

    // 2. High-Performance Boids/Potential Field Kiting Navigation
    const p = g.p;
    let repX = 0, repY = 0;
    let nearestDist = 9999;
    let nearestEnemy = null;
    let enemyCount = 0;

    for (const e of g.enemies) {
      if (e.dead) continue;
      const dx = p.x - e.x;
      const dy = p.y - e.y;
      const d = Math.hypot(dx, dy);
      if (d < nearestDist) {
        nearestDist = d;
        nearestEnemy = e;
      }

      if (d < 300) {
        // Inverse square repulsive field
        const weight = (e.isBoss ? 4.0 : 1.0) / Math.max(15, d * d);
        repX += (dx / (d || 1)) * weight;
        repY += (dy / (d || 1)) * weight;
        enemyCount++;
      }
    }

    let moveX = 0, moveY = 0;
    if (enemyCount > 0) {
      // Normalize repulsive force
      const repLen = Math.hypot(repX, repY);
      if (repLen > 0.0001) {
        moveX = repX / repLen;
        moveY = repY / repLen;
      }

      // Add tangential strafing to circle around the horde
      if (nearestDist > 110) {
        moveX += -moveY * 0.45;
        moveY += moveX * 0.45;
      }
    } else {
      // Move toward closest gem / pickup if no enemies threatening
      if (g.gems && g.gems.length > 0) {
        const gm = g.gems[0];
        const gdx = gm.x - p.x, gdy = gm.y - p.y;
        const gd = Math.hypot(gdx, gdy);
        moveX = gdx / (gd || 1);
        moveY = gdy / (gd || 1);
      }
    }

    // Boss Shockwave and Telegraph Avoidance
    if (g.bossShockwaves && g.bossShockwaves.length > 0) {
      for (const sw of g.bossShockwaves) {
        const swDx = p.x - sw.x, swDy = p.y - sw.y;
        const swDist = Math.hypot(swDx, swDy);
        if (swDist < 140) {
          moveX += (swDx / (swDist || 1)) * 2.5;
          moveY += (swDy / (swDist || 1)) * 2.5;
        }
      }
    }

    // Arena boundary containment
    if (g.bossArena) {
      const ax = g.bossArena.x, ay = g.bossArena.y, asize = g.bossArena.size;
      const pad = 80;
      if (p.x < ax + pad) moveX += 2.0;
      if (p.x > ax + asize - pad) moveX -= 2.0;
      if (p.y < ay + pad) moveY += 2.0;
      if (p.y > ay + asize - pad) moveY -= 2.0;
    }

    const moveLen = Math.hypot(moveX, moveY);
    if (moveLen > 0.1) {
      moveX /= moveLen;
      moveY /= moveLen;
    }

    env.keys.KeyD = moveX > 0.15;
    env.keys.KeyA = moveX < -0.15;
    env.keys.KeyS = moveY > 0.15;
    env.keys.KeyW = moveY < -0.15;

    // 3. Track Boss Events
    const boss = g.enemies.find(e => e.isBoss && !e.dead);
    if (boss && !currentBossName) {
      currentBossName = boss.name;
      currentBossStart = g.t;
      console.log(`  [t=${g.t.toFixed(1)}s, W${g.wave}] ⚔️ BOSS SPAWNED: ${boss.name} (HP: ${boss.hp.toLocaleString()})`);
    } else if (!boss && currentBossName) {
      const duration = g.t - currentBossStart;
      bossKillTimes[currentBossName] = duration;
      console.log(`  [t=${g.t.toFixed(1)}s, W${g.wave}] 💥 BOSS DEFEATED: ${currentBossName} in ${duration.toFixed(1)}s!`);
      currentBossName = '';
    }

    // 4. Update Game Step
    try {
      env.update(dt);
    } catch (err) {
      console.error(`FATAL CRASH in update() at wave ${g.wave}, step ${step}:`, err);
      return { success: false, crash: true, error: err.message };
    }

    if (p.hp < minHp) minHp = p.hp;
    if (p.maxHp > maxHpSeen) maxHpSeen = p.maxHp;

    if (g.wave > lastReportWave) {
      console.log(`  [t=${g.t.toFixed(1)}s] Wave ${lastReportWave} cleared -> Wave ${g.wave} | Lv:${g.lvl} HP:${p.hp.toFixed(0)}/${p.maxHp.toFixed(0)} Kills:${g.kills} Abilities:${abilitiesPicked}`);
      lastReportWave = g.wave;
    }

    if (!g.run) {
      if (p.hp > 0) {
        victory = true;
      }
      break;
    }
  }

  const result = {
    chapter: chapterNum,
    victory,
    finalWave: g.wave,
    maxWaves: g.lvlConfig?.maxWaves || 30,
    timeSurvived: g.t,
    finalLvl: g.lvl,
    abilitiesPicked,
    kills: g.kills,
    coins: g.coinsCollected,
    crystals: g.crystalsCollected,
    minHpRecorded: minHp,
    maxHpAchieved: maxHpSeen,
    bossKills: bossKillTimes
  };

  console.log(`\nRUN SUMMARY: ${victory ? '🏆 VICTORY!' : '💀 DEFEAT'}`);
  console.log(`  Final Wave: ${result.finalWave}/${result.maxWaves}`);
  console.log(`  Survive Time: ${result.timeSurvived.toFixed(1)}s (${(result.timeSurvived / 60).toFixed(1)} min)`);
  console.log(`  Level Reached: ${result.finalLvl} (${result.abilitiesPicked} abilities chosen)`);
  console.log(`  Kills: ${result.kills}`);
  console.log(`  Min HP: ${result.minHpRecorded.toFixed(1)} / Max HP: ${result.maxHpAchieved.toFixed(1)}`);
  console.log(`  Boss Fights:`, JSON.stringify(result.bossKills));
  return result;
}

// 1. Chapter 1: Standard Starter Progression (John + M1911)
simulateRun(1, 'john', 'w_pistol', { hpLv: 2, dmgLv: 2, spdLv: 1, shield: 'sh_buckler' });

// 2. Chapter 1: Shotgun Build (Rebel Sawed-off, 1★)
simulateRun(1, 'marcus', 'w_rebel', { hpLv: 3, dmgLv: 3, spdLv: 2, shield: 'sh_riot', pet: 'pet_slime' });

// 3. Chapter 2: Midgame Build (Vector SMG + Titan Shield)
simulateRun(2, 'leon', 'w_vector', { hpLv: 5, dmgLv: 5, spdLv: 4, rateLv: 3, shield: 'sh_plasma', pet: 'pet_bat' });

// 4. Chapter 3: Endgame Build (Nova Plasma / Marauder AK47)
simulateRun(3, 'viktor', 'w_nova', { hpLv: 8, dmgLv: 8, spdLv: 5, rateLv: 5, shield: 'sh_titan', pet: 'pet_mimic' });
