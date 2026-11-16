const fs = require('fs');
const content = fs.readFileSync('index.html', 'utf8');
const lines = content.split('\n');

const bosses = [];
for (let i = 12050; i < 13000; i++) {
  const line = lines[i];
  if (line && line.includes('g.activeBoss = boss;')) {
    const context = lines.slice(Math.max(0, i - 40), i + 20).join('\n');
    bosses.push({ line: i + 1, context });
  }
}

bosses.forEach((b, idx) => {
  console.log(`\n=== BOSS ${idx + 1} at line ${b.line} ===`);
  const nameMatch = b.context.match(/name:\s*['"]([^'"]+)['"]/);
  const hpMatch = b.context.match(/maxHp\s*=\s*([^;\n]+)/);
  const waveMatch = b.context.match(/(wave|w)\s*===?\s*(\d+)/i) || b.context.match(/case\s+(\d+):/);
  const lvlMatch = b.context.match(/(lvl|level|curLvl|curLevel|lvlId|id)\s*===?\s*(\d+|['"][^'"]+['"])/);
  console.log('Name:', nameMatch ? nameMatch[1] : 'unknown');
  console.log('HP formula:', hpMatch ? hpMatch[0] : 'unknown');
  console.log('Wave match:', waveMatch ? waveMatch[0] : 'unknown');
  console.log('Lvl match:', lvlMatch ? lvlMatch[0] : 'unknown');
  // Print 10 lines around boss definition
  const snippet = b.context.split('\n').filter(l => l.includes('maxHp') || l.includes('name:') || l.includes('boss =') || l.includes('switch') || l.includes('case') || l.includes('if(')).slice(-8);
  console.log('Snippet:\n  ' + snippet.join('\n  '));
});
