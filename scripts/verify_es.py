# scripts/verify_es.py
import json, pathlib, re

base = pathlib.Path('app/services/content/data/es')
EN_WORDS = ('Spring', 'Winter', 'Forge', 'Extreme')
EN_PAT = re.compile(r'\b(' + '|'.join(EN_WORDS) + r')\b')

issues = []

# 1. 모든 JSON UTF-8 + JSON 유효성
for f in sorted(base.rglob('*.json')):
    try:
        json.loads(f.read_text('utf-8'))
    except Exception as e:
        issues.append(f'[INVALID JSON] {f.relative_to(base)}: {e}')

# 2. core_pillars name 필드 English leakage
for f in sorted((base / 'core_pillars').glob('*.json')):
    try: d = json.loads(f.read_text('utf-8'))
    except: continue
    name = d.get('name', '')
    if EN_PAT.search(name):
        issues.append(f'[NAME EN] {f.name}: {name}')
    # pure bug
    for i, kw in enumerate(d.get('keywords', [])):
        m = re.match(r'^también\s+([甲乙丙丁戊己庚辛壬癸])$', kw)
        if m:
            issues.append(f'[PURE BUG] {f.name} keywords[{i}]: {kw}')
    # pillar field space/hyphen
    p = d.get('pillar', '')
    if ' ' in p or '-' in p:
        issues.append(f'[PILLAR FORMAT] {f.name}: {p!r}')

# 3. pillar_names.json
d = json.loads((base / 'pillar_names.json').read_text('utf-8'))
for k, v in d.items():
    if EN_PAT.search(v.get('name', '')):
        issues.append(f'[PILLAR_NAMES EN] {k}: {v["name"]}')

# 4. sections.json — MODE 키 오염
VALID_MODES = {f'THE_{x}' for x in ('OFFICER','MENTOR','FLOW','CREATOR','CHALLENGER','SURVIVOR','MYSTIC','GENERALIST','STEWARD','OPERATOR','TWIN','RIVAL','ALLY','EMPATH','PIONEER','ADAPTER','RADIATOR','KEEPER','ANCHOR','CULTIVATOR','BLADE','GEM','DEEP','SPRING')}
d = json.loads((base / 'sections.json').read_text('utf-8'))
for sec in ('MONEY_CONTENT', 'WORK_CONTENT', 'BONDS_CONTENT'):
    for mode, content in d.get(sec, {}).items():
        for field in ('best_match', 'challenging_match'):
            for v in content.get(field, []):
                if v not in VALID_MODES:
                    issues.append(f'[SECTIONS BAD MODE] {sec}.{mode}.{field}: {v!r}')

print(f'\n=== Found {len(issues)} issues ===\n')
for i in issues: print(i)