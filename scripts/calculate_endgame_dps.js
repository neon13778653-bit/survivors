const fs = require('fs');

// Accurate simulation with the exact game engine formulas from index.html:
// - clampPlayerCooldown with archetype ceilings (maxRate 15/s for rapid, 8.5/s for medium, 5.2/s for heavy)
// - Absolute p.cd floor = 0.0625s (16.0 shots/sec)
// - Multi-projectile scaling: extraProjRatio > 1.25 ? (1 / Math.pow(extraProjRatio, 0.24)) : 1
// - Boss HP formula: scaledBossHp(g, baseHp) = Math.round(baseHp * (1 + (tier-1)*0.05) * lvlMultHp)

function simulateLoadout(config) {
  const {
    name,
    charId,
    wepId,
    wepStars,
    wepForge, // { dmg: 0-10, rate: 0-10 }
    metaTalents, // { hp, dmg, rate, spd, pick }
    shieldId,
    shieldForge,
    petId,
    petStars,
    petForge,
    artifacts, // [{ id, upDmg }]
    abilities, // { abId: level }
    evolutions // [evoId]
  } = config;

  // Characters
  const CHARS = {
    john: { hpMod: 1.0, spdMod: 1.0, dmgMod: 1.0, coolMod: 1.0, projMod: 1 },
    marcus: { hpMod: 1.4, spdMod: 0.9, dmgMod: 1.0, coolMod: 1.0, projMod: 2 },
    leon: { hpMod: 0.85, spdMod: 1.2, dmgMod: 0.95, coolMod: 0.65, projMod: 1 },
    viktor: { hpMod: 0.85, spdMod: 0.95, dmgMod: 1.5, coolMod: 1.1, projMod: 1 },
    kael: { hpMod: 0.75, spdMod: 1.3, dmgMod: 1.25, coolMod: 0.9, projMod: 1 }
  };
  const char = CHARS[charId] || CHARS.john;

  // Weapons
  const WEAPONS = {
    w_pistol: { dmg: 10, rate: 2.2, proj: 1, r: 1, m: {} },
    w_vector: { dmg: 7, rate: 7.5, proj: 1, r: 2, m: { dmg: 0.08, cool: 0.94 } },
    w_vepr_auto: { dmg: 13, rate: 2.2, proj: 6, r: 3, m: { dmg: 0.12, critChance: 0.05 } },
    w_nova: { dmg: 32, rate: 1.4, proj: 6, r: 4, m: { dmg: 0.22, critChance: 0.08 } },
    w_phantom: { dmg: 110, rate: 1.1, proj: 1, r: 5, m: { dmg: 0.35, cool: 0.88, critChance: 0.16 } },
    w_laser: { dmg: 7.5, rate: 6.0, proj: 2, r: 5, isLaser: true, m: { dmg: 0.32, cool: 0.86, critChance: 0.14 } },
    m_astral: { dmg: 86, rate: 1.05, proj: 1, r: 5, kind: 'magic', m: { dmg: 0.35, cool: 0.86, critChance: 0.15 } }
  };
  const wep = WEAPONS[wepId] || WEAPONS.w_pistol;

  // Equipment Mods (EM)
  let emDmg = (wep.m.dmg || 0);
  let emCool = (wep.m.cool || 1.0);
  let emCrit = (wep.m.critChance || 0);
  let emProj = (wep.m.proj || 0);

  // Weapon Forge (+10%..45%)
  const r = wepStars || wep.r;
  const dmgStep = r === 5 ? 0.045 : (r === 4 ? 0.034 : (r === 3 ? 0.026 : (r === 2 ? 0.020 : 0.016)));
  const rateStep = r === 5 ? 0.032 : (r === 4 ? 0.025 : (r === 3 ? 0.020 : (r === 2 ? 0.015 : 0.012)));
  if (wepForge?.dmg) emDmg += wepForge.dmg * dmgStep;
  if (wepForge?.rate) emCool /= (1 + rateStep * wepForge.rate);

  // Artifacts
  const ART_DEFS = {
    art_compass: { spd: 0.10, pick: 0.08, r: 1 },
    art_scope: { dmg: 0.10, cool: 0.94, r: 1 },
    art_boots: { spd: 0.08, hp: 0.08, r: 1 },
    art_plate: { armor: 0.10, hp: 0.15, r: 2 },
    art_gloves: { cool: 0.90, critChance: 0.06, r: 2 },
    art_crystal: { dmg: 0.25, r: 3 },
    art_chronos: { cool: 0.80, spd: 0.08, r: 4 },
    art_crown: { dmg: 0.35, cool: 0.76, spd: 0.12, r: 5 },
    art_singularity: { dmg: 0.40, critChance: 0.18, r: 5 },
    art_heart: { hp: 0.65, dmg: 0.30, regen: 2.0, r: 5 }
  };

  (artifacts || []).forEach(art => {
    const def = ART_DEFS[art.id];
    if (!def) return;
    if (def.dmg) emDmg += def.dmg;
    if (def.cool) emCool *= def.cool;
    if (def.critChance) emCrit += def.critChance;
    if (art.upDmg) {
      const aDmgStep = def.r === 5 ? 0.040 : (def.r === 4 ? 0.030 : 0.022);
      emDmg += art.upDmg * aDmgStep;
    }
  });

  emCool = Math.max(0.65, emCool);

  // Talents
  const tDmg = metaTalents?.dmg || 0;
  const tRate = metaTalents?.rate || 0;
  const metaDmgBonus = 1 + 0.02 * tDmg;
  const metaRateBonus = 1 + 0.015 * tRate;

  // Base Stats at game start
  const baseDmg = wep.dmg * metaDmgBonus * char.dmgMod * (1 + emDmg);
  const baseRate = wep.rate;
  const rawCool = ((1 / baseRate) * char.coolMod * emCool) / metaRateBonus;

  // clampPlayerCooldown
  let maxRate = 5.2;
  if (baseRate >= 5.0) maxRate = 15.0;
  else if (baseRate >= 2.0) maxRate = 8.5;
  else maxRate = Math.min(5.2, Math.max(2.4, baseRate * 3.2));
  const minCool = 1 / maxRate;
  let cool = Math.max(minCool, rawCool);
  let proj = wep.proj + (char.projMod - 1) + emProj;

  // In-run Ability Processing
  let p = {
    dmg: baseDmg,
    cool: cool,
    proj: proj,
    critChance: emCrit,
    critMult: 2.0,
    leadstorm: 0,
    leadstormEvolved: false,
    critEvolved: false,
    explosive_ammo: 0,
    got: abilities || {}
  };

  const hasEvo = id => (evolutions || []).includes(id);

  if (abilities?.fmj_ammo) p.dmg *= (1 + 0.10 * abilities.fmj_ammo);
  if (abilities?.fast_reload) {
    p.cool /= (1 + 0.08 * abilities.fast_reload);
    p.cool = Math.max(minCool, p.cool);
  }
  if (abilities?.extra_projectile) {
    const stepP = Math.max(1, Math.ceil(wep.proj * 0.35));
    p.proj += Math.ceil(abilities.extra_projectile / 2) * stepP;
    p.dmg *= (1 + 0.08 * abilities.extra_projectile);
  }
  if (hasEvo('extra_projectile_evo')) {
    const stepP = Math.max(1, Math.ceil(wep.proj * 0.35));
    p.proj += 2 * stepP;
    p.cool = Math.max(minCool, p.cool * 0.80);
  }
  if (abilities?.sniper_crit) {
    p.critChance = Math.min(0.85, p.critChance + abilities.sniper_crit * 0.08);
    p.critMult += abilities.sniper_crit * 0.20;
  }
  if (hasEvo('sniper_crit_evo')) {
    p.critEvolved = true;
    p.critChance = Math.min(0.90, p.critChance + 0.25);
    p.critMult += 0.60;
  }
  if (abilities?.leadstorm) {
    p.leadstorm = abilities.leadstorm;
    p.cool /= (1 + 0.05 * abilities.leadstorm);
    p.cool = Math.max(minCool, p.cool);
  }
  if (hasEvo('leadstorm_evo')) {
    p.leadstorm += 2;
    p.leadstormEvolved = true;
    p.dmg *= 1.20;
    p.cool = Math.max(minCool, p.cool * 0.88);
  }
  if (abilities?.explosive_ammo) {
    p.explosive_ammo = abilities.explosive_ammo;
  }
  if (hasEvo('explosive_ammo_evo')) {
    p.dmg *= 1.25;
    p.explosive_ammo += 2;
  }

  // Multi-projectile balance factor
  const baseProj = wep.proj || 1;
  const extraProjRatio = Math.max(1, p.proj / baseProj);
  const multiScale = extraProjRatio > 1.25 ? (1 / Math.pow(extraProjRatio, 0.24)) : 1;

  // Single bullet damage with crit
  const avgBulletDmg = (p.dmg * (1 - p.critChance) + p.dmg * p.critMult * p.critChance) * multiScale;

  // Leadstorm uptime & rate calculation:
  // Base rate clamped by p.cd >= 0.0625 (16/s)
  let normalCd = Math.max(0.0625, p.cool);
  let normalRate = 1 / normalCd;

  let leadstormRate = normalRate;
  let leadstormDmgMult = 1.0;
  let leadstormUptime = 0;

  if (p.leadstorm > 0) {
    const dur = p.leadstormEvolved ? 4.0 : (1.5 + p.leadstorm * 0.35);
    const cd = 5.8;
    leadstormUptime = dur / (dur + cd);

    const lsMult = p.leadstormEvolved ? (1 / 2.20) : (1 / (1.40 + p.leadstorm * 0.12));
    const rawLsCd = p.cool * lsMult;
    const lsCd = Math.max(0.0625, rawLsCd); // Universal floor: 16 shots/sec
    leadstormRate = 1 / lsCd;
    leadstormDmgMult = p.leadstormEvolved ? 1.35 : 1.0;
  }

  const effectiveRate = normalRate * (1 - leadstormUptime) + leadstormRate * leadstormUptime;
  const effectiveBulletDmg = avgBulletDmg * ((1 - leadstormUptime) + leadstormUptime * leadstormDmgMult);
  const weaponDps = effectiveRate * p.proj * effectiveBulletDmg;

  // Pet DPS
  let petDps = 0;
  if (petId) {
    const petRarMult = petStars === 5 ? 3.2 : (petStars === 4 ? 2.4 : (petStars === 3 ? 1.8 : (petStars === 2 ? 1.35 : 1.0)));
    const petDmgStep = petStars === 5 ? 0.08 : (petStars === 4 ? 0.062 : (petStars === 3 ? 0.048 : (petStars === 2 ? 0.035 : 0.025)));
    const petCoolStep = petStars === 5 ? 0.048 : (petStars === 4 ? 0.038 : (petStars === 3 ? 0.030 : (petStars === 2 ? 0.024 : 0.018)));
    const petDmgMult = 1 + (petForge?.dmg || 0) * petDmgStep;
    const petCoolMult = Math.max(0.45, 1 - (petForge?.cool || 0) * petCoolStep);
    const basePetCd = petId === 'pet_treant' ? 1.2 : (petId === 'pet_ghoul' ? 1.0 : (petId === 'pet_rat' ? 1.8 : 2.5));
    const petAtkCd = basePetCd * petCoolMult;
    const petAtkDmg = p.dmg * petRarMult * petDmgMult;
    petDps = petAtkDmg / petAtkCd;
  }

  const totalDps = weaponDps + petDps;

  return {
    name,
    char: charId,
    wep: wepId,
    dmgPerBullet: p.dmg.toFixed(1),
    proj: p.proj,
    fireRate: effectiveRate.toFixed(1) + '/s',
    crit: (p.critChance * 100).toFixed(0) + '% (x' + p.critMult.toFixed(2) + ')',
    weaponDps: Math.round(weaponDps),
    petDps: Math.round(petDps),
    totalDps: Math.round(totalDps)
  };
}

