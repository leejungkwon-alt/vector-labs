# -*- coding: utf-8 -*-
import json, pathlib, shutil

root = pathlib.Path('app/services/content/data')
log = []

# es: 명백한 영어 잔존 / 확정 오타만
es_fix = {
    'El Pioneer': 'El Pionero',
    'el listó': 'el listón',
}

for f in (root / 'es').glob('*.json'):
    try:
        txt = f.read_text(encoding='utf-8')
    except Exception as e:
        print(f'[skip] {f.name}: {e}')
        continue
    new = txt
    for a, b in es_fix.items():
        if a in new:
            new = new.replace(a, b)
            log.append(f'{f.name}: "{a}" -> "{b}"')
    if new != txt:
        shutil.copy(f, str(f) + '.pre_autofix')
        f.write_text(new, encoding='utf-8')

print('수정 내역:')
for l in log:
    print(' ', l)
print(f'총 {len(log)}건')