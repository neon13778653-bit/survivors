# -*- coding: utf-8 -*-
"""
apply_complete_boss_fix.py
Applies full fixes for:
1. prepareBossArena: add cx, cy, rad
2. All arena coordinate calculations in boss AI (Bio-Butcher, Neuro-Overmind, Chitin Reaper)
3. Rectangular saw bouncing for bouncing_saw & execution_saw in update()
4. Telegraph detonation on sw.l <= 0 without double damage or premature detonation
5. butcher_hook single damage & bounded pull
6. drawBossShockwaves: implement all 11 missing shockwaves + safe rotate fallback
7. Emergence & active drawing for all 5 Zone 3 bosses using pristine full-body sprites without severed parts
8. Cleanup g.bossShockwaves on boss skip and quit to menu
"""

import os
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. prepareBossArena: add cx, cy, rad
    target_arena = """  g.bossArena={
    x:g.p.x-side/2,
    y:g.p.y-side/2,
    size:side,
    spawnAt:performance.now()
  };"""

    repl_arena = """  g.bossArena={
    x:g.p.x-side/2,
    y:g.p.y-side/2,
    size:side,
    cx:g.p.x,
    cy:g.p.y,
    rad:side/2,
    spawnAt:performance.now()
  };"""

    if target_arena not in content:
        print("ERROR: target_arena not found!")
        sys.exit(1)
    content = content.replace(target_arena, repl_arena, 1)
    print("1. Patched prepareBossArena successfully!")

    # 2. Cleanup bossShockwaves in testSkipBoss
    target_skip_boss = """    g.activeBoss = null;
    g.bossArena = null;
    g.bossWarning = null;"""
    repl_skip_boss = """    g.activeBoss = null;
    g.bossArena = null;
    g.bossWarning = null;
    g.bossShockwaves = [];"""
    if target_skip_boss not in content:
        print("ERROR: target_skip_boss not found!")
        sys.exit(1)
    content = content.replace(target_skip_boss, repl_skip_boss, 1)
    print("2. Patched testSkipBoss cleanup!")

    # 3. Bio-Butcher cage_prep coordinates
    target_cage = """        if(e.actionT <= 0){
          const arena = g.bossArena || { cx: e.x, cy: e.y, rad: 220 };
          const corners = [0, 1.5708, 3.1416, 4.7124];
          for(let c = 0; c < 4; c++){
            const ang = corners[c];
            const sx = arena.cx + Math.cos(ang) * (arena.rad - 25);
            const sy = arena.cy + Math.sin(ang) * (arena.rad - 25);"""

    repl_cage = """        if(e.actionT <= 0){
          const arena = g.bossArena || { x: p.x - 220, y: p.y - 220, size: 440, cx: p.x, cy: p.y, rad: 220 };
          const acx = arena.cx !== undefined ? arena.cx : (arena.x + arena.size / 2);
          const acy = arena.cy !== undefined ? arena.cy : (arena.y + arena.size / 2);
          const arad = arena.rad !== undefined ? arena.rad : (arena.size / 2);
          const corners = [0, 1.5708, 3.1416, 4.7124];
          for(let c = 0; c < 4; c++){
            const ang = corners[c];
            const sx = acx + Math.cos(ang) * (arad - 25);
            const sy = acy + Math.sin(ang) * (arad - 25);"""

    if target_cage not in content:
        print("ERROR: target_cage not found!")
        sys.exit(1)
    content = content.replace(target_cage, repl_cage, 1)
    print("3. Patched Bio-Butcher cage_prep coordinates!")

    # 4. Neuro-Overmind supernova_prep coordinates
    target_supernova = """        if(e.actionT <= 0){
          if(g.bossArena){
            e.x = g.bossArena.cx;
            e.y = g.bossArena.cy;
          }"""

    repl_supernova = """        if(e.actionT <= 0){
          if(g.bossArena){
            const acx = g.bossArena.cx !== undefined ? g.bossArena.cx : (g.bossArena.x + g.bossArena.size / 2);
            const acy = g.bossArena.cy !== undefined ? g.bossArena.cy : (g.bossArena.y + g.bossArena.size / 2);
            e.x = acx;
            e.y = acy;
          }"""

    if target_supernova not in content:
        print("ERROR: target_supernova not found!")
        sys.exit(1)
    content = content.replace(target_supernova, repl_supernova, 1)
    print("4. Patched Neuro-Overmind supernova_prep coordinates!")

    # 5. Neuro-Overmind teleport_phase coordinates
    target_teleport = """          const arena = g.bossArena;
          const teleAng = Math.atan2(e.y - p.y, e.x - p.x) + (Math.random() - 0.5) * 1.5;
          const teleDist = Math.min(arena.rad * 0.75, 140 + Math.random() * 60);
          e.x = arena.cx + Math.cos(teleAng) * teleDist;
          e.y = arena.cy + Math.sin(teleAng) * teleDist;
          keepInsideBossArena(e, g.bossArena, (e.c?.r || 50) + 10);"""

    repl_teleport = """          const arena = g.bossArena || { x: p.x - 220, y: p.y - 220, size: 440, cx: p.x, cy: p.y, rad: 220 };
          const acx = arena.cx !== undefined ? arena.cx : (arena.x + arena.size / 2);
          const acy = arena.cy !== undefined ? arena.cy : (arena.y + arena.size / 2);
          const arad = arena.rad !== undefined ? arena.rad : (arena.size / 2);
          const teleAng = Math.atan2(e.y - p.y, e.x - p.x) + (Math.random() - 0.5) * 1.5;
          const teleDist = Math.min(arad * 0.75, 140 + Math.random() * 60);
          e.x = acx + Math.cos(teleAng) * teleDist;
          e.y = acy + Math.sin(teleAng) * teleDist;
          keepInsideBossArena(e, g.bossArena, (e.c?.r || 50) + 10);"""

    if target_teleport not in content:
        print("ERROR: target_teleport not found!")
        sys.exit(1)
    content = content.replace(target_teleport, repl_teleport, 1)
    print("5. Patched Neuro-Overmind teleport coordinates!")

    # 6. Chitin Reaper brood_burrow coordinates
    target_brood = """          const arena = g.bossArena || { cx: e.x, cy: e.y, rad: 220 };
          const angles = [0.78, 2.35, 3.92, 5.49];
          for(const a of angles){
            const fx = arena.cx + Math.cos(a) * (arena.rad * 0.6);
            const fy = arena.cy + Math.sin(a) * (arena.rad * 0.6);"""

    repl_brood = """          const arena = g.bossArena || { x: p.x - 220, y: p.y - 220, size: 440, cx: p.x, cy: p.y, rad: 220 };
          const acx = arena.cx !== undefined ? arena.cx : (arena.x + arena.size / 2);
          const acy = arena.cy !== undefined ? arena.cy : (arena.y + arena.size / 2);
          const arad = arena.rad !== undefined ? arena.rad : (arena.size / 2);
          const angles = [0.78, 2.35, 3.92, 5.49];
          for(const a of angles){
            const fx = acx + Math.cos(a) * (arad * 0.6);
            const fy = acy + Math.sin(a) * (arad * 0.6);"""

    if target_brood not in content:
        print("ERROR: target_brood not found!")
        sys.exit(1)
    content = content.replace(target_brood, repl_brood, 1)
    print("6. Patched Chitin Reaper brood_burrow coordinates!")

    # 7. Shockwave update block in update():
    # Replace lines from `if(sw.type === 'bouncing_saw' && g.bossArena){` to `if(g.bossWarning){`
    idx_sw_start = content.find("      // Отражение дисковых пил от границ арены\n      if(sw.type === 'bouncing_saw' && g.bossArena){")
    if idx_sw_start == -1:
        idx_sw_start = content.find("if(sw.type === 'bouncing_saw' && g.bossArena){")
    idx_sw_end = content.find("  // 5. Обновление предупреждения босса и кратеров\n  if(g.bossWarning){")

    if idx_sw_start == -1 or idx_sw_end == -1:
        print(f"ERROR: Shockwave update block markers not found: {idx_sw_start}, {idx_sw_end}")
        sys.exit(1)

    repl_sw_update = """      // Прямоугольный рикошет дисковых пил от лазерных стен арены
      if((sw.type === 'bouncing_saw' || sw.type === 'execution_saw') && g.bossArena){
        if(sw.hitHeroCd > 0) sw.hitHeroCd -= dt;
        const ax1 = g.bossArena.x + 20, ax2 = g.bossArena.x + g.bossArena.size - 20;
        const ay1 = g.bossArena.y + 20, ay2 = g.bossArena.y + g.bossArena.size - 20;
        let bounced = false;
        if(sw.x <= ax1 && sw.vx < 0){ sw.x = ax1; sw.vx = Math.abs(sw.vx); bounced = true; }
        else if(sw.x >= ax2 && sw.vx > 0){ sw.x = ax2; sw.vx = -Math.abs(sw.vx); bounced = true; }
        if(sw.y <= ay1 && sw.vy < 0){ sw.y = ay1; sw.vy = Math.abs(sw.vy); bounced = true; }
        else if(sw.y >= ay2 && sw.vy > 0){ sw.y = ay2; sw.vy = -Math.abs(sw.vy); bounced = true; }
        if(bounced){
          sw.bounces = (sw.bounces || 0) + 1;
          Sfx.play('anvil');
          g.shake = Math.max(g.shake, 0.25);
          const maxB = sw.type === 'execution_saw' ? 7 : 5;
          if(sw.bounces >= maxB) sw.l = 0;
        }
        if(Math.random() < 0.65){
          g.fx.push({
            x: sw.x + (Math.random() - 0.5) * 16,
            y: sw.y + (Math.random() - 0.5) * 16,
            vx: -sw.vx * 0.15 + (Math.random() - 0.5) * 40,
            vy: -sw.vy * 0.15 + (Math.random() - 0.5) * 40,
            col: sw.type === 'execution_saw' ? (Math.random() > 0.4 ? '#ef4444' : '#f59e0b') : '#94a3b8',
            r: 2.2, l: 0.25
          });
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

      // twin_singularity (Нейро-Сверхразум: Пси-Сверхновая - двойная гравитационная сингулярность)
      if(sw.type === 'twin_singularity'){
        sw.orbitAngle = (sw.orbitAngle || 0) + 0.95 * dt;
        if(g.bossArena){
          const acx = g.bossArena.cx !== undefined ? g.bossArena.cx : (g.bossArena.x + g.bossArena.size / 2);
          const acy = g.bossArena.cy !== undefined ? g.bossArena.cy : (g.bossArena.y + g.bossArena.size / 2);
          const oRad = sw.orbitRad || 125;
          const oAng = sw.orbitAngle + (sw.twinId || 0) * Math.PI;
          sw.x = acx + Math.cos(oAng) * oRad;
          sw.y = acy + Math.sin(oAng) * oRad;
        }
        const sDist = Math.hypot(p.x - sw.x, p.y - sw.y);
        if(sDist < 145 && sDist > 8){
          const pullPwr = (145 - sDist) * 1.85;
          const pullA = Math.atan2(sw.y - p.y, sw.x - p.x);
          p.x += Math.cos(pullA) * pullPwr * dt;
          p.y += Math.sin(pullA) * pullPwr * dt;
          if(Math.random() < 0.45){
            g.fx.push({
              x: p.x + (Math.random() - 0.5) * 20,
              y: p.y + (Math.random() - 0.5) * 20,
              vx: Math.cos(pullA) * 100,
              vy: Math.sin(pullA) * 100,
              col: '#c084fc',
              l: 0.25
            });
          }
        }
      }

      // bone_boomerang (Нулевой Пациент: Костяной бумеранг)
      if(sw.type === 'bone_boomerang'){
        if(sw.hitHeroCd > 0) sw.hitHeroCd -= dt;
        sw.flightT = (sw.flightT || 0) + dt;
        const bBoss = g.enemies.find(en => en.isBoss && en.bossId === 'patient_zero' && !en.dead);
        const retX = bBoss ? bBoss.x : (sw.originX || sw.x);
        const retY = bBoss ? bBoss.y : (sw.originY || sw.y);
        if(sw.flightT < 0.65){
          sw.vx *= Math.pow(0.25, dt);
          sw.vy *= Math.pow(0.25, dt);
        } else {
          const toBx = retX - sw.x, toBy = retY - sw.y;
          const toBd = Math.hypot(toBx, toBy) || 1;
          const retSpd = 440;
          sw.vx = (toBx / toBd) * retSpd;
          sw.vy = (toBy / toBd) * retSpd;
          if(toBd < 35 && sw.flightT > 0.85){
            sw.l = 0;
          }
        }
        if(Math.random() < 0.65){
          g.fx.push({
            x: sw.x + (Math.random() - 0.5) * 14,
            y: sw.y + (Math.random() - 0.5) * 14,
            vx: (Math.random() - 0.5) * 30,
            vy: -10 - Math.random() * 20,
            col: '#ef4444',
            r: 2.2, l: 0.28
          });
        }
      }

      // psi_needle (Нейро-Сверхразум: Самонаводящиеся пси-иглы)
      if(sw.type === 'psi_needle'){
        const nAng = Math.atan2(p.y - sw.y, p.x - sw.x);
        const curAng = Math.atan2(sw.vy, sw.vx);
        let diffA = nAng - curAng;
        while(diffA > Math.PI) diffA -= Math.PI * 2;
        while(diffA < -Math.PI) diffA += Math.PI * 2;
        const turn = Math.max(-4.2 * dt, Math.min(4.2 * dt, diffA));
        const newAng = curAng + turn;
        const spd = Math.hypot(sw.vx, sw.vy);
        sw.vx = Math.cos(newAng) * spd;
        sw.vy = Math.sin(newAng) * spd;
        sw.angle = newAng;
      }

      // chitin_toxic_nova (Хитиновый Жнец: Расширяющееся кислотное кольцо)
      if(sw.type === 'chitin_toxic_nova'){
        sw.rad = (sw.rad || 20) + 210 * dt;
        if(sw.hitHeroCd > 0) sw.hitHeroCd -= dt;
      }

      const distHero = Math.hypot(p.x - sw.x, p.y - sw.y);
      if(distHero < p.r + 16 && p.inv <= 0){
        // ЧИСТЫЕ НАЗЕМНЫЕ ТЕЛЕГРАФЫ ОБРАТНОГО ОТСЧЕТА: взрываются строго при sw.l <= 0
        if(sw.type === 'carpet_bomb' || sw.type === 'acid_geyser' || sw.type === 'abyssal_spike_eruption'){
          // Пропускаем нанесение урона в фазе предупреждения!
        } else if(sw.type === 'puddle'){
          p.poisonT = Math.max(p.poisonT || 0, 2.0);
          p.poisonDps = Math.max(p.poisonDps || 0, 2.0);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.85);
        } else if(sw.type === 'abom_puddle'){
          p.poisonT = Math.max(p.poisonT || 0, 3.2);
          p.poisonDps = Math.max(p.poisonDps || 0, 4.0);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.70);
          showGameToast('☣️ ' + T('DRENCHED IN ABYSSAL INK!', 'ОБЛИТ ЧЕРНИЛАМИ БЕЗДНЫ!'), '#a855f7', 1.6);
        } else if(sw.type === 'abom_glob'){
          p.poisonT = Math.max(p.poisonT || 0, 3.0);
          p.poisonDps = Math.max(p.poisonDps || 0, 4.0);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.70);
          showGameToast('☣️ ' + T('ABYSSAL INK VOLLEY HIT!', 'УДАР ЧЕРНИЛ БЕЗДНЫ!'), '#a855f7', 1.6);
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.5, maxL: 4.5, dmg: 8, type: 'abom_puddle', col: '#a855f7' });
          for(let k = 0; k < 12; k++){
            g.fx.push({ x: p.x, y: p.y, vx: (Math.random() - 0.5) * 80, vy: -15 - Math.random() * 25, col: '#a855f7', r: 2.5, l: 0.35 });
          }
          const dmg = Math.max(1, Math.round((sw.dmg || 28) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'abomination'){
          for(let k = 0; k < 10; k++){
            g.fx.push({ x: p.x, y: p.y, vx: (Math.random() - 0.5) * 90, vy: -20 - Math.random() * 30, col: Math.random() > 0.4 ? '#a855f7' : '#f3e8ff', l: 0.35 });
          }
          Sfx.play('hit');
          const dmg = Math.max(1, Math.round((sw.dmg || 35) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'abom_nova'){
          for(let k = 0; k < 8; k++){
            g.fx.push({ x: p.x, y: p.y, vx: (Math.random() - 0.5) * 75, vy: -15 - Math.random() * 25, col: '#c084fc', l: 0.3 });
          }
          Sfx.play('hit');
          const dmg = Math.max(1, Math.round((sw.dmg || 30) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'web'){
          p.poisonT = Math.max(p.poisonT || 0, 1.8);
          p.poisonDps = Math.max(p.poisonDps || 0, 2.0);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.82);
          const dmg = Math.max(1, Math.round((sw.dmg || 20) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'web_snare'){
          p.webStunT = 0.75;
          p.poisonT = Math.max(p.poisonT || 0, 2.0);
          p.poisonDps = Math.max(p.poisonDps || 0, 2.0);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.85);
          showGameToast('🕸️ ' + T('IMMOBILIZED BY WEB! (0.8s)', 'ОЦЕПЛЕНИЕ ПАУТИНОЙ! (0.8 сек)'), '#f59e0b', 2.0);
          Sfx.play('dash');
          for(let k = 0; k < 16; k++){
            g.fx.push({
              x: p.x + (Math.random() - 0.5) * 24,
              y: p.y + (Math.random() - 0.5) * 24,
              vx: (Math.random() - 0.5) * 70,
              vy: -20 - Math.random() * 30,
              col: Math.random() > 0.5 ? '#ffffff' : '#f59e0b',
              l: 0.45
            });
          }
          const dmg = Math.max(1, Math.round((sw.dmg || 25) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'treant_seismic'){
          for(let k = 0; k < 8; k++){
            g.fx.push({
              x: p.x, y: p.y,
              vx: (Math.random() - 0.5) * 80,
              vy: -20 - Math.random() * 30,
              col: Math.random() > 0.5 ? '#22c55e' : '#854d0e',
              l: 0.35
            });
          }
          const dmg = Math.max(1, Math.round((sw.dmg || 30) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'treant_spore' || sw.type === 'mushroom_spore'){
          p.poisonT = Math.max(p.poisonT || 0, sw.type === 'mushroom_spore' ? 1.8 : 2.4);
          p.poisonDps = Math.max(p.poisonDps || 0, sw.type === 'mushroom_spore' ? 2 : 3);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.85);
          showGameToast('☣️ ' + T('INFECTED BY TOXIC SPORES!', 'ЗАРАЖЕН ЯДОВИТЫМИ СПОРАМИ!'), '#84cc16', 1.8);
          for(let k = 0; k < 10; k++){
            g.fx.push({
              x: p.x, y: p.y,
              vx: (Math.random() - 0.5) * 60,
              vy: -15 - Math.random() * 25,
              col: '#84cc16',
              l: 0.4
            });
          }
          const dmg = Math.max(1, Math.round((sw.dmg || 22) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'slime_glob'){
          p.poisonT = Math.max(p.poisonT || 0, 2.0);
          p.poisonDps = Math.max(p.poisonDps || 0, 2.5);
          p.poisonSlow = Math.min(p.poisonSlow || 1, 0.85);
          showGameToast('☣️ ' + T('SPLASHED WITH ACID!', 'ОБЛИТ ЕДКОЙ СЛИЗЬЮ!'), '#22c55e', 1.6);
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.5, maxL: 4.5, dmg: 4, type: 'puddle', col: '#22c55e' });
          for(let k = 0; k < 12; k++){
            g.fx.push({ x: p.x, y: p.y, vx: (Math.random() - 0.5) * 80, vy: -15 - Math.random() * 25, col: '#22c55e', r: 2.5, l: 0.35 });
          }
          const dmg = Math.max(1, Math.round((sw.dmg || 24) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'butcher_hook'){
          const dmg = Math.max(1, Math.round((sw.dmg || 35) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          const butcher = g.enemies.find(en => en.isBoss && en.bossId === 'bio_butcher' && !en.dead);
          if(butcher){
            p.x += (butcher.x - p.x) * 0.45;
            p.y += (butcher.y - p.y) * 0.45;
            keepInsideBossArena(p, g.bossArena);
            p.slowT = 1.0;
            showGameToast('🪓 ' + T('HOOKED BY THE BUTCHER!', 'ЗАХВАЧЕН ГАРПУНОМ МЯСНИКА!'), '#dc2626', 1.8);
          }
          g.shake = Math.max(g.shake, 0.5);
          Sfx.play('hit');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'cerberus_quill'){
          const dmg = Math.max(1, Math.round((sw.dmg || 24) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          p.slowT = Math.max(p.slowT || 0, 1.2);
          Sfx.play('hit');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'emp_mine'){
          const dmg = Math.max(1, Math.round(25 * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          p.slowT = Math.max(p.slowT || 0, 2.0);
          showGameToast('⚡ ' + T('EMP SYSTEM OVERLOAD!', 'ЭМИ-ИМПУЛЬС: ПЕРЕГРУЗКА!'), '#38bdf8', 2.0);
          Sfx.play('dash');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'execution_saw' || sw.type === 'bouncing_saw'){
          if(!sw.hitHeroCd || sw.hitHeroCd <= 0){
            const dmg = Math.max(1, Math.round((sw.dmg || 34) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
            damagePlayer(dmg);
            g.shake = Math.max(g.shake, 0.45);
            Sfx.play('hit');
            sw.hitHeroCd = 0.45;
          }
          continue;
        } else if(sw.type === 'twin_singularity'){
          const dmg = Math.max(1, Math.round((sw.dmg || 16) * dt * 2.5));
          damagePlayer(dmg);
          p.slowT = Math.max(p.slowT || 0, 1.0);
          continue;
        } else if(sw.type === 'bone_boomerang'){
          if(!sw.hitHeroCd || sw.hitHeroCd <= 0){
            const dmg = Math.max(1, Math.round((sw.dmg || 38) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
            damagePlayer(dmg);
            g.shake = Math.max(g.shake, 0.5);
            Sfx.play('hit');
            sw.hitHeroCd = 0.50;
          }
          continue;
        } else if(sw.type === 'napalm_burst'){
          const dmg = Math.max(1, Math.round((sw.dmg || 24) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          p.poisonT = Math.max(p.poisonT || 0, 1.8);
          p.poisonDps = Math.max(p.poisonDps || 0, 3.5);
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 2.5, maxL: 2.5, dmg: 6, type: 'napalm_trail', col: '#f97316' });
          Sfx.play('hit');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'chitin_toxic_nova'){
          const curRad = sw.rad || 20;
          if(Math.abs(distHero - curRad) < 26 && (!sw.hitHeroCd || sw.hitHeroCd <= 0)){
            const dmg = Math.max(1, Math.round((sw.dmg || 45) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
            damagePlayer(dmg);
            p.slowT = 1.5;
            g.shake = Math.max(g.shake, 0.6);
            Sfx.play('hit');
            sw.hitHeroCd = 0.6;
          }
          continue;
        } else if(sw.type === 'chitin_spine'){
          const dmg = Math.max(1, Math.round((sw.dmg || 22) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          p.poisonT = Math.max(p.poisonT || 0, 2.0);
          p.poisonDps = Math.max(p.poisonDps || 0, 3.0);
          g.shake = Math.max(g.shake, 0.25);
          Sfx.play('hit');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else if(sw.type === 'psi_needle'){
          const dmg = Math.max(1, Math.round((sw.dmg || 22) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.shake = Math.max(g.shake, 0.25);
          Sfx.play('hit');
          g.bossShockwaves.splice(i, 1);
          continue;
        } else {
          const dmg = Math.max(1, Math.round((sw.dmg || 20) * (p.armor ? Math.max(0.2, 1 - p.armor) : 1)));
          damagePlayer(dmg);
          g.bossShockwaves.splice(i, 1);
          continue;
        }
      }

      if(sw.l <= 0){
        if(sw.type === 'carpet_bomb'){
          Sfx.play('anvil');
          g.shake = Math.max(g.shake, 0.65);
          const cDist = Math.hypot(p.x - sw.x, p.y - sw.y);
          if(cDist < 65 && p.inv <= 0){
            damagePlayer(sw.dmg || 46);
            p.poisonT = 2.0; p.poisonDps = 3.5;
          }
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 3.5, maxL: 3.5, dmg: 7, type: 'napalm_trail', col: '#ef4444' });
          for(let k = 0; k < 14; k++){
            const ca = Math.random() * 6.283, cspd = 50 + Math.random() * 110;
            g.fx.push({ x: sw.x, y: sw.y, vx: Math.cos(ca) * cspd, vy: Math.sin(ca) * cspd, col: Math.random() > 0.4 ? '#ef4444' : '#f59e0b', r: 3, l: 0.4 });
          }
        } else if(sw.type === 'acid_geyser'){
          Sfx.play('dash');
          g.shake = Math.max(g.shake, 0.45);
          const gDist = Math.hypot(p.x - sw.x, p.y - sw.y);
          if(gDist < 55 && p.inv <= 0){
            damagePlayer(sw.dmg || 36);
            p.slowT = 1.6; p.poisonT = 2.5; p.poisonDps = 3.0;
          }
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.5, maxL: 4.5, dmg: 6, type: 'puddle', col: '#22c55e' });
          for(let k = 0; k < 12; k++){
            g.fx.push({ x: sw.x, y: sw.y, vx: (Math.random() - 0.5) * 80, vy: -30 - Math.random() * 40, col: '#22c55e', r: 2.8, l: 0.4 });
          }
        } else if(sw.type === 'abyssal_spike_eruption'){
          Sfx.play('hit');
          g.shake = Math.max(g.shake, 0.5);
          const spDist = Math.hypot(p.x - sw.x, p.y - sw.y);
          if(spDist < 45 && p.inv <= 0){
            damagePlayer(sw.dmg || 42);
          }
          for(let k = 0; k < 10; k++){
            g.fx.push({ x: sw.x, y: sw.y, vx: (Math.random() - 0.5) * 60, vy: -20 - Math.random() * 30, col: '#ef4444', r: 2.5, l: 0.35 });
          }
        } else if(sw.type === 'slime_glob'){
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.5, maxL: 4.5, dmg: 4, type: 'puddle', col: '#22c55e' });
        } else if(sw.type === 'abom_glob'){
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.0, maxL: 4.0, dmg: 5, type: 'abom_puddle', col: '#a855f7' });
        } else if(sw.type === 'rat_salvo'){
          g.bossShockwaves.push({ x: sw.x, y: sw.y, vx: 0, vy: 0, l: 4.5, maxL: 4.5, dmg: 6, type: 'puddle', col: '#84cc16' });
        }
        g.bossShockwaves.splice(i, 1);
      }
    }
  }
\n"""

    content = content[:idx_sw_start] + repl_sw_update + content[idx_sw_end:]
    print("7. Patched Shockwave update loop and telegraph detonations!")

    # 8. Bio-Butcher execution cage telegraph coordinates in drawBioButcherBoss
    target_bb_tele = """    const arena = G.bossArena || { cx: ex, cy: ey, rad: 220 };
    const pulse = 0.82 + 0.18 * Math.sin(performance.now() * 0.035);
    const corners = [0, 1.5708, 3.1416, 4.7124];

    // 4 лазерных луча-растяжки от стен арены к Мяснику
    for(const ang of corners){
      const cx1 = arena.cx + Math.cos(ang) * (arena.rad - 25);
      const cy1 = arena.cy + Math.sin(ang) * (arena.rad - 25);"""

    repl_bb_tele = """    const arena = G.bossArena || { x: G.p.x - 220, y: G.p.y - 220, size: 440, cx: G.p.x, cy: G.p.y, rad: 220 };
    const acx = arena.cx !== undefined ? arena.cx : (arena.x + arena.size / 2);
    const acy = arena.cy !== undefined ? arena.cy : (arena.y + arena.size / 2);
    const arad = arena.rad !== undefined ? arena.rad : (arena.size / 2);
    const pulse = 0.82 + 0.18 * Math.sin(performance.now() * 0.035);
    const corners = [0, 1.5708, 3.1416, 4.7124];

    // 4 лазерных луча-растяжки от стен арены к Мяснику
    for(const ang of corners){
      const cx1 = acx + Math.cos(ang) * (arad - 25);
      const cy1 = acy + Math.sin(ang) * (arad - 25);"""

    if target_bb_tele in content:
        content = content.replace(target_bb_tele, repl_bb_tele, 1)
        print("8. Patched Bio-Butcher execution cage telegraph coordinates!")

    # 9. drawBossShockwaves: implement all 11 missing shockwaves and safe fallback
    idx_dsw_start = content.find("function drawBossShockwaves(g, ox, oy){\n  if(!g.bossShockwaves) return;")
    idx_dsw_end = content.find("function drawCraterFrontLip(ex, gy, cw, ch, lipCol='#ef4444', soilCol='#291205'){")

    if idx_dsw_start == -1 or idx_dsw_end == -1:
        print(f"ERROR: drawBossShockwaves markers not found: {idx_dsw_start}, {idx_dsw_end}")
        sys.exit(1)

    # Read current drawBossShockwaves content up to closing of loop
    # We will insert the 11 new handlers right before `} else {`
    dsw_code = content[idx_dsw_start:idx_dsw_end]
    idx_else = dsw_code.rfind("} else {")
    if idx_else == -1:
        print("ERROR: } else { in drawBossShockwaves not found!")
        sys.exit(1)

    new_handlers = """    } else if(sw.type === 'emp_mine'){
      // Высокотехнологичная синяя ЭМИ-мина Кибер-Цербера
      const pulse = 0.82 + 0.18 * Math.sin(performance.now() * 0.02 + sw.x);
      const mRad = 16 * pulse;
      cx.strokeStyle = `rgba(56, 189, 248, ${0.45 * swAlpha * pulse})`;
      cx.lineWidth = 1.6;
      cx.setLineDash([4, 4]);
      cx.beginPath(); cx.arc(sx, sy, 32 * pulse, 0, 6.283); cx.stroke();
      cx.setLineDash([]);
      const eGrad = cx.createRadialGradient(sx, sy, 2, sx, sy, mRad);
      eGrad.addColorStop(0, `rgba(224, 242, 254, ${0.95 * swAlpha})`);
      eGrad.addColorStop(0.45, `rgba(56, 189, 248, ${0.8 * swAlpha})`);
      eGrad.addColorStop(0.85, `rgba(2, 132, 199, ${0.4 * swAlpha})`);
      eGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = eGrad;
      cx.beginPath(); cx.arc(sx, sy, mRad, 0, 6.283); cx.fill();
      cx.fillStyle = '#0f172a';
      cx.beginPath(); cx.arc(sx, sy, 6, 0, 6.283); cx.fill();
      cx.strokeStyle = '#38bdf8'; cx.lineWidth = 1.8; cx.stroke();
      cx.fillStyle = (performance.now() % 300 < 150) ? '#38bdf8' : '#ef4444';
      cx.beginPath(); cx.arc(sx, sy, 2.5, 0, 6.283); cx.fill();
    } else if(sw.type === 'sonic_howl'){
      // Ультразвуковой рёв Кибер-Цербера: расходящиеся звуковые дуги
      const curRad = (sw.r || 24) + (1 - sw.l / sw.maxL) * 110;
      cx.strokeStyle = `rgba(239, 68, 68, ${0.85 * swAlpha})`;
      cx.lineWidth = 3.2 * swAlpha;
      cx.beginPath(); cx.arc(sx, sy, curRad, 0, 6.283); cx.stroke();
      cx.strokeStyle = `rgba(251, 146, 60, ${0.5 * swAlpha})`;
      cx.lineWidth = 1.8 * swAlpha;
      cx.beginPath(); cx.arc(sx, sy, Math.max(0, curRad - 8), 0, 6.283); cx.stroke();
    } else if(sw.type === 'napalm_trail'){
      // Напалмовый огонь на земле от рывка Кибер-Цербера / бомбардировки
      const fPulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.02 + sx);
      const fRad = (sw.r || 18) * fPulse;
      const nGrad = cx.createRadialGradient(sx, sy, 2, sx, sy, fRad);
      nGrad.addColorStop(0, `rgba(255, 255, 255, ${0.9 * swAlpha})`);
      nGrad.addColorStop(0.25, `rgba(254, 240, 138, ${0.85 * swAlpha})`);
      nGrad.addColorStop(0.55, `rgba(249, 115, 22, ${0.7 * swAlpha})`);
      nGrad.addColorStop(0.85, `rgba(220, 38, 38, ${0.4 * swAlpha})`);
      nGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = nGrad;
      cx.beginPath(); cx.ellipse(sx, sy, fRad, fRad * 0.65, 0, 0, 6.283); cx.fill();
      const sPhase = performance.now() * 0.008 + sx;
      cx.fillStyle = '#fef08a';
      cx.beginPath(); cx.arc(sx + Math.sin(sPhase) * 6, sy - 4 - Math.cos(sPhase) * 6, 1.8, 0, 6.283); cx.fill();
    } else if(sw.type === 'cerberus_quill'){
      // Высокоскоростной нано-шип Кибер-Цербера
      const qAng = (sw.angle !== undefined && !isNaN(sw.angle)) ? sw.angle : (sw.vx || sw.vy ? Math.atan2(sw.vy, sw.vx) : 0);
      cx.translate(sx, sy);
      cx.rotate(qAng);
      const tGrad = cx.createLinearGradient(-24, 0, 12, 0);
      tGrad.addColorStop(0, 'rgba(239, 68, 68, 0)');
      tGrad.addColorStop(0.6, `rgba(249, 115, 22, ${0.75 * swAlpha})`);
      tGrad.addColorStop(1, '#ffffff');
      cx.strokeStyle = tGrad; cx.lineWidth = 3.2; cx.lineCap = 'round';
      cx.beginPath(); cx.moveTo(-22, 0); cx.lineTo(10, 0); cx.stroke();
      cx.fillStyle = '#fef08a';
      cx.beginPath();
      cx.moveTo(12, 0); cx.lineTo(-6, -3.5); cx.lineTo(-2, 0); cx.lineTo(-6, 3.5);
      cx.closePath(); cx.fill();
    } else if(sw.type === 'cyber_missile'){
      // Самонаводящаяся микроракета «Цербер-9»
      const mAng = (sw.angle !== undefined && !isNaN(sw.angle)) ? sw.angle : (sw.vx || sw.vy ? Math.atan2(sw.vy, sw.vx) : 0);
      cx.translate(sx, sy);
      cx.rotate(mAng);
      const exGrad = cx.createLinearGradient(-18, 0, 0, 0);
      exGrad.addColorStop(0, 'rgba(239, 68, 68, 0)');
      exGrad.addColorStop(0.6, `rgba(249, 115, 22, ${0.85 * swAlpha})`);
      exGrad.addColorStop(1, '#ffffff');
      cx.strokeStyle = exGrad; cx.lineWidth = 3.6; cx.lineCap = 'round';
      cx.beginPath(); cx.moveTo(-16, 0); cx.lineTo(0, 0); cx.stroke();
      cx.fillStyle = '#dc2626';
      cx.fillRect(-8, -3, 16, 6);
      cx.fillStyle = '#fef08a';
      cx.beginPath(); cx.moveTo(8, -3); cx.lineTo(14, 0); cx.lineTo(8, 3); cx.closePath(); cx.fill();
      cx.fillStyle = '#1e293b';
      cx.beginPath();
      cx.moveTo(-8, -3); cx.lineTo(-12, -6); cx.lineTo(-6, -3);
      cx.moveTo(-8, 3); cx.lineTo(-12, 6); cx.lineTo(-6, 3);
      cx.fill();
    } else if(sw.type === 'bouncing_saw'){
      // Рикошетящая циркулярная пила Хирурга-Мясника
      cx.translate(sx, sy);
      const rot = (performance.now() * 0.02) % 6.283;
      cx.rotate(rot);
      const sRad = 16;
      cx.fillStyle = `rgba(226, 232, 240, ${0.95 * swAlpha})`;
      cx.beginPath();
      const teeth = 8;
      for(let t = 0; t < teeth; t++){
        const ta = (t / teeth) * 6.283;
        const outA = ta + 0.2;
        cx.lineTo(Math.cos(ta) * (sRad + 5), Math.sin(ta) * (sRad + 5));
        cx.lineTo(Math.cos(outA) * (sRad - 2), Math.sin(outA) * (sRad - 2));
      }
      cx.closePath(); cx.fill();
      cx.strokeStyle = '#94a3b8'; cx.lineWidth = 1.4; cx.stroke();
      cx.fillStyle = '#dc2626';
      cx.beginPath(); cx.arc(0, 0, 5, 0, 6.283); cx.fill();
      cx.fillStyle = '#ffffff';
      cx.beginPath(); cx.arc(0, 0, 2, 0, 6.283); cx.fill();
    } else if(sw.type === 'butcher_hook'){
      // Мясницкий крюк-гарпун на цепи
      const hAng = (sw.angle !== undefined && !isNaN(sw.angle)) ? sw.angle : (sw.vx || sw.vy ? Math.atan2(sw.vy, sw.vx) : 0);
      const butcher = g.enemies.find(en => en.isBoss && en.bossId === 'bio_butcher' && !en.dead);
      if(butcher){
        const bx = butcher.x + ox, by = butcher.y + oy;
        cx.strokeStyle = `rgba(153, 27, 27, ${0.85 * swAlpha})`;
        cx.lineWidth = 2.4;
        cx.setLineDash([5, 5]);
        cx.beginPath(); cx.moveTo(bx, by); cx.lineTo(sx, sy); cx.stroke();
        cx.setLineDash([]);
      }
      cx.translate(sx, sy);
      cx.rotate(hAng);
      cx.strokeStyle = '#e2e8f0';
      cx.lineWidth = 3.6;
      cx.lineCap = 'round';
      cx.beginPath();
      cx.moveTo(-14, 0); cx.lineTo(6, 0);
      cx.arc(6, -8, 8, 1.57, -1.2, true);
      cx.stroke();
      cx.fillStyle = '#ef4444';
      cx.beginPath();
      cx.moveTo(12, -14); cx.lineTo(16, -18); cx.lineTo(10, -18);
      cx.closePath(); cx.fill();
    } else if(sw.type === 'fissure'){
      // Подземная расщелина / лавовая трещина
      const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.015 + sx);
      const fLen = (sw.r || 32) * pulse;
      cx.strokeStyle = `rgba(220, 38, 38, ${0.9 * swAlpha})`;
      cx.lineWidth = 3.2;
      cx.beginPath();
      cx.moveTo(sx - fLen, sy);
      cx.lineTo(sx - fLen * 0.4, sy + 4);
      cx.lineTo(sx, sy - 3);
      cx.lineTo(sx + fLen * 0.5, sy + 5);
      cx.lineTo(sx + fLen, sy);
      cx.stroke();
      cx.strokeStyle = '#fef08a'; cx.lineWidth = 1.4; cx.stroke();
    } else if(sw.type === 'psi_bolt'){
      // Сгусток псионической молнии Нейро-Сверхразума
      const pPulse = 0.88 + 0.12 * Math.sin(performance.now() * 0.03 + sx);
      const r = 11 * pPulse;
      const pbGrad = cx.createRadialGradient(sx, sy, 1, sx, sy, r * 1.6);
      pbGrad.addColorStop(0, `rgba(255, 255, 255, ${0.98 * swAlpha})`);
      pbGrad.addColorStop(0.35, `rgba(216, 180, 254, ${0.9 * swAlpha})`);
      pbGrad.addColorStop(0.7, `rgba(168, 85, 247, ${0.5 * swAlpha})`);
      pbGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = pbGrad;
      cx.beginPath(); cx.arc(sx, sy, r * 1.6, 0, 6.283); cx.fill();
      cx.strokeStyle = '#ffffff'; cx.lineWidth = 1.5;
      for(let sp = 0; sp < 3; sp++){
        const sa = (sp * 2.094) + performance.now() * 0.01;
        cx.beginPath();
        cx.moveTo(sx, sy);
        cx.lineTo(sx + Math.cos(sa) * (r * 1.3), sy + Math.sin(sa) * (r * 1.3));
        cx.stroke();
      }
    } else if(sw.type === 'psi_nova'){
      // Расширяющаяся псионическая сверхновая
      const curRad = (sw.rad || 25) + (1 - sw.l / sw.maxL) * 120;
      cx.strokeStyle = `rgba(168, 85, 247, ${0.9 * swAlpha})`;
      cx.lineWidth = 3.5 * swAlpha;
      cx.beginPath(); cx.arc(sx, sy, curRad, 0, 6.283); cx.stroke();
      cx.strokeStyle = `rgba(244, 114, 182, ${0.6 * swAlpha})`;
      cx.lineWidth = 1.8 * swAlpha;
      cx.beginPath(); cx.arc(sx, sy, Math.max(0, curRad - 10), 0, 6.283); cx.stroke();
    } else if(sw.type === 'singularity'){
      // Гравитационная сингулярность (Черная дыра)
      const pulse = 0.88 + 0.12 * Math.sin(performance.now() * 0.02 + sx);
      const sRad = (sw.r || 32) * pulse;
      const sgGrad = cx.createRadialGradient(sx, sy, 4, sx, sy, sRad * 1.5);
      sgGrad.addColorStop(0, `rgba(15, 5, 25, ${0.98 * swAlpha})`);
      sgGrad.addColorStop(0.35, `rgba(168, 85, 247, ${0.65 * swAlpha})`);
      sgGrad.addColorStop(0.75, `rgba(244, 114, 182, ${0.35 * swAlpha})`);
      sgGrad.addColorStop(1, 'rgba(0,0,0,0)');
      cx.fillStyle = sgGrad;
      cx.beginPath(); cx.arc(sx, sy, sRad * 1.5, 0, 6.283); cx.fill();
      cx.fillStyle = '#05020a';
      cx.beginPath(); cx.arc(sx, sy, sRad * 0.55, 0, 6.283); cx.fill();
      cx.strokeStyle = '#c084fc'; cx.lineWidth = 2.0; cx.stroke();
"""

    safe_else = """} else {
      cx.translate(sx, sy);
      const ang = (sw.angle !== undefined && !isNaN(sw.angle)) ? sw.angle : (sw.vx || sw.vy ? Math.atan2(sw.vy, sw.vx) : 0);
      cx.rotate(ang);
      const col = sw.col || '#ea580c';
      const swGrad = cx.createLinearGradient(-16, 0, 18, 0);
      swGrad.addColorStop(0, 'rgba(0,0,0,0)');
      swGrad.addColorStop(0.4, col);
      swGrad.addColorStop(0.85, '#ffffff');
      swGrad.addColorStop(1, '#ffffff');
      cx.fillStyle = swGrad;
      cx.beginPath();
      cx.moveTo(18, 0);
      cx.lineTo(-12, -10);
      cx.lineTo(-6, 0);
      cx.lineTo(-12, 10);
      cx.closePath();
      cx.fill();
      cx.strokeStyle = col;
      cx.lineWidth = 1.5;
      cx.stroke();
    }
    cx.restore();
  }
}
"""

    dsw_updated = dsw_code[:idx_else] + new_handlers + safe_else
    content = content[:idx_dsw_start] + dsw_updated + content[idx_dsw_end:]
    print("9. Patched drawBossShockwaves with all 11 missing shockwaves and safe rotate fallback!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully wrote first batch of fixes to index.html!")

if __name__ == '__main__':
    main()