const setups = [
  // 1. Starter (Chapter 1 early)
  {
    name: '1. Новичок (Глава 1: M1911 Пистолет, без прокачки)',
    charId: 'john',
    wepId: 'w_pistol',
    wepStars: 1,
    metaTalents: { dmg: 2, rate: 2 },
    petId: 'pet_slime',
    petStars: 1,
    artifacts: [{ id: 'art_compass' }],
    abilities: { fmj_ammo: 2, fast_reload: 2 }
  },
  // 2. Midgame Ch1/Ch2 (AK-47 / Vepr-12 3★)
  {
    name: '2. Мидгейм (Глава 2: Вепрь-12 3★, таланты 10, кузница 5)',
    charId: 'john',
    wepId: 'w_vepr_auto',
    wepStars: 3,
    wepForge: { dmg: 5, rate: 5 },
    metaTalents: { dmg: 10, rate: 10 },
    petId: 'pet_rat',
    petStars: 3,
    petForge: { dmg: 5, cool: 5 },
    artifacts: [{ id: 'art_crystal' }, { id: 'art_gloves' }, { id: 'art_plate' }],
    abilities: { fmj_ammo: 5, fast_reload: 4, extra_projectile: 3, sniper_crit: 2 }
  },
  // 3. Late-Midgame (Chapter 2 boss / Chapter 3 start)
  {
    name: '3. Предтоп (Глава 2 Босс / Глава 3 Старт: Плазма Нова 4★)',
    charId: 'marcus',
    wepId: 'w_nova',
    wepStars: 4,
    wepForge: { dmg: 8, rate: 8 },
    metaTalents: { dmg: 15, rate: 15 },
    petId: 'pet_ghoul',
    petStars: 4,
    petForge: { dmg: 8, cool: 8 },
    artifacts: [{ id: 'art_chronos' }, { id: 'art_crystal' }, { id: 'art_gloves' }],
    abilities: { fmj_ammo: 5, fast_reload: 5, extra_projectile: 5, sniper_crit: 4 },
    evolutions: ['extra_projectile_evo']
  },
  // 4. Endgame: Prometheus Laser 5★ (Full Build)
  {
    name: '4. Эндгейм Прометей 5★ (Лазер, таланты 20, кузница 10, 4 эволюции)',
    charId: 'viktor',
    wepId: 'w_laser',
    wepStars: 5,
    wepForge: { dmg: 10, rate: 10 },
    metaTalents: { dmg: 20, rate: 20 },
    petId: 'pet_treant',
    petStars: 5,
    petForge: { dmg: 10, cool: 10 },
    artifacts: [
      { id: 'art_crown', upDmg: 10 },
      { id: 'art_singularity', upDmg: 10 },
      { id: 'art_heart', upDmg: 10 }
    ],
    abilities: { fmj_ammo: 5, fast_reload: 5, extra_projectile: 5, sniper_crit: 5, leadstorm: 5 },
    evolutions: ['extra_projectile_evo', 'leadstorm_evo', 'sniper_crit_evo']
  },
  // 5. Endgame: Phantom Gauss 5★ (Full Build)
  {
    name: '5. Эндгейм Гаусс 5★ (Винтовка Фантом, таланты 20, кузница 10, 4 эволюции)',
    charId: 'viktor',
    wepId: 'w_phantom',
    wepStars: 5,
    wepForge: { dmg: 10, rate: 10 },
    metaTalents: { dmg: 20, rate: 20 },
    petId: 'pet_treant',
    petStars: 5,
    petForge: { dmg: 10, cool: 10 },
    artifacts: [
      { id: 'art_crown', upDmg: 10 },
      { id: 'art_singularity', upDmg: 10 },
      { id: 'art_heart', upDmg: 10 }
    ],
    abilities: { fmj_ammo: 5, fast_reload: 5, extra_projectile: 5, sniper_crit: 5, leadstorm: 5 },
    evolutions: ['extra_projectile_evo', 'leadstorm_evo', 'sniper_crit_evo']
  },
  // 6. Endgame: Astral Staff 5★ (Magic Full Build)
  {
    name: '6. Эндгейм Сверхновая 5★ (Астральный посох, таланты 20, кузница 10, 4 эволюции)',
    charId: 'kael',
    wepId: 'm_astral',
    wepStars: 5,
    wepForge: { dmg: 10, rate: 10 },
    metaTalents: { dmg: 20, rate: 20 },
    petId: 'pet_treant',
    petStars: 5,
    petForge: { dmg: 10, cool: 10 },
    artifacts: [
      { id: 'art_crown', upDmg: 10 },
      { id: 'art_singularity', upDmg: 10 },
      { id: 'art_heart', upDmg: 10 }
    ],
    abilities: { fmj_ammo: 5, fast_reload: 5, extra_projectile: 5, sniper_crit: 5, leadstorm: 5 },
    evolutions: ['extra_projectile_evo', 'leadstorm_evo', 'sniper_crit_evo']
  }
];

