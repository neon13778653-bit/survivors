#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import sys

INDEX_PATH = r"C:\Users\alexg\Desktop\survivors\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Image declarations
target_images = """const bossCyberCerberusImg=new Image();bossCyberCerberusImg.src='img/monsters/boss_cyber_cerberus.webp';
const bossBioButcherImg=new Image();bossBioButcherImg.src='img/monsters/boss_bio_butcher.webp';
const bossNeuroOvermindImg=new Image();bossNeuroOvermindImg.src='img/monsters/boss_neuro_overmind.webp';"""

replacement_images = """const bossCyberCerberusImg=new Image();bossCyberCerberusImg.src='img/monsters/boss_cyber_cerberus.webp';
const bossCyberCerberusWalkImg=new Image();bossCyberCerberusWalkImg.src='img/monsters/boss_cyber_cerberus_walk.webp';
const bossCyberCerberusAttackImg=new Image();bossCyberCerberusAttackImg.src='img/monsters/boss_cyber_cerberus_attack.webp';
const bossCyberCerberusSheetImg=new Image();bossCyberCerberusSheetImg.src='img/monsters/boss_cyber_cerberus_sheet.webp';
const bossBioButcherImg=new Image();bossBioButcherImg.src='img/monsters/boss_bio_butcher.webp';
const bossBioButcherWalkImg=new Image();bossBioButcherWalkImg.src='img/monsters/boss_bio_butcher_walk.webp';
const bossBioButcherAttackImg=new Image();bossBioButcherAttackImg.src='img/monsters/boss_bio_butcher_attack.webp';
const bossBioButcherSheetImg=new Image();bossBioButcherSheetImg.src='img/monsters/boss_bio_butcher_sheet.webp';
const bossNeuroOvermindImg=new Image();bossNeuroOvermindImg.src='img/monsters/boss_neuro_overmind.webp';
const bossNeuroOvermindFloatImg=new Image();bossNeuroOvermindFloatImg.src='img/monsters/boss_neuro_overmind_float.webp';
const bossNeuroOvermindAttackImg=new Image();bossNeuroOvermindAttackImg.src='img/monsters/boss_neuro_overmind_attack.webp';
const bossNeuroOvermindSheetImg=new Image();bossNeuroOvermindSheetImg.src='img/monsters/boss_neuro_overmind_sheet.webp';"""

# Normalize CRLF for replacement
target_images_crlf = target_images.replace("\n", "\r\n")
replacement_images_crlf = replacement_images.replace("\n", "\r\n")

if target_images_crlf in content:
    content = content.replace(target_images_crlf, replacement_images_crlf, 1)
    print("1. Image declarations replaced successfully (CRLF).")
elif target_images in content:
    content = content.replace(target_images, replacement_images, 1)
    print("1. Image declarations replaced successfully (LF).")
else:
    print("Warning: target_images not found!")
    sys.exit(1)

# 2. Emergence animation updates
target_cerberus_emerge = """  if(bossCyberCerberusImg && bossCyberCerberusImg.complete && bossCyberCerberusImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossCyberCerberusImg, -bw / 2, -bh / 2 - 6, bw, bh);
  }"""
replace_cerberus_emerge = """  const emergeFrame = Math.min(7, Math.floor(prog * 8));
  const cImg = (bossCyberCerberusWalkImg.complete && bossCyberCerberusWalkImg.naturalWidth > 0) ? bossCyberCerberusWalkImg : (bossCyberCerberusImg.complete ? bossCyberCerberusImg : null);
  if(cImg){
    cx.imageSmoothingEnabled = false;
    if(cImg === bossCyberCerberusWalkImg) cx.drawImage(cImg, emergeFrame * 340, 0, 340, 300, -bw / 2, -bh / 2 - 6, bw, bh);
    else cx.drawImage(cImg, -bw / 2, -bh / 2 - 6, bw, bh);
  }"""

if target_cerberus_emerge.replace("\n", "\r\n") in content:
    content = content.replace(target_cerberus_emerge.replace("\n", "\r\n"), replace_cerberus_emerge.replace("\n", "\r\n"), 1)
    print("2a. Cyber Cerberus emergence updated (CRLF).")
elif target_cerberus_emerge in content:
    content = content.replace(target_cerberus_emerge, replace_cerberus_emerge, 1)
    print("2a. Cyber Cerberus emergence updated (LF).")

