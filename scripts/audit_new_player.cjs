const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
let harness = fs.readFileSync(path.join(root, 'scripts/test_web_platform_fixes.js'), 'utf8');
harness = harness.slice(0, harness.lastIndexOf('\n(async () => {'));
harness = harness.replace("style: { setProperty() {} }, textContent: '', innerHTML: '',", `style: { setProperty() {} }, textContent: '', _html: '', _buttons: [],
get innerHTML(){return this._html;}, set innerHTML(v){this._html=v;this._buttons=[...v.matchAll(/data-i="(\\d+)"/g)].map(m=>({dataset:{i:m[1]}}));},`);
harness = harness.replace("querySelectorAll: () => [], appendChild() {},", "querySelectorAll(selector){return selector==='button'?this._buttons:[];}, appendChild() {},");
harness = harness.replace("vm.runInContext(code, context,", "vm.runInContext(code.replace('boxEl.innerHTML=ch.map', 'window.__balanceChoices=ch; boxEl.innerHTML=ch.map'), context,");
const make = new Function('require', '__dirname', harness + '\nreturn environment;')(require, path.join(root, 'scripts'));
function battle(e){
  return e.run(`(()=>{
    const g=G,p=g.p,dt=1/(__run.fps||30),max=__run.seconds||1800;let steps=0,choices=[],waves=[],prevWave=0;
    moveVec=()=>window.__move||[0,0];drawGame=()=>{};drawLobby=()=>{};
    for(;steps<max/dt&&g.run;steps++){
      if(g.pause){
        const offered=window.__balanceChoices||[];
        const pref=__run.priority||['extra_projectile','arcane_multicast','wep_pistol_pointblank','wep_rebel_buckshot','wep_rune_triad','wep_bone_splinters','fmj_ammo','arcane_power','wep_pistol_rapid','wep_rebel_choke','wep_rune_luminance','wep_bone_curse','fast_reload','quick_cast'];
        const score=a=>a.isEvolved?10000:(pref.includes(a.id)?1000-pref.indexOf(a.id)*10:(g.p.got[a.id]?20:0)+(a.cat==='defense'?3:0));
        const sorted=offered.map((a,i)=>({a,i,s:score(a)})).sort((a,b)=>b.s-a.s);
        const c=sorted[0];if(!c)throw Error('Paused without choices');
        choices.push(c.a.id);const button=document.getElementById('levelup-cards-box').querySelectorAll('button')[c.i];
        if(!button?.onclick)throw Error('Missing choice button');button.onclick();
      }
      if(g.wave!==prevWave){waves.push({wave:g.wave,time:+g.t.toFixed(1),level:g.lvl,hp:+p.hp.toFixed(1)});prevWave=g.wave;}
      if(steps % 15 === 0){
        const drop=[...g.crates,...g.airdrops.filter(a=>a.landed&&!a.dead)].find(o=>Math.abs(o.x-p.x)<W/2-12&&Math.abs(o.y-p.y)<H/2-20);
        if(drop)tryClickInteractable(drop.x-p.x+W/2,drop.y-p.y+H/2-10);
      }
      let vx=0,vy=0;const boss=g.enemies.find(e=>e.isBoss&&!e.dead);
      let danger=0;
      for(const en of g.enemies){if(en.dead)continue;const dx=p.x-en.x,dy=p.y-en.y,d=Math.hypot(dx,dy)||1;
        const safe=(en.isBoss?230:115)+(en.c?.r||0);if(d<safe){const k=(safe-d)/safe;vx+=dx/d*k*(en.isBoss?3:1);vy+=dy/d*k*(en.isBoss?3:1);danger+=k;}}
      if(boss){const dx=boss.x-p.x,dy=boss.y-p.y,d=Math.hypot(dx,dy)||1;vx+=-dy/d*.65;vy+=dx/d*.65;if(d>180){vx+=dx/d*.75;vy+=dy/d*.75;}}
      else if(danger<.25){const gem=g.gems.filter(m=>!m.mag).sort((a,b)=>(a.x-p.x)**2+(a.y-p.y)**2-((b.x-p.x)**2+(b.y-p.y)**2))[0];if(gem){const d=Math.hypot(gem.x-p.x,gem.y-p.y)||1;vx+=(gem.x-p.x)/d;vy+=(gem.y-p.y)/d;}}
      let d=Math.hypot(vx,vy);__move=d?[vx/d,vy/d]:[0,0];
      loop(last+dt*1000);
    }
    return {...__run,stopped:!g.run,alive:p.hp>0,wave:g.wave,seconds:+g.t.toFixed(1),level:g.lvl,kills:g.kills,hp:+p.hp.toFixed(1),gold:g.coinsCollected,crystals:g.crystalsCollected,accountXp:(g.accXpKills||0)+(g.accXpWaves||0),got:p.got,choices,waves};
  })()`);
}

