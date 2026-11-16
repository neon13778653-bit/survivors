// Run with: node scripts/test_web_platform_fixes.js
// Executes the real classic scripts in one browser-like global scope.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const code = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/i)[1];
const bridge = fs.readFileSync(path.join(root, 'js/platform.js'), 'utf8');
const flush = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };

function environment({ local = null, search = '', sdk = null } = {}) {
  let now = 0, nextTimer = 0;
  const timers = new Map(), images = [], elements = new Map(), events = new Map();
  const storage = new Map(local ? [['surv_save', JSON.stringify(local)]] : []);
  const listen = (event, fn) => {
    if (!events.has(event)) events.set(event, []);
    events.get(event).push(fn);
  };
  class CanvasRenderingContext2D {}
  for (const method of ['save','restore','translate','rotate','scale','setTransform','beginPath','arc','ellipse','fill','stroke','closePath','rect','roundRect','fillRect','strokeRect','clearRect','clip','drawImage','fillText','strokeText','setLineDash','lineTo','moveTo','quadraticCurveTo','bezierCurveTo']) {
    CanvasRenderingContext2D.prototype[method] = () => {};
  }
  CanvasRenderingContext2D.prototype.measureText = () => ({ width: 50 });
  CanvasRenderingContext2D.prototype.createLinearGradient =
    CanvasRenderingContext2D.prototype.createRadialGradient = () => ({ addColorStop() {} });
  CanvasRenderingContext2D.prototype.createPattern = () => ({});
  function element(id) {
    if (elements.has(id)) return elements.get(id);
    const classes = new Set();
    const el = {
      style: { setProperty() {} }, textContent: '', innerHTML: '',
      classList: {
        add: (...names) => names.forEach(n => classes.add(n)),
        remove: (...names) => names.forEach(n => classes.delete(n)),
        contains: name => classes.has(name),
        toggle(name, force = !classes.has(name)) { if (force) classes.add(name); else classes.delete(name); }
      },
      addEventListener() {}, querySelector: selector => element(id + selector),
      querySelectorAll: () => [], appendChild() {}, setAttribute() {},
      getBoundingClientRect: () => ({ left: 0, top: 0, right: 400, bottom: 800, width: 400, height: 800 }),
      getContext: () => new CanvasRenderingContext2D(), focus() {}, blur() {}, remove() {}
    };
    elements.set(id, el);
    return el;
  }
  const context = {
    console: { log() {}, warn() {}, error: (...args) => { throw new Error(args.join(' ')); } },
    document: {
      readyState: 'loading', hidden: false, body: element('body'), documentElement: element('html'),
      getElementById: element, querySelector: element, querySelectorAll: () => [],
      createElement: () => element('created'), createTreeWalker: () => ({ nextNode: () => null }),
      addEventListener: listen
    },
    localStorage: { getItem: k => storage.get(k) ?? null, setItem: (k,v) => storage.set(k,v), removeItem: k => storage.delete(k) },
    addEventListener: listen, requestAnimationFrame() {}, cancelAnimationFrame() {},
    Image: class { constructor() { this.complete = true; this.naturalWidth = 280; this.naturalHeight = 280; images.push(this); } },
    Audio: class { play() {} pause() {} },
    MutationObserver: class { observe() {} disconnect() {} },
    NodeFilter: { SHOW_TEXT: 4 }, CanvasRenderingContext2D,
    URLSearchParams, location: { search }, performance: { now: () => now },
    setTimeout: (fn, delay = 0) => { timers.set(++nextTimer, { fn, due: now + delay }); return nextTimer; },
    clearTimeout: id => timers.delete(id), innerWidth: 400, innerHeight: 800
  };
  context.window = context;
  if (sdk) context.FBInstant = sdk;
  vm.createContext(context);
  vm.runInContext(bridge, context, { filename: 'js/platform.js' });
  vm.runInContext(code, context, { filename: 'index.html inline script' });
  let readyCalls = 0;
  context.Platform.gameReady = () => { readyCalls++; };
  function advance(ms) {
    const until = now + ms;
    for (;;) {
      const next = [...timers].filter(([,t]) => t.due <= until).sort((a,b) => a[1].due-b[1].due)[0];
      if (!next) break;
      now = next[1].due;
      timers.delete(next[0]);
      next[1].fn();
    }
    now = until;
  }
  return {
    context, element, images, timers, storage, advance,
    run: source => vm.runInContext(source, context),
    emit: event => (events.get(event) || []).forEach(fn => fn({ code: 'Digit1', preventDefault() {} })),
    loaders: () => images.filter(img => img.onload && img.onload === img.onerror),
    readyCalls: () => readyCalls,
    async loadAll() { this.loaders().forEach(img => img.onload()); advance(200); await flush(); }
  };
}

