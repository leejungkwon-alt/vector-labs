# -*- coding: utf-8 -*-
import json, pathlib, re

root = pathlib.Path('app/services/content/data')
langs = ['ko', 'en', 'ja', 'zh_cn', 'es']

# ─── 패턴 ───
eng_word = re.compile(r'\b(the|and|with|your|you|are|is|was|were|this|that|from|for|not|but|what|when|who|how|which|Pioneer|Explorer|Creator)\b')
korean   = re.compile(r'[가-힣]')
chinese  = re.compile(r'[\u4e00-\u9fff]')  # 한자
japanese_kana = re.compile(r'[\u3040-\u30ff]')  # 히라가나/가타카나
spanish_accent_typo = re.compile(r'\bel listó\b')

def walk_strings(obj, path=''):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f'{path}[{i}]')

report_lines = []

for lang in langs:
    d = root / lang
    if not d.exists():
        continue
    for f in sorted(d.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            report_lines.append(f'[{lang}] {f.name}: JSON ERROR {e}')
            continue

        for keypath, s in walk_strings(data):
            # es에 영어 단어 남음
            if lang == 'es':
                m = eng_word.search(s)
                if m:
                    report_lines.append(
                        f'[es/english-leak] {f.name} :: {keypath}\n    match: "{m.group(1)}"\n    text: {s[:120]}'
                    )
            # ja에 한글
            if lang == 'ja':
                m = korean.search(s)
                if m:
                    report_lines.append(
                        f'[ja/korean-leak] {f.name} :: {keypath}\n    text: {s[:120]}'
                    )
            # zh_cn에 한글
            if lang == 'zh_cn':
                m = korean.search(s)
                if m:
                    report_lines.append(
                        f'[zh_cn/korean-leak] {f.name} :: {keypath}\n    text: {s[:120]}'
                    )
            # es 오타 (확장)
            if lang == 'es':
                if spanish_accent_typo.search(s):
                    report_lines.append(
                        f'[es/typo] {f.name} :: {keypath}\n    text: {s[:120]}'
                    )

out = pathlib.Path('i18n_audit_report.txt')
out.write_text('\n'.join(report_lines) if report_lines else '(no issues found)', encoding='utf-8')
print(f'총 {len(report_lines)}건 → {out}')
print('앞 30건:')
for l in report_lines[:30]:
    print(l)