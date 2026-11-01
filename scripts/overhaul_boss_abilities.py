#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overhaul Location 3 Boss Abilities in survivors/index.html:
1. Cyber-Cerberus (Wave 10): Napalm flame trail on dash, twin rebound dash in rage, micro-missile pod barrage, EMP shock mines, quill burst tail whip.
2. Bio-Butcher (Wave 20): Meat hook pull & drag, executioner cleaver smash with ground fissure shockwave, bio-hazard cloud, whirlwind cleaver spin, bouncing saw blades in rage.
3. Neuro-Overmind (Wave 40): Psionic singularity with active gravitational vortex pull, death ray laser from central eye, chain psi-lightning, orbital drones, phase shift quantum teleport.
4. Clean up shockwaves physics in update() and add rich visual rendering in drawBossShockwaves().
"""

import sys

INDEX_PATH = r"C:\Users\alexg\Desktop\survivors\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# ------------------------------------------------------------------------------
# STEP 1: Update spawn functions to initialize new cooldowns
# ------------------------------------------------------------------------------
old_cerberus_spawn_props = """    dashCd: 3.5,
    howlCd: 6.0,
    tailCd: 2.5,
    chargeVx: 0,
    chargeVy: 0,
    chargeAng: 0,
    enraged: false"""

new_cerberus_spawn_props = """    dashCd: 3.5,
    howlCd: 6.0,
    tailCd: 2.5,
    missileCd: 5.0,
    mineCd: 9.0,
    chargeVx: 0,
    chargeVy: 0,
    chargeAng: 0,
    hasRebounded: false,
    enraged: false"""

old_butcher_spawn_props = """    hookCd: 4.5,
    cleaverCd: 3.5,
    toxicGasCd: 7.0,
    hookTargetX: 0,
    hookTargetY: 0,
    enraged: false"""

new_butcher_spawn_props = """    hookCd: 4.5,
    cleaverCd: 3.0,
    toxicGasCd: 5.5,
    spinCd: 7.5,
    sawScatterCd: 8.5,
    hookTargetX: 0,
    hookTargetY: 0,
    enraged: false"""

old_overmind_spawn_props = """    singularityCd: 5.0,
    psiLightningCd: 3.5,
    droneCd: 8.0,
    enraged: false"""

new_overmind_spawn_props = """    singularityCd: 5.0,
    psiLightningCd: 3.0,
    droneCd: 7.5,
    beamCd: 6.5,
    teleportCd: 8.5,
    beamAngle: 0,
    enraged: false"""

for old_prop, new_prop, name in [
    (old_cerberus_spawn_props, new_cerberus_spawn_props, "Cyber Cerberus"),
    (old_butcher_spawn_props, new_butcher_spawn_props, "Bio Butcher"),
    (old_overmind_spawn_props, new_overmind_spawn_props, "Neuro Overmind")
]:
    if old_prop.replace("\n", "\r\n") in content:
        content = content.replace(old_prop.replace("\n", "\r\n"), new_prop.replace("\n", "\r\n"), 1)
        print(f"1. Updated {name} spawn properties (CRLF).")
    elif old_prop in content:
        content = content.replace(old_prop, new_prop, 1)
        print(f"1. Updated {name} spawn properties (LF).")
    else:
        print(f"Warning: {name} spawn properties not found!")

# ------------------------------------------------------------------------------
# STEP 2: Replace Location 3 Boss AI in update(dt)
# ------------------------------------------------------------------------------
ai_start_marker = "    // ==========================================\n    // БОСС 1 (ЛОК. 3): КИБЕР-ЦЕРБЕР (CYBER-CERBERUS)\n    // =========================================="
ai_end_marker = "    const dx=p.x-e.x,dy=p.y-e.y,d=Math.hypot(dx,dy)||1;"

# Find between ai_start_marker and the generic monster chase right after neuro_overmind
# Let's locate the slice
pos_ai_start = content.find("// БОСС 1 (ЛОК. 3): КИБЕР-ЦЕРБЕР (CYBER-CERBERUS)")
if pos_ai_start == -1:
    print("Error: Could not find start of Location 3 Boss AI!")
    sys.exit(1)

# Find start of line
pos_ai_start_line = content.rfind("\n", 0, pos_ai_start) + 1

# Find end: after neuro_overmind boss block
pos_overmind_boss = content.find("bossId === 'neuro_overmind'", pos_ai_start)
pos_ai_end = content.find("const dx=p.x-e.x,dy=p.y-e.y,d=Math.hypot(dx,dy)||1;", pos_overmind_boss)

if pos_ai_end == -1:
    print("Error: Could not find end of Location 3 Boss AI!")
    sys.exit(1)

new_boss_ai = """    // ==========================================
    // БОСС 1 (ЛОК. 3): КИБЕР-ЦЕРБЕР (CYBER-CERBERUS)
    // ==========================================
    if(e.isBoss && e.bossId === 'cyber_cerberus'){
      if(e.fl > 0) e.fl -= dt;
      if(e.oh > 0) e.oh -= dt;

      if(e.spawnState === 'emerging'){
        e.spawnT -= dt;
        if(e.spawnT <= 0){
          e.spawnState = 'active';
          e.spawnT = 0;
          e.action = 'idle';
          e.actionT = 0;
        }
        continue;
      }

      const dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;

      if(!e.enraged && e.hp <= e.maxHp * 0.5){
        e.enraged = true;
        e.c.speed = 140;
        g.shake = Math.max(g.shake, 0.7);
        showGameToast('🐺 ' + T('CYBER-CERBERUS OVERDRIVE! (+DOUBLE REBOUND / EMP MINES)', 'КИБЕР-ЦЕРБЕР: ПЕРЕГРУЗКА СИСТЕМ! (+ДВОЙНОЙ РЫВОК / ЭМИ-МИНЫ)'), '#ef4444', 3.5);
        Sfx.play('dash');
        for(let k = 0; k < 3; k++){
          const ma = (k / 3) * 6.283 + Math.random() * 0.5;
          const md = 50 + Math.random() * 60;
          g.bossShockwaves.push({
            x: e.x + Math.cos(ma) * md,
            y: e.y + Math.sin(ma) * md,
            vx: 0, vy: 0,
            l: 7.0, maxL: 7.0,
            dmg: 25,
            type: 'emp_mine',
            col: '#38bdf8'
          });
        }
      }

      e.dashCd = (e.dashCd !== undefined ? e.dashCd : 4.0) - dt;
      e.howlCd = (e.howlCd !== undefined ? e.howlCd : 6.0) - dt;
      e.tailCd = (e.tailCd !== undefined ? e.tailCd : 3.0) - dt;
      e.missileCd = (e.missileCd !== undefined ? e.missileCd : 5.0) - dt;
      e.mineCd = (e.mineCd !== undefined ? e.mineCd : 9.0) - dt;

      // 1. Атака: Хлыст хвостом и веер нано-шипов (Anti-Melee)
      if(e.action === 'idle' && d < 95 && e.tailCd <= 0){
        e.action = 'tail_swipe';
        e.actionT = 0.5;
        e.tailCd = e.enraged ? 2.2 : 3.5;
        continue;
      }
      if(e.action === 'tail_swipe'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'idle';
          Sfx.play('anvil');
          if(d <= 105 && p.inv <= 0){
            damagePlayer(60);
            p.x += (dx / d) * 35;
            p.y += (dy / d) * 35;
            g.shake = Math.max(g.shake, 0.45);
          }
          // Веер из 5 металлических нано-шипов во все стороны
          const baseAng = Math.atan2(dy, dx);
          for(let k = -2; k <= 2; k++){
            const qa = baseAng + k * 0.35;
            const qSpd = 340;
            g.bossShockwaves.push({
              x: e.x, y: e.y,
              vx: Math.cos(qa) * qSpd,
              vy: Math.sin(qa) * qSpd,
              l: 1.4, maxL: 1.4,
              dmg: 24,
              type: 'cerberus_quill',
              col: '#ef4444'
            });
          }
        }
        continue;
      }

      // 2. Атака: Гипер-рывок по лазерному лучу (с напалмовым следом и двойным отскоком в ярости)
      if(e.action === 'idle' && e.dashCd <= 0){
        e.action = 'dash_prep';
        e.actionT = e.enraged ? 0.50 : 0.70;
        e.chargeAng = Math.atan2(dy, dx);
        e.dashCd = e.enraged ? 3.0 : 4.5;
        e.hasRebounded = false;
        continue;
      }
      if(e.action === 'dash_prep'){
        e.actionT -= dt;
        e.chargeAng = Math.atan2(p.y - e.y, p.x - e.x);
        if(e.actionT <= 0){
          e.action = 'dash_run';
          e.actionT = 0.45;
          const dSpd = e.enraged ? 520 : 440;
          e.chargeVx = Math.cos(e.chargeAng) * dSpd;
          e.chargeVy = Math.sin(e.chargeAng) * dSpd;
          Sfx.play('dash');
          g.shake = Math.max(g.shake, 0.35);
        }
        continue;
      }
      if(e.action === 'dash_run' || e.action === 'dash_rebound'){
        e.actionT -= dt;
        e.x += e.chargeVx * dt;
        e.y += e.chargeVy * dt;
        e.facing = e.chargeVx >= 0 ? 1 : -1;
        keepInsideBossArena(e, g.bossArena, (e.c?.r || 44) + 10);
        
        // Горящий напалмовый след за Цербером
        if(Math.random() < 0.65){
          g.bossShockwaves.push({
            x: e.x + (Math.random() - 0.5) * 16,
            y: e.y + 16 + (Math.random() - 0.5) * 8,
            vx: 0, vy: 0,
            l: 3.2, maxL: 3.2,
            dmg: 15,
            type: 'napalm_trail',
            col: '#f97316'
          });
        }
        // Урон игроку при таране
        if(d <= e.c.r + p.r && p.inv <= 0){
          damagePlayer(Math.round(55 * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          p.x += Math.cos(e.chargeAng) * 30;
          p.y += Math.sin(e.chargeAng) * 30;
          g.shake = Math.max(g.shake, 0.5);
          Sfx.play('hit');
        }
        if(e.actionT <= 0){
          if(e.enraged && !e.hasRebounded && e.action === 'dash_run'){
            e.hasRebounded = true;
            e.action = 'dash_rebound';
            e.actionT = 0.40;
            const rebAng = Math.atan2(p.y - e.y, p.x - e.x);
            e.chargeAng = rebAng;
            const rSpd = 540;
            e.chargeVx = Math.cos(rebAng) * rSpd;
            e.chargeVy = Math.sin(rebAng) * rSpd;
            Sfx.play('dash');
            g.shake = Math.max(g.shake, 0.45);
          } else {
            e.action = 'idle';
          }
        }
        continue;
      }

      // 3. Атака: Залп микроракет «Цербер-9»
      if(e.action === 'idle' && e.missileCd <= 0){
        e.action = 'missile_salvo';
        e.actionT = 0.65;
        e.missileCd = e.enraged ? 4.5 : 7.0;
        continue;
      }
      if(e.action === 'missile_salvo'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'idle';
          Sfx.play('shoot');
          const mCount = e.enraged ? 6 : 4;
          for(let m = 0; m < mCount; m++){
            const launchAng = -Math.PI / 2 + (m - (mCount - 1) / 2) * 0.4 + (Math.random() - 0.5) * 0.2;
            const launchSpd = 280 + Math.random() * 80;
            g.bossShockwaves.push({
              x: e.x + (e.facing > 0 ? -15 : 15),
              y: e.y - 20,
              vx: Math.cos(launchAng) * launchSpd,
              vy: Math.sin(launchAng) * launchSpd,
              l: 2.2, maxL: 2.2,
              dmg: 36,
              type: 'cyber_missile',
              col: '#ef4444'
            });
          }
        }
        continue;
      }

      // 4. Атака: Ультразвуковой лай подавления (Sonic Howl)
      if(e.action === 'idle' && e.howlCd <= 0){
        e.action = 'howl';
        e.actionT = 0.8;
        e.howlCd = e.enraged ? 5.5 : 8.0;
        Sfx.play('hit');
        g.shake = Math.max(g.shake, 0.4);
        for(let w = 0; w < 3; w++){
          g.bossShockwaves.push({
            x: e.x, y: e.y - 8,
            vx: 0, vy: 0,
            l: 0.9 + w * 0.25, maxL: 0.9 + w * 0.25,
            dmg: 25,
            type: 'sonic_howl',
            col: '#ef4444'
          });
        }
        if(d <= 150 && p.inv <= 0){
          damagePlayer(25);
          p.slowT = 2.5;
        }
        continue;
      }
      if(e.action === 'howl'){
        e.actionT -= dt;
        if(e.actionT <= 0) e.action = 'idle';
        continue;
      }

      // 5. Разбрасывание ЭМИ-мин в ярости
      if(e.enraged && e.action === 'idle' && e.mineCd <= 0){
        e.mineCd = 8.0;
        for(let k = 0; k < 2; k++){
          const ma = Math.random() * 6.283;
          const md = 60 + Math.random() * 80;
          g.bossShockwaves.push({
            x: e.x + Math.cos(ma) * md,
            y: e.y + Math.sin(ma) * md,
            vx: 0, vy: 0,
            l: 6.5, maxL: 6.5,
            dmg: 25,
            type: 'emp_mine',
            col: '#38bdf8'
          });
        }
      }

      if(e.action === 'idle'){
        const spd = (e.enraged ? 140 : 105) * g.lvlConfig.multSpeed;
        e.x += (dx / d) * spd * dt;
        e.y += (dy / d) * spd * dt;
        e.facing = dx >= 0 ? 1 : -1;
        e.animT = (e.animT || 0) + dt * (e.enraged ? 12 : 9);
        keepInsideBossArena(e, g.bossArena, (e.c?.r || 44) + 10);
      }
      continue;
    }

    // ==========================================
    // БОСС 2 (ЛОК. 3): ХИРУРГ-МЯСНИК (THE BIO-BUTCHER)
    // ==========================================
    if(e.isBoss && e.bossId === 'bio_butcher'){
      if(e.fl > 0) e.fl -= dt;
      if(e.oh > 0) e.oh -= dt;

      if(e.spawnState === 'emerging'){
        e.spawnT -= dt;
        if(e.spawnT <= 0){
          e.spawnState = 'active';
          e.spawnT = 0;
          e.action = 'idle';
          e.actionT = 0;
        }
        continue;
      }

      const dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;

      if(!e.enraged && e.hp <= e.maxHp * 0.5){
        e.enraged = true;
        e.c.speed = 100;
        g.shake = Math.max(g.shake, 0.7);
        showGameToast('🪓 ' + T('THE BIO-BUTCHER ENRAGED! (+WHIRLWIND / BOUNCING SAWS)', 'ХИРУРГ-МЯСНИК В ЯРОСТИ! (+ВИХРЬ МЯСОРУБКИ / ДИСКОВЫЕ ПИЛЫ)'), '#dc2626', 3.5);
        Sfx.play('anvil');
      }

      e.hookCd = (e.hookCd !== undefined ? e.hookCd : 4.0) - dt;
      e.cleaverCd = (e.cleaverCd !== undefined ? e.cleaverCd : 3.0) - dt;
      e.toxicGasCd = (e.toxicGasCd !== undefined ? e.toxicGasCd : 5.5) - dt;
      e.spinCd = (e.spinCd !== undefined ? e.spinCd : 7.5) - dt;
      e.sawScatterCd = (e.sawScatterCd !== undefined ? e.sawScatterCd : 8.5) - dt;

      // 1. Атака: Вихрь мясорубки (Whirlwind Cleaver Spin)
      if(e.action === 'idle' && d < 140 && e.spinCd <= 0){
        e.action = 'spin_cleaver';
        e.actionT = 1.4;
        e.spinCd = e.enraged ? 5.5 : 8.5;
        Sfx.play('dash');
        continue;
      }
      if(e.action === 'spin_cleaver'){
        e.actionT -= dt;
        const spinSpd = (e.enraged ? 130 : 95) * g.lvlConfig.multSpeed;
        e.x += (dx / d) * spinSpd * dt;
        e.y += (dy / d) * spinSpd * dt;
        e.facing = dx >= 0 ? 1 : -1;
        keepInsideBossArena(e, g.bossArena, (e.c?.r || 48) + 10);
        if(Math.random() < 0.7){
          const sa = Math.random() * 6.283;
          g.fx.push({
            x: e.x + Math.cos(sa) * 35,
            y: e.y + Math.sin(sa) * 35,
            vx: Math.cos(sa) * 80,
            vy: Math.sin(sa) * 80,
            col: Math.random() > 0.4 ? '#dc2626' : '#991b1b',
            r: 2.2, l: 0.35
          });
        }
        if(d <= 75 && p.inv <= 0){
          damagePlayer(Math.round(28 * dt * 3));
          p.slowT = 0.5;
          g.shake = Math.max(g.shake, 0.3);
        }
        if(e.actionT <= 0) e.action = 'idle';
        continue;
      }

      // 2. Атака: Пневматический гарпун «Потрошитель» (Chain Meat Hook)
      if(e.action === 'idle' && e.hookCd <= 0 && d > 120 && d < 380){
        e.action = 'hook_prep';
        e.actionT = 0.60;
        e.hookTargetX = p.x;
        e.hookTargetY = p.y;
        e.hookCd = e.enraged ? 4.0 : 6.0;
        continue;
      }
      if(e.action === 'hook_prep'){
        e.actionT -= dt;
        e.hookTargetX = p.x; e.hookTargetY = p.y;
        if(e.actionT <= 0){
          e.action = 'hook_throw';
          e.actionT = 0.55;
          Sfx.play('dash');
          const hookAng = Math.atan2(p.y - e.y, p.x - e.x);
          g.bossShockwaves.push({
            x: e.x, y: e.y - 6,
            vx: Math.cos(hookAng) * 480,
            vy: Math.sin(hookAng) * 480,
            l: 0.70, maxL: 0.70,
            dmg: 35,
            type: 'butcher_hook',
            col: '#dc2626'
          });
        }
        continue;
      }
      if(e.action === 'hook_throw'){
        e.actionT -= dt;
        if(e.actionT <= 0) e.action = 'idle';
        continue;
      }

      // 3. Атака: Казнящий разруб тесаком (Cleaver Slam & Ground Fissure)
      if(e.action === 'idle' && d < 115 && e.cleaverCd <= 0){
        e.action = 'cleaver_prep';
        e.actionT = 0.65;
        e.cleaverCd = e.enraged ? 2.8 : 4.0;
        continue;
      }
      if(e.action === 'cleaver_prep'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'cleaver_strike';
          e.actionT = 0.35;
          g.shake = Math.max(g.shake, 0.7);
          Sfx.play('anvil');
          if(d <= 125 && p.inv <= 0){
            damagePlayer(Math.round(85 * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          }
          const fAng = Math.atan2(p.y - e.y, p.x - e.x);
          const fSpd = 360;
          g.bossShockwaves.push({
            x: e.x + (e.facing > 0 ? 30 : -30),
            y: e.y + 15,
            vx: Math.cos(fAng) * fSpd,
            vy: Math.sin(fAng) * fSpd,
            l: 0.65, maxL: 0.65,
            dmg: 45,
            type: 'fissure',
            col: '#dc2626'
          });
          g.bossShockwaves.push({
            x: e.x + (e.facing > 0 ? 30 : -30),
            y: e.y + 15,
            vx: 0, vy: 0,
            l: 5.0, maxL: 5.0,
            dmg: 8,
            type: 'puddle',
            col: '#991b1b'
          });
        }
        continue;
      }
      if(e.action === 'cleaver_strike'){
        e.actionT -= dt;
        if(e.actionT <= 0) e.action = 'idle';
        continue;
      }

      // 4. Бросок рикошетящих циркулярных пил в ярости
      if(e.enraged && e.action === 'idle' && e.sawScatterCd <= 0){
        e.action = 'saw_scatter';
        e.actionT = 0.50;
        e.sawScatterCd = 7.5;
        continue;
      }
      if(e.action === 'saw_scatter'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'idle';
          Sfx.play('anvil');
          const baseA = Math.atan2(dy, dx);
          for(const off of [-0.4, 0.4]){
            const sAng = baseA + off;
            const sSpd = 320;
            g.bossShockwaves.push({
              x: e.x, y: e.y - 10,
              vx: Math.cos(sAng) * sSpd,
              vy: Math.sin(sAng) * sSpd,
              l: 4.5, maxL: 4.5,
              dmg: 30,
              bounces: 0,
              type: 'bouncing_saw',
              col: '#e2e8f0'
            });
          }
        }
        continue;
      }

      // 5. Выброс ядовитого пара дезинфектора
      if(e.action === 'idle' && e.toxicGasCd <= 0){
        e.toxicGasCd = e.enraged ? 4.5 : 7.0;
        for(let k = 0; k < 6; k++){
          const ga = Math.random() * 6.283;
          const gDist = 20 + Math.random() * 45;
          g.bossShockwaves.push({
            x: e.x + Math.cos(ga) * gDist,
            y: e.y + Math.sin(ga) * gDist,
            vx: 0, vy: 0,
            l: 4.5, maxL: 4.5,
            dmg: 6,
            type: 'puddle',
            col: '#16a34a'
          });
        }
      }

      if(e.action === 'idle'){
        const spd = (e.enraged ? 100 : 78) * g.lvlConfig.multSpeed;
        e.x += (dx / d) * spd * dt;
        e.y += (dy / d) * spd * dt;
        e.facing = dx >= 0 ? 1 : -1;
        e.animT = (e.animT || 0) + dt * (e.enraged ? 8 : 6);
        keepInsideBossArena(e, g.bossArena, (e.c?.r || 48) + 10);
      }
      continue;
    }

    // ==========================================
    // БОСС 4 (ЛОК. 3): НЕЙРО-СВЕРХРАЗУМ (NEURO OVERMIND)
    // ==========================================
    if(e.isBoss && e.bossId === 'neuro_overmind'){
      if(e.fl > 0) e.fl -= dt;
      if(e.oh > 0) e.oh -= dt;

      if(e.spawnState === 'emerging'){
        e.spawnT -= dt;
        if(e.spawnT <= 0){
          e.spawnState = 'active';
          e.spawnT = 0;
          e.action = 'idle';
          e.actionT = 0;
        }
        continue;
      }

      const dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;

      if(!e.enraged && e.hp <= e.maxHp * 0.5){
        e.enraged = true;
        e.c.speed = 88;
        g.shake = Math.max(g.shake, 0.8);
        showGameToast('🧠 ' + T('NEURO-OVERMIND OVERLOAD! (+DEATH RAY / PHASE SHIFT)', 'НЕЙРО-СВЕРХРАЗУМ: ПЕРЕГРУЗКА ЯДРА! (+ЛУЧ СМЕРТИ / ФАЗОВЫЙ СДВИГ)'), '#a855f7', 3.8);
        Sfx.play('dash');
      }

      e.singularityCd = (e.singularityCd !== undefined ? e.singularityCd : 5.0) - dt;
      e.psiLightningCd = (e.psiLightningCd !== undefined ? e.psiLightningCd : 3.0) - dt;
      e.beamCd = (e.beamCd !== undefined ? e.beamCd : 6.5) - dt;
      e.teleportCd = (e.teleportCd !== undefined ? e.teleportCd : 8.5) - dt;
      e.droneCd = (e.droneCd !== undefined ? e.droneCd : 8.0) - dt;

      // 1. Атака: Орбитальный луч смерти «Око Судного Дня» (Psionic Death Beam)
      if(e.action === 'idle' && e.beamCd <= 0){
        e.action = 'beam_prep';
        e.actionT = 0.85;
        e.beamAngle = Math.atan2(dy, dx);
        e.beamCd = e.enraged ? 6.0 : 9.0;
        continue;
      }
      if(e.action === 'beam_prep'){
        e.actionT -= dt;
        e.beamAngle = Math.atan2(p.y - (e.y - 12), p.x - e.x);
        if(e.actionT <= 0){
          e.action = 'beam_fire';
          e.actionT = 1.6;
          Sfx.play('dash');
          g.shake = Math.max(g.shake, 0.4);
        }
        continue;
      }
      if(e.action === 'beam_fire'){
        e.actionT -= dt;
        const targetAng = Math.atan2(p.y - (e.y - 12), p.x - e.x);
        let diffA = targetAng - e.beamAngle;
        while(diffA > Math.PI) diffA -= Math.PI * 2;
        while(diffA < -Math.PI) diffA += Math.PI * 2;
        e.beamAngle += Math.max(-1.4 * dt, Math.min(1.4 * dt, diffA));

        // Коллизия луча с игроком
        const beamLen = 420;
        const bx1 = e.x, by1 = e.y - 12;
        const bx2 = e.x + Math.cos(e.beamAngle) * beamLen;
        const by2 = e.y - 12 + Math.sin(e.beamAngle) * beamLen;
        
        const lDx = bx2 - bx1, lDy = by2 - by1, lLenSq = lDx * lDx + lDy * lDy;
        const proj = Math.max(0, Math.min(1, ((p.x - bx1) * lDx + (p.y - by1) * lDy) / lLenSq));
        const nearX = bx1 + proj * lDx, nearY = by1 + proj * lDy;
        const distToBeam = Math.hypot(p.x - nearX, p.y - nearY);

        if(distToBeam < p.r + 14 && p.inv <= 0){
          damagePlayer(Math.round(48 * dt * 2.5));
          p.slowT = 0.5;
          g.shake = Math.max(g.shake, 0.35);
        }

        if(e.actionT <= 0) e.action = 'idle';
        continue;
      }

      // 2. Фазовый телепорт (Phase Shift) при сближении или по таймеру
      if(e.action === 'idle' && d < 125 && e.teleportCd <= 0 && g.bossArena){
        e.action = 'teleport_phase';
        e.actionT = 0.45;
        e.teleportCd = e.enraged ? 7.0 : 10.0;
        continue;
      }
      if(e.action === 'teleport_phase'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'idle';
          g.bossShockwaves.push({
            x: e.x, y: e.y,
            vx: 0, vy: 0,
            l: 0.8, maxL: 0.8,
            dmg: 30,
            type: 'psi_nova',
            col: '#a855f7'
          });
          const arena = g.bossArena;
          const teleAng = Math.atan2(e.y - p.y, e.x - p.x) + (Math.random() - 0.5) * 1.5;
          const teleDist = Math.min(arena.rad * 0.75, 140 + Math.random() * 60);
          e.x = arena.cx + Math.cos(teleAng) * teleDist;
          e.y = arena.cy + Math.sin(teleAng) * teleDist;
          keepInsideBossArena(e, g.bossArena, (e.c?.r || 50) + 10);
          Sfx.play('dash');
          g.shake = Math.max(g.shake, 0.5);
        }
        continue;
      }

      // 3. Атака: Гравитационная воронка (Psionic Singularity Vortex)
      if(e.action === 'idle' && e.singularityCd <= 0){
        e.action = 'singularity_cast';
        e.actionT = 0.75;
        e.singularityCd = e.enraged ? 6.5 : 9.5;
        continue;
      }
      if(e.action === 'singularity_cast'){
        e.actionT -= dt;
        if(e.actionT <= 0){
          e.action = 'idle';
          Sfx.play('dash');
          g.bossShockwaves.push({
            x: p.x, y: p.y,
            vx: 0, vy: 0,
            l: 4.2, maxL: 4.2,
            dmg: 16,
            type: 'singularity',
            col: '#a855f7'
          });
        }
        continue;
      }

      // 4. Атака: Каскадные пси-сферы (Chain Psi-Lightning Orbs)
      if(e.action === 'idle' && e.psiLightningCd <= 0){
        e.psiLightningCd = e.enraged ? 2.8 : 4.0;
        Sfx.play('shoot');
        const boltCount = e.enraged ? 7 : 5;
        for(let k = 0; k < boltCount; k++){
          const baseA = Math.atan2(dy, dx);
          const bAng = baseA + (k - (boltCount - 1) / 2) * 0.26;
          const bSpd = 270 + Math.random() * 50;
          g.bossShockwaves.push({
            x: e.x, y: e.y - 10,
            vx: Math.cos(bAng) * bSpd,
            vy: Math.sin(bAng) * bSpd,
            l: 1.6, maxL: 1.6,
            dmg: 28,
            type: 'psi_bolt',
            col: '#c084fc'
          });
        }
      }

      // 5. Призыв охранных дронов
      if(e.action === 'idle' && e.droneCd <= 0 && g.enemies.length < CONFIG.waves.maxEnemies){
        e.droneCd = e.enraged ? 8.5 : 12.0;
        const count = e.enraged ? 3 : 2;
        for(let k = 0; k < count; k++){
          const da = Math.random() * 6.283;
          g.enemies.push({
            x: e.x + Math.cos(da) * 55,
            y: e.y + Math.sin(da) * 55,
            hp: 95 * (g.lvlConfig?.multHp || 1),
            maxHp: 95 * (g.lvlConfig?.multHp || 1),
            c: { r: 13, speed: 115, damage: 16, color: '#c084fc', xp: 6 },
            isMinion: true,
            minionType: 'drone',
            oh: 0, fl: 0, dead: false, frame: 0, animT: Math.random() * 8, facing: 1
          });
        }
        showGameToast('🧠 ' + T('SECURITY DRONES DEPLOYED!', 'БОЕВЫЕ ДРОНЫ АКТИВИРОВАНЫ!'), '#a855f7', 2.0);
      }

      if(e.action === 'idle'){
        const spd = (e.enraged ? 88 : 66) * g.lvlConfig.multSpeed;
        e.x += (dx / d) * spd * dt;
        e.y += (dy / d) * spd * dt;
        e.facing = dx >= 0 ? 1 : -1;
        e.animT = (e.animT || 0) + dt * (e.enraged ? 6 : 4.5);
        keepInsideBossArena(e, g.bossArena, (e.c?.r || 50) + 10);
      }
      continue;
    }
