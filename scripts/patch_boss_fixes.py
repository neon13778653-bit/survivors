import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

orig_crlf = '\r\n' in text
norm = text.replace('\r\n', '\n')

# 1. Update Gravedigger image declarations
old_gd = '''const bossGravediggerImg=new Image();bossGravediggerImg.src='img/monsters/boss_gravedigger.webp';
const bossGravediggerWalkImg=new Image();bossGravediggerWalkImg.src='img/monsters/boss_gravedigger_walk.webp';
const bossGravediggerSlamImg=new Image();bossGravediggerSlamImg.src='img/monsters/boss_gravedigger_slam.webp';
const bossGravediggerDigImg=new Image();bossGravediggerDigImg.src='img/monsters/boss_gravedigger_dig.webp';
const bossGravediggerRoarImg=new Image();bossGravediggerRoarImg.src='img/monsters/boss_gravedigger_roar.webp';'''

new_gd = '''const bossGravediggerImg=new Image();bossGravediggerImg.src='img/monsters/boss_gravedigger.webp?v=18';
const bossGravediggerWalkImg=new Image();bossGravediggerWalkImg.src='img/monsters/boss_gravedigger_walk.webp?v=18';
const bossGravediggerSlamImg=new Image();bossGravediggerSlamImg.src='img/monsters/boss_gravedigger_slam.webp?v=18';
const bossGravediggerDigImg=new Image();bossGravediggerDigImg.src='img/monsters/boss_gravedigger_dig.webp?v=18';
const bossGravediggerRoarImg=new Image();bossGravediggerRoarImg.src='img/monsters/boss_gravedigger_roar.webp?v=18';'''

assert old_gd in norm, 'old_gd not found'
norm = norm.replace(old_gd, new_gd)

# 2. Update all Chapter 3 bosses from ?v=17 to ?v=18 in declarations
ch3_decls = [
    'boss_cyber_cerberus.webp?v=17',
    'boss_cyber_cerberus_sheet.webp?v=17',
    'boss_cyber_cerberus_walk.webp?v=17',
    'boss_cyber_cerberus_attack.webp?v=17',
    'boss_bio_butcher.webp?v=17',
    'boss_bio_butcher_sheet.webp?v=17',
    'boss_bio_butcher_walk.webp?v=17',
    'boss_bio_butcher_attack.webp?v=17',
    'boss_chitin_reaper.webp?v=17',
    'boss_chitin_reaper_sheet.webp?v=17',
    'boss_chitin_reaper_walk.webp?v=17',
    'boss_chitin_reaper_attack.webp?v=17',
    'boss_neuro_overmind.webp?v=17',
    'boss_neuro_overmind_sheet.webp?v=17',
    'boss_neuro_overmind_float.webp?v=17',
    'boss_neuro_overmind_attack.webp?v=17',
    'boss_patient_zero.webp?v=17',
    'boss_patient_zero_sheet.webp?v=17',
    'boss_patient_zero_walk.webp?v=17',
    'boss_patient_zero_attack.webp?v=17',
]

for s in ch3_decls:
    s_new = s.replace('?v=17', '?v=18')
    assert s in norm, f'{s} not found'
    norm = norm.replace(s, s_new)

# Preload Gravedigger with ?v=18
old_gd_preload = "'img/monsters/boss_gravedigger.webp',"
new_gd_preload = """'img/monsters/boss_gravedigger.webp?v=18',
  'img/monsters/boss_gravedigger_walk.webp?v=18',
  'img/monsters/boss_gravedigger_slam.webp?v=18',
  'img/monsters/boss_gravedigger_dig.webp?v=18',
  'img/monsters/boss_gravedigger_roar.webp?v=18',"""
assert old_gd_preload in norm, 'old_gd_preload not found'
norm = norm.replace(old_gd_preload, new_gd_preload)

# 3. Enhance showScreen to reset canvas context when returning to menu/start
old_show_screen = """function showScreen(name){
  currentScreen=name;
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  const el=document.getElementById('screen-'+name);
  if(el)el.classList.add('active');
  if(name==='menu')updateMenuUI();
}"""

new_show_screen = """function showScreen(name){
  currentScreen=name;
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  const el=document.getElementById('screen-'+name);
  if(el)el.classList.add('active');
  if(name==='menu'||name==='start'){
    updateMenuUI();
    if(typeof resize==='function') resize();
  }
}"""
assert old_show_screen in norm, 'old_show_screen not found'
norm = norm.replace(old_show_screen, new_show_screen)

# 4. Enhance computeBossSpawnCoords
old_spawn_coords = """function computeBossSpawnCoords(p, g, bossRadius = 78){
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
}"""

