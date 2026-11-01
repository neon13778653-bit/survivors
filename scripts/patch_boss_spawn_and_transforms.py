import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add computeBossSpawnCoords helper right before spawnCyberCerberusBoss
helper_code = '''// Расчет точки спавна босса: строго по вертикали в поле зрения игрока,
// с мягким центрированием по X, чтобы босс и все кольца телеграфа гарантированно помещались в экран
function computeBossSpawnCoords(p, g, bossRadius = 78){
  const arenaY = g.bossArena ? g.bossArena.y : (p.y - 300);
  const topMargin = p.y - arenaY;
  // Если у игрока сверху достаточно места на арене (>160px) — спавним сверху (классический вход босса)
  const spawnAbove = topMargin > 160;
  const dirY = spawnAbove ? -1 : 1;
  const distY = 118 + Math.random() * 22;
  const dy = dirY * distY;

  // Ограничиваем X так, чтобы босс (~160-192px) и его 140px телеграфные кольца не касались краёв экрана
  const safePad = Math.max(15, Math.min(38, (W * 0.5) - bossRadius - 25));
  const dx = (Math.random() - 0.5) * 2 * safePad;

  return {
    bx: p.x + dx,
    by: p.y + dy
  };
}

// ===== БОСС 1 (ВОЛНА 10, ЛОК. 3): КИБЕР-ЦЕРБЕР ====='''

old_cerberus_head = '''// ===== БОСС 1 (ВОЛНА 10, ЛОК. 3): КИБЕР-ЦЕРБЕР ====='''

if old_cerberus_head in content:
    content = content.replace(old_cerberus_head, helper_code, 1)
    print("Added computeBossSpawnCoords")
else:
    print("Warning: old_cerberus_head not found")

# Replace spawn coordinates computation in all 5 Zone 3 bosses
# Boss 1: Cyber-Cerberus
old_cerb_spawn = '''  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 110 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;'''

new_cerb_spawn = '''  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 78);'''

if old_cerb_spawn in content:
    content = content.replace(old_cerb_spawn, new_cerb_spawn, 1)
    print("Replaced Cyber-Cerberus spawn coords")
else:
    print("Warning: old_cerb_spawn not found")

# Boss 2: Bio-Butcher
old_butcher_spawn = '''  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 110 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;'''

new_butcher_spawn = '''  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 96);'''

if old_butcher_spawn in content:
    content = content.replace(old_butcher_spawn, new_butcher_spawn, 1)
    print("Replaced Bio-Butcher spawn coords")
else:
    print("Warning: old_butcher_spawn not found")

# Boss 3: Chitin-Reaper
old_reaper_spawn = '''  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 115 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;'''

new_reaper_spawn = '''  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 78);'''

if old_reaper_spawn in content:
    content = content.replace(old_reaper_spawn, new_reaper_spawn, 1)
    print("Replaced Chitin-Reaper spawn coords")
else:
    print("Warning: old_reaper_spawn not found")

# Boss 4: Neuro-Overmind
old_overmind_spawn = '''  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 110 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;'''

new_overmind_spawn = '''  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 78);'''

if old_overmind_spawn in content:
    content = content.replace(old_overmind_spawn, new_overmind_spawn, 1)
    print("Replaced Neuro-Overmind spawn coords")
else:
    print("Warning: old_overmind_spawn not found")

# Boss 5: Patient Zero
old_patient_spawn = '''  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 115 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;'''

new_patient_spawn = '''  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 86);'''

if old_patient_spawn in content:
    content = content.replace(old_patient_spawn, new_patient_spawn, 1)
    print("Replaced Patient Zero spawn coords")
else:
    print("Warning: old_patient_spawn not found")

# 2. Update quitToMenu to cleanly reset all boss states & transform
old_quit = '''function quitToMenu(){
  if(G){
    const totalAccXp=(G.accXpKills||0)+(G.accXpWaves||0);
    const xpG=totalAccXp-(G.xpGiven||0);
    if(xpG>0){
      G.xpGiven=totalAccXp;
      gainAccXp(xpG);
    }
  }
  document.querySelectorAll('.modal-overlay').forEach(m=>m.classList.remove('open'));
  G=null;
  showScreen('menu');
  if(window.Platform&&Platform.gameplayStop)Platform.gameplayStop();
  if(window.Platform&&Platform.interstitial)Platform.interstitial();
}'''

new_quit = '''function quitToMenu(){
  if(G){
    const totalAccXp=(G.accXpKills||0)+(G.accXpWaves||0);
    const xpG=totalAccXp-(G.xpGiven||0);
    if(xpG>0){
      G.xpGiven=totalAccXp;
      gainAccXp(xpG);
    }
    G.run = false;
    G.activeBoss = null;
    G.bossArena = null;
    G.bossWarning = null;
    G.bossShockwaves = [];
    G.bossCraters = [];
  }
  document.querySelectorAll('.modal-overlay').forEach(m=>m.classList.remove('open'));
  G=null;
  showScreen('menu');
  const d=Math.min(window.devicePixelRatio||1,2);
  cx.setTransform(d,0,0,d,0,0);
  if(window.Platform&&Platform.gameplayStop)Platform.gameplayStop();
  if(window.Platform&&Platform.interstitial)Platform.interstitial();
}'''

if old_quit in content:
    content = content.replace(old_quit, new_quit, 1)
    print("Updated quitToMenu")
else:
    print("Warning: old_quit not found")

# 3. Add clean transform reset at start of loop()
old_loop_start = '''function loop(now){
  let rawDt=(now-last)/1000;last=now;
  if(rawDt>0.15)rawDt=0.15;

  try {'''

new_loop_start = '''function loop(now){
  let rawDt=(now-last)/1000;last=now;
  if(rawDt>0.15)rawDt=0.15;

  try {
    const d=Math.min(window.devicePixelRatio||1,2);
    cx.setTransform(d,0,0,d,0,0);'''

if old_loop_start in content:
    content = content.replace(old_loop_start, new_loop_start, 1)
    print("Updated loop start with cx.setTransform")
else:
    print("Warning: old_loop_start not found")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done patching index.html")