target_butcher_emerge = """  if(bossBioButcherImg && bossBioButcherImg.complete && bossBioButcherImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossBioButcherImg, -bw / 2, -bh / 2 - 10, bw, bh);
  }"""
replace_butcher_emerge = """  const emergeFrame = Math.min(7, Math.floor(prog * 8));
  const bImg = (bossBioButcherWalkImg.complete && bossBioButcherWalkImg.naturalWidth > 0) ? bossBioButcherWalkImg : (bossBioButcherImg.complete ? bossBioButcherImg : null);
  if(bImg){
    cx.imageSmoothingEnabled = false;
    if(bImg === bossBioButcherWalkImg) cx.drawImage(bImg, emergeFrame * 360, 0, 360, 300, -bw / 2, -bh / 2 - 10, bw, bh);
    else cx.drawImage(bImg, -bw / 2, -bh / 2 - 10, bw, bh);
  }"""

if target_butcher_emerge.replace("\n", "\r\n") in content:
    content = content.replace(target_butcher_emerge.replace("\n", "\r\n"), replace_butcher_emerge.replace("\n", "\r\n"), 1)
    print("2b. Bio Butcher emergence updated (CRLF).")
elif target_butcher_emerge in content:
    content = content.replace(target_butcher_emerge, replace_butcher_emerge, 1)
    print("2b. Bio Butcher emergence updated (LF).")

target_neuro_emerge = """  if(bossNeuroOvermindImg && bossNeuroOvermindImg.complete && bossNeuroOvermindImg.naturalWidth > 0){
    cx.imageSmoothingEnabled = false;
    cx.drawImage(bossNeuroOvermindImg, -bw / 2, -bh / 2 - 8, bw, bh);
  }"""
replace_neuro_emerge = """  const emergeFrame = Math.min(7, Math.floor(prog * 8));
  const oImg = (bossNeuroOvermindFloatImg.complete && bossNeuroOvermindFloatImg.naturalWidth > 0) ? bossNeuroOvermindFloatImg : (bossNeuroOvermindImg.complete ? bossNeuroOvermindImg : null);
  if(oImg){
    cx.imageSmoothingEnabled = false;
    if(oImg === bossNeuroOvermindFloatImg) cx.drawImage(oImg, emergeFrame * 320, 0, 320, 320, -bw / 2, -bh / 2 - 8, bw, bh);
    else cx.drawImage(oImg, -bw / 2, -bh / 2 - 8, bw, bh);
  }"""

if target_neuro_emerge.replace("\n", "\r\n") in content:
    content = content.replace(target_neuro_emerge.replace("\n", "\r\n"), replace_neuro_emerge.replace("\n", "\r\n"), 1)
    print("2c. Neuro Overmind emergence updated (CRLF).")
elif target_neuro_emerge in content:
    content = content.replace(target_neuro_emerge, replace_neuro_emerge, 1)
    print("2c. Neuro Overmind emergence updated (LF).")

# 3. Replace Boss Draw Functions (lines ~22801 to ~23241)
# Find start: // ===== ДИНАМИЧЕСКАЯ ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР =====
# Find end before: function drawSlimeBoss(e, ox, oy){

draw_funcs_start_marker = "// ===== ДИНАМИЧЕСКАЯ ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР ====="
draw_funcs_end_marker = "function drawSlimeBoss(e, ox, oy){"

