#!/usr/bin/env python3
"""남은 3개 실패 정밀 진단."""
import re
from pathlib import Path


def hdr(t): print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


# ---------- 1. 섹션 구조 덤프
hdr("① 현재 섹션 구조")
try:
    from tests.test_full_report import _report_1974
    from tests.test_ko_report import _ko_report_1974
    for label, fn in [("money (EN)", lambda: _report_1974()),
                      ("bonds (KO)", lambda: _ko_report_1974())]:
        rpt = fn()
        key = "money" if "money" in label else "bonds"
        sec = rpt["sections"][key]
        print(f"\n[{label}] keys = {list(sec.keys())}")
        for k, v in sec.items():
            print(f"    {k:>10}: {repr(v)[:110]}")
except Exception as e:
    print(f"⚠️ import 실패: {type(e).__name__}: {e}")


# ---------- 2. content_writer.py 소스 컨텍스트
hdr("② content_writer.py — money/bonds 섹션 조립부")
cw = Path("app/services/content_writer.py").read_text(encoding="utf-8")
lines = cw.splitlines()
for i, line in enumerate(lines, 1):
    if re.search(r'"(money|bonds)"\s*[:=]', line) and "sections" not in line:
        lo, hi = max(0, i - 4), min(len(lines), i + 12)
        print(f"\n--- L{i} ---")
        for j in range(lo, hi):
            mark = ">>" if j + 1 == i else "  "
            print(f"{mark} {j+1:>4}| {lines[j]}")
# action 키 존재 여부
print(f"\n'action' 리터럴 총 {cw.count(chr(34)+'action'+chr(34))}회")
print(f"'body' 리터럴 총 {cw.count(chr(34)+'body'+chr(34))}회")


# ---------- 3. visual_generator.py work_mode
hdr("③ visual_generator.py — work_mode 매핑")
vg = Path("app/services/visual_generator.py").read_text(encoding="utf-8")
for i, line in enumerate(vg.splitlines(), 1):
    if any(x in line for x in ("work_mode", "challenger", "generalist", "work_mode_map", "_MODE")):
        print(f"L{i:>4}| {line.rstrip()[:130]}")


# ---------- 4. 테스트 기대값
hdr("④ 테스트 기대값")
for f in ("tests/test_visual_pipeline.py", "tests/test_full_report.py", "tests/test_ko_report.py"):
    print(f"\n--- {f} ---")
    src = Path(f).read_text(encoding="utf-8")
    for i, line in enumerate(src.splitlines(), 1):
        if any(x in line for x in ("generalist", "challenger", '"action"', '"money"', '"bonds"')):
            print(f"L{i:>4}| {line.rstrip()[:130]}")


# ---------- 5. 프로필/URL 계산값
hdr("⑤ 프로필·URL 계산 결과")
try:
    from tests.test_visual_pipeline import _profile
    from app.services.visual_generator import get_daily_wallpaper_url
    p74 = _profile()
    p90 = _profile("1990-05-05", "14:30:00")
    for tag, p in [("1974", p74), ("1990", p90)]:
        print(f"\n[{tag}] type={type(p).__name__}")
        if isinstance(p, dict):
            for k in ("work_mode", "day_master", "element", "ten_god"):
                if k in p: print(f"    {k} = {p[k]!r}")
        else:
            for a in ("work_mode", "day_master", "element", "ten_god"):
                if hasattr(p, a): print(f"    {a} = {getattr(p, a)!r}")
        print(f"    url = {get_daily_wallpaper_url(p)}")
except Exception as e:
    print(f"⚠️ 실패: {type(e).__name__}: {e}")

print("\n✅ 진단 완료 — 이 출력 전체를 붙여주세요.")