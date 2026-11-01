# -*- coding: utf-8 -*-
"""
patch_boss_emergence_and_drawing.py
Upgrades emergence and combat rendering for all 5 Zone 3 bosses:
1. Cyber-Cerberus (Wave 10)
2. Bio-Butcher (Wave 20)
3. Chitin Reaper (Wave 30) - fixes the severed head and clipping box from Screenshot 3
4. Neuro-Overmind (Wave 40)
5. Patient Zero (Wave 50)
Uses pristine, intact full-body monster sprites with organic breathing, attack squashes,
wide non-destructive ground clipping, and screen shakes.
"""

import os
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find start of Zone 3 boss emergence functions
    idx_start = content.find("// ===== 1. КИБЕР-ЦЕРБЕР (ВОЛНА 10) =====\nfunction drawCyberCerberusEmergence")
    if idx_start == -1:
        idx_start = content.find("function drawCyberCerberusEmergence(e, ex, ey, gy){")
    
    # Find start of drawSlimeBoss (which comes right after drawPatientZeroBoss)
    idx_end = content.find("function drawSlimeBoss(e, ox, oy){")

    if idx_start == -1 or idx_end == -1:
        print(f"ERROR: Target markers not found: idx_start={idx_start}, idx_end={idx_end}")
        sys.exit(1)

    replacement_code = """// ===== 1. КИБЕР-ЦЕРБЕР (ВОЛНА 10) =====
function drawCyberCerberusEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 1.5;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 0.7)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const bw = 168, bh = 148;
  const hatchExpand = Math.min(1, prog * 2.5);
  const cw = 58 * hatchExpand + 6;
  const ch = 20 * hatchExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  pitGrad.addColorStop(0, '#1a0505');
  pitGrad.addColorStop(0.55, '#3b0808');
  pitGrad.addColorStop(0.85, '#6b1111');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 1.8;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: сенсоры трёх голов
  if(prog < 0.28){
    cx.save();
    const sensorAlpha = Math.min(1, prog / 0.28);
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.02);
    cx.fillStyle = `rgba(239, 68, 68, ${0.95 * sensorAlpha * pulse})`;
    cx.shadowColor = '#ef4444';
    cx.shadowBlur = 10;
    for(const offX of [-18, 0, 18]){
      cx.beginPath(); cx.arc(ex + offX, gy - 8, 3.5, 0, 6.283); cx.fill();
    }
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  // Фаза 2: Выход из шлюза с широким клиппингом по уровню земли
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 54;
    const heaveY = Math.abs(Math.sin(subProg * Math.PI * 4)) * 3.0;

    cx.save();
    cx.beginPath();
    cx.rect(ex - 160, gy - 260, 320, 260 + 2);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY - heaveY);
    if(e.facing > 0) cx.scale(-1, 1);
    const breath = 1 + Math.sin(subProg * Math.PI * 3) * 0.03;
    cx.scale(breath, 2 - breath);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(239, 68, 68, 0.75))';
    if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
      cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 8, bw, bh);
    } else {
      circle(0, 0, e.c.r, '#ef4444');
    }
    cx.restore();
    cx.restore();

    drawCyberCerberusHatchLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Приземление и готовность к бою
  if(!e.emergeSlamDone){
    e.emergeSlamDone = true;
    Sfx.play('dash');
    if(g) g.shake = Math.max(g.shake || 0, 0.55);
    if(g && g.fx){
      for(let k = 0; k < 20; k++){
        const ra = Math.random() * 6.283;
        const spd = 60 + Math.random() * 100;
        g.fx.push({
          x: e.x, y: e.y + 20,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 30,
          col: Math.random() < 0.6 ? '#ef4444' : '#f97316',
          r: 2.8, l: 0.5
        });
      }
    }
  }

  const slamProg = (prog - 0.74) / 0.26;
  const breath = 1 + Math.sin(slamProg * Math.PI * 3) * 0.04;

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 54, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(239, 68, 68, 0.85))';
  if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();

  drawCyberCerberusHatchLip(ex, gy, cw, ch);
}

// ===== 2. ХИРУРГ-МЯСНИК (ВОЛНА 20) =====
function drawBioButcherEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 1.5;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 0.7)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const bw = 192, bh = 168;
  const pitExpand = Math.min(1, prog * 2.5);
  const cw = 56 * pitExpand + 6;
  const ch = 22 * pitExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  pitGrad.addColorStop(0, '#1a0404');
  pitGrad.addColorStop(0.55, '#450a0a');
  pitGrad.addColorStop(0.85, '#7f1d1d');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#dc2626';
  cx.lineWidth = 2.0;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: тесак и крюк пробивают породу
  if(prog < 0.28){
    cx.save();
    const bladeH = (prog / 0.28) * 26;
    cx.translate(ex + (e.facing > 0 ? -14 : 14), gy - 4);
    cx.fillStyle = '#475569';
    cx.strokeStyle = '#dc2626';
    cx.lineWidth = 1.5;
    cx.beginPath();
    cx.moveTo(0, -bladeH);
    cx.lineTo(-12, 0);
    cx.lineTo(12, 0);
    cx.closePath();
    cx.fill(); cx.stroke();
    cx.restore();
    return;
  }

  // Фаза 2: Выход Мясника из коллектора с широким клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 52;
    const heaveY = Math.abs(Math.sin(subProg * Math.PI * 4)) * 3.2;

    cx.save();
    cx.beginPath();
    cx.rect(ex - 160, gy - 260, 320, 260 + 2);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY - heaveY);
    if(e.facing > 0) cx.scale(-1, 1);
    const breath = 1 + Math.sin(subProg * Math.PI * 3) * 0.03;
    cx.scale(breath, 2 - breath);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(220, 38, 38, 0.75))';
    if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
      cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
    } else {
      circle(0, 0, e.c.r, '#dc2626');
    }
    cx.restore();
    cx.restore();

    drawBioButcherFissureLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Землетрясение от шага Мясника
  if(!e.emergeSlamDone){
    e.emergeSlamDone = true;
    Sfx.play('anvil');
    if(g) g.shake = Math.max(g.shake || 0, 0.6);
    if(g && g.fx){
      for(let k = 0; k < 22; k++){
        const ra = Math.random() * 6.283;
        const spd = 70 + Math.random() * 110;
        g.fx.push({
          x: e.x, y: e.y + 25,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 35,
          col: Math.random() < 0.5 ? '#dc2626' : '#991b1b',
          r: 3.0, l: 0.55
        });
      }
    }
  }

  const slamProg = (prog - 0.74) / 0.26;
  const breath = 1 + Math.sin(slamProg * Math.PI * 3) * 0.04;

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.56)';
  cx.beginPath(); cx.ellipse(ex, gy, 58, 18, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(220, 38, 38, 0.85))';
  if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#dc2626');
  }
  cx.restore();

  drawBioButcherFissureLip(ex, gy, cw, ch);
}

// ===== 3. ХИТИНОВЫЙ ЖНЕЦ (ВОЛНА 30) =====
function drawChitinReaperEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 1.8;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 0.9)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const bw = 168, bh = 168;
  const pitExpand = Math.min(1, prog * 2.5);
  const cw = 54 * pitExpand + 6;
  const ch = 20 * pitExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  pitGrad.addColorStop(0, '#052e16');
  pitGrad.addColorStop(0.55, '#14532d');
  pitGrad.addColorStop(0.85, '#166534');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#22c55e';
  cx.lineWidth = 1.8;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: острие жвал и косы
  if(prog < 0.28){
    cx.save();
    const scytheH = (prog / 0.28) * 24;
    cx.translate(ex, gy - 2);
    cx.strokeStyle = '#4ade80';
    cx.lineWidth = 2.2;
    cx.beginPath();
    cx.moveTo(-12, 0); cx.lineTo(-20, -scytheH);
    cx.moveTo(12, 0); cx.lineTo(20, -scytheH);
    cx.stroke();
    cx.restore();
    return;
  }

  // Фаза 2: Выползание скорпиона с широким клиппингом по уровню земли (цельный спрайт!)
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 48;
    const heaveY = Math.abs(Math.sin(subProg * Math.PI * 4)) * 2.8;

    cx.save();
    cx.beginPath();
    // Широкий клип, гарантированно не срезающий боковые лапы и клешни босса!
    cx.rect(ex - 160, gy - 260, 320, 260 + 2);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY - heaveY);
    if(e.facing > 0) cx.scale(-1, 1);
    const breath = 1 + Math.sin(subProg * Math.PI * 3) * 0.03;
    cx.scale(breath, 2 - breath);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(34, 197, 94, 0.75))';
    if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
      cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
    } else {
      circle(0, 0, e.c.r, '#22c55e');
    }
    cx.restore();
    cx.restore();

    drawChitinReaperCraterLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Всплеск кислоты и появление скорпиона в полный рост
  if(!e.emergeSlamDone){
    e.emergeSlamDone = true;
    Sfx.play('dash');
    if(g) g.shake = Math.max(g.shake || 0, 0.55);
    if(g && g.fx){
      for(let k = 0; k < 20; k++){
        const ra = Math.random() * 6.283;
        const spd = 65 + Math.random() * 110;
        g.fx.push({
          x: e.x, y: e.y + 20,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 35,
          col: Math.random() < 0.5 ? '#22c55e' : '#84cc16',
          r: 2.8, l: 0.5
        });
      }
    }
  }

  const slamProg = (prog - 0.74) / 0.26;
  const breath = 1 + Math.sin(slamProg * Math.PI * 3) * 0.04;

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 56, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.85))';
  if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
    cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#22c55e');
  }
  cx.restore();

  drawChitinReaperCraterLip(ex, gy, cw, ch);
}

// ===== 4. НЕЙРО-СВЕРХРАЗУМ (ВОЛНА 40) =====
function drawNeuroOvermindEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 1.6;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 0.8)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const bw = 168, bh = 168;
  const vortexExpand = Math.min(1, prog * 2.5);
  const cw = 58 * vortexExpand + 6;
  const ch = 22 * vortexExpand + 2;

  cx.save();
  const vGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  vGrad.addColorStop(0, '#1e052e');
  vGrad.addColorStop(0.5, '#4a044e');
  vGrad.addColorStop(0.85, '#701a75');
  vGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = vGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#a855f7';
  cx.lineWidth = 2.0;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: Псионические лучи из центра разлома
  if(prog < 0.28){
    cx.save();
    const beamH = (prog / 0.28) * 45;
    const beamGrad = cx.createLinearGradient(ex, gy, ex, gy - beamH);
    beamGrad.addColorStop(0, 'rgba(168, 85, 247, 0.8)');
    beamGrad.addColorStop(1, 'rgba(236, 72, 153, 0)');
    cx.fillStyle = beamGrad;
    cx.beginPath();
    cx.moveTo(ex - 12, gy); cx.lineTo(ex - 20, gy - beamH);
    cx.lineTo(ex + 20, gy - beamH); cx.lineTo(ex + 12, gy);
    cx.closePath(); cx.fill();
    cx.restore();
    return;
  }

  // Фаза 2: Левитация ядра из воронки с широким клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 55;
    const floatBob = Math.sin(subProg * Math.PI * 4) * 3.5;

    cx.save();
    cx.beginPath();
    cx.rect(ex - 160, gy - 260, 320, 260 + 2);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY + floatBob);
    if(e.facing > 0) cx.scale(-1, 1);
    const breath = 1 + Math.sin(subProg * Math.PI * 3) * 0.035;
    cx.scale(breath, 2 - breath);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 14px rgba(168, 85, 247, 0.85))';
    if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
      cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
    } else {
      circle(0, 0, e.c.r, '#a855f7');
    }
    cx.restore();
    cx.restore();

    drawNeuroOvermindVortexLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Псионический взрыв
  if(!e.emergeSlamDone){
    e.emergeSlamDone = true;
    Sfx.play('dash');
    if(g) g.shake = Math.max(g.shake || 0, 0.6);
    if(g && g.fx){
      for(let k = 0; k < 20; k++){
        const ra = Math.random() * 6.283;
        const spd = 70 + Math.random() * 110;
        g.fx.push({
          x: e.x, y: e.y + 15,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 25,
          col: Math.random() < 0.5 ? '#a855f7' : '#ec4899',
          r: 2.8, l: 0.55
        });
      }
    }
  }

  const slamProg = (prog - 0.74) / 0.26;
  const breath = 1 + Math.sin(slamProg * Math.PI * 3) * 0.04;

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 56, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 16px rgba(168, 85, 247, 0.95))';
  if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#a855f7');
  }
  cx.restore();

  drawNeuroOvermindVortexLip(ex, gy, cw, ch);
}

// ===== 5. НУЛЕВОЙ ПАЦИЕНТ (ВОЛНА 50) =====
function drawPatientZeroEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 2.0;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 0.9)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const bw = 184, bh = 184;
  const craterExpand = Math.min(1, prog * 2.5);
  const cw = 64 * craterExpand + 8;
  const ch = 24 * craterExpand + 3;

  cx.save();
  const rGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  rGrad.addColorStop(0, '#260404');
  rGrad.addColorStop(0.5, '#570a0a');
  rGrad.addColorStop(0.85, '#991b1b');
  rGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = rGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 2.2;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: пульсация био-мутагена
  if(prog < 0.28){
    cx.save();
    const pulse = 0.75 + 0.25 * Math.sin(performance.now() * 0.02);
    cx.fillStyle = `rgba(239, 68, 68, ${0.85 * pulse * (prog / 0.28)})`;
    cx.shadowColor = '#ef4444';
    cx.shadowBlur = 12;
    cx.beginPath();
    cx.arc(ex, gy - 6, 14 * (prog / 0.28), 0, 6.283);
    cx.fill();
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  // Фаза 2: Подъем колосса из реактора с широким клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 56;
    const heaveY = Math.abs(Math.sin(subProg * Math.PI * 4)) * 3.4;

    cx.save();
    cx.beginPath();
    cx.rect(ex - 160, gy - 260, 320, 260 + 2);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY - heaveY);
    if(e.facing > 0) cx.scale(-1, 1);
    const breath = 1 + Math.sin(subProg * Math.PI * 3) * 0.035;
    cx.scale(breath, 2 - breath);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 12px rgba(239, 68, 68, 0.85))';
    if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
      cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 10, bw, bh);
    } else {
      circle(0, 0, e.c.r, '#ef4444');
    }
    cx.restore();
    cx.restore();

    drawPatientZeroCraterLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Взрыв реактора и выход в полный рост
  if(!e.emergeSlamDone){
    e.emergeSlamDone = true;
    Sfx.play('anvil');
    if(g) g.shake = Math.max(g.shake || 0, 0.7);
    if(g && g.fx){
      for(let k = 0; k < 25; k++){
        const ra = Math.random() * 6.283;
        const spd = 80 + Math.random() * 130;
        g.fx.push({
          x: e.x, y: e.y + 25,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 40,
          col: Math.random() < 0.5 ? '#ef4444' : '#b91c1c',
          r: 3.2, l: 0.6
        });
      }
    }
  }

  const slamProg = (prog - 0.74) / 0.26;
  const breath = 1 + Math.sin(slamProg * Math.PI * 3) * 0.04;

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.56)';
  cx.beginPath(); cx.ellipse(ex, gy, 62, 20, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 14px rgba(239, 68, 68, 0.9))';
  if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
    cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 10, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();

  drawPatientZeroCraterLip(ex, gy, cw, ch);
}

// ===== ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР (CYBER-CERBERUS) =====
function drawCyberCerberusBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 52;

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

  // 4. Телеграф огнеметного залпа (Flamethrower Sweep)
  if(e.action === 'flame_prep'){
    cx.save();
    const fAng = e.flameAng !== undefined ? e.flameAng : Math.atan2(G.p.y - e.y, G.p.x - e.x);
    const fRad = 270;
    cx.translate(ex, ey - 4);
    const fGrad = cx.createRadialGradient(0, 0, 10, 0, 0, fRad);
    fGrad.addColorStop(0, 'rgba(254, 240, 138, 0.45)');
    fGrad.addColorStop(0.35, 'rgba(249, 115, 22, 0.35)');
    fGrad.addColorStop(0.75, 'rgba(239, 68, 68, 0.2)');
    fGrad.addColorStop(1, 'rgba(239, 68, 68, 0)');
    cx.fillStyle = fGrad;
    cx.beginPath();
    cx.moveTo(0, 0);
    cx.arc(0, 0, fRad, fAng - 0.45, fAng + 0.45);
    cx.closePath(); cx.fill();
    cx.restore();
  }

  // 5. Огнеметный поток
  if(e.action === 'flame_fire'){
    cx.save();
    const sweep = Math.sin(performance.now() * 0.012) * 0.45;
    const curA = (e.flameAng || 0) + sweep;
    const fLen = 290;
    cx.translate(ex, ey - 6);
    const fGrad = cx.createRadialGradient(0, 0, 15, 0, 0, fLen);
    fGrad.addColorStop(0, '#ffffff');
    fGrad.addColorStop(0.2, '#facc15');
    fGrad.addColorStop(0.55, '#f97316');
    fGrad.addColorStop(0.85, '#dc2626');
    fGrad.addColorStop(1, 'rgba(153, 27, 27, 0)');
    cx.fillStyle = fGrad;
    cx.beginPath();
    cx.moveTo(0, 0);
    cx.arc(0, 0, fLen, curA - 0.35, curA + 0.35);
    cx.closePath(); cx.fill();
    cx.restore();
  }

  // 6. Телеграф ультимейта
  if(e.action === 'overdrive_prep'){
    cx.save();
    const pulse = 0.82 + 0.18 * Math.sin(performance.now() * 0.04);
    const spin = performance.now() * 0.004;
    cx.translate(ex, ey);
    cx.rotate(spin);
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 3.2;
    cx.beginPath();
    for(let o = 0; o < 8; o++){
      const oa = o * (6.283 / 8);
      const orx = Math.cos(oa) * 78, ory = Math.sin(oa) * 78;
      if(o === 0) cx.moveTo(orx, ory); else cx.lineTo(orx, ory);
    }
    cx.closePath(); cx.stroke();
    cx.fillStyle = `rgba(239, 68, 68, ${0.16 * pulse})`;
    cx.fill();
    cx.restore();
  }

  // 7. Тень под лапами
  const isDashing = (e.action === 'dash_run' || e.action === 'dash_rebound');
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, shadowY, isDashing ? 65 : 52, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 8. Отрисовка спрайта Цербера с органической анимацией
  const bw = 168, bh = 148;
  const breath = 1 + Math.sin(performance.now() * 0.005) * 0.03;
  const dashStretch = isDashing ? 1.2 : 1.0;
  const bobY = Math.sin(performance.now() * 0.008) * 3;

  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath * dashStretch, (2 - breath) / dashStretch);

  if(e.fl > 0) cx.filter = 'brightness(1.8) contrast(1.2)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(239, 68, 68, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.55))';

  if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 6, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();
}

// ===== ОТРИСОВКА БОССА 2: ХИРУРГ-МЯСНИК (BIO-BUTCHER) =====
function drawBioButcherBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 56;

  if(e.spawnState === 'emerging'){
    drawBioButcherEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Телеграф броска гарпуна
  if(e.action === 'hook_windup'){
    cx.save();
    const hLen = 320;
    const hAng = Math.atan2(G.p.y - e.y, G.p.x - e.x);
    cx.translate(ex, ey);
    cx.rotate(hAng);
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(220, 38, 38, ${0.16 * pulse})`;
    cx.fillRect(0, -18, hLen, 36);
    cx.strokeStyle = `rgba(239, 68, 68, ${0.92 * pulse})`;
    cx.lineWidth = 2.4;
    cx.setLineDash([8, 6]);
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(hLen, 0); cx.stroke();
    cx.setLineDash([]);
    cx.restore();
  }

  // 2. Телеграф сокрушительного удара тесаком
  if(e.action === 'cleaver_windup'){
    cx.save();
    const cRad = 110;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(220, 38, 38, ${0.25 * pulse})`;
    cx.beginPath(); cx.arc(ex, ey, cRad, 0, 6.283); cx.fill();
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.4; cx.stroke();
    cx.restore();
  }

  // 3. Телеграф «Стальной капкан» (Execution Cage)
  if(e.action === 'cage_prep'){
    cx.save();
    const arena = G.bossArena || { x: G.p.x - 220, y: G.p.y - 220, size: 440, cx: G.p.x, cy: G.p.y, rad: 220 };
    const acx = arena.cx !== undefined ? arena.cx : (arena.x + arena.size / 2);
    const acy = arena.cy !== undefined ? arena.cy : (arena.y + arena.size / 2);
    const arad = arena.rad !== undefined ? arena.rad : (arena.size / 2);
    const pulse = 0.82 + 0.18 * Math.sin(performance.now() * 0.035);
    const corners = [0, 1.5708, 3.1416, 4.7124];
    for(const ang of corners){
      const cx1 = acx + Math.cos(ang) * (arad - 25);
      const cy1 = acy + Math.sin(ang) * (arad - 25);
      cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
      cx.lineWidth = 2.8;
      cx.beginPath();
      cx.moveTo(cx1 + ox, cy1 + oy);
      cx.lineTo(ex, ey);
      cx.stroke();
      cx.fillStyle = '#ef4444';
      cx.beginPath(); cx.arc(cx1 + ox, cy1 + oy, 14 * pulse, 0, 6.283); cx.fill();
    }
    cx.restore();
  }

  // 4. Тень под ногами
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 58, 18, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 5. Отрисовка спрайта Мясника
  const bw = 192, bh = 168;
  const breath = 1 + Math.sin(performance.now() * 0.005) * 0.03;
  const isSpinning = (e.action === 'spin_cleaver');
  const bobY = Math.sin(performance.now() * 0.007) * 3;

  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);
  if(isSpinning){
    cx.rotate(Math.sin(performance.now() * 0.03) * 0.15);
  }
  cx.scale(breath, 2 - breath);

  if(e.fl > 0) cx.filter = 'brightness(1.8) contrast(1.2)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(220, 38, 38, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(185, 28, 28, 0.55))';

  if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#dc2626');
  }
  cx.restore();
}

// ===== ОТРИСОВКА БОССА 3: ХИТИНОВЫЙ ЖНЕЦ (CHITINOUS REAPER) =====
function drawChitinReaperBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 54;

  if(e.spawnState === 'emerging'){
    drawChitinReaperEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Нахождение под землей (Burrow travel): отрисовка трещин вместо спрайта
  if(e.action === 'burrow_travel' || e.action === 'brood_burrow'){
    cx.save();
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.04);
    cx.fillStyle = `rgba(20, 83, 45, ${0.45 * pulse})`;
    cx.beginPath(); cx.ellipse(ex, ey + 10, 36, 16, 0, 0, 6.283); cx.fill();
    cx.strokeStyle = '#22c55e';
    cx.lineWidth = 2.0;
    for(let cr = 0; cr < 5; cr++){
      const cra = cr * 1.25 + performance.now() * 0.005;
      cx.beginPath();
      cx.moveTo(ex, ey + 10);
      cx.lineTo(ex + Math.cos(cra) * 28, ey + 10 + Math.sin(cra) * 14);
      cx.stroke();
    }
    cx.restore();
    return;
  }

  // 2. Телеграф прорыва из-под земли
  if(e.action === 'burrow_erupt' || e.action === 'brood_erupt'){
    cx.save();
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(34, 197, 94, ${0.35 * pulse})`;
    cx.beginPath(); cx.arc(ex, ey, 95, 0, 6.283); cx.fill();
    cx.strokeStyle = `rgba(132, 204, 22, ${0.95 * pulse})`;
    cx.lineWidth = 2.4;
    cx.stroke();
    cx.restore();
  }

  // 3. Телеграф серповидного разруба жвалами
  if(e.action === 'slash_windup'){
    cx.save();
    const sAng = Math.atan2(G.p.y - e.y, G.p.x - e.x);
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(34, 197, 94, ${0.28 * pulse})`;
    cx.beginPath();
    cx.moveTo(ex, ey);
    cx.arc(ex, ey, 105, sAng - 0.6, sAng + 0.6);
    cx.closePath(); cx.fill();
    cx.strokeStyle = `rgba(163, 230, 53, ${0.95 * pulse})`;
    cx.lineWidth = 2.0;
    cx.stroke();
    cx.restore();
  }

  // 4. Тень под ногами
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 56, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 5. Отрисовка цельного спрайта Жнеца (без расчленения и артефактов!)
  const bw = 168, bh = 168;
  const breath = 1 + Math.sin(performance.now() * 0.005) * 0.03;
  const attackStretch = (e.action === 'slash_strike') ? 1.15 : 1.0;
  const bobY = Math.sin(performance.now() * 0.007) * 3;

  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath * attackStretch, (2 - breath) / attackStretch);

  if(e.fl > 0) cx.filter = 'brightness(1.75) contrast(1.15)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(34, 197, 94, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(22, 163, 74, 0.6))';

  if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    cx.fillStyle = '#22c55e';
    cx.beginPath(); cx.arc(0, 0, e.c.r, 0, 6.283); cx.fill();
  }
  cx.restore();
}

// ===== ОТРИСОВКА БОССА 4: НЕЙРО-СВЕРХРАЗУМ (NEURO-OVERMIND) =====
function drawNeuroOvermindBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 52;

  if(e.spawnState === 'emerging'){
    drawNeuroOvermindEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Вращающийся квадро-луч в ярости (Supernova fire)
  if(e.action === 'supernova_fire'){
    cx.save();
    const rot = e.supernovaRot || 0;
    const bLen = 380;
    cx.translate(ex, ey - 12);
    for(let arm = 0; arm < 4; arm++){
      const bAng = rot + arm * (Math.PI / 2);
      const bGrad = cx.createLinearGradient(0, 0, Math.cos(bAng) * bLen, Math.sin(bAng) * bLen);
      bGrad.addColorStop(0, '#ffffff');
      bGrad.addColorStop(0.3, 'rgba(168, 85, 247, 0.85)');
      bGrad.addColorStop(1, 'rgba(236, 72, 153, 0)');
      cx.strokeStyle = bGrad;
      cx.lineWidth = 10;
      cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(Math.cos(bAng) * bLen, Math.sin(bAng) * bLen); cx.stroke();
      cx.strokeStyle = '#ffffff';
      cx.lineWidth = 3;
      cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(Math.cos(bAng) * bLen, Math.sin(bAng) * bLen); cx.stroke();
    }
    cx.restore();
  }

  // 2. Тень под левитирующим ядром
  const hoverY = Math.sin(performance.now() * 0.0035) * 6;
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.45)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 52, 15, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 3. Отрисовка ядра
  const bw = 168, bh = 168;
  const breath = 1 + Math.sin(performance.now() * 0.006) * 0.035;

  cx.save();
  cx.translate(ex, ey - 8 + hoverY);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);

  if(e.fl > 0) cx.filter = 'brightness(1.8) contrast(1.2)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 18px rgba(168, 85, 247, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 10px rgba(168, 85, 247, 0.65))';

  if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#a855f7');
  }
  cx.restore();
}

// ===== ОТРИСОВКА БОССА 5: НУЛЕВОЙ ПАЦИЕНТ (PATIENT ZERO) =====
function drawPatientZeroBoss(e, ox, oy){
  const ex = e.x + ox, ey = e.y + oy;
  const shadowY = ey + 58;

  if(e.spawnState === 'emerging'){
    drawPatientZeroEmergence(e, ex, ey, shadowY);
    return;
  }

  // 1. Апокалипсис скверны: 8 вращающихся лучей в ярости
  if(e.action === 'apocalypse_channel'){
    cx.save();
    const rot = e.apocalypseRot || 0;
    const bLen = 360;
    cx.translate(ex, ey - 10);
    for(let arm = 0; arm < 8; arm++){
      const bAng = rot + arm * (Math.PI / 4);
      const bGrad = cx.createLinearGradient(0, 0, Math.cos(bAng) * bLen, Math.sin(bAng) * bLen);
      bGrad.addColorStop(0, '#ffffff');
      bGrad.addColorStop(0.3, 'rgba(239, 68, 68, 0.85)');
      bGrad.addColorStop(1, 'rgba(153, 27, 27, 0)');
      cx.strokeStyle = bGrad;
      cx.lineWidth = 8;
      cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(Math.cos(bAng) * bLen, Math.sin(bAng) * bLen); cx.stroke();
      cx.strokeStyle = '#ffffff';
      cx.lineWidth = 2.4;
      cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(Math.cos(bAng) * bLen, Math.sin(bAng) * bLen); cx.stroke();
    }
    cx.restore();
  }

  // 2. Тень под ногами
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.54)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 62, 18, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 3. Отрисовка колосса
  const bw = 184, bh = 184;
  const breath = 1 + Math.sin(performance.now() * 0.005) * 0.035;
  const bobY = Math.sin(performance.now() * 0.007) * 3;

  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.scale(breath, 2 - breath);

  if(e.fl > 0) cx.filter = 'brightness(1.8) contrast(1.2)';
  else if(e.phase3) cx.filter = 'drop-shadow(0 0 20px rgba(239, 68, 68, 1)) contrast(1.35)';
  else if(e.enraged) cx.filter = 'drop-shadow(0 0 16px rgba(239, 68, 68, 0.95)) contrast(1.25)';
  else cx.filter = 'drop-shadow(0 0 8px rgba(220, 38, 38, 0.6))';

  if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 10, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();
}

"""

    content = content[:idx_start] + replacement_code + content[idx_end:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched boss emergence and drawing for all 5 bosses!")

if __name__ == '__main__':
    main()
