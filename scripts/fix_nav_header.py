# scripts/fix_nav_header.py
"""
_ layout.tsx 에서 birth-input의 네비게이션 title 하드코딩을 찾아 패치.
전략:
- 이미 useT() 있으면 → t("birthInput.navTitle")로 교체
- 없으면 → title: "" (텍스트 숨김, 뒤로가기는 유지) + 필요시 주석
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 모든 _layout.tsx 스캔
layouts = list(Path("frontend/app").rglob("_layout.tsx"))
if not layouts:
    print("❌ _layout.tsx를 찾지 못했습니다.")
    sys.exit(1)

print(f"🔎 _layout.tsx 파일 {len(layouts)}개 스캔...\n")

found_files = []
for p in layouts:
    txt = p.read_text(encoding="utf-8")
    if "출생 정보 입력" in txt or ("birth-input" in txt and "출생" in txt):
        found_files.append((p, txt))
        print(f"📂 발견: {p}")
        for i, line in enumerate(txt.splitlines(), 1):
            if "출생 정보 입력" in line or ("birth-input" in line and "title" in line.lower()):
                print(f"   L{i}: {line.strip()}")
        print()

if not found_files:
    print("❌ '출생 정보 입력' 하드코딩을 _layout.tsx에서 못 찾았습니다.")
    print("   다른 곳에 있을 수 있습니다. 다음 명령으로 확인:")
    print("   Get-ChildItem -Path 'frontend' -Recurse -Filter '*.tsx' | Select-String '출생 정보 입력'")
    sys.exit(1)

# ---------- 패치 ----------
for p, txt in found_files:
    orig = txt
    has_useT = "useT()" in txt or "useT (" in txt

    # 패턴: <Stack.Screen name="birth-input" options={{ title: "출생 정보 입력" }} />
    # 또는 멀티라인 가능
    pattern = re.compile(
        r'(<Stack\.Screen\s+name=["\']birth-input["\'][^>]*?)title\s*:\s*["\']출생 정보 입력["\']',
        re.DOTALL,
    )

    if has_useT:
        # useT 있으면 i18n으로
        new_txt, n = pattern.subn(r'\1title: t("birthInput.navTitle")', txt)
        print(f"✅ [useT 있음] {p} → t() 교체 시도 ({n}건)")
    else:
        # useT 없으면 빈 문자열로 (텍스트만 숨기고 뒤로가기는 유지)
        new_txt, n = pattern.subn(r'\1title: ""', txt)
        print(f"✅ [useT 없음] {p} → title: \"\" 로 변경 ({n}건)")

    if n == 0:
        # 다른 형태 탐색 (options={{ title: "출생 정보 입력" }} 외 형태)
        simple_pat = re.compile(r'title\s*:\s*["\']출생 정보 입력["\']')
        new_txt, n2 = simple_pat.subn('title: ""', txt)
        if n2 > 0:
            new_txt = new_txt
            print(f"✅ [fallback] 단순 치환 {n2}건")
            n = n2

    if n == 0:
        print(f"⚠️ {p}: title 패턴 못 찾음. 수동 확인 필요")
        continue

    if new_txt != orig:
        if APPLY:
            p.write_text(new_txt, encoding="utf-8")
            print(f"🎉 저장: {p}")
        else:
            print(f"🧪 미리보기: {p}")

# ---------- JSON에 navTitle 키 추가 (useT 케이스 대비) ----------
TRANS = {
    "ko": "출생 정보 입력", "en": "Birth Data",
    "ja": "出生情報入力", "zh": "输入出生信息", "es": "Datos de nacimiento",
}

def lang_key(f):
    s = f.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

import json
print()
for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if not lang:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if "birthInput" not in data:
        data["birthInput"] = {}
    if "navTitle" not in data["birthInput"]:
        data["birthInput"]["navTitle"] = TRANS[lang]
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            print(f"🎉 {f}: birthInput.navTitle 추가")
        else:
            print(f"🧪 {f}: navTitle 추가 예정")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_nav_header.py --apply")