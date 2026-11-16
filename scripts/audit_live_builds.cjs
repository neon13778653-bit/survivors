const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { make, battle } = require('./audit_new_player.cjs');

const builds = {
  w_python: {
    damage: ['extra_projectile', 'wep_python_magnum', 'fmj_ammo', 'fast_reload', 'sniper_crit'],
    crowd: ['explosive_ammo', 'ricochet_rounds', 'shrapnel_burst', 'piercing_slugs', 'shock_rounds'],
    defense: ['kevlar_vest', 'nanite_repair', 'combat_stim', 'tac_heal', 'tac_sprint'],
  },
  m_storm: {
    damage: ['arcane_multicast', 'arcane_power', 'quick_cast', 'wep_storm_overload', 'arcane_focus'],
    crowd: ['chain_lightning', 'frost_nova', 'toxic_miasma', 'fireball_burst', 'spell_pierce'],
    defense: ['mana_shield', 'essence_regen', 'magic_vitality', 'rejuvenation_aura', 'astral_haste'],
  },
};

async function main() {
  const seed = Number(process.argv[2] || 101);
  const geared = process.argv[3] === 'geared';
  const late = geared || process.argv[3] === 'late';
  const results = [];
  for (const chapter of geared ? [3] : late ? [2, 3] : [1, 3]) {
    for (const [baseWeapon, profiles] of Object.entries(builds)) {
      const weapon = late ? ({w_python:'w_laser', m_storm:'m_astral'})[baseWeapon] : baseWeapon;
      for (const [profile, cards] of Object.entries(profiles)) {
        const priority = cards.map(id => late ? ({
          wep_python_magnum: 'wep_laser_bifurcation',
          wep_storm_overload: 'wep_astral_nova_blast',
        }[id] || id) : id);
        const e = make();
        await e.loadAll();
        e.context.__run = { seed, chapter, weapon, priority, geared, seconds: 1800 };
        e.run(`
          let rngState = __run.seed;
          Math.random = () => {
            let t = rngState += 0x6D2B79F5;
            t = Math.imul(t ^ t >>> 15, t | 1);
            t ^= t + Math.imul(t ^ t >>> 7, t | 61);
            return ((t ^ t >>> 14) >>> 0) / 4294967296;
          };
          W = 400; H = 800;
          save = createDefaultSave();
          save.unlockedLvls = [1, 2, 3];
          save.inv.push(__run.weapon);
          save.equip.weapon = __run.weapon;
          if (__run.geared) {
            const gear = {shield:'sh_aegis', pet:'pet_treant', art1:'art_crown', art2:'art_singularity', art3:'art_phoenix'};
            save.inv.push(...Object.values(gear));
            Object.assign(save.equip, gear);
          }
          for (const key of ['hpLv','dmgLv','rateLv','spdLv','pickLv']) save[key] = __run.geared ? 20 : 5;
          selectedLvlIdx = __run.chapter - 1;
          startGame();
        `);
        const r = battle(e);
        assert.ok(r.stopped, 'time limit reached');
        const boss = e.run('G.activeBoss && ({id:G.activeBoss.bossId, hp:G.activeBoss.hp, maxHp:G.activeBoss.maxHp})');
        results.push({ ...r, profile, boss });
      }
    }
  }
  const file = path.resolve(__dirname, '../docs/balance-2026-11-15', 'live-builds-' + (geared ? 'geared-' : late ? 'late-' : '') + seed + '.json');
  fs.writeFileSync(file, JSON.stringify(results, null, 1));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
