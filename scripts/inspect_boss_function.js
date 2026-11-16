const fs = require('fs');
const content = fs.readFileSync('index.html', 'utf8');
const lines = content.split('\n');

// Find the function definition enclosing line 12100
let funcStart = -1;
for (let i = 12000; i >= 11800; i--) {
  if (lines[i].includes('function ')) {
    funcStart = i;
    break;
  }
}
console.log('Enclosing function at line', funcStart + 1, ':', lines[funcStart]);

// Let's print out lines around the boss spawning conditions
for (let i = 12050; i < 12900; i++) {
  const line = lines[i];
  if (line.includes('function spawn') || line.includes('bossId') || line.includes('const maxHp') || line.includes('let maxHp') || line.includes('curLvl') || line.includes('bossWave') || line.includes('G.wave')) {
    console.log(`${i+1}: ${line.trim()}`);
  }
}
