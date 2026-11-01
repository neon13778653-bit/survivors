import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all g.bossShockwaves.push({ ... type: 'xyz' ... })
pushed_matches = re.findall(r'bossShockwaves\.push\(\s*\{([^}]+)\}', text)
pushed_types = set()
for m in pushed_matches:
    tm = re.search(r'type:\s*[\'\"]([^\'\"]+)[\'\"]', m)
    if tm:
        pushed_types.add(tm.group(1))

# Find drawBossShockwaves function
draw_match = re.search(r'function drawBossShockwaves\(.*?\)\s*\{([\s\S]*?)\nfunction', text)
draw_code = draw_match.group(1) if draw_match else ''

drawn_types = set(re.findall(r'sw\.type\s*===?\s*[\'\"]([^\'\"]+)[\'\"]', draw_code))

print("All pushed shockwave types:", sorted(pushed_types))
print("\nTypes with explicit drawing handler in drawBossShockwaves:", sorted(drawn_types))
print("\nPUSHED TYPES MISSING IN drawBossShockwaves:")
for pt in sorted(pushed_types):
    if pt not in drawn_types:
        print(f"  - {pt}")