async function testLoading() {
  const e = environment();
  await flush();
  e.loaders()[0].onload();
  assert.equal(e.readyCalls(), 0);
  assert.ok([...e.timers.values()].some(t => t.due === 4000), 'First response must preserve the deadline');
  e.advance(4200);
  await flush();
  assert.equal(e.readyCalls(), 1, 'Stalled resources must not block startup');
  e.loaders().forEach(img => { img.onload(); img.onerror(); });
  e.advance(5000);
  await flush();
  assert.equal(e.readyCalls(), 1, 'Late and duplicate callbacks must not finish twice');
  assert.equal(e.element('btn-start-play').style.display, 'inline-flex');
  const normal = environment();
  await normal.loadAll();
  assert.equal(normal.readyCalls(), 1);
  assert.equal(normal.timers.size, 0, 'Complete loads must cancel the deadline');
}

async function testProgression() {
  const e = environment();
  await e.loadAll();
  assert.equal(e.run('JSON.stringify(save.unlockedLvls)'), '[1]');
  e.run('selectedLvlIdx=2; updateMenuUI(); ensureInv(); startGame();');
  assert.equal(e.run('JSON.stringify(save.unlockedLvls)'), '[1]', 'Browsing/inventory must not unlock chapters');
  assert.equal(e.context.G, null, 'Locked chapters cannot start');
  assert.equal(e.run('DEV_TOOLS'), false);
  assert.notEqual(e.element('btn-test-skip-wave').style.display, 'none');
  assert.notEqual(e.element('btn-test-skip-boss').style.display, 'none');
  e.run('selectedLvlIdx=0; startGame();');
  e.emit('keydown');
  assert.equal(e.context.G.wave, 1, 'Release keyboard shortcuts must not skip waves');
  e.run('die(true)');
  assert.equal(e.run('JSON.stringify(save.unlockedLvls)'), '[1,2]', 'Winning Chapter 1 must unlock Chapter 2');
  const existing = environment({ local: { unlockedLvls: [1,2,3] } });
  assert.equal(existing.run('JSON.stringify(save.unlockedLvls)'), '[1,2,3]', 'Keep existing unlocks');
  existing.run('resetAllGameProgress()');
  assert.equal(existing.run('JSON.stringify(save.unlockedLvls)'), '[1]', 'Reset must restore release progression');
  const dev = environment({ search: '?dev=1' });
  assert.equal(dev.run('DEV_TOOLS'), true);
  assert.notEqual(dev.element('btn-test-skip-wave').style.display, 'none');
}

async function testLifecycleAndAds() {
  const e = environment();
  await e.loadAll();
  e.run('startGame()');
  const firstRun = e.context.G;
  assert.ok(firstRun && firstRun.run);
  const audio = { state: 'running', resume() { this.state='running'; return Promise.resolve(); }, suspend() { this.state='suspended'; return Promise.resolve(); } };
  e.context.Sfx.ctx = audio;
  e.context.document.hidden = true;
  e.emit('visibilitychange');
  assert.equal(firstRun.pause, true);
  assert.equal(audio.state, 'suspended', 'Pause-modal click must not undo suspension');
  assert.ok(e.element('modal-pause').classList.contains('open'));
  e.context.document.hidden = false;
  e.emit('visibilitychange');
  assert.equal(firstRun.pause, true, 'Returning to the tab must await explicit resume');
  e.run('resumeGame(); startGame();');
  assert.notEqual(e.context.G, firstRun, 'The bridge must follow replacement runs');
  let finish;
  e.context.Platform.type = 'poki';
  e.context.PokiSDK = { rewardedBreak: () => new Promise(resolve => { finish=resolve; }) };
  e.context.Sfx.setVolume(0.37);
  let rewarded;
  e.context.Platform.rewarded(ok => { rewarded=ok; });
  assert.equal(e.context.Sfx.volume, 0);
  finish(true);
  await flush();
  assert.equal(e.context.Sfx.volume, 0.37);
  assert.equal(rewarded, true);
  e.context.Platform.type = 'web';
  e.run('quitToMenu()');
  assert.equal(e.context.G, null);
}

