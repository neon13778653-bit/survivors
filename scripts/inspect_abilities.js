const fs = require('fs');
const lines = fs.readFileSync('index.html', 'utf8').split('\n');

const inspect = [
  'fmj_ammo', 'fast_reload', 'extra_projectile', 'sniper_crit', 'leadstorm', 'orbital_strike',
  'extra_projectile_evo', 'explosive_ammo_evo', 'leadstorm_evo', 'sniper_crit_evo'
];

inspect.forEach(id => {
  const idx = lines.findIndex(l => l.includes(`id: '${id}'`));
  if (idx !== -1) {
    console.log(`\n=== ${id} (line ${idx + 1}) ===`);
    console.log(lines.slice(idx, idx + 15).join('\n'));
  }
});