new_boss_draw_functions = """// ===== ДИНАМИЧЕСКАЯ ПОКАДРОВАЯ ОТРИСОВКА БОССА 1: КИБЕР-ЦЕРБЕР =====
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

    // Зона коридора рывка
    cx.fillStyle = `rgba(239, 68, 68, ${0.15 * pulse})`;
    cx.fillRect(0, -22, cLen, 44);

    // Лазерная траектория
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.5;
    cx.setLineDash([10, 6]);
    cx.lineDashOffset = -performance.now() * 0.06;
    cx.beginPath();
    cx.moveTo(0, 0); cx.lineTo(cLen, 0);
    cx.stroke();
    cx.setLineDash([]);

    // Бегущие шевроны ускорения >>>>>
    cx.strokeStyle = '#fef08a';
    cx.lineWidth = 2.0;
    const chevOff = (performance.now() * 0.12) % 40;
    for(let d = chevOff; d < cLen; d += 40){
      cx.beginPath();
      cx.moveTo(d - 6, -10); cx.lineTo(d + 4, 0); cx.lineTo(d - 6, 10);
      cx.stroke();
    }
    cx.restore();
  }

  // 2. Телеграф взмаха хвостом (360-градусный опасный круг)
  if(e.action === 'tail_swipe'){
    cx.save();
    const r = 95;
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    cx.fillStyle = `rgba(239, 68, 68, ${0.28 * pulse})`;
    cx.beginPath(); cx.arc(ex, ey, r, 0, 6.283); cx.fill();
    cx.strokeStyle = `rgba(239, 68, 68, ${0.95 * pulse})`;
    cx.lineWidth = 2.2;
    cx.stroke();
    cx.restore();
  }

  // 3. Тень под лапами
  const isDashing = (e.action === 'dash_run');
  const isHowling = (e.action === 'howl');
  const shadowScale = isDashing ? 1.25 : (isHowling ? 0.9 : 1.0);
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.52)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 52 * shadowScale, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 4. Выбор покадрового спрайта (Spritesheet 8 кадров: 340x300)
  const fw = 340, fh = 300;
  const bw = 156, bh = 138;
  let currentSheet = bossCyberCerberusWalkImg;
  let frame = 0;
  let bobY = 0;

  if(e.action === 'dash_prep'){
    currentSheet = bossCyberCerberusAttackImg;
    const windProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.75)));
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
  } else {
    currentSheet = bossCyberCerberusWalkImg;
    frame = Math.floor(e.animT || 0) % 8;
  }
  e.frame = frame;

  // 5. Отрисовка полупрозрачных неоновых шлейфов скорости (Afterimages) во время рывка
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

  // 6. Основная отрисовка покадрового спрайта босса
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

  // 1. Телеграф пневматического гарпуна (лазерное наведение на игрока)
  if(e.action === 'hook_prep'){
    cx.save();
    const hLen = 340;
    const hAng = Math.atan2((e.hookTargetY || G.p.y) - e.y, (e.hookTargetX || G.p.x) - e.x);
    cx.translate(ex, ey - 6);
    cx.rotate(hAng);
    const pulse = 0.8 + 0.2 * Math.sin(performance.now() * 0.025);
    
    // Красный лазерный луч
    cx.strokeStyle = `rgba(220, 38, 38, ${0.9 * pulse})`;
    cx.lineWidth = 2.2;
    cx.setLineDash([10, 6]);
    cx.lineDashOffset = -performance.now() * 0.05;
    cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(hLen, 0); cx.stroke();
    cx.setLineDash([]);

    // Прицельное перекрестие на дальности
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

  // 2. Телеграф казнящего разруба тесаком (красный опасный сектор)
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
    cx.restore();
  }

  // 3. Тень под сапогами
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.55)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 56, 16, 0, 0, 6.283); cx.fill();
  cx.restore();

  // 4. Выбор покадрового спрайта (Spritesheet 8 кадров: 360x300)
  const fw = 360, fh = 300;
  const bw = 192, bh = 160;
  let currentSheet = bossBioButcherWalkImg;
  let frame = 0;
  let bobY = 0;

  if(e.action === 'cleaver_prep'){
    currentSheet = bossBioButcherAttackImg;
    const windProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.70)));
    frame = Math.min(3, Math.floor(windProg * 4));
    bobY = -6 * windProg;
  } else if(e.action === 'cleaver_strike'){
    currentSheet = bossBioButcherAttackImg;
    frame = 4 + (Math.floor(performance.now() / 80) % 2);
    bobY = 4;
  } else if(e.action === 'hook_prep'){
    currentSheet = bossBioButcherAttackImg;
    const prepProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.65)));
    frame = Math.min(5, 4 + Math.floor(prepProg * 2));
    bobY = 2;
  } else if(e.action === 'hook_throw'){
    currentSheet = bossBioButcherAttackImg;
    const throwProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.55)));
    frame = Math.min(7, 6 + Math.floor(throwProg * 2));
    bobY = 0;
  } else {
    currentSheet = bossBioButcherWalkImg;
    frame = Math.floor(e.animT || 0) % 8;
    bobY = (frame === 1 || frame === 5) ? 3 : 0;
  }
  e.frame = frame;

  // 5. Отрисовка покадрового спрайта Мясника
  cx.save();
  cx.translate(ex, ey + bobY);
  if(e.facing > 0) cx.scale(-1, 1);

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

  // 1. Телеграф псионической гравитации (Сингулярности)
  if(e.action === 'singularity_cast'){
    cx.save();
    const pulse = 0.85 + 0.15 * Math.sin(performance.now() * 0.03);
    const sRad = 110;
    const spin = performance.now() * 0.008;

    cx.translate(G.p.x + ox, G.p.y + oy);
    cx.rotate(spin);

    // Зона гравитационного притяжения
    cx.strokeStyle = `rgba(168, 85, 247, ${0.9 * pulse})`;
    cx.lineWidth = 2.4;
    cx.setLineDash([12, 6]);
    cx.beginPath(); cx.arc(0, 0, sRad, 0, 6.283); cx.stroke();
    cx.setLineDash([]);

    // Сходящиеся фиолетовые кольца
    cx.strokeStyle = `rgba(236, 72, 153, ${0.65 * pulse})`;
    cx.lineWidth = 1.6;
    [0.35, 0.7].forEach(fr => {
      cx.beginPath(); cx.arc(0, 0, sRad * fr, 0, 6.283); cx.stroke();
    });

    cx.restore();
  }

  // 2. Плавная невесомость и тень на земле
  const floatY = Math.sin(performance.now() * 0.003) * 6.5;
  const shadowPulse = 1.0 - (floatY / 30);
  cx.save();
  cx.fillStyle = 'rgba(0,0,0,0.48)';
  cx.beginPath(); cx.ellipse(ex, shadowY, 48 * shadowPulse, 16 * shadowPulse, 0, 0, 6.283); cx.fill();

  // Псионическое силовое кольцо под капсулой
  const ringPulse = 0.75 + 0.25 * Math.sin(performance.now() * 0.006);
  cx.strokeStyle = `rgba(168, 85, 247, ${0.65 * ringPulse})`;
  cx.lineWidth = 2.2;
  cx.beginPath(); cx.ellipse(ex, ey + floatY + 16, 46, 18, 0, 0, 6.283); cx.stroke();
  cx.restore();

  // 3. Выбор покадрового спрайта (Spritesheet 8 кадров: 320x320)
  const fw = 320, fh = 320;
  const bw = 156, bh = 156;
  let currentSheet = bossNeuroOvermindFloatImg;
  let frame = 0;

  if(e.action === 'singularity_cast'){
    currentSheet = bossNeuroOvermindAttackImg;
    const castProg = Math.max(0, Math.min(1, 1 - (e.actionT / 0.8)));
    frame = Math.min(7, Math.floor(castProg * 8));
  } else {
    currentSheet = bossNeuroOvermindFloatImg;
    frame = Math.floor(e.animT || 0) % 8;
  }
  e.frame = frame;

  // 4. Отрисовка покадрового спрайта капсулы и мозга
  cx.save();
  cx.translate(ex, ey + floatY);
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

start_pos = content.find(draw_funcs_start_marker)
end_pos = content.find(draw_funcs_end_marker)

if start_pos != -1 and end_pos != -1:
    is_crlf = "\r\n" in content[start_pos:end_pos]
    if is_crlf:
        replacement = new_boss_draw_functions.replace("\n", "\r\n")
    else:
        replacement = new_boss_draw_functions
    content = content[:start_pos] + replacement + content[end_pos:]
    print("3. Replaced drawCyberCerberusBoss, drawBioButcherBoss, drawNeuroOvermindBoss successfully!")
else:
    print(f"Warning: markers not found! start_pos={start_pos}, end_pos={end_pos}")
    sys.exit(1)

# 4. Update preload list at bottom of index.html
old_preload = """  'img/monsters/boss_cyber_cerberus.webp',
  'img/monsters/boss_bio_butcher.webp',
  'img/monsters/boss_neuro_overmind.webp',"""

new_preload = """  'img/monsters/boss_cyber_cerberus.webp',
  'img/monsters/boss_cyber_cerberus_walk.webp',
  'img/monsters/boss_cyber_cerberus_attack.webp',
  'img/monsters/boss_bio_butcher.webp',
  'img/monsters/boss_bio_butcher_walk.webp',
  'img/monsters/boss_bio_butcher_attack.webp',
  'img/monsters/boss_neuro_overmind.webp',
  'img/monsters/boss_neuro_overmind_float.webp',
  'img/monsters/boss_neuro_overmind_attack.webp',"""

if old_preload.replace("\n", "\r\n") in content:
    content = content.replace(old_preload.replace("\n", "\r\n"), new_preload.replace("\n", "\r\n"), 1)
    print("4. Preload list updated (CRLF).")
elif old_preload in content:
    content = content.replace(old_preload, new_preload, 1)
    print("4. Preload list updated (LF).")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to index.html successfully!")