const results = setups.map(s => simulateLoadout(s));

console.log('========================================================================================');
console.log('                        РЕАЛЬНЫЙ РАСЧЁТ DPS В ЗАВИСИМОСТИ ОТ БИЛДА                      ');
console.log('========================================================================================');
results.forEach(r => {
  console.log(`\n▶ ${r.name}`);
  console.log(`  Герой: ${r.char} | Базовый урон пули: ${r.dmgPerBullet} | Снарядов: ${r.proj} | Темп: ${r.fireRate}`);
  console.log(`  Крит: ${r.crit}`);
  console.log(`  ⚔️ ОРУЖЕЙНЫЙ DPS: ${r.weaponDps.toLocaleString()} | 🐾 ПИТОМЕЦ DPS: ${r.petDps.toLocaleString()} | 💥 ИТОГОВЫЙ DPS: ${r.totalDps.toLocaleString()}`);
});

// Boss Battle TTK Table
const bosses = [
  // Chapter 1 (multHp = 1.0)
  { chapter: 1, wave: 10, name: 'Могильщик', baseHp: 1200, mult: 1.0, recTier: 0 },
  { chapter: 1, wave: 20, name: 'Крысиный Король', baseHp: 4800, mult: 1.0, recTier: 0 },
  { chapter: 1, wave: 30, name: 'Кракен / Мерзость', baseHp: 12500, mult: 1.0, recTier: 1 },
  // Chapter 2 (multHp = 1.5)
  { chapter: 2, wave: 10, name: 'Мать выводка', baseHp: 9500, mult: 1.5, recTier: 1 },
  { chapter: 2, wave: 20, name: 'Токсичный слизень', baseHp: 23500, mult: 1.5, recTier: 1 },
  { chapter: 2, wave: 40, name: 'Древень-хранитель', baseHp: 47000, mult: 1.5, recTier: 2 },
  // Chapter 3 (multHp = 1.85)
  { chapter: 3, wave: 10, name: 'Кибер-Цербер', baseHp: 90000, mult: 1.85, recTier: 3 },
  { chapter: 3, wave: 20, name: 'Био-Мясник', baseHp: 140000, mult: 1.85, recTier: 3 },
  { chapter: 3, wave: 30, name: 'Хитиновый Жнец', baseHp: 195000, mult: 1.85, recTier: 3 },
  { chapter: 3, wave: 40, name: 'Нейро-Сверхразум', baseHp: 280000, mult: 1.85, recTier: 3 },
  { chapter: 3, wave: 50, name: 'Нулевой Пациент', baseHp: 420000, mult: 1.85, recTier: 3 }
];

