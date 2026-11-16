// node scripts/test_stats_screen.cjs
// Runs actual rendering and purchase handlers in the shared browser fixture.
const fs=require('node:fs'),assert=require('node:assert/strict');
const fixture=fs.readFileSync(require('node:path').join(__dirname,'test_web_platform_fixes.js'),'utf8');
const make=new Function('require','__dirname',fixture.slice(0,fixture.lastIndexOf('\n(async () => {'))+'\nreturn environment;')(require,__dirname);
async function fresh(){const e=make();await e.loadAll();return e;}
function buyHero(e,key){e.run(`document.getElementById('stat-up-list').onclick({target:{closest:()=>({dataset:{up:${JSON.stringify(key)}},disabled:false})}})`);}
function buyPet(e,key){e.run(`document.getElementById('stat-pet-box').onclick({target:{closest:s=>s==='[data-petup]'?{dataset:{petup:${JSON.stringify(key)}},disabled:false}:null}})`);}
async function tabs(){
 const e=await fresh();e.run("openModal('modal-stats')");
 assert.equal(e.element('stats-hero-panel').hidden,false);assert.equal(e.element('stats-pets-panel').hidden,true);
 e.element('#modal-stats .modal-body').scrollTop=90;e.run("selectStatsTab('pets')");
 assert.equal(e.element('stats-hero-panel').hidden,true);assert.equal(e.element('stats-pets-panel').hidden,false);
 e.run("selectStatsTab('hero')");assert.equal(e.element('#modal-stats .modal-body').scrollTop,90);
 e.run("selectStatsTab('unknown')");assert.equal(e.run('statsActiveTab'),'hero');
}
async function heroTransactions(){
 const e=await fresh();e.run('save.gold=1000;save.hpLv=0;save.accLv=1;renderStats()');buyHero(e,'hp');
 assert.equal(e.run('save.hpLv'),1);assert.equal(e.run('save.gold'),880);
 e.run('save.hpLv=4;save.gold=1000');buyHero(e,'hp');assert.equal(e.run('save.hpLv'),4);assert.equal(e.run('save.gold'),1000);
 e.run('save.hpLv=20;save.accLv=20');buyHero(e,'hp');assert.equal(e.run('save.hpLv'),20);assert.equal(e.run('save.gold'),1000);
 e.run('save.hpLv=0;save.gold=0');buyHero(e,'hp');assert.equal(e.run('save.hpLv'),0);assert.equal(e.run('save.gold'),0);
 e.run("save.inv=Object.keys(ITEMS);save.selectedChar='kael';save.gold=1000;save.spdLv=0;save.equip={weapon:'w_pistol',shield:'sh_aegis',pet:'pet_bat',art1:'art_crown',art2:'art_overdrive',art3:'art_stim'}");
 assert.equal(e.run('calcStats().spd'),315);buyHero(e,'spd');assert.equal(e.run('save.spdLv'),0);assert.equal(e.run('save.gold'),1000);
}
async function petTransactions(){
 const e=await fresh();e.run("save.inv=Object.keys(ITEMS);statsPetSel='pet_treant';save.gems=1000;save.itemUpgrades={};selectStatsTab('pets')");
 buyPet(e,'dmg');assert.equal(e.run('save.itemUpgrades.pet_treant.dmg'),1);assert.equal(e.run('save.gems'),973);
 e.run('save.itemUpgrades.pet_treant.dmg=10');buyPet(e,'dmg');assert.equal(e.run('save.gems'),973);assert.equal(e.run('save.itemUpgrades.pet_treant.dmg'),10);
 e.run('save.gems=0');buyPet(e,'cool');assert.equal(e.run('save.itemUpgrades.pet_treant.cool||0'),0);assert.equal(e.run('save.gems'),0);
 e.run("document.getElementById('stat-pet-box').onclick({target:{closest:s=>s==='[data-petsel]'?{dataset:{petsel:'pet_bat'}}:null}})");assert.equal(e.run('statsPetSel'),'pet_bat');
 e.run("document.getElementById('stat-pet-box').onclick({target:{closest:s=>s==='[data-peteq]'?{}:null}})");assert.equal(e.run('save.equip.pet'),'pet_bat');
}
(async()=>{for(const test of [tabs,heroTransactions,petTransactions]){await test();console.log('PASS '+test.name);}})().catch(e=>{console.error(e);process.exitCode=1;});
