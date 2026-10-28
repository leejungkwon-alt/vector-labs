#!/usr/bin/env python3
"""scripts/migrations/fix_p0_i18n_residue.py

P0 결정론적 잔존 수정 (톤 판단 불필요):
  1. zh_cn grade labels "Peak" → "顶峰"
  2. zh_cn/monthly MONTHLY_GRADE_CONTEXT 5줄 번역
  3. zh_cn/free_gating "当前时间" → "当前流势"
  4. zh_cn/core_pillars/辛酉 hero 번역
  5. zh_cn/core_pillars/辛卯 "Spring Jade" → "春玉"
  6. es/pillar_names + es/core_pillars name 스팽글리시 → 스페인어
  7. es/core_pillars 키워드 2건

실행:
  python scripts/migrations/fix_p0_i18n_residue.py            # dry-run
  python scripts/migrations/fix_p0_i18n_residue.py --apply
"""
from __future__ import annotations
import shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def patch(p: Path, pairs: list[tuple[str, str]], label: str) -> None:
    if not p.exists():
        print(f"  ❌ 없음: {p.relative_to(DATA)}")
        return
    src = p.read_text(encoding="utf-8")
    applied = 0
    for old, new in pairs:
        if old in src:
            src = src.replace(old, new)
            applied += 1
    if applied == 0:
        print(f"  ➖ {label}: 이미 완료")
        return
    if APPLY:
        backup(p)
        p.write_text(src, encoding="utf-8")
        print(f"  ✅ {label}: {applied}건")
    else:
        print(f"  🔍 {label}: {applied}건 (--apply 로 적용)")


def main() -> int:
    print("=" * 66); print(f"  fix_p0_i18n_residue ({'APPLY' if APPLY else 'DRY-RUN'})"); print("=" * 66)

    # 1. zh_cn grade labels
    peak = [('"PEAK": "Peak"', '"PEAK": "顶峰"')]
    for f in ("labels.json", "daily.json", "monthly.json", "premium_insights.json"):
        patch(DATA / "zh_cn" / f, peak, f"zh_cn/{f} PEAK")

    # 2. zh_cn/monthly MONTHLY_GRADE_CONTEXT
    patch(DATA / "zh_cn" / "monthly.json", [
        ('"Root energy (Earthly Branches) is favorable this month — separate from the theme."',
         '"本月底气（地支）顺畅，与主题无关。"'),
        ('"Gentle tailwinds from the root energy."', '"地支能量温和，顺风而行。"'),
        ('"Mixed root energy — the theme carries the month."', '"地支能量混合，主题决定这个月的性格。"'),
        ('"Root energy is cautious — keep the pace slow."', '"地支能量偏谨慎，放慢节奏。"'),
        ('"Heavy root energy — protect your margins."', '"地支能量偏重，守住余量。"'),
    ], "zh_cn/monthly context")

    # 3. zh_cn/free_gating
    patch(DATA / "zh_cn" / "free_gating.json",
          [('"timing": "当前时间"', '"timing": "当前流势"')],
          "zh_cn/free_gating timing")

    # 4. zh_cn/辛酉 hero
    patch(DATA / "zh_cn" / "core_pillars" / "辛酉.json", [(
        '"hero": "You\'re a fully cut gem. 辛\'s energy condensed to its purest form — beauty that doesn\'t shake.",',
        '"hero": "你是精雕细琢的宝石。辛的能量凝聚到最纯粹的形态——一种不会动摇的美。",',
    )], "zh_cn/辛酉 hero")

    # 5. zh_cn/辛卯 keyword
    patch(DATA / "zh_cn" / "core_pillars" / "辛卯.json",
          [('"Spring Jade"', '"春玉"')], "zh_cn/辛卯 keyword")

    # 6. es name 스팽글리시
    name_fixes = [
        ("Blade en la Forja",         "Filo en la Forja"),
        ("Blade en el lago Deep",     "Filo en el lago profundo"),
        ("Blade: Abriendo el bosque", "Filo abriendo el bosque"),
        ("Blade en tierra seca",      "Filo en tierra seca"),
        ("Mar helado Deep",           "Mar helado profundo"),
        ("Lago Misty",                "Lago brumoso"),
        ("Perfect Gem",               "Gema perfecta"),
    ]
    name_pairs = [(f'"name": "{o}"', f'"name": "{n}"') for o, n in name_fixes]
    patch(DATA / "es" / "pillar_names.json", name_pairs, "es/pillar_names")
    core_dir = DATA / "es" / "core_pillars"
    if core_dir.exists():
        for fp in sorted(core_dir.glob("*.json")):
            patch(fp, name_pairs, f"es/{fp.name} name")

    # 7. es/core_pillars 키워드
    patch(DATA / "es" / "core_pillars" / "戊戌.json",
          [('"Kai Gang decide"', '"Decisión Kuigang"')], "es/戊戌 keyword")
    patch(DATA / "es" / "core_pillars" / "辛卯.json",
          [('"Spring Jade"', '"Jade de primavera"')], "es/辛卯 keyword")

    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    else:
        print(f"  백업: *. {TS} .bak")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())