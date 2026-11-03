# -*- coding: utf-8 -*-
import json, pathlib

root = pathlib.Path('app/services/content/data')
langs = ['ko', 'en', 'ja', 'zh_cn', 'es']

def keys_of(obj, path=''):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f'{path}.{k}' if path else k
            out.add(p)
            out |= keys_of(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out |= keys_of(v, f'{path}[{i}]')
    return out

# 기준: ko
for f in sorted((root / 'ko').glob('*.json')):
    name = f.name
    try:
        base = keys_of(json.loads(f.read_text(encoding='utf-8')))
    except Exception as e:
        print(f'[ko] {name}: ERROR {e}')
        continue

    print(f'\n=== {name} (ko 기준 {len(base)} keys) ===')
    for lang in langs[1:]:
        target = root / lang / name
        if not target.exists():
            print(f'  [{lang}] MISSING FILE')
            continue
        try:
            t = keys_of(json.loads(target.read_text(encoding='utf-8')))
        except Exception as e:
            print(f'  [{lang}] ERROR {e}')
            continue
        missing = base - t
        extra   = t - base
        if missing or extra:
            print(f'  [{lang}] missing {len(missing)}, extra {len(extra)}')
            for m in sorted(missing)[:5]:
                print(f'       - missing: {m}')
            for x in sorted(extra)[:5]:
                print(f'       + extra:   {x}')
        else:
            print(f'  [{lang}] OK')