import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    idx1 = text.find('// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 3: ХИТИНОВЫЙ ЖНЕЦ =====')
    idx2 = text.find('function drawCyberCerberusBoss(e, ox, oy){')

    if idx1 == -1 or idx2 == -1:
        print("ERROR: Target not found!")
        sys.exit(1)

    replacement = '''// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 1: КИБЕР-ЦЕРБЕР =====
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

  // Механический шлюз бункера: стальные створки и плазменное свечение из шахты
  const hatchExpand = Math.min(1, prog * 2.5);
  const hw = 58 * hatchExpand + 6;
  const hh = 20 * hatchExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, hw);
  pitGrad.addColorStop(0, '#1a0505');
  pitGrad.addColorStop(0.55, '#3b0808');
  pitGrad.addColorStop(0.85, '#6b1111');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, hw, hh, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 1.8;
  cx.beginPath();
  cx.ellipse(ex, gy, hw, hh, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  if(prog < 0.3){
    cx.save();
    const sensorAlpha = Math.min(1, prog / 0.3);
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.02);
    cx.fillStyle = `rgba(239, 68, 68, ${0.95 * sensorAlpha * pulse})`;
    cx.shadowColor = '#ef4444';
    cx.shadowBlur = 10;
    for(const offX of [-16, 0, 16]){
      cx.beginPath(); cx.arc(ex + offX, gy - 10, 3, 0, 6.283); cx.fill();
    }
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  if(!e.emergeSlamDone && prog >= 0.74){
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

  const subProg = (prog - 0.3) / 0.7;
  const riseY = (1 - subProg) * 45;
  const bw = 156, bh = 138;

  cx.save();
  cx.translate(ex, ey + riseY);
  if(e.facing < 0) cx.scale(-1, 1);
  cx.globalAlpha = Math.min(1, subProg * 1.4);
  cx.imageSmoothingEnabled = false;

  const currentSheet = bossCyberCerberusWalkImg || bossCyberCerberusSheetImg;
  const frame = Math.floor(subProg * 8) % 8;
  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.drawImage(currentSheet, frame * 340, 0, 340, 300, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();
}

// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 2: ХИРУРГ-МЯСНИК =====
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

  const pitExpand = Math.min(1, prog * 2.5);
  const pw = 56 * pitExpand + 6;
  const ph = 22 * pitExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, pw);
  pitGrad.addColorStop(0, '#1a0404');
  pitGrad.addColorStop(0.55, '#450a0a');
  pitGrad.addColorStop(0.85, '#7f1d1d');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, pw, ph, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#dc2626';
  cx.lineWidth = 2.0;
  cx.beginPath();
  cx.ellipse(ex, gy, pw, ph, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  if(prog < 0.3){
    cx.save();
    const bladeH = (prog / 0.3) * 26;
    cx.translate(ex + (e.facing > 0 ? 14 : -14), gy - 4);
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

  if(!e.emergeSlamDone && prog >= 0.74){
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

  const subProg = (prog - 0.3) / 0.7;
  const riseY = (1 - subProg) * 48;
  const bw = 152, bh = 142;

  cx.save();
  cx.translate(ex, ey + riseY);
  if(e.facing < 0) cx.scale(-1, 1);
  cx.globalAlpha = Math.min(1, subProg * 1.4);
  cx.imageSmoothingEnabled = false;

  const currentSheet = bossBioButcherWalkImg || bossBioButcherSheetImg;
  const frame = Math.floor(subProg * 8) % 8;
  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.drawImage(currentSheet, frame * 320, 0, 320, 300, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#dc2626');
  }
  cx.restore();
}

// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 3: ХИТИНОВЫЙ ЖНЕЦ =====
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

  const pitExpand = Math.min(1, prog * 2.5);
  const pw = 54 * pitExpand + 6;
  const ph = 20 * pitExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, pw);
  pitGrad.addColorStop(0, '#052e16');
  pitGrad.addColorStop(0.55, '#14532d');
  pitGrad.addColorStop(0.85, '#166534');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, pw, ph, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#22c55e';
  cx.lineWidth = 1.8;
  cx.beginPath();
  cx.ellipse(ex, gy, pw, ph, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  if(prog < 0.3){
    cx.save();
    const scytheH = (prog / 0.3) * 24;
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

  if(!e.emergeSlamDone && prog >= 0.74){
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

  const subProg = (prog - 0.3) / 0.7;
  const riseY = (1 - subProg) * 44;
  const bw = 148, bh = 140;

  cx.save();
  cx.translate(ex, ey + riseY);
  if(e.facing < 0) cx.scale(-1, 1);
  cx.globalAlpha = Math.min(1, subProg * 1.4);
  cx.imageSmoothingEnabled = false;

  const currentSheet = bossChitinReaperWalkImg || bossChitinReaperSheetImg;
  const frame = Math.floor(subProg * 8) % 8;
  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.drawImage(currentSheet, frame * 320, 0, 320, 300, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
    cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#22c55e');
  }
  cx.restore();
}

// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 4: НЕЙРО-СВЕРХРАЗУМ =====
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

  const vortexExpand = Math.min(1, prog * 2.5);
  const vw = 52 * vortexExpand + 6;
  const vh = 22 * vortexExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, vw);
  pitGrad.addColorStop(0, '#1e052e');
  pitGrad.addColorStop(0.55, '#581c87');
  pitGrad.addColorStop(0.85, '#7e22ce');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, vw, vh, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#c084fc';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy, vw, vh, performance.now() * 0.002, 0, 6.283);
  cx.stroke();
  cx.restore();

  if(prog < 0.3){
    cx.save();
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.025);
    cx.strokeStyle = `rgba(192, 132, 252, ${0.9 * pulse})`;
    cx.lineWidth = 1.5;
    for(let a = 0; a < 6.28; a += 1.25){
      cx.beginPath();
      cx.moveTo(ex, gy - 8);
      cx.lineTo(ex + Math.cos(a) * 25 * (prog / 0.3), gy - 8 + Math.sin(a) * 16 * (prog / 0.3));
      cx.stroke();
    }
    cx.restore();
    return;
  }

  if(!e.emergeSlamDone && prog >= 0.74){
    e.emergeSlamDone = true;
    Sfx.play('hit');
    if(g) g.shake = Math.max(g.shake || 0, 0.5);
    if(g && g.fx){
      for(let k = 0; k < 22; k++){
        const ra = Math.random() * 6.283;
        const spd = 60 + Math.random() * 90;
        g.fx.push({
          x: e.x, y: e.y,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd - 20,
          col: Math.random() < 0.6 ? '#c084fc' : '#e9d5ff',
          r: 2.5, l: 0.55
        });
      }
    }
  }

  const subProg = (prog - 0.3) / 0.7;
  const riseY = (1 - subProg) * 40;
  const bw = 138, bh = 138;

  cx.save();
  cx.translate(ex, ey + riseY);
  if(e.facing < 0) cx.scale(-1, 1);
  cx.globalAlpha = Math.min(1, subProg * 1.4);
  cx.imageSmoothingEnabled = false;

  const currentSheet = bossNeuroOvermindFloatImg || bossNeuroOvermindSheetImg;
  const frame = Math.floor(subProg * 8) % 8;
  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.drawImage(currentSheet, frame * 300, 0, 300, 300, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#a855f7');
  }
  cx.restore();
}

// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 5: НУЛЕВОЙ ПАЦИЕНТ =====
function drawPatientZeroEmergence(e, ex, ey, gy){
  const g = G;
  const emergeMax = e.emergeMaxT || 2.0;
  const prog = Math.min(1, Math.max(0, 1 - (e.spawnT / emergeMax)));
  const tele = e.spawnT > emergeMax;

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 1.0)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const craterExpand = Math.min(1, prog * 2.5);
  const cw = 64 * craterExpand + 8;
  const ch = 24 * craterExpand + 3;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  pitGrad.addColorStop(0, '#1c0303');
  pitGrad.addColorStop(0.55, '#5c0a0a');
  pitGrad.addColorStop(0.85, '#991b1b');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 2.4;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.stroke();
  cx.restore();

  if(prog < 0.3){
    cx.save();
    const pulse = 0.75 + 0.25 * Math.sin(performance.now() * 0.02);
    cx.fillStyle = `rgba(239, 68, 68, ${0.85 * pulse * (prog / 0.3)})`;
    cx.shadowColor = '#ef4444';
    cx.shadowBlur = 12;
    cx.beginPath();
    cx.arc(ex, gy - 6, 12 * (prog / 0.3), 0, 6.283);
    cx.fill();
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  if(!e.emergeSlamDone && prog >= 0.74){
    e.emergeSlamDone = true;
    Sfx.play('anvil');
    if(g) g.shake = Math.max(g.shake || 0, 0.7);
    if(g && g.fx){
      for(let k = 0; k < 28; k++){
        const ra = Math.random() * 6.283;
        const spd = 80 + Math.random() * 140;
        g.fx.push({
          x: e.x, y: e.y + 20,
          vx: Math.cos(ra) * spd,
          vy: Math.sin(ra) * spd * 0.5 - 45,
          col: Math.random() < 0.6 ? '#ef4444' : '#facc15',
          r: 3.4, l: 0.65
        });
      }
    }
  }

  const subProg = (prog - 0.3) / 0.7;
  const riseY = (1 - subProg) * 55;
  const bw = 160, bh = 152;

  cx.save();
  cx.translate(ex, ey + riseY);
  if(e.facing < 0) cx.scale(-1, 1);
  cx.globalAlpha = Math.min(1, subProg * 1.4);
  cx.imageSmoothingEnabled = false;

  const currentSheet = bossPatientZeroWalkImg || bossPatientZeroSheetImg;
  const frame = Math.floor(subProg * 8) % 8;
  if(currentSheet && currentSheet.complete && currentSheet.naturalWidth > 0){
    cx.drawImage(currentSheet, frame * 320, 0, 320, 300, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
    cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 8, bw, bh);
  } else {
    circle(0, 0, e.c.r, '#ef4444');
  }
  cx.restore();
}

'''

    new_text = text[:idx1] + replacement + text[idx2:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully patched emergence functions!")

if __name__ == '__main__':
    main()
