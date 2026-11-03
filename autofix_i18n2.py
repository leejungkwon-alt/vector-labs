# -*- coding: utf-8 -*-
import json, pathlib, shutil

root = pathlib.Path('app/services/content/data')
log = []

# (lang, 파일)별 확정 오역만
FIXES = {
    'ja': {
        # THE_ANCHOR keywords에 영어 'Ambition'
        '"Ambition"': '"リーダーシップ"',
    },
    'zh_cn': {
        # THE_ANCHOR keywords에 영어 'Ambition'
        '"Ambition"': '"领导力"',
        # 기계번역 실패 - 탈옥/외출금지
        '"已越狱"': '"根基"',
        '"被禁足"': '"核心"',
    },
    'ko': {
        # 한국어 문법 오류: "바로 입니다" → "바로 당신입니다"
        '사람이 바로 입니다.': '사람이 바로 당신입니다.',
        '사람이 바로 입니다': '사람이 바로 당신입니다',
    },
}

for lang, fixes in FIXES.items():
    for f in (root / lang).glob('*.json'):
        try:
            txt = f.read_text(encoding='utf-8')
        except Exception as e:
            print(f'[skip] {lang}/{f.name}: {e}')
            continue
        new = txt
        for a, b in fixes.items():
            if a in new:
                cnt = new.count(a)
                new = new.replace(a, b)
                log.append(f'{lang}/{f.name}: {cnt}건 "{a}" -> "{b}"')
        if new != txt:
            shutil.copy(f, str(f) + '.pre_v2')
            f.write_text(new, encoding='utf-8')

print('수정:')
for l in log:
    print(' ', l)
print(f'총 {len(log)}건')