async function testCloudStartup() {
  let resolveInit, resolveData, initCalls=0, reads=0, writes=0;
  const sdk = {
    initializeAsync: () => { initCalls++; return new Promise(resolve => { resolveInit=resolve; }); },
    player: {
      getDataAsync: () => { reads++; return new Promise(resolve => { resolveData=resolve; }); },
      setDataAsync: async () => { writes++; }
    }
  };
  const e = environment({ sdk });
  const p1=e.context.Platform.init(), p2=e.context.Platform.init();
  assert.equal(p1, p2, 'Initialization must share one promise');
  e.run('persist(); startGame();');
  await e.loadAll();
  assert.equal(reads, 0, 'Cloud reads must wait for SDK initialization');
  assert.equal(writes, 0, 'Startup must not overwrite cloud with local defaults');
  assert.equal(e.context.G, null);
  assert.equal(e.readyCalls(), 0, 'Assets alone must not signal ready');
  resolveInit();
  await flush();
  assert.equal(initCalls, 1);
  assert.equal(reads, 1);
  resolveData({ surv_save: {
    gold: 321, hpLv: 999, dmgLv: -8, selectedLvl: 2, unlockedLvls: [1,2],
    inv: ['w_shotgun','a_vest','pet_dog',null,7],
    equip: { weapon: 'w_shotgun', armor: 'a_vest', pet: 'pet_dog' },
    itemUpgrades: { pet_dog: { pick: 2 } },
    settings: { lang: 'ru', sfx: false, volume: 8 }
  } });
  await flush();
  assert.equal(e.readyCalls(), 1);
  const save=JSON.parse(e.run('JSON.stringify(save)'));
  assert.equal(save.gold, 321);
  assert.equal(save.hpLv, 20);
  assert.equal(save.dmgLv, 0);
  assert.deepEqual(save.unlockedLvls, [1,2]);
  assert.equal(save.equip.weapon, 'w_vepr_auto');
  assert.equal(save.equip.shield, 'sh_buckler');
  assert.equal(save.equip.pet, 'pet_bat');
  assert.equal(save.itemUpgrades.pet_bat.spd, 2);
  assert.equal(save.settings.volume, 1);
  assert.equal(e.run('selectedLvlIdx'), 1);
  assert.equal(e.context.document.documentElement.lang, 'ru');
  assert.equal(e.context.Sfx.enabled, false);
  assert.equal(JSON.parse(e.storage.get('surv_save')).gold, 321);
  e.run('persist()');
  await flush();
  assert.equal(writes, 1);
}

function testIcons() {
  const e=environment();
  const icons=JSON.parse(e.run('JSON.stringify(ABILITY_ICON_FILES)'));
  for (const [id,file] of Object.entries(icons)) {
    assert.ok(fs.existsSync(path.join(root,file)), `Missing ability icon: ${id}: ${file}`);
  }
  for (const id of ['wep_grimoire_corpse_explosion','wep_grimoire_soul_drain']) {
    assert.ok(e.run(`getAbilityIcon('${id}',false)`).includes(icons[id]));
  }
}

(async () => {
  for (const test of [testLoading,testProgression,testLifecycleAndAds,testCloudStartup,testIcons]) {
    await test();
    console.log(`PASS ${test.name}`);
  }
})().catch(err => { console.error(err); process.exitCode=1; });
