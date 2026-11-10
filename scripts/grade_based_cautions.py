# scripts/grade_based_cautions.py
"""
CAUTIONS를 grade 심각도별로 분기 (KO + EN)
- CHALLENGING → danger (강한 경고)
- CAUTION     → warning (중간 주의)
- NEUTRAL     → neutral (담담)
- FAVORABLE/PEAK → positive (격려)
"""
import ast
import json
import shutil
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BASE = Path("app/services/content/data")

# ═══════════════════════════════════════════════════════════
# 새 CAUTIONS 구조: relation × severity
# ═══════════════════════════════════════════════════════════
KO_CAUTIONS = {
    "same": {
        "danger": "같은 방향이라 지루해지기 쉬워요. 의식적으로 새로운 자극을 만들어보세요.",
        "warning": "매너리즘이 올 수 있어요. 한 가지씩 새로 시도해보세요.",
        "neutral": "흐름을 유지하되, 작은 변화를 준비해두세요.",
        "positive": "지금의 결을 즐기세요. 같은 방향의 힘이 서로를 밀어줍니다.",
    },
    "generates_me": {
        "danger": "받기만 하면 무뎌져요. 받은 만큼 꼭 돌려주세요.",
        "warning": "채워지는 만큼, 흘려보내는 것도 잊지 마세요.",
        "neutral": "받는 것에 감사하고, 적당히 흘려보내세요.",
        "positive": "받은 기운을 잘 활용하면 큰 도약이 됩니다.",
    },
    "i_generate": {
        "danger": "베풀다 지칠 수 있어요. 자신을 먼저 채우세요.",
        "warning": "주는 것과 받는 것의 균형을 확인하세요.",
        "neutral": "베풀되, 무리하지 마세요.",
        "positive": "베풀수록 채워지는 시기예요. 마음껏 나누세요.",
    },
    "i_control": {
        "danger": "통제하려는 마음이 강해지면 관계가 상해요. 놓아줄 건 놓아주세요.",
        "warning": "다루되, 다스리려 하지 마세요. 힘을 빼는 연습이 필요해요.",
        "neutral": "적당히 다루면서 균형을 잡으세요.",
        "positive": "다루는 감각이 좋아요. 지금 페이스를 유지하세요.",
    },
    "controls_me": {
        "danger": "압박이 클수록 조급해져요. 남의 속도와 비교하지 마세요.",
        "warning": "지금은 저항보다 흐름에 맡기는 게 나아요.",
        "neutral": "압박을 인정하고, 자신의 페이스를 지키세요.",
        "positive": "약간의 압박은 오히려 성장의 원동력이에요.",
    },
}

EN_CAUTIONS = {
    "same": {
        "danger": "Same direction gets dull fast. Build in new stimulation on purpose.",
        "warning": "Complacency is coming. Try one new thing at a time.",
        "neutral": "Keep the flow, but prep a small change.",
        "positive": "Enjoy this grain. Same-direction forces push each other.",
    },
    "generates_me": {
        "danger": "Only receiving makes you numb. Give back what you get.",
        "warning": "As you fill up, don't forget to pass it on.",
        "neutral": "Be grateful, and let it flow.",
        "positive": "Use this support well — it becomes a big leap.",
    },
    "i_generate": {
        "danger": "Giving drains you. Fill yourself first.",
        "warning": "Check the balance of giving and receiving.",
        "neutral": "Give — but not past your limit.",
        "positive": "The more you give, the more you're filled. Share freely.",
    },
    "i_control": {
        "danger": "Holding too tight hurts the bond. Let go of what you can't hold.",
        "warning": "Handle it — don't control it. Practice loosening your grip.",
        "neutral": "Manage it gently, and find balance.",
        "positive": "Your handling is good right now. Keep this pace.",
    },
    "controls_me": {
        "danger": "Pressure feeds urgency. Don't race against others' pace.",
        "warning": "Don't resist now — let the current carry you.",
        "neutral": "Acknowledge the pressure, keep your pace.",
        "positive": "A bit of pressure is fuel for growth.",
    },
}

# 기존 데이터 로드 (THEMES/PRACTICES 등 유지)
for lang, cautions in [("ko", KO_CAUTIONS), ("en", EN_CAUTIONS)]:
    path = BASE / lang / "timeline_themes.json"
    if not path.exists():
        print(f"❌ {path} 없음")
        sys.exit(1)
    data = json.load(path.open(encoding="utf-8"))
    data["CAUTIONS"] = cautions
    if APPLY:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ {lang}: CAUTIONS grade별 4단계 재작성")

# ja/zh_cn/es EN 복사
for lang in ["ja", "zh_cn", "es"]:
    src = BASE / "en" / "timeline_themes.json"
    dst = BASE / lang / "timeline_themes.json"
    if APPLY:
        shutil.copy(src, dst)
        print(f"✅ {lang}: EN 복사")

# ═══════════════════════════════════════════════════════════
# content_writer.py: grade → severity 매핑
# ═══════════════════════════════════════════════════════════
CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

OLD = '''    rel = d.get("branch_relation") or d.get("stem_relation")
    elem = d.get("branch_element") or d.get("stem_element")
    print(f"[DEBUG-THEME] rel={rel} elem={elem} keys={list(d.keys())[:15]}")
    if not rel or not elem:
        return {}'''

# 디버그 print 있으면 제거
if "[DEBUG-THEME]" in txt:
    lines = txt.splitlines(keepends=True)
    txt = "".join(l for l in lines if "[DEBUG-THEME]" not in l)
    print("✅ 디버그 print 제거")

# _resolve_theme 함수 안에서 caution 처리 부분 교체
OLD_CAUTION = '''    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": cautions.get(rel, ""),
        "practice": practices.get(rel, ""),
    }'''

NEW_CAUTION = '''    # grade → severity 매핑
    grade = str(d.get("grade", "NEUTRAL"))
    severity = "neutral"
    if grade == "CHALLENGING":
        severity = "danger"
    elif grade == "CAUTION":
        severity = "warning"
    elif grade in ("FAVORABLE", "PEAK"):
        severity = "positive"

    # cautions[rel]이 dict(severity별) 또는 str(하위 호환)
    rel_caution = cautions.get(rel, "")
    if isinstance(rel_caution, dict):
        caution_text = rel_caution.get(severity, rel_caution.get("neutral", ""))
    else:
        caution_text = rel_caution

    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": caution_text,
        "practice": practices.get(rel, ""),
    }'''

if OLD_CAUTION not in txt:
    print("❌ caution return 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'app/services/content_writer.py' | Select-String 'cautions.get' -Context 2,2")
    sys.exit(1)

txt = txt.replace(OLD_CAUTION, NEW_CAUTION, 1)
print("✅ grade → severity 매핑 로직 추가")

try:
    ast.parse(txt)
    print("✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)

if APPLY:
    CW.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/grade_based_cautions.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")