new_spawn_coords = """function computeBossSpawnCoords(p, g, bossRadius = 78){
  const arenaY = g.bossArena ? g.bossArena.y : (p.y - 300);
  const topMargin = p.y - arenaY;
  // Если у игрока сверху достаточно места на арене (>160px) — спавним сверху (классический вход босса)
  const spawnAbove = topMargin > 160;
  const dirY = spawnAbove ? -1 : 1;
  const distY = 118 + Math.random() * 22;
  const dy = dirY * distY;

  // Босс спавнится прямо перед игроком по вертикали с минимальным смещением по X (<= 24px),
  // чтобы спрайт босса и эффекты никогда не выходили за левый/правый край экрана
  const maxDx = Math.min(24, Math.max(8, ((W || 400) * 0.5) - bossRadius - 35));
  const dx = (Math.random() - 0.5) * 2 * maxDx;

  let bx = p.x + dx;
  let by = p.y + dy;

  // Гарантируем безопасное расстояние от границ арены босса
  if(g.bossArena){
    const pad = Math.max(bossRadius + 24, 90);
    bx = Math.max(g.bossArena.x + pad, Math.min(g.bossArena.x + g.bossArena.size - pad, bx));
    by = Math.max(g.bossArena.y + pad, Math.min(g.bossArena.y + g.bossArena.size - pad, by));
  }

  return { bx, by };
}"""
assert old_spawn_coords in norm, 'old_spawn_coords not found'
norm = norm.replace(old_spawn_coords, new_spawn_coords)

# 5. Update Bio-Butcher, Chitin-Reaper, Neuro-Overmind, Patient-Zero spawn coords
old_butcher_spawn = """function spawnBioButcherBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'bio_butcher' && !e.dead)) return;

  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 110 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;"""

new_butcher_spawn = """function spawnBioButcherBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'bio_butcher' && !e.dead)) return;

  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 84);"""
assert old_butcher_spawn in norm, 'old_butcher_spawn not found'
norm = norm.replace(old_butcher_spawn, new_butcher_spawn)

old_reaper_spawn = """function spawnChitinReaperBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'chitin_reaper' && !e.dead)) return;

  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 115 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;"""

new_reaper_spawn = """function spawnChitinReaperBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'chitin_reaper' && !e.dead)) return;

  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 86);"""
assert old_reaper_spawn in norm, 'old_reaper_spawn not found'
norm = norm.replace(old_reaper_spawn, new_reaper_spawn)

old_overmind_spawn = """function spawnNeuroOvermindBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'neuro_overmind' && !e.dead)) return;

  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 110 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;"""

new_overmind_spawn = """function spawnNeuroOvermindBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'neuro_overmind' && !e.dead)) return;

  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 92);"""
assert old_overmind_spawn in norm, 'old_overmind_spawn not found'
norm = norm.replace(old_overmind_spawn, new_overmind_spawn)

old_patient_spawn = """function spawnPatientZeroBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'patient_zero' && !e.dead)) return;

  prepareBossArena(g);
  const ang = Math.random() * 6.283;
  const dist = 115 + Math.random() * 30;
  const maxDx = Math.max(70, W * 0.35 - 30);
  const maxDy = Math.max(80, H * 0.28 - 30);
  const dx = Math.max(-maxDx, Math.min(maxDx, Math.cos(ang) * dist));
  const dy = Math.max(-maxDy, Math.min(maxDy, Math.sin(ang) * dist));
  const bx = p.x + dx;
  const by = p.y + dy;"""

new_patient_spawn = """function spawnPatientZeroBoss(){
  if(!G || !G.run) return;
  const g = G, p = g.p;
  if(g.enemies.some(e => e.isBoss && e.bossId === 'patient_zero' && !e.dead)) return;

  prepareBossArena(g);
  const { bx, by } = computeBossSpawnCoords(p, g, 90);"""
assert old_patient_spawn in norm, 'old_patient_spawn not found'
norm = norm.replace(old_patient_spawn, new_patient_spawn)

# 6. Deep background clean in drawLobby
old_draw_lobby = """function drawLobby(now){
  const t=now/1000;
  const lvl=LEVELS[selectedLvlIdx]||LEVELS[0];

  // 1. Плавный кроссфейд перехода между фонами уровней"""

new_draw_lobby = """function drawLobby(now){
  const t=now/1000;
  const lvl=LEVELS[selectedLvlIdx]||LEVELS[0];

  // Глубокая очистка холста перед отрисовкой лобби (исключает наложение элементов боя)
  cx.fillStyle = '#060a12';
  cx.fillRect(0, 0, W, H);

  // 1. Плавный кроссфейд перехода между фонами уровней"""
assert old_draw_lobby in norm, 'old_draw_lobby not found'
norm = norm.replace(old_draw_lobby, new_draw_lobby)

# 7. Widen emergence clip boxes
# Gravedigger
old_gd_clip = "cx.rect(ex - 90, gy - 200, 180, 200 + 4);"
new_gd_clip = "cx.rect(ex - 240, gy - 360, 480, 360 + 4);"
assert old_gd_clip in norm, 'old_gd_clip not found'
norm = norm.replace(old_gd_clip, new_gd_clip)

# Cyber-Cerberus, Bio-Butcher, Chitin-Reaper, Neuro-Overmind, Patient-Zero
old_loc3_clip = "cx.rect(ex - 160, gy - 260, 320, 260 + 2);"
new_loc3_clip = "cx.rect(ex - 300, gy - 380, 600, 380 + 4);"
count_loc3 = norm.count(old_loc3_clip)
print(f'Found {count_loc3} occurrences of old_loc3_clip (expected 5)')
assert count_loc3 == 5, f'Expected 5 occurrences of old_loc3_clip, got {count_loc3}'
norm = norm.replace(old_loc3_clip, new_loc3_clip)

# Restore line endings
if orig_crlf:
    out = norm.replace('\n', '\r\n')
else:
    out = norm

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(out)

print('SUCCESSFULLY PATCHED index.html!')