console.log('\n========================================================================================');
console.log('             ВРЕМЯ УБИЙСТВА БОССОВ (TIME TO KILL - TTK) ПО СТАДИЯМ ИГРЫ                 ');
console.log('========================================================================================');
console.log('Босс [Глава-Волна]        | Реальное HP | Новичок 1★ | Мидгейм 3★ | Предтоп 4★ | Эндгейм 5★ (Лазер/Гаусс)');
console.log('----------------------------------------------------------------------------------------');

bosses.forEach(b => {
  const hp1Star = Math.round(b.baseHp * 1.0 * b.mult);
  const hp3Star = Math.round(b.baseHp * 1.1 * b.mult);
  const hp4Star = Math.round(b.baseHp * 1.15 * b.mult);
  const hp5Star = Math.round(b.baseHp * 1.2 * b.mult);

  const t0 = (hp1Star / results[0].totalDps).toFixed(1) + 'с';
  const t1 = (hp3Star / results[1].totalDps).toFixed(1) + 'с';
  const t2 = (hp4Star / results[2].totalDps).toFixed(1) + 'с';
  const t3 = (hp5Star / results[3].totalDps).toFixed(1) + 'с';
  const t4 = (hp5Star / results[4].totalDps).toFixed(1) + 'с';

  const label = `${b.name} [Гл.${b.chapter} В.${b.wave}]`.padEnd(25);
  const hpStr = (hp5Star.toLocaleString() + ' HP').padStart(11);
  console.log(`${label} | ${hpStr} | ${t0.padStart(10)} | ${t1.padStart(10)} | ${t2.padStart(10)} | ${t3.padStart(11)} (${t4})`);
});
