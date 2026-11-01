import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Fix testSkipWaves for lvl === 3
    target_skip = """  }else if(lvl===3){
    if(g.wave===10)spawnGravediggerBoss();
    else if(g.wave===20)spawnRatKingBoss();
    else if(g.wave===30)spawnSlimeBoss();
    else if(g.wave===40)spawnBroodmotherBoss();
    else if(g.wave===50)spawnKrakenBoss();
  }"""
    replacement_skip = """  }else if(lvl===3){
    if(g.wave===10)spawnCyberCerberusBoss();
    else if(g.wave===20)spawnBioButcherBoss();
    else if(g.wave===30)spawnChitinReaperBoss();
    else if(g.wave===40)spawnNeuroOvermindBoss();
    else if(g.wave===50)spawnPatientZeroBoss();
  }"""

    if target_skip in text:
        text = text.replace(target_skip, replacement_skip, 1)
        print("Fixed testSkipWaves bosses for lvl 3.")
    else:
        print("WARNING: target_skip not found!")

    # 2. Add warpToWave right after testSkipWaves
    target_after_skip = """  showGameToast('⏩ '+T('WARPED TO WAVE '+target+'!','ПЕРЕХОД К ВОЛНЕ '+target+'!'),'#38bdf8',2.0);
}
function testSkipBoss(){"""
    
    warp_to_wave_code = """  showGameToast('⏩ '+T('WARPED TO WAVE '+target+'!','ПЕРЕХОД К ВОЛНЕ '+target+'!'),'#38bdf8',2.0);
}

function warpToWave(targetWave){
  if(!G || !G.run) return;
  const g = G;
  const lvl = g.lvlConfig?.id || 1;
  const maxWaves = g.lvlConfig?.maxWaves || (lvl === 1 ? 30 : (lvl === 2 ? 40 : 50));
  const target = Math.max(1, Math.min(maxWaves, Math.floor(targetWave) || 1));

  if(g.activeBoss){
    g.activeBoss.dead = true;
    g.activeBoss.hp = 0;
    g.activeBoss = null;
  }
  g.bossArena = null;
  g.bossWarning = null;
  for(const e of g.enemies){
    e.dead = true;
    e.hp = 0;
  }
  g.enemies = [];

  const gameHudEl = document.getElementById('screen-game');
  if(gameHudEl) gameHudEl.classList.remove('boss-hud-active', 'boss-warning-active');
  const nameEl = document.getElementById('hud-boss-name');
  if(nameEl) nameEl.textContent = '';
  const curEl = document.getElementById('hud-boss-hp-cur');
  if(curEl) curEl.textContent = '';

  const waveDuration = CONFIG.waves.waveDuration || 12;
  g.waveProgressT = (target - 1) * waveDuration + 0.01;
  g.waveElapsedT = 0;
  g.waveSpawnedCount = 0;
  g.wave = target;

  const hwVal = document.getElementById('hud-wave-val');
  if(hwVal) hwVal.textContent = g.wave;
  if(g.wave > (save.maxWave || 1)){ save.maxWave = g.wave; persist(); }
  if(!save.maxWaveByLvl) save.maxWaveByLvl = {};
  if(g.wave > (save.maxWaveByLvl[lvl] || 0)){ save.maxWaveByLvl[lvl] = g.wave; persist(); }

  if(lvl === 1){
    if(g.wave === 10) spawnGravediggerBoss(false);
    else if(g.wave === 20) spawnGravediggerBoss(true);
    else if(g.wave === 30) spawnRatKingBoss();
  }else if(lvl === 2){
    if(g.wave === 10) spawnBroodmotherBoss();
    else if(g.wave === 20) spawnSlimeBoss();
    else if(g.wave === 30) spawnTreantBoss();
    else if(g.wave === 40) spawnKrakenBoss();
  }else if(lvl === 3){
    if(g.wave === 10) spawnCyberCerberusBoss();
    else if(g.wave === 20) spawnBioButcherBoss();
    else if(g.wave === 30) spawnChitinReaperBoss();
    else if(g.wave === 40) spawnNeuroOvermindBoss();
    else if(g.wave === 50) spawnPatientZeroBoss();
  }

  showGameToast('⏩ ' + T('WARPED TO WAVE ' + target + '!', 'ПЕРЕХОД К ВОЛНЕ ' + target + '!'), '#38bdf8', 2.0);
}
window.warpToWave = warpToWave;

function testSkipBoss(){"""

    if target_after_skip in text:
        text = text.replace(target_after_skip, warp_to_wave_code, 1)
        print("Added warpToWave function.")
    else:
        print("WARNING: target_after_skip not found!")

    # 3. Add keyboard shortcuts for wave warping and boss testing
    target_keydown = """addEventListener('keydown',e=>{
  keys[e.code]=1;
  const charEl=document.getElementById('modal-characters');"""

    replacement_keydown = """addEventListener('keydown',e=>{
  keys[e.code]=1;
  if(!e.target || (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA')){
    if(G && G.run && !G.pause){
      if(e.code === 'Digit1'){ warpToWave(10); e.preventDefault(); }
      else if(e.code === 'Digit2'){ warpToWave(20); e.preventDefault(); }
      else if(e.code === 'Digit3'){ warpToWave(30); e.preventDefault(); }
      else if(e.code === 'Digit4'){ warpToWave(40); e.preventDefault(); }
      else if(e.code === 'Digit5'){ warpToWave(50); e.preventDefault(); }
      else if(e.code === 'KeyB'){ testSkipBoss(); e.preventDefault(); }
    }
  }
  const charEl=document.getElementById('modal-characters');"""

    if target_keydown in text:
        text = text.replace(target_keydown, replacement_keydown, 1)
        print("Added debug key shortcuts (1-5 to warp to waves 10/20/30/40/50, B to skip boss).")
    else:
        print("WARNING: target_keydown not found!")

    # 4. Fix ensureInv unlockedLvls default
    target_ensure = """function ensureInv(){
  if(!save.unlockedLvls||!Array.isArray(save.unlockedLvls))save.unlockedLvls=[1];
  if(!save.unlockedLvls.includes(1))save.unlockedLvls.push(1);"""

    replacement_ensure = """function ensureInv(){
  if(!save.unlockedLvls||!Array.isArray(save.unlockedLvls))save.unlockedLvls=[1,2,3];
  if(!save.unlockedLvls.includes(1))save.unlockedLvls.push(1);
  if(!save.unlockedLvls.includes(2))save.unlockedLvls.push(2);
  if(!save.unlockedLvls.includes(3))save.unlockedLvls.push(3);"""

    if target_ensure in text:
        text = text.replace(target_ensure, replacement_ensure, 1)
        print("Fixed ensureInv to guarantee levels 1, 2, 3 are unlocked.")
    else:
        print("WARNING: target_ensure not found!")

    # 5. Fix updateMenuUI unlockedLvls fallback
    target_menu = """  const card=document.getElementById('lvl-card-frame');
  if(!save.unlockedLvls)save.unlockedLvls=[1];
  const isUnlocked=save.unlockedLvls.includes(lvl.id);"""

    replacement_menu = """  const card=document.getElementById('lvl-card-frame');
  if(!save.unlockedLvls||!Array.isArray(save.unlockedLvls))save.unlockedLvls=[1,2,3];
  if(!save.unlockedLvls.includes(lvl.id))save.unlockedLvls.push(lvl.id);
  const isUnlocked=save.unlockedLvls.includes(lvl.id);"""

    if target_menu in text:
        text = text.replace(target_menu, replacement_menu, 1)
        print("Fixed updateMenuUI unlockedLvls check.")
    else:
        print("WARNING: target_menu not found!")

    # 6. Update boss kill XP in hurt()
    target_xp = """    let kXp = 1;
    if(e.isBoss){
      kXp = (e.bossId === 'kraken' || e.bossId === 'abomination') ? 650 : (e.bossId === 'treant' ? 340 : (e.bossId === 'toxic_slime' ? 300 : (e.bossId === 'rat_king' ? 220 : (e.bossId === 'broodmother' ? 180 : 150))));"""

    replacement_xp = """    let kXp = 1;
    if(e.isBoss){
      kXp = (e.bossId === 'patient_zero') ? 1000 : (e.bossId === 'neuro_overmind') ? 700 : (e.bossId === 'chitin_reaper') ? 550 : (e.bossId === 'bio_butcher') ? 400 : (e.bossId === 'cyber_cerberus') ? 300 : ((e.bossId === 'kraken' || e.bossId === 'abomination') ? 650 : (e.bossId === 'treant' ? 340 : (e.bossId === 'toxic_slime' ? 300 : (e.bossId === 'rat_king' ? 220 : (e.bossId === 'broodmother' ? 180 : 150)))));"""

    if target_xp in text:
        text = text.replace(target_xp, replacement_xp, 1)
        print("Updated boss kill XP to include Zone 3 bosses.")
    else:
        print("WARNING: target_xp not found!")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Done writing index.html!")

if __name__ == '__main__':
    main()
