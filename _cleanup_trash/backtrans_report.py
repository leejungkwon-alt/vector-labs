# -*- coding: utf-8 -*-
import json, pathlib

root = pathlib.Path('app/services/content/data')
P0 = ['errors', 'labels', 'sections', 'core']

def flatten(obj, path=''):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f'{path}[{i}]')

out_lines = []
for name in P0:
    f = root / 'ko' / f'{name}.json'
    if not f.exists():
        continue
    ko = dict(flatten(json.loads(f.read_text(encoding='utf-8'))))
    ja = {}
    zh = {}
    es = {}
    for lang, dest in [('ja', ja), ('zh_cn', zh), ('es', es)]:
        p = root / lang / f'{name}.json'
        if p.exists():
            dest.update(dict(flatten(json.loads(p.read_text(encoding='utf-8')))))

    out_lines.append(f'\n{"="*70}\n=== {name}.json ===\n{"="*70}')
    for k, ko_val in ko.items():
        out_lines.append(f'\n[KEY] {k}')
        out_lines.append(f'  ko: {ko_val}')
        if k in ja:
            out_lines.append(f'  ja: {ja[k]}')
        if k in zh:
            out_lines.append(f'  zh_cn: {zh[k]}')
        if k in es:
            out_lines.append(f'  es: {es[k]}')

out = pathlib.Path('backtrans_review.txt')
out.write_text('\n'.join(out_lines), encoding='utf-8')
print(f'생성: {out}  ({out.stat().st_size:,} bytes)')