"""

is_crlf = "\r\n" in content[pos_ai_start_line:pos_ai_end]
if is_crlf:
    replacement_ai = new_boss_ai.replace("\n", "\r\n")
else:
    replacement_ai = new_boss_ai

content = content[:pos_ai_start_line] + replacement_ai + content[pos_ai_end:]
print("2. Replaced Location 3 Boss AI successfully!")

# ------------------------------------------------------------------------------
# STEP 3: Fix shockwaves in update(dt) (remove misplaced render code)
# ------------------------------------------------------------------------------
# We locate: else if(sw.type === 'butcher_hook'){ ... else if(sw.type === 'abom_nova'){
misplaced_render_start = "        } else if(sw.type === 'butcher_hook'){\n      // Тяжелый металлический гарпун Хирурга-Мясника на цепи"
misplaced_render_end = "        } else if(sw.type === 'abom_nova'){"

p1 = content.find("} else if(sw.type === 'butcher_hook')")
p2 = content.find("} else if(sw.type === 'abom_nova')", p1)

if p1 != -1 and p2 != -1:
    correct_update_shockwaves = """        } else if(sw.type === 'butcher_hook'){
          damagePlayer(sw.dmg || 35);
          const butcher = g.enemies.find(en => en.isBoss && en.bossId === 'bio_butcher' && !en.dead);
          if(butcher){
            p.x += (butcher.x - p.x) * 0.55;
            p.y += (butcher.y - p.y) * 0.55;
            p.slowT = 1.0;
            showGameToast('🪓 ' + T('HOOKED BY THE BUTCHER!', 'ЗАХВАЧЕН ГАРПУНОМ МЯСНИКА!'), '#dc2626', 1.8);
          }
          g.shake = Math.max(g.shake, 0.5);
          Sfx.play('hit');
          sw.l = 0;
        } else if(sw.type === 'sonic_howl'){
          damagePlayer(sw.dmg || 24);
          p.slowT = Math.max(p.slowT || 0, 2.5);
          p.x += (p.x - sw.x > 0 ? 1 : -1) * 20;
          p.y += (p.y - sw.y > 0 ? 1 : -1) * 20;
          Sfx.play('hit');
        } else if(sw.type === 'psi_bolt'){
          damagePlayer(sw.dmg || 28);
          g.shake = Math.max(g.shake, 0.35);
          Sfx.play('hit');
          sw.l = 0;
        } else if(sw.type === 'singularity'){
          damagePlayer(Math.round((sw.dmg || 14) * dt * 2.5));
          p.slowT = Math.max(p.slowT || 0, 1.0);
        } else if(sw.type === 'napalm_trail'){
          damagePlayer(Math.round(18 * dt));
          p.poisonT = Math.max(p.poisonT || 0, 1.2);
          p.poisonDps = Math.max(p.poisonDps || 0, 3.0);
        } else if(sw.type === 'cerberus_quill'){
          damagePlayer(sw.dmg || 22);
          g.shake = Math.max(g.shake, 0.25);
          Sfx.play('hit');
          sw.l = 0;
        } else if(sw.type === 'cyber_missile'){
          damagePlayer(sw.dmg || 38);
          g.shake = Math.max(g.shake, 0.6);
          Sfx.play('anvil');
          sw.l = 0;
          for(let k = 0; k < 18; k++){
            const a = Math.random() * 6.283;
            const spd = 40 + Math.random() * 100;
            g.fx.push({ x: sw.x, y: sw.y, vx: Math.cos(a) * spd, vy: Math.sin(a) * spd, col: Math.random() > 0.4 ? '#ef4444' : '#f97316', r: 3, l: 0.4 });
          }
        } else if(sw.type === 'bouncing_saw'){
          damagePlayer(sw.dmg || 30);
          g.shake = Math.max(g.shake, 0.35);
          Sfx.play('hit');
        } else if(sw.type === 'fissure'){
          damagePlayer(sw.dmg || 45);
          g.shake = Math.max(g.shake, 0.5);
          Sfx.play('hit');
        } else if(sw.type === 'emp_mine'){
          damagePlayer(25);
          p.slowT = Math.max(p.slowT || 0, 2.0);
          showGameToast('⚡ ' + T('EMP SYSTEM OVERLOAD!', 'ЭМИ-ИМПУЛЬС: ПЕРЕГРУЗКА!'), '#38bdf8', 2.0);
          Sfx.play('dash');
          sw.l = 0;
        """
    is_crlf = "\r\n" in content[p1:p2]
    if is_crlf:
        rep_sw = correct_update_shockwaves.replace("\n", "\r\n")
    else:
        rep_sw = correct_update_shockwaves
    content = content[:p1] + rep_sw + content[p2:]
    print("3. Cleaned misplaced render code in update() and added physics handlers!")
else:
    print(f"Warning: misplaced render marker not found! p1={p1}, p2={p2}")

# Also add special active physics for singularity, bouncing_saw, cyber_missile in update loop right before hero distance check
pos_dist_hero = content.find("const distHero=Math.hypot(p.x-sw.x,p.y-sw.y);")
if pos_dist_hero != -1:
    extra_sw_physics = """      // Активная гравитация сингулярности (Черная дыра)
      if(sw.type === 'singularity'){
        const sDist = Math.hypot(p.x - sw.x, p.y - sw.y);
        if(sDist < 130 && sDist > 8){
          const pullPwr = (130 - sDist) * 1.6;
          const pullA = Math.atan2(sw.y - p.y, sw.x - p.x);
          p.x += Math.cos(pullA) * pullPwr * dt;
          p.y += Math.sin(pullA) * pullPwr * dt;
          if(Math.random() < 0.4){
            g.fx.push({
              x: p.x + (Math.random() - 0.5) * 20,
              y: p.y + (Math.random() - 0.5) * 20,
              vx: Math.cos(pullA) * 90,
              vy: Math.sin(pullA) * 90,
              col: '#c084fc',
              l: 0.25
            });
          }
        }
      }
      // Отражение дисковых пил от границ арены
      if(sw.type === 'bouncing_saw' && g.bossArena){
        const arena = g.bossArena;
        const bRad = arena.rad || 220;
        const aDist = Math.hypot(sw.x - arena.cx, sw.y - arena.cy);
        if(aDist > bRad - 15){
          const nA = Math.atan2(sw.y - arena.cy, sw.x - arena.cx);
          const vAng = Math.atan2(sw.vy, sw.vx);
          const refAng = 2 * nA - vAng + Math.PI;
          const spd = Math.hypot(sw.vx, sw.vy);
          sw.vx = Math.cos(refAng) * spd;
          sw.vy = Math.sin(refAng) * spd;
          sw.bounces = (sw.bounces || 0) + 1;
          Sfx.play('anvil');
          if(sw.bounces >= 4) sw.l = 0;
        }
      }
      // Самонаведение микроракет на игрока в полете
      if(sw.type === 'cyber_missile'){
        if(sw.l > sw.maxL * 0.35){
          const mAng = Math.atan2(p.y - sw.y, p.x - sw.x);
          const curAng = Math.atan2(sw.vy, sw.vx);
          let diffA = mAng - curAng;
          while(diffA > Math.PI) diffA -= Math.PI * 2;
          while(diffA < -Math.PI) diffA += Math.PI * 2;
          const turn = Math.max(-3.2 * dt, Math.min(3.2 * dt, diffA));
          const newAng = curAng + turn;
          const spd = Math.hypot(sw.vx, sw.vy);
          sw.vx = Math.cos(newAng) * spd;
          sw.vy = Math.sin(newAng) * spd;
          sw.angle = newAng;
        }
        if(Math.random() < 0.6){
          g.fx.push({
            x: sw.x, y: sw.y,
            vx: -sw.vx * 0.2 + (Math.random() - 0.5) * 20,
            vy: -sw.vy * 0.2 + (Math.random() - 0.5) * 20,
            col: Math.random() > 0.4 ? '#f97316' : '#78716c',
            r: 2, l: 0.3
          });
        }
      }
"""
    is_crlf = "\r\n" in content[pos_dist_hero-100:pos_dist_hero]
    if is_crlf:
        rep_extra = extra_sw_physics.replace("\n", "\r\n")
    else:
        rep_extra = extra_sw_physics
    content = content[:pos_dist_hero] + rep_extra + content[pos_dist_hero:]
    print("3b. Added active physics for singularity, bouncing_saw, cyber_missile!")

# ------------------------------------------------------------------------------
# STEP 4: Add complete visual renderers in drawBossShockwaves
# ------------------------------------------------------------------------------
pos_draw_sw = content.find("function drawBossShockwaves(g, ox, oy){")
pos_draw_sw_else = content.find("} else {\n      cx.translate(sx, sy);\n      cx.rotate(sw.angle);", pos_draw_sw)
if pos_draw_sw_else == -1:
    pos_draw_sw_else = content.find("} else {\r\n      cx.translate(sx, sy);\r\n      cx.rotate(sw.angle);", pos_draw_sw)

if pos_draw_sw_else != -1:
    extra_shockwaves_render = """    } else if(sw.type === 'butcher_hook'){
      // Тяжелый металлический гарпун Хирурга-Мясника на цепи
      cx.translate(sx, sy);
      cx.rotate(sw.angle || Math.atan2(sw.vy, sw.vx));
      const pulse = 0.92 + 0.08 * Math.sin(performance.now() * 0.025);
      cx.fillStyle = `rgba(148, 163, 184, ${0.95 * swAlpha})`;
      cx.beginPath();
      cx.moveTo(18 * pulse, 0); cx.lineTo(-10, -10); cx.lineTo(-6, -4); cx.lineTo(-18, -3);
      cx.lineTo(-18, 3); cx.lineTo(-6, 4); cx.lineTo(-10, 10); cx.closePath();
      cx.fill();
      cx.strokeStyle = `rgba(220, 38, 38, ${0.9 * swAlpha})`;
      cx.lineWidth = 2.0; cx.stroke();
      // Зазубрины
      cx.fillStyle = '#ef4444';
      cx.beginPath(); cx.moveTo(-4, -10); cx.lineTo(-12, -16); cx.lineTo(-8, -8); cx.fill();
      cx.beginPath(); cx.moveTo(-4, 10); cx.lineTo(-12, 16); cx.lineTo(-8, 8); cx.fill();
      // Искры на острие
      cx.fillStyle = '#fef08a';
      cx.beginPath(); cx.arc(18 * pulse, 0, 2.5, 0, 6.283); cx.fill();

      // Натянутая цепь от Мясника
      if(G && G.enemies){
        const butcher = G.enemies.find(en => en.isBoss && en.bossId === 'bio_butcher' && !en.dead);
        if(butcher){
          cx.restore();
          cx.save();
          const bx = butcher.x + ox, by = butcher.y + oy;
          const chainDx = sx - bx, chainDy = sy - by;
          const chainDist = Math.hypot(chainDx, chainDy) || 1;
          const chainAng = Math.atan2(chainDy, chainDx);
          const linkStep = 11;
          const numLinks = Math.floor(chainDist / linkStep);
          cx.lineWidth = 2.4;
          for(let li = 1; li < numLinks; li++){
            const frac = li / numLinks;
            const sag = Math.sin(frac * Math.PI) * (4 + Math.sin(performance.now() * 0.03 + li) * 2.5);
            const lx = bx + chainDx * frac + Math.cos(chainAng + Math.PI/2) * sag;
            const ly = by + chainDy * frac + Math.sin(chainAng + Math.PI/2) * sag;
            cx.save();
            cx.translate(lx, ly);
            cx.rotate(chainAng);
            if(li % 2 === 0){
              cx.strokeStyle = `rgba(148, 163, 184, ${0.9 * swAlpha})`;
              cx.fillStyle = `rgba(30, 41, 59, ${0.85 * swAlpha})`;
              cx.beginPath(); cx.ellipse(0, 0, 5.5, 2.8, 0, 0, 6.283); cx.fill(); cx.stroke();
            } else {
              cx.strokeStyle = `rgba(203, 213, 225, ${0.95 * swAlpha})`;
              cx.lineWidth = 3.0;
              cx.beginPath(); cx.moveTo(0, -3.2); cx.lineTo(0, 3.2); cx.stroke();
            }
            cx.restore();
          }
        }
      }
    } else if(sw.type === 'sonic_howl'){
      // Ультразвуковая волна Кибер-Цербера
      const prog = 1 - (sw.l / sw.maxL);
      const rad = 28 + prog * 155;
      const pulse = 0.88 + 0.12 * Math.sin(performance.now() * 0.03);
      cx.strokeStyle = `rgba(239, 68, 68, ${0.85 * swAlpha * pulse})`;
      cx.lineWidth = 3.4 * swAlpha;
      cx.beginPath(); cx.arc(sx, sy, rad, 0, 6.283); cx.stroke();
      cx.strokeStyle = `rgba(253, 224, 71, ${0.7 * swAlpha * pulse})`;
      cx.lineWidth = 1.8;
      cx.beginPath(); cx.arc(sx, sy, Math.max(0, rad - 14), 0, 6.283); cx.stroke();
      const rays = 12;
      cx.strokeStyle = `rgba(248, 113, 113, ${0.45 * swAlpha})`;
      cx.lineWidth = 1.2;
      for(let r = 0; r < rays; r++){
        const ra = (r / rays) * 6.283 + performance.now() * 0.003;
        cx.beginPath();
        cx.moveTo(sx + Math.cos(ra) * (rad - 18), sy + Math.sin(ra) * (rad - 18));
        cx.lineTo(sx + Math.cos(ra) * rad, sy + Math.sin(ra) * rad);
        cx.stroke();
      }
    } else if(sw.type === 'psi_bolt'){
      // Псионический плазменный снаряд Нейро-Сверхразума
      cx.translate(sx, sy);
      cx.rotate(sw.angle || Math.atan2(sw.vy, sw.vx));
      const pulse = 0.88 + 0.12 * Math.sin(performance.now() * 0.03);
      const r = 12 * pulse;
      const pGrad = cx.createRadialGradient(0, 0, 2, 0, 0, r * 1.8);
      pGrad.addColorStop(0, `rgba(255, 255, 255, ${0.98 * swAlpha})`);
      pGrad.addColorStop(0.35, `rgba(216, 180, 254, ${0.9 * swAlpha})`);
      pGrad.addColorStop(0.7, `rgba(168, 85, 247, ${0.55 * swAlpha})`);
      pGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = pGrad;
      cx.beginPath(); cx.arc(0, 0, r * 1.8, 0, 6.283); cx.fill();
      cx.fillStyle = `rgba(192, 132, 252, ${0.95 * swAlpha})`;
      cx.beginPath(); cx.ellipse(2, 0, r, r * 0.65, 0, 0, 6.283); cx.fill();
      cx.strokeStyle = '#ffffff';
      cx.lineWidth = 1.5;
      for(let a = 0; a < 3; a++){
        const arcA = a * 2.09 + performance.now() * 0.01;
        cx.beginPath();
        cx.moveTo(Math.cos(arcA) * 4, Math.sin(arcA) * 4);
        cx.lineTo(Math.cos(arcA) * (r + 6), Math.sin(arcA) * (r + 6));
        cx.stroke();
      }
    } else if(sw.type === 'singularity'){
      // Гравитационная воронка (Сингулярность) Нейро-Сверхразума
      const prog = 1 - (sw.l / sw.maxL);
      const spin = performance.now() * 0.006;
      const sRad = 80;
      const pulse = 0.9 + 0.1 * Math.sin(performance.now() * 0.02);
      const aGrad = cx.createRadialGradient(sx, sy, 8, sx, sy, sRad * pulse);
      aGrad.addColorStop(0, `rgba(15, 7, 26, ${0.95 * swAlpha})`);
      aGrad.addColorStop(0.4, `rgba(147, 51, 234, ${0.48 * swAlpha})`);
      aGrad.addColorStop(0.8, `rgba(192, 132, 252, ${0.25 * swAlpha})`);
      aGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = aGrad;
      cx.beginPath(); cx.arc(sx, sy, sRad * pulse, 0, 6.283); cx.fill();
      cx.save();
      cx.translate(sx, sy);
      cx.rotate(spin);
      cx.lineWidth = 1.8;
      for(let arm = 0; arm < 3; arm++){
        cx.rotate((6.283 / 3));
        cx.strokeStyle = `rgba(216, 180, 254, ${0.75 * swAlpha})`;
        cx.beginPath();
        for(let t = 0; t < 1; t += 0.08){
          const theta = t * 3.5;
          const tr = 10 + t * (sRad - 14);
          const px = Math.cos(theta) * tr;
          const py = Math.sin(theta) * tr;
          if(t === 0) cx.moveTo(px, py); else cx.lineTo(px, py);
        }
        cx.stroke();
      }
      cx.restore();
      cx.fillStyle = '#030712';
      cx.beginPath(); cx.arc(sx, sy, 15 * pulse, 0, 6.283); cx.fill();
      cx.strokeStyle = `rgba(236, 72, 153, ${0.9 * swAlpha})`;
      cx.lineWidth = 2.2;
      cx.stroke();
    } else if(sw.type === 'cyber_missile'){
      // Микроракета Кибер-Цербера
      cx.translate(sx, sy);
      cx.rotate(sw.angle || Math.atan2(sw.vy, sw.vx));
      // Корпус ракеты
      cx.fillStyle = '#475569';
      cx.fillRect(-10, -3.5, 16, 7);
      cx.fillStyle = '#ef4444';
      cx.beginPath(); cx.moveTo(6, -3.5); cx.lineTo(13, 0); cx.lineTo(6, 3.5); cx.closePath(); cx.fill();
      // Стабилизаторы
      cx.fillStyle = '#94a3b8';
      cx.beginPath(); cx.moveTo(-10, -7); cx.lineTo(-6, -3.5); cx.lineTo(-10, -3.5); cx.fill();
      cx.beginPath(); cx.moveTo(-10, 7); cx.lineTo(-6, 3.5); cx.lineTo(-10, 3.5); cx.fill();
      // Реактивная струя
      const mFlame = 8 + Math.sin(performance.now() * 0.05) * 4;
      cx.fillStyle = '#f97316';
      cx.beginPath(); cx.moveTo(-10, -2.5); cx.lineTo(-10 - mFlame, 0); cx.lineTo(-10, 2.5); cx.fill();
      cx.fillStyle = '#fef08a';
      cx.beginPath(); cx.moveTo(-10, -1.2); cx.lineTo(-10 - mFlame * 0.6, 0); cx.lineTo(-10, 1.2); cx.fill();
    } else if(sw.type === 'napalm_trail'){
      // Горящий напалмовый след Цербера
      const nProg = Math.sin(performance.now() * 0.015 + sx * 0.1) * 3;
      const nGrad = cx.createRadialGradient(sx, sy, 2, sx, sy, 18);
      nGrad.addColorStop(0, `rgba(254, 240, 138, ${0.9 * swAlpha})`);
      nGrad.addColorStop(0.35, `rgba(249, 115, 22, ${0.8 * swAlpha})`);
      nGrad.addColorStop(0.75, `rgba(239, 68, 68, ${0.4 * swAlpha})`);
      nGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = nGrad;
      cx.beginPath(); cx.ellipse(sx, sy, 18, 9, 0, 0, 6.283); cx.fill();
      // Язык пламени
      cx.fillStyle = `rgba(254, 240, 138, ${0.85 * swAlpha})`;
      cx.beginPath(); cx.moveTo(sx - 4, sy); cx.lineTo(sx, sy - 10 + nProg); cx.lineTo(sx + 4, sy); cx.fill();
    } else if(sw.type === 'cerberus_quill'){
      // Металлический нано-шип хвоста Цербера
      cx.translate(sx, sy);
      cx.rotate(Math.atan2(sw.vy, sw.vx));
      cx.fillStyle = '#cbd5e1';
      cx.beginPath(); cx.moveTo(12, 0); cx.lineTo(-8, -3); cx.lineTo(-4, 0); cx.lineTo(-8, 3); cx.closePath(); cx.fill();
      cx.strokeStyle = '#ef4444'; cx.lineWidth = 1.2; cx.stroke();
    } else if(sw.type === 'fissure'){
      // Разлом бетона от сокрушительного удара тесаком Мясника
      cx.translate(sx, sy);
      cx.rotate(Math.atan2(sw.vy, sw.vx));
      cx.strokeStyle = `rgba(220, 38, 38, ${0.9 * swAlpha})`;
      cx.lineWidth = 4.0;
      cx.beginPath(); cx.moveTo(-20, 0); cx.lineTo(20, 0); cx.stroke();
      cx.strokeStyle = `rgba(254, 240, 138, ${0.85 * swAlpha})`;
      cx.lineWidth = 1.8;
      cx.beginPath(); cx.moveTo(-16, 0); cx.lineTo(16, 0); cx.stroke();
    } else if(sw.type === 'bouncing_saw'){
      // Вращающаяся циркулярная дисковая пила
      cx.translate(sx, sy);
      cx.rotate(performance.now() * 0.02);
      const r = 16;
      cx.fillStyle = `rgba(148, 163, 184, ${0.95 * swAlpha})`;
      cx.beginPath(); cx.arc(0, 0, r, 0, 6.283); cx.fill();
      cx.strokeStyle = '#dc2626'; cx.lineWidth = 2.0; cx.stroke();
      // 8 зубьев пилы
      cx.fillStyle = '#ef4444';
      for(let z = 0; z < 8; z++){
        const za = z * (6.283 / 8);
        cx.beginPath();
        cx.moveTo(Math.cos(za) * r, Math.sin(za) * r);
        cx.lineTo(Math.cos(za + 0.25) * (r + 5), Math.sin(za + 0.25) * (r + 5));
        cx.lineTo(Math.cos(za + 0.35) * r, Math.sin(za + 0.35) * r);
        cx.fill();
      }
      cx.fillStyle = '#1e293b'; cx.beginPath(); cx.arc(0, 0, 4, 0, 6.283); cx.fill();
    } else if(sw.type === 'emp_mine'){
      // ЭМИ-мина
      const mPulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.02);
      cx.fillStyle = '#1e293b'; cx.beginPath(); cx.arc(sx, sy, 10, 0, 6.283); cx.fill();
      cx.strokeStyle = `rgba(56, 189, 248, ${0.95 * swAlpha * mPulse})`; cx.lineWidth = 2.2; cx.stroke();
      cx.fillStyle = `rgba(56, 189, 248, ${0.8 * swAlpha * mPulse})`; cx.beginPath(); cx.arc(sx, sy, 5, 0, 6.283); cx.fill();
      // Электрические дуги
      cx.strokeStyle = '#e0f2fe'; cx.lineWidth = 1.2;
      for(let a = 0; a < 3; a++){
        const aa = a * 2.09 + performance.now() * 0.008;
        cx.beginPath(); cx.moveTo(sx, sy); cx.lineTo(sx + Math.cos(aa) * 16, sy + Math.sin(aa) * 16); cx.stroke();
      }
    } else if(sw.type === 'psi_nova'){
      // Расширяющаяся пси-волна после квантового телепорта
      const prog = 1 - (sw.l / sw.maxL);
      const rad = 20 + prog * 110;
      cx.strokeStyle = `rgba(168, 85, 247, ${0.85 * swAlpha})`;
      cx.lineWidth = 3.5 * (1 - prog);
      cx.beginPath(); cx.arc(sx, sy, rad, 0, 6.283); cx.stroke();
"""
    is_crlf = "\r\n" in content[pos_draw_sw_else-100:pos_draw_sw_else]
    if is_crlf:
        rep_render = extra_shockwaves_render.replace("\n", "\r\n")
    else:
        rep_render = extra_shockwaves_render
    content = content[:pos_draw_sw_else] + rep_render + content[pos_draw_sw_else:]
    print("4. Added all 11 boss shockwave renderers in drawBossShockwaves!")
else:
    print("Warning: could not find insertion point in drawBossShockwaves!")

# ------------------------------------------------------------------------------
# STEP 5: Enhance Boss Draw Functions with new telegraphs & attack visuals
# ------------------------------------------------------------------------------
# In drawCyberCerberusBoss: add missile salvo telegraph & visuals
# In drawBioButcherBoss: add whirlwind spin & fissure line telegraph
# In drawNeuroOvermindBoss: add death ray beam telegraph & beam rendering!
pos_cerb_draw = content.find("function drawCyberCerberusBoss(e, ox, oy){")
pos_cerb_tail = content.find("if(e.action === 'tail_swipe'){", pos_cerb_draw)

# We can replace the 3 draw functions with the updated, enhanced versions
pos_draw_funcs_start = content.find("// ===== ДИНАМИЧЕСКАЯ ПОКАДРОВАЯ ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР =====")
pos_draw_funcs_end = content.find("function drawSlimeBoss(e, ox, oy){", pos_draw_funcs_start)

if pos_draw_funcs_start != -1 and pos_draw_funcs_end != -1:
    new_enhanced_draw_funcs = """// ===== ДИНАМИЧЕСКАЯ ПОКАДРОВАЯ ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР =====
function drawCyberCerberusBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 50;

  if(e.spawnState === 'emerging'){
    drawCyberCerberusEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Телеграф рывка: лазерный целеуказатель с анимированными шевронами
  if(e.action === 'dash_prep'){
    cx.save();
    const cLen = 340;
    const cAng = e.chargeAng !== undefined ? e.chargeAng : Math.atan2(G.p.y - e.y, G.p.x - e.x);
    cx.translate(ex, ey);
    cx.rotate(cAng);
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.02);

    cx.fillStyle = `rgba(239, 68, 68, ${0.15 * pulse})`;
    cx.fillRect(0, -22, cLen, 44);

    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.5;
    cx.setLineDash([10, 6]);
    cx.lineDashOffset = -performance.now() * 0.06;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(cLen, 0); cx.stroke();
    cx.setLineDash([]);

    cx.strokeStyle = '#fef08a';
    cx.lineWidth = 2.0;
    const chevOff = (performance.now() * 0.12) % 40;
    for(let d = chevOff; d < cLen; d += 40){
      cx.beginPath(); cx.moveTo(d - 6, -10); cx.lineTo(d + 4, 0); cx.lineTo(d - 6, 10); cx.stroke();
    }
    cx.restore();
  }

  // 2. Телеграф взмаха хвостом (360-градусный круг с шипами)
  if(e.action === 'tail_swipe'){
    cx.save();
    const r = 95;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(239, 68, 68, ${0.28 * pulse})`;
    cx.beginPath(); cx.arc(ex, ey, r, 0, 6.283); cx.fill();
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.2; cx.stroke();
    cx.restore();
  }

  // 3. Телеграф ракетного залпа: прицельный перекрестный маркер на игроке
  if(e.action === 'missile_salvo'){
    cx.save();
    const px = G.p.x + ox, py = G.p.y + oy;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.translate(px, py);
    cx.strokeStyle = `rgba(239, 68, 68, ${0.92 * pulse})`;
    cx.lineWidth = 2.0;
    cx.setLineDash([6, 4]);
    cx.beginPath(); cx.arc(0, 0, 32 * pulse, 0, 6.283); cx.stroke();
    cx.setLineDash([]);
    cx.beginPath(); cx.moveTo(-40, 0); cx.lineTo(40, 0); cx.moveTo(0, -40); cx.lineTo(0, 40); cx.stroke();
    cx.restore();
  }

  // 4. Тень под лапами
  const isDashing = (e.action === 'dash_run' || e.action === 'dash_rebound');
  const isHowling = (e.action === 'howl');
  const shadowScale = isDashing ? 1.25 : (isHowling ? 0.9 : 1.0);
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 52 * shadowScale, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 5. Выбор покадрового спрайта
  const fw = 340, fh = 300;
  const bw = 156, bh = 138;
  let currentSheet = bossCyberCerberusWalkImg;
  let frame = 0;
  let bobY = 0;

  if(e.action === 'dash_prep'){
    currentSheet = bossCyberCerberusAttackImg;
    const windProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.70)));
    frame = Math.min(2, Math.floor(windProg * 3));
    bobY = 4 * windProg;
  } else if(isDashing){
    currentSheet = bossCyberCerberusAttackImg;
    const runProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.45)));
    frame = Math.min(5, 3 + Math.floor(runProg * 3));
    bobY = -2;
  } else if(isHowling){
    currentSheet = bossCyberCerberusAttackImg;
    const howlProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.8)));
    frame = Math.min(7, 6 + Math.floor(howlProg * 2));
    bobY = -4;
  } else if(e.action === 'tail_swipe'){
    currentSheet = bossCyberCerberusAttackImg;
    const swipeProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.5)));
    frame = Math.min(5, 3 + Math.floor(swipeProg * 3));
  } else if(e.action === 'missile_salvo'){
    currentSheet = bossCyberCerberusAttackImg;
    frame = 1;
    bobY = 3;
  } else {
    currentSheet = bossCyberCerberusWalkImg;
    frame = Math.floor(e.animT || 0) % 8;
  }
  e.frame = frame;

  // 6. Полупрозрачные шлейфы скорости при рывке
  if(isDashing){
    for(let ghost = 2; ghost >= 1; ghost--){
      cx.save();
      const ghostDist = ghost * 22;
      const gx = ex - Math.cos(e.chargeAng || 0) * ghostDist;
      const gy = ey - Math.sin(e.chargeAng || 0) * ghostDist;
      cx.translate(gx, gy + bobY);
      if(e.facing > 0) cx.scale(-1, 1);
      cx.globalAlpha = 0.28 / ghost;
      cx.filter = 'drop-shadow(0 0 14px #ef4444) brightness(1.5)';
      if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
        cx.imageSmoothingEnabled = false;
        cx.drawImage(currentSheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 4, bw, bh);
      }
      cx.restore();
    }
  }

  // 7. Основная отрисовка покадрового спрайта
  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);

  if(e.fl > 0) cx.filter = 'brightness(3)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(239, 68, 68, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.5))';

  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(currentSheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 4, bw, bh);
  } else if(bossCyberCerberusSheetImg && bossCyberCerberusSheetImg.complete && bossCyberCerberusSheetImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossCyberCerberusSheetImg, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 4, bw, bh);
  } else if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 4, bw, bh);
  } else {
    cx.fillStyle = '#ef4444';
    cx.beginPath(); cx.arc(0, 0, e.c.r, 0, 6.283); cx.fill();
  }
  cx.filter = 'none';

  cx.restore();
}

// ===== ДИНАМИЧЕСКАЯ ПОКАДРОВАЯ ОТРИСОВКА БОССА 2: ХИРУРГ-МЯСНИК =====
function drawBioButcherBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 56;

  if(e.spawnState === 'emerging'){
    drawBioButcherEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Телеграф пневматического гарпуна
  if(e.action === 'hook_prep'){
    cx.save();
    const hLen = 340;
    const hAng = Math.atan2((e.hookTargetY || G.p.y) - e.y, (e.hookTargetX || G.p.x) - e.x);
    cx.translate(ex, ey - 6);
    cx.rotate(hAng);
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.025);
    
    cx.strokeStyle = `rgba(220, 38, 38, ${0.9 * pulse})`;
    cx.lineWidth = 2.2;
    cx.setLineDash([10, 6]);
    cx.lineDashOffset = -performance.now() * 0.05;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(hLen, 0); cx.stroke();
    cx.setLineDash([]);

    const tx = (e.hookTargetX || G.p.x) + ox, ty = (e.hookTargetY || G.p.y) + oy;
    cx.restore();
    cx.save();
    cx.translate(tx, ty);
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 1.8;
    cx.beginPath(); cx.arc(0, 0, 14 * pulse, 0, 6.283); cx.stroke();
    cx.beginPath(); cx.moveTo(-18, 0); cx.lineTo(18, 0); cx.stroke();
    cx.beginPath(); cx.moveTo(0, -18); cx.lineTo(0, 18); cx.stroke();
    cx.restore();
  }

  // 2. Телеграф казнящего разруба тесаком (опасный сектор и линия разлома)
  if(e.action === 'cleaver_prep'){
    cx.save();
    const cAng = Math.atan2(G.p.y - e.y, G.p.x - e.x);
    const cRad = 135;
    const halfA = 0.55;
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.025);
    cx.fillStyle = `rgba(220, 38, 38, ${0.28 * pulse})`;
    cx.beginPath();
    cx.moveTo(ex, ey + 10);
    cx.arc(ex, ey + 10, cRad, cAng - halfA, cAng + halfA);
    cx.closePath(); cx.fill();
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.2;
    cx.stroke();
    // Направляющая линия разлома
    cx.strokeStyle = '#fef08a';
    cx.lineWidth = 1.8;
    cx.beginPath();
    cx.moveTo(ex, ey + 10);
    cx.lineTo(ex + Math.cos(cAng) * 220, ey + 10 + Math.sin(cAng) * 220);
    cx.stroke();
    cx.restore();
  }

  // 3. Вихрь мясорубки: опасный вращающийся ореол
  if(e.action === 'spin_cleaver'){
    cx.save();
    const sRad = 75;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.04);
    cx.fillStyle = `rgba(220, 38, 38, ${0.32 * pulse})`;
    cx.beginPath(); cx.arc(ex, ey, sRad, 0, 6.283); cx.fill();
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 3.0;
    cx.setLineDash([12, 6]);
    cx.lineDashOffset = performance.now() * 0.05;
    cx.stroke();
    cx.restore();
  }

  // 4. Тень под сапогами
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.55)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 56, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 5. Выбор покадрового спрайта
  const fw = 360, fh = 300;
  const bw = 192, bh = 160;
  let currentSheet = bossBioButcherWalkImg;
  let frame = 0;
  let bobY = 0;

  if(e.action === 'cleaver_prep'){
    currentSheet = bossBioButcherAttackImg;
    const windProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.65)));
    frame = Math.min(3, Math.floor(windProg * 4));
    bobY = -6 * windProg;
  } else if(e.action === 'cleaver_strike'){
    currentSheet = bossBioButcherAttackImg;
    frame = 4 + (Math.floor(performance.now() / 80) % 2);
    bobY = 4;
  } else if(e.action === 'hook_prep'){
    currentSheet = bossBioButcherAttackImg;
    const prepProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.60)));
    frame = Math.min(5, 4 + Math.floor(prepProg * 2));
    bobY = 2;
  } else if(e.action === 'hook_throw'){
    currentSheet = bossBioButcherAttackImg;
    const throwProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.55)));
    frame = Math.min(7, 6 + Math.floor(throwProg * 2));
    bobY = 0;
  } else if(e.action === 'saw_scatter'){
    currentSheet = bossBioButcherAttackImg;
    frame = 2;
    bobY = -2;
  } else if(e.action === 'spin_cleaver'){
    currentSheet = bossBioButcherWalkImg;
    frame = Math.floor(performance.now() / 60) % 8;
  } else {
    currentSheet = bossBioButcherWalkImg;
    frame = Math.floor(e.animT || 0) % 8;
    bobY = (frame === 1 || frame === 5) ? 3 : 0;
  }
  e.frame = frame;

  // 6. Отрисовка спрайта Мясника
  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.action === 'spin_cleaver'){
    cx.rotate(performance.now() * 0.02);
  } else if(e.facing > 0){
    cx.scale(-1, 1);
  }

  if(e.fl > 0) cx.filter = 'brightness(3)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(220, 38, 38, 0.95)) contrast(1.2)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(185, 28, 28, 0.6))';

  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(currentSheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossBioButcherSheetImg && bossBioButcherSheetImg.complete && bossBioButcherSheetImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossBioButcherSheetImg, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    cx.fillStyle = '#dc2626';
    cx.beginPath(); cx.arc(0, 0, e.c.r, 0, 6.283); cx.fill();
  }
  cx.filter = 'none';

  cx.restore();
}

// ===== ДИНАМИЧЕСКАЯ ПОКАДРОВАЯ ОТРИСОВКА БОССА 4: НЕЙРО-СВЕРХРАЗУМ =====
function drawNeuroOvermindBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 52;

  if(e.spawnState === 'emerging'){
    drawNeuroOvermindEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Телеграф прицельного лазерного луча «Око Судного Дня»
  if(e.action === 'beam_prep'){
    cx.save();
    const bAng = e.beamAngle || Math.atan2(G.p.y - (e.y - 12), G.p.x - e.x);
    const bLen = 420;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.translate(ex, ey - 12);
    cx.rotate(bAng);
    // Тонкий красный прицельный луч
    cx.strokeStyle = `rgba(239, 68, 68, ${0.9 * pulse})`;
    cx.lineWidth = 1.8;
    cx.setLineDash([8, 4]);
    cx.lineDashOffset = -performance.now() * 0.05;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(bLen, 0); cx.stroke();
    cx.setLineDash([]);
    // Прицельная точка на конце луча
    cx.fillStyle = '#fef08a';
    cx.beginPath(); cx.arc(bLen, 0, 4, 0, 6.283); cx.fill();
    cx.restore();
  }

  // 2. Отрисовка активного луча смерти (Beam Fire)
  if(e.action === 'beam_fire'){
    cx.save();
    const bAng = e.beamAngle;
    const bLen = 440;
    const pulse = 0.90 + 0.10 * Math.sin(performance.now() * 0.04);
    cx.translate(ex, ey - 12);
    cx.rotate(bAng);

    // Внешняя фиолетовая аура луча
    const beamW = 22 * pulse;
    const bGrad = cx.createLinearGradient(0, -beamW, 0, beamW);
    bGrad.addColorStop(0, 'rgba(168, 85, 247, 0)');
    bGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.7)');
    bGrad.addColorStop(1, 'rgba(168, 85, 247, 0)');
    cx.fillStyle = bGrad;
    cx.fillRect(0, -beamW, bLen, beamW * 2);

    // Бело-розовое горячее ядро луча
    cx.strokeStyle = '#ffffff';
    cx.lineWidth = 6 * pulse;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(bLen, 0); cx.stroke();

    cx.strokeStyle = '#f472b6';
    cx.lineWidth = 12 * pulse;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(bLen, 0); cx.stroke();

    // Вспышка на глазу босса
    cx.fillStyle = '#ffffff';
    cx.beginPath(); cx.arc(0, 0, 14 * pulse, 0, 6.283); cx.fill();
    cx.fillStyle = '#c084fc';
    cx.beginPath(); cx.arc(0, 0, 20 * pulse, 0, 6.283); cx.fill();
    cx.restore();
  }

  // 3. Телеграф сингулярности
  if(e.action === 'singularity_cast'){
    cx.save();
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    const sRad = 110;
    const spin = performance.now() * 0.008;
    cx.translate(G.p.x + ox, G.p.y + oy);
    cx.rotate(spin);
    cx.strokeStyle = `rgba(168, 85, 247, ${0.9 * pulse})`;
    cx.lineWidth = 2.4;
    cx.setLineDash([12, 6]);
    cx.beginPath(); cx.arc(0, 0, sRad, 0, 6.283); cx.stroke();
    cx.setLineDash([]);
    cx.restore();
  }

  // 4. Плавная невесомость и тень на земле
  const floatY = Math.sin(performance.now() * 0.003) * 6.5;
  const shadowPulse = 1.0 - (floatY / 30);
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.48)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 48 * shadowPulse, 16 * shadowPulse, 0, 0, 6.283); cx.fill();
  const ringPulse = 0.75 + 0.25 * Math.sin(performance.now() * 0.006);
  cx.strokeStyle = `rgba(168, 85, 247, ${0.65 * ringPulse})`;
  cx.lineWidth = 2.2;
  cx.beginPath(); cx.ellipse(ex, ey + floatY + 16, 46, 18, 0, 0, 6.283); cx.stroke();
  cx.restore();

  // 5. Выбор покадрового спрайта
  const fw = 320, fh = 320;
  const bw = 156, bh = 156;
  let currentSheet = bossNeuroOvermindFloatImg;
  let frame = 0;

  if(e.action === 'singularity_cast' || e.action === 'beam_prep' || e.action === 'beam_fire'){
    currentSheet = bossNeuroOvermindAttackImg;
    const prog = Math.max(0, Math.min(1, 1 - (e.actionT / 0.85)));
    frame = Math.min(7, Math.floor(prog * 8));
  } else {
    currentSheet = bossNeuroOvermindFloatImg;
    frame = Math.floor(e.animT || 0) % 8;
  }
  e.frame = frame;

  // 6. Отрисовка покадрового спрайта капсулы и мозга
  cx.save();
  cx.translate(ex, ey + floatY);
  if(e.action === 'teleport_phase'){
    cx.globalAlpha = 0.35 + 0.35 * Math.sin(performance.now() * 0.05); // мерцание
  }
  if(e.facing > 0) cx.scale(-1, 1);

  if(e.fl > 0) cx.filter = 'brightness(3)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 18px rgba(168, 85, 247, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 10px rgba(168, 85, 247, 0.65))';

  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(currentSheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossNeuroOvermindSheetImg && bossNeuroOvermindSheetImg.complete && bossNeuroOvermindSheetImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossNeuroOvermindSheetImg, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    cx.fillStyle = '#a855f7';
    cx.beginPath(); cx.arc(0, 0, e.c.r, 0, 6.283); cx.fill();
  }
  cx.filter = 'none';

  cx.restore();
}

"""
    is_crlf = "\r\n" in content[pos_draw_funcs_start:pos_draw_funcs_end]
    if is_crlf:
        rep_draw = new_enhanced_draw_funcs.replace("\n", "\r\n")
    else:
        rep_draw = new_enhanced_draw_funcs
    content = content[:pos_draw_funcs_start] + rep_draw + content[pos_draw_funcs_end:]
    print("5. Enhanced draw functions with all new abilities and telegraphs!")
else:
    print("Warning: could not find draw functions markers!")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("All boss abilities overhauled successfully!")
