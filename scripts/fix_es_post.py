# scripts/fix_es_post.py
import json, pathlib, re

base = pathlib.Path('app/services/content/data/es')

def load(p): return json.loads(p.read_text('utf-8'))
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf-8')

# --- Fix 1: sections.json (P0) ---
p = base / 'sections.json'; d = load(p)
d['WORK_CONTENT']['THE_CREATOR']['best_match'] = ['THE_OFFICER', 'THE_MENTOR']
d['WORK_CONTENT']['THE_SURVIVOR']['best_match'] = ['THE_MENTOR', 'THE_FLOW']
save(p, d); print('OK sections.json')

# --- Fix 2: pillar_names.json (P1) ---
p = base / 'pillar_names.json'; d = load(p)
d.setdefault('庚午', {})['name'] = 'Espada en la forja'
save(p, d); print('OK pillar_names.json')

# --- Fix 3: core_pillars name 필드 (P1) ---
NAME_FIXES = {
    '丁卯.json': 'Vela en una rama primaveral',
    '乙卯.json': 'Flores silvestres de primavera',
    '壬寅.json': 'Mar que se encuentra con la primavera',
    '己卯.json': 'Campo que se abre a la primavera',
    '戊子.json': 'Manantial de montaña',
    '癸亥.json': 'Río profundo del invierno',
    '癸卯.json': 'Jardín de lluvia primaveral',
    '辛丑.json': 'Joya en el jardín de invierno',
    '辛卯.json': 'Jade en el jardín de primavera',
}
for fn, new_name in NAME_FIXES.items():
    p = base / 'core_pillars' / fn
    if not p.exists(): continue
    d = load(p); d['name'] = new_name; save(p, d)
    print(f'OK name {fn}')

# --- Fix 4: "pure" → "también" bug (P2) ---
for f in sorted((base / 'core_pillars').glob('*.json')):
    d = load(f)
    kws = d.get('keywords', [])
    changed = False
    for i, kw in enumerate(kws):
        m = re.match(r'^también\s+([甲乙丙丁戊己庚辛壬癸])$', kw)
        if m:
            kws[i] = 'puro ' + m.group(1)
            changed = True
    if changed:
        d['keywords'] = kws; save(f, d)
        print(f'OK pure-bug {f.name}')

# --- Fix 5: pillar 필드 복원 (P3, hygiene) ---
for f in sorted((base / 'core_pillars').glob('*.json')):
    d = load(f)
    expected = f.stem  # 파일명이 곧 중국어 기둥 이름
    if d.get('pillar') != expected:
        d['pillar'] = expected; save(f, d)
        print(f'OK pillar-field {f.name}')

print('\nAll done.')