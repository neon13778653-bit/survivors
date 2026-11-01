import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    idx1 = text.find('// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССА 1: КИБЕР-ЦЕРБЕР =====')
    idx2 = text.find('function drawCyberCerberusBoss(e, ox, oy){')

    if idx1 == -1 or idx2 == -1:
        print("ERROR: Target markers not found!")
        sys.exit(1)

    code = '''// ===== АНИМАЦИЯ ПОЯВЛЕНИЯ БОССОВ ЗОНЫ 3 (СЕКРЕТНЫЙ БУНКЕР) =====

function drawCyberCerberusHatchLip(ex, gy, cw, ch){
  cx.save();
  cx.fillStyle = '#0f172a';
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.95, ch * 0.5, 0, 0, Math.PI);
  cx.fill();
  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.9, ch * 0.5, 0, 0.1, Math.PI - 0.1);
  cx.stroke();
  cx.restore();
}

function drawBioButcherFissureLip(ex, gy, cw, ch){
  cx.save();
  cx.fillStyle = '#1c0505';
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.95, ch * 0.5, 0, 0, Math.PI);
  cx.fill();
  cx.strokeStyle = '#dc2626';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.9, ch * 0.5, 0, 0.1, Math.PI - 0.1);
  cx.stroke();
  cx.restore();
}

function drawChitinReaperCraterLip(ex, gy, cw, ch){
  cx.save();
  cx.fillStyle = '#052e16';
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.95, ch * 0.5, 0, 0, Math.PI);
  cx.fill();
  cx.strokeStyle = '#22c55e';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.9, ch * 0.5, 0, 0.1, Math.PI - 0.1);
  cx.stroke();
  cx.restore();
}

function drawNeuroOvermindVortexLip(ex, gy, cw, ch){
  cx.save();
  cx.fillStyle = '#1e052e';
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.95, ch * 0.5, 0, 0, Math.PI);
  cx.fill();
  cx.strokeStyle = '#c084fc';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.9, ch * 0.5, 0, 0.1, Math.PI - 0.1);
  cx.stroke();
  cx.restore();
}

function drawPatientZeroCraterLip(ex, gy, cw, ch){
  cx.save();
  cx.fillStyle = '#180404';
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.95, ch * 0.5, 0, 0, Math.PI);
  cx.fill();
  cx.strokeStyle = '#ef4444';
  cx.lineWidth = 1.8;
  cx.beginPath();
  cx.ellipse(ex, gy + 2, cw * 0.9, ch * 0.5, 0, 0.1, Math.PI - 0.1);
  cx.stroke();
  cx.restore();
}

// ===== 1. КИБЕР-ЦЕРБЕР (ВОЛНА 10) =====
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

  const fw = 340, fh = 300, bw = 156, bh = 138;
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
    for(const offX of [-16, 0, 16]){
      cx.beginPath(); cx.arc(ex + offX, gy - 8, 3, 0, 6.283); cx.fill();
    }
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  const sheet = (bossCyberCerberusWalkImg && bossCyberCerberusWalkImg.complete && bossCyberCerberusWalkImg.naturalWidth > 0) ? bossCyberCerberusWalkImg : bossCyberCerberusSheetImg;

  // Фаза 2: Выход из шлюза с клиппингом по уровню земли
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 50;
    const climbFrame = Math.min(7, Math.floor(subProg * 8));

    cx.save();
    cx.beginPath();
    cx.rect(ex - 110, gy - 200, 220, 200 + 4);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY);
    if(e.facing > 0) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(239, 68, 68, 0.75))';
    if(sheet && sheet.complete && sheet.naturalWidth > 0){
      cx.drawImage(sheet, climbFrame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
    } else if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
      cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 8, bw, bh);
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
  const frame = Math.min(7, Math.floor(slamProg * 8));

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 52, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(239, 68, 68, 0.85))';
  if(sheet && sheet.complete && sheet.naturalWidth > 0){
    cx.drawImage(sheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 8, bw, bh);
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

  const fw = 360, fh = 300, bw = 192, bh = 160;
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

  const sheet = (bossBioButcherWalkImg && bossBioButcherWalkImg.complete && bossBioButcherWalkImg.naturalWidth > 0) ? bossBioButcherWalkImg : bossBioButcherSheetImg;

  // Фаза 2: Выход Мясника из коллектора с клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 52;
    const climbFrame = Math.min(7, Math.floor(subProg * 8));

    cx.save();
    cx.beginPath();
    cx.rect(ex - 120, gy - 210, 240, 210 + 4);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY);
    if(e.facing > 0) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(220, 38, 38, 0.75))';
    if(sheet && sheet.complete && sheet.naturalWidth > 0){
      cx.drawImage(sheet, climbFrame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
    } else if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
      cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
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
  const frame = Math.min(7, Math.floor(slamProg * 8));

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.56)';
  cx.beginPath(); cx.ellipse(ex, gy, 56, 18, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(220, 38, 38, 0.85))';
  if(sheet && sheet.complete && sheet.naturalWidth > 0){
    cx.drawImage(sheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 8, bw, bh);
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

  const fw = 280, fh = 280, bw = 156, bh = 156;
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

  const sheet = (bossChitinReaperWalkImg && bossChitinReaperWalkImg.complete && bossChitinReaperWalkImg.naturalWidth > 0) ? bossChitinReaperWalkImg : bossChitinReaperSheetImg;

  // Фаза 2: Выползание скорпиона с клиппингом по уровню земли
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 48;
    const climbFrame = Math.min(7, Math.floor(subProg * 8));

    cx.save();
    cx.beginPath();
    cx.rect(ex - 110, gy - 200, 220, 200 + 4);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY);
    if(e.facing > 0) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 10px rgba(34, 197, 94, 0.75))';
    if(sheet && sheet.complete && sheet.naturalWidth > 0){
      cx.drawImage(sheet, climbFrame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
    } else if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
      cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
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
  const frame = Math.min(7, Math.floor(slamProg * 8));

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 54, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.85))';
  if(sheet && sheet.complete && sheet.naturalWidth > 0){
    cx.drawImage(sheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossChitinReaperImg && bossChitinReaperImg.complete && bossChitinReaperImg.naturalWidth > 0){
    cx.drawImage(bossChitinReaperImg, -bw / 2, -bh / 2 - 8, bw, bh);
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

  const fw = 320, fh = 320, bw = 156, bh = 156;
  const vortexExpand = Math.min(1, prog * 2.5);
  const cw = 52 * vortexExpand + 6;
  const ch = 22 * vortexExpand + 2;

  cx.save();
  const pitGrad = cx.createRadialGradient(ex, gy, 4, ex, gy, cw);
  pitGrad.addColorStop(0, '#1e052e');
  pitGrad.addColorStop(0.55, '#581c87');
  pitGrad.addColorStop(0.85, '#7e22ce');
  pitGrad.addColorStop(1, 'rgba(0,0,0,0)');
  cx.fillStyle = pitGrad;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, 0, 0, 6.283);
  cx.fill();

  cx.strokeStyle = '#c084fc';
  cx.lineWidth = 1.6;
  cx.beginPath();
  cx.ellipse(ex, gy, cw, ch, performance.now() * 0.002, 0, 6.283);
  cx.stroke();
  cx.restore();

  // Фаза 1: псионические молнии
  if(prog < 0.28){
    cx.save();
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.025);
    cx.strokeStyle = `rgba(192, 132, 252, ${0.9 * pulse})`;
    cx.lineWidth = 1.5;
    for(let a = 0; a < 6.28; a += 1.25){
      cx.beginPath();
      cx.moveTo(ex, gy - 8);
      cx.lineTo(ex + Math.cos(a) * 25 * (prog / 0.28), gy - 8 + Math.sin(a) * 16 * (prog / 0.28));
      cx.stroke();
    }
    cx.restore();
    return;
  }

  const sheet = (bossNeuroOvermindFloatImg && bossNeuroOvermindFloatImg.complete && bossNeuroOvermindFloatImg.naturalWidth > 0) ? bossNeuroOvermindFloatImg : bossNeuroOvermindSheetImg;

  // Фаза 2: Левитация из портала с клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 44;
    const climbFrame = Math.min(7, Math.floor(subProg * 8));

    cx.save();
    cx.beginPath();
    cx.rect(ex - 110, gy - 200, 220, 200 + 4);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY);
    if(e.facing > 0) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 12px rgba(168, 85, 247, 0.85))';
    if(sheet && sheet.complete && sheet.naturalWidth > 0){
      cx.drawImage(sheet, climbFrame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
    } else if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
      cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
    }
    cx.restore();
    cx.restore();

    drawNeuroOvermindVortexLip(ex, gy, cw, ch);
    return;
  }

  // Фаза 3: Пси-детонация и переход в парение
  if(!e.emergeSlamDone){
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

  const slamProg = (prog - 0.74) / 0.26;
  const frame = Math.min(7, Math.floor(slamProg * 8));

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, gy, 52, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 14px rgba(168, 85, 247, 0.9))';
  if(sheet && sheet.complete && sheet.naturalWidth > 0){
    cx.drawImage(sheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 8, bw, bh);
  } else if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
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

  const tk = Math.min(1, Math.max(0, 1 - (e.spawnT - emergeMax) / (e.emergeDelay || 1.0)));
  const padProg = tele ? Math.min(0.6, tk * 4) : (prog < 0.74 ? 0.6 : 0.6 + (prog - 0.74) / 0.26 * 0.4);
  drawBossSpawnPad(e, ex, gy, padProg);
  if(tele){
    drawBossTelegraphRings(e, ex, gy);
    return;
  }

  const fw = 280, fh = 280, bw = 172, bh = 172;
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

  // Фаза 1: пульсация био-мутагена
  if(prog < 0.28){
    cx.save();
    const pulse = 0.75 + 0.25 * Math.sin(performance.now() * 0.02);
    cx.fillStyle = `rgba(239, 68, 68, ${0.85 * pulse * (prog / 0.28)})`;
    cx.shadowColor = '#ef4444';
    cx.shadowBlur = 12;
    cx.beginPath();
    cx.arc(ex, gy - 6, 12 * (prog / 0.28), 0, 6.283);
    cx.fill();
    cx.shadowBlur = 0;
    cx.restore();
    return;
  }

  const sheet = (bossPatientZeroWalkImg && bossPatientZeroWalkImg.complete && bossPatientZeroWalkImg.naturalWidth > 0) ? bossPatientZeroWalkImg : bossPatientZeroSheetImg;

  // Фаза 2: Подъем колосса из реактора с клиппингом
  if(prog < 0.74){
    const subProg = (prog - 0.28) / (0.74 - 0.28);
    const riseY = (1 - subProg) * 56;
    const climbFrame = Math.min(7, Math.floor(subProg * 8));

    cx.save();
    cx.beginPath();
    cx.rect(ex - 120, gy - 220, 240, 220 + 4);
    cx.clip();

    cx.save();
    cx.translate(ex, ey + riseY);
    if(e.facing > 0) cx.scale(-1, 1);
    cx.imageSmoothingEnabled = false;
    cx.filter = 'drop-shadow(0 0 12px rgba(239, 68, 68, 0.85))';
    if(sheet && sheet.complete && sheet.naturalWidth > 0){
      cx.drawImage(sheet, climbFrame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 10, bw, bh);
    } else if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
      cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 10, bw, bh);
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

  const slamProg = (prog - 0.74) / 0.26;
  const frame = Math.min(7, Math.floor(slamProg * 8));

  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.56)';
  cx.beginPath(); cx.ellipse(ex, gy, 58, 18, 0, 0, 6.283); cx.fill();
  cx.restore();

  cx.save();
  cx.translate(ex, ey);
  if(e.facing > 0) cx.scale(-1, 1);
  cx.imageSmoothingEnabled = false;
  cx.filter = 'drop-shadow(0 0 14px rgba(239, 68, 68, 0.9))';
  if(sheet && sheet.complete && sheet.naturalWidth > 0){
    cx.drawImage(sheet, frame * fw, 0, fw, fh, -bw / 2, -bh / 2 - 10, bw, bh);
  } else if(bossPatientZeroImg && bossPatientZeroImg.complete && bossPatientZeroImg.naturalWidth > 0){
    cx.drawImage(bossPatientZeroImg, -bw / 2, -bh / 2 - 10, bw, bh);
  }
  cx.restore();

  drawPatientZeroCraterLip(ex, gy, cw, ch);
}

'''

    new_text = text[:idx1] + code + text[idx2:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Rebuilt emergence functions with 100% exact sprite dimensions and clipping!")

if __name__ == '__main__':
    main()
