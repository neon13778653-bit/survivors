// node scripts/test_balance_fixes.cjs
// Execute the actual game script; reuse the existing browser fixture.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
let source=fs.readFileSync(path.join(__dirname,'test_web_platform_fixes.js'),'utf8');
source=source.slice(0,source.lastIndexOf('\n(async () => {'));
source=source.replace("style: { setProperty() {} }, textContent: '', innerHTML: '',",`style: { setProperty() {} }, textContent: '', _html: '', _buttons: [],
get innerHTML(){return this._html;},set innerHTML(v){this._html=v;this._buttons=[...v.matchAll(/data-i="(\\d+)"/g)].map(m=>({dataset:{i:m[1]}}));},`);
source=source.replace('querySelectorAll: () => [], appendChild() {},',"querySelectorAll(selector){return selector==='button'?this._buttons:[];},appendChild() {},");
const environment=new Function('require','__dirname',source+'\nreturn environment;')(require,__dirname);
async function fresh(){const e=environment();await e.loadAll();e.run('startGame();drawGame=()=>{};drawLobby=()=>{};');return e;}
async function testFrameTransitions(){
 for(const fps of [20,30,60,120]){
  let e=await fresh();e.run(`G.coinsCollected=100;G.crystalsCollected=10;G.kills=20;G.p.hp=0;loop(last+1000/${fps});if(${fps}>60)loop(last+1000/${fps});`);
  assert.equal(e.run('save.gold'),100);assert.equal(e.run('save.gems'),25);assert.equal(e.run('save.totalKills'),20);
  e.run('die(false)');assert.equal(e.run('save.gold'),100);
  e=await fresh();e.run(`G.pet=null;G.xp=1000;loop(last+1000/${fps});if(${fps}>60)loop(last+1000/${fps});`);assert.equal(e.run('G.lvl'),2);
  for(let i=0;i<3;i++){
   e.run("document.getElementById('levelup-cards-box').querySelectorAll('button')[0].onclick();");
   e.run(`loop(last+1000/${fps});if(${fps}>60)loop(last+1000/${fps})`);
  }
  assert.equal(e.run('Object.values(G.p.got).reduce((a,b)=>a+b,0)'),3);
 }
}
async function testRevive(){
 const e=await fresh();e.run('G.coinsCollected=100;G.crystalsCollected=10;G.kills=20;die(false);Platform.rewarded=cb=>cb(true);');
 e.run("document.getElementById('btn-go-revive').onclick();G.crystalsCollected+=2;G.kills+=3;die(false);");
 assert.equal(e.run('save.gems'),27);assert.equal(e.run('save.totalKills'),23);assert.equal(e.run('save.totalGoldEarned'),100);
}
async function testDamageAndStats(){
 const e=await fresh();
 e.run("G.p.dmg=100;G.p.got={};FIREARM_ABILITIES.find(a=>a.id==='tac_sprint').apply(G.p);FIREARM_ABILITIES.find(a=>a.id==='fmj_ammo').apply(G.p);");
 assert.ok(Math.abs(e.run('G.p.dmg')-110)<1e-9,'Speed must not dilute damage bonuses');
 e.run("FIREARM_ABILITIES.find(a=>a.id==='stopping_power').apply(G.p);");
 assert.ok(Math.abs(e.run('G.p.dmg')-119)<1e-9,'Damage card bonuses must add within their own budget');
 e.run('G.p.shield=0;G.p.armor=.5;G.p.hp=100;G.p.inv=0;damagePlayer(40);');assert.equal(e.run('G.p.hp'),80);
 e.run("G.p.armor=.8;FIREARM_ABILITIES.find(a=>a.id==='kevlar_vest').apply(G.p);G.p.critChance=.9;FIREARM_ABILITIES.find(a=>a.id==='laser_pointer').apply(G.p)");
 assert.equal(e.run('G.p.armor'),.8);assert.equal(e.run('G.p.critChance'),.9);
 e.run("save.inv.push('w_vector');save.equip.weapon='w_vector';startGame()");
 assert.equal(e.run('calcStats().dmg'),e.run('G.p.dmg'));assert.equal(e.run('calcStats().rate'),e.run('1/G.p.cool'));
}
async function testEconomyAndRarity(){
 const e=await fresh();e.run('G.p.goldBonus=.25;');assert.equal(e.run('Array.from({length:100},()=>collectCoinValue(1)).reduce((a,b)=>a+b,0)'),125);
 e.run("save.inv=Object.keys(ITEMS).filter(id=>id!=='w_phantom'&&id!=='pet_treant');");
 assert.equal(e.run('ITEMS[rollWeaponId(1)].r'),1);assert.equal(e.run('ITEMS[rollGearId(1)].r'),1);
}
async function testSecondaryAndWaves(){
 const e=await fresh();assert.equal(e.run("G.weaponDef={fireRate:'1.5',projectiles:1};secondaryDamage({dmg:20})"),20);
 assert.equal(e.run("G.weaponDef={fireRate:'6',projectiles:1};secondaryDamage({dmg:5})"),20);
 const hp=e.run('G.enemies=[];G.waveSpawnedCount=0;spawn(CONFIG.enemies.zombie,0,100);G.enemies[0].hp');
 assert.equal(e.run('G.enemies=[];G.waveSpawnedCount=0;G.t=1200;spawn(CONFIG.enemies.zombie,0,100);G.enemies[0].hp'),hp);
}
async function testGroundDamageAndHealing(){
 const values=[];
 for(const count of [1,30]){
  const e=await fresh();values.push(e.run(`(()=>{G.pet=null;G.p.cd=1e9;G.spawn=1e9;G.waveSpawnedCount=12;G.nextAirdropT=1e9;const t={x:0,y:-100,hp:1e6,maxHp:1e6,isDummy:true,c:{...CONFIG.enemies.zombie,speed:0},frame:0,animT:0};G.enemies=[t];G.firePatches=Array.from({length:${count}},()=>({x:0,y:-100,rad:50,l:4,dmg:10,tick:0}));for(let i=0;i<60;i++)update(1/60);return 1e6-t.hp;})()`));
 }
 assert.equal(values[0],values[1]);
 const e=await fresh();e.run('G.p.hp=1;G.p.maxHp=1000;G.p.petHealBudget=12;');
 assert.equal(e.run('Array.from({length:30},()=>healFromPet(G.p,100)).reduce((a,b)=>a+b,0)'),12);
}
async function testEvolutionSlots(){
 const e=await fresh();e.run("save.inv=Object.keys(ITEMS);save.equip.weapon='m_astral';startGame();G.p.got={mana_shield:5,mana_shield_evo:1,arcane_power:1,quick_cast:1,arcane_focus:1};G.p.evolved={mana_shield:true,mana_shield_evo:true};");
 // Deterministic RNG selects a new weapon skill if it is still in the legal pool.
 const html=e.run("(()=>{let result='';for(let i=0;i<100;i++){triggerLevelUp();result+=document.getElementById('levelup-cards-box').innerHTML;}return result;})()");
 assert.ok(html.includes('arcane_multicast.webp')||html.includes('meteor_rain.webp'));
}
async function testCadenceAndRefund(){
 const damage=[];
 for(const fps of [20,30,60,120]){
  const e=await fresh();damage.push(e.run(`(()=>{save.inv.push('w_vector');save.equip={weapon:'w_vector'};startGame();G.spawn=1e9;G.waveSpawnedCount=12;G.nextAirdropT=1e9;G.enemies=[{x:0,y:-100,hp:1e6,maxHp:1e6,isDummy:true,c:{...CONFIG.enemies.zombie,speed:0},frame:0,animT:0}];const target=G.enemies[0],start=last;for(let i=1;i<=10*${fps};i++)loop(start+i*1000/${fps});return 1e6-target.hp;})()`));
 }
 assert.ok(damage.every(x=>x===damage[0]),JSON.stringify(damage));
 const e=await fresh();e.run("save.itemUpgrades.w_pistol={dmg:2,rate:1};save.gems=0;refundItemUpgrades('w_pistol');");
 assert.equal(e.run('save.gems'),52);e.run("refundItemUpgrades('w_pistol')");assert.equal(e.run('save.gems'),52);
}
(async()=>{for(const test of [testFrameTransitions,testRevive,testDamageAndStats,testEconomyAndRarity,testSecondaryAndWaves,testGroundDamageAndHealing,testEvolutionSlots,testCadenceAndRefund]){await test();console.log('PASS '+test.name);}})().catch(e=>{console.error(e);process.exitCode=1;});

