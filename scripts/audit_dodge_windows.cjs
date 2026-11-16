const { make, battle } = require('./audit_new_player.cjs');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

async function main() {
  const env = make();
  await env.loadAll();
  env.run(`
    W=400; H=800;
    let state=101;
    Math.random=()=>{let t=state+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296;};
    function resetFight(chapter=3, controlBuild=false){
      save=createDefaultSave();
      save.unlockedLvls=[1,2,3];
      if(controlBuild){
        save.inv.push('w_python');
        save.equip.weapon='w_python';
        for(const key of ['hpLv','dmgLv','rateLv','spdLv','pickLv']) save[key]=5;
      }
      selectedLvlIdx=chapter-1;
      startGame();
      joy.on=false; keys.KeyD=false; keys.KeyS=false;
    }
    const normalDamage=damagePlayer;
    let hits=[];
    damagePlayer=function(...args){
      const p=G.p, before=p.hp+p.shield, boss=G.activeBoss;
      normalDamage(...args);
      if(before>p.hp+p.shield){
        hits.push({time:G.t,wave:G.wave,action:boss?.action,loss:before-p.hp-p.shield,
          caller:new Error().stack.split('\\n')[2].trim()});
      }
    };
  `);
  const cases = [];
  for (const attack of ['tail','dash']) {
    for (const distance of attack==='tail' ? [65,85,94] : [85,130,180]) {
      for (const delay of [0,0.2,0.35,0.45]) {
        for (const input of ['keyboard','touch30','touch60']) {
          env.context.trial={attack,distance,delay,input};
          const result=env.run(`(()=>{
            state=101; resetFight(); G.wave=10; spawnCyberCerberusBoss();
            const b=G.activeBoss, p=G.p;
            p.inv=0; G.spawnT=0;
            b.spawnState='active'; b.y=p.y; b.x=p.x-trial.distance;
            for(const key of ['flameCd','dashCd','tailCd','howlCd','missileCd','mineCd']) b[key]=100;
            b[trial.attack==='tail'?'tailCd':'dashCd']=0;
            hits=[]; update(1/60);
            const warning=b.action;
            for(let frame=0; frame<(trial.attack==='tail'?32:70); frame++){
              if(frame/60>=trial.delay){
                const radial=trial.attack==='tail';
                if(trial.input==='keyboard') keys[radial?'KeyD':'KeyS']=true;
                else {
                  const offset=trial.input==='touch60'?60:30;
                  Object.assign(joy,{on:true,ox:0,oy:0,x:radial?offset:0,y:radial?0:offset});
                }
              }
              update(1/60);
            }
            return {warning,hits:hits.slice(),speed:p.speed};
          })()`);
          assert.equal(result.warning,attack==='tail'?'tail_swipe':'dash_prep');
          cases.push({...env.context.trial,...result});
        }
      }
    }
  }
  const runs=[];
  for(const chapter of [1,2,3]){
    env.context.chapter=chapter;
    env.context.__run={seconds:1800};
    env.run('state=101; resetFight(chapter,true); hits=[]');
    const r=battle(env);
    assert.ok(r.stopped);
    runs.push({chapter,wave:r.wave,seconds:r.seconds,hits:env.run('hits.slice()')});
  }
  fs.writeFileSync(path.resolve(__dirname,'../docs/balance-2026-11-15/dodge-windows.json'),JSON.stringify({cases,runs},null,1));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