const assert = require('node:assert/strict');
function accountSnapshot(){
  return JSON.parse(JSON.stringify({
    gold:save.gold,gems:save.gems,level:save.accLv,xp:save.accXp,inv:save.inv,
    equip:save.equip,hero:save.selectedChar,open:save.unlockedLvls,cleared:save.completedLvls||[],
    stats:Object.fromEntries(STAT_UP.map(u=>[u.k,save[u.lv]||0])),up:save.itemUpgrades
  }));
}

function shop(){
  const purchases=[];
  function log(type,id,gold,gems){purchases.push({type,id,gold,gems});}
  if(__policy==='early'){
    for(const level of LEVELS){
      if(save.unlockedLvls.includes(level.id)||save.accLv<level.reqLv||save.gold<level.cost)continue;
      selectedLvlIdx=level.id-1;updateMenuUI();document.getElementById('btn-lvl-unlock').onclick();
      log('chapter',level.id,level.cost,0);
    }
  }
  const marcus=CHARACTERS.findIndex(c=>c.id==='marcus');
  if(!save.unlockedChars.includes('marcus')&&save.gold>=CHARACTERS[marcus].cost){
    showcaseCharIdx=marcus;buyCurrentShowcaseHero();log('hero','marcus',CHARACTERS[marcus].cost,0);
  }
  const owned=save.inv.filter(id=>ITEMS[id]).sort((a,b)=>ITEMS[b].r-ITEMS[a].r);
  for(const slot of ['weapon','shield','pet']){
    const candidate=owned.find(id=>ITEMS[id].s===slot);
    if(candidate&&ITEMS[candidate].r>(ITEMS[save.equip[slot]]?.r||0))save.equip[slot]=candidate;
  }
  const arts=owned.filter(id=>ITEMS[id].s==='artifact').slice(0,3);
  arts.forEach((id,i)=>save.equip['art'+(i+1)]=id);
  while(true){
    const cur=calcStats();
    const options=STAT_UP.filter(u=>u.unlock<=save.accLv&&(save[u.lv]||0)<statCap()&&upCost(u)<=save.gold&&calcStats({[u.lv]:(save[u.lv]||0)+1})[u.k]>cur[u.k]+1e-8).sort((a,b)=>upCost(a)-upCost(b));
    if(!options.length)break;
    const u=options[0],before=save.gold;
    document.getElementById('stat-up-list').onclick({target:{closest:()=>({dataset:{up:u.k}})}});
    if(before===save.gold)throw Error('Purchase failed');
    log('hero stat',u.k,before-save.gold,0);
  }
  statsPetSel=save.equip.pet;
  while(statsPetSel){
    const d=petUpgradeDefs(statsPetSel).filter(d=>['cool','dmg'].includes(d.key)&&d.lv<d.max&&d.cost<=save.gems).sort((a,b)=>a.cost-b.cost)[0];
    if(!d)break;
    const before=save.gems;
    document.getElementById('stat-pet-box').onclick({target:{closest:s=>s==='[data-petup]'?{dataset:{petup:d.key}}:null}});
    if(save.gems===before)throw Error('Pet purchase failed');
    log('pet',statsPetSel+'/'+d.key,0,before-save.gems);
  }
  persist();return purchases;
}

module.exports = { make, battle };

if (require.main === module) (async()=>{
  const seed=Number(process.argv[2]||101),policy=process.argv[3]||'clear';
  assert.ok(['early','clear'].includes(policy));
  const e=make();await e.loadAll();e.context.__policy=policy;e.context.__run={seconds:1800};
  e.run('window.accountSnapshot='+accountSnapshot.toString()+';window.shop='+shop.toString());
  e.run(`window.__seed=${seed};Math.random=()=>{let t=__seed+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296};W=400;H=800;`);
  const initial=e.run('accountSnapshot()');assert.equal(initial.gold,0);assert.deepEqual([...initial.open],[1]);assert.equal(initial.inv.length,6);
  const log={seed,policy,initial,runs:[]};
  const dest=path.join(root,'docs/balance-2026-11-15','new-player-'+policy+'-'+seed+'.json');
  for(let attempt=1;attempt<=20;attempt++){
    const purchases=e.run('shop()');
    const start=e.run('accountSnapshot()');
    const chapter=Math.max(...start.open);
    e.run(`selectedLvlIdx=${chapter-1};startGame()`);
    const b=battle(e);assert.ok(b.stopped,'run exceeded time budget');
    const end=e.run('accountSnapshot()');
    assert.ok(start.equip.weapon&&Object.values(start.equip).every(id=>!id||start.inv.includes(id)));
    log.runs.push({attempt,chapter,purchases,start,end,wave:b.wave,seconds:b.seconds,level:b.level,kills:b.kills,won:b.alive,boss:e.run('G.activeBoss && ({id:G.activeBoss.bossId,hp:G.activeBoss.hp,maxHp:G.activeBoss.maxHp})'),got:b.got});
    fs.writeFileSync(dest,JSON.stringify(log,null,1));console.log(attempt,chapter,b.wave,b.alive,Math.round(b.seconds),end.gold,end.level);
    if(end.cleared.includes(3))break;
  }
})().catch(e=>{console.error(e);process.exitCode=1});
