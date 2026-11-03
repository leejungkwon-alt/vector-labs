# -*- coding: utf-8 -*-
import json, pathlib, shutil

root = pathlib.Path('app/services/content/data')
log = []

# 확정 오역만 (문맥 판단 필요 없는 것)
fixes = {
    # es 영어 잔존 → 정확한 스페인어
    'El Adapter': 'El Adaptador',
    'El Radiator': 'El Radiador',
    'El Keeper': 'El Guardián',
    'El Anchor': 'El Ancla',
    'El Cultivator': 'El Cultivador',
    'El Gem': 'La Gema',
    'El Spring': 'El Manantial',
    # es 텍스트 중간 영어
    '«Creator»': '«Creador»',
    # es 오타 (제가 만든 것)
    'el listónn': 'el listón',
    'El listónn': 'El listón',
}

for lang in ['es']:
    for f in (root / lang).glob('*.json'):
        try:
            txt = f.read_text(encoding='utf-8')
        except Exception as e:
            print(f'[skip] {f.name}: {e}')
            continue
        new = txt
        for a, b in fixes.items():
            if a in new:
                new = new.replace(a, b)
                log.append(f'{f.name}: "{a}" -> "{b}"')
        if new != txt:
            shutil.copy(f, str(f) + '.pre_autofix2')
            f.write_text(new, encoding='utf-8')

print('수정:')
for l in log:
    print(' ', l)
print(f'총 {len(log)}건')