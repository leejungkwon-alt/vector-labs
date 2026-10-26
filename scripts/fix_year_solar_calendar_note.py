#!/usr/bin/env python3
"""
Step 3-A (P3 UX): 절기년 기준 UX 주석.
- en/ko year.json 에 SOLAR_CALENDAR_NOTE 추가
- content_writer.write_year_section 에 solar_calendar_note 필드
- entitlements free tier keep 에 solar_calendar_note 포함 (메타라 무료 노출)
- frontend types.ts / YearSection.tsx 반영
- 테스트 3건 추가
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app/services/content/data"

NOTES = {
    "en": (
        "The year above follows the solar-term calendar (Lichun to Lichun). "
        "In January, the previous solar year is still active."
    ),
    "ko": (
        "위의 연도는 절기년(입춘~입춘) 기준입니다. "
        "1월에는 아직 전년도 절기년이 적용됩니다."
    ),
}


def add_note(lang: str) -> bool:
    path = DATA / lang / "year.json"
    if not path.exists():
        print(f"  ❌ {path.relative_to(ROOT)} 없음")
        return False
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    note = NOTES[lang]
    if data.get("SOLAR_CALENDAR_NOTE") == note:
        print(f"  ⏭  {lang}/year.json 이미 있음")
        return True
    data["SOLAR_CALENDAR_NOTE"] = note
    (path.parent / (path.name + ".bak.p3a")).write_text(text, encoding="utf-8")
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  ✅ {lang}/year.json SOLAR_CALENDAR_NOTE")
    return True


def patch(path_rel, old, new, label):
    p = ROOT / path_rel
    if not p.exists():
        print(f"  ❌ {path_rel} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if old not in src:
        if new.split("\n")[0].strip() in src:
            print(f"  ⏭  {label} (already)")
            return True
        print(f"  ❌ {label}: 패턴 미발견")
        print(f"     {old[:120]!r}")
        return False
    (p.parent / (p.name + ".bak.p3a")).write_text(src, encoding="utf-8")
    p.write_text(src.replace(old, new, 1), encoding="utf-8")
    print(f"  ✅ {label}")
    return True


def append(path_rel, block, marker):
    p = ROOT / path_rel
    if not p.exists():
        print(f"  ❌ {path_rel} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if marker in src:
        print(f"  ⏭  {path_rel} (already)")
        return True
    (p.parent / (p.name + ".bak.p3a")).write_text(src, encoding="utf-8")
    p.write_text(src.rstrip() + "\n\n\n" + block.strip() + "\n", encoding="utf-8")
    print(f"  ✅ append {path_rel}")
    return True


def main() -> int:
    print("=" * 60)
    print("[Step 3-A] 절기년 UX 주석")
    print("=" * 60)
    ok = True

    # ── 1. 콘텐츠 ──
    print("\n[1/8] 콘텐츠")
    ok &= add_note("en")
    ok &= add_note("ko")

    # ── 2. content_writer.write_year_section ──
    print("\n[2/8] app/services/content_writer.py")
    ok &= patch(
        "app/services/content_writer.py",
        (
            '    pack = load_pack(lang, "year")\n'
            '    theme_map = pack.get("YEAR_THEME_CONTENT", {})\n'
            '    default_theme = pack.get("DEFAULT_YEAR_THEME", {})\n'
        ),
        (
            '    pack = load_pack(lang, "year")\n'
            '    theme_map = pack.get("YEAR_THEME_CONTENT", {})\n'
            '    default_theme = pack.get("DEFAULT_YEAR_THEME", {})\n'
            '    solar_calendar_note = pack.get("SOLAR_CALENDAR_NOTE", "")\n'
        ),
        "solar_calendar_note 로드",
    )
    ok &= patch(
        "app/services/content_writer.py",
        (
            '        "watch_for": theme.get("watch_for", ""),\n'
            '        "lean_into": theme.get("lean_into", ""),\n'
            '        "life_stage_context": life_stage_context,\n'
            '    }'
        ),
        (
            '        "watch_for": theme.get("watch_for", ""),\n'
            '        "lean_into": theme.get("lean_into", ""),\n'
            '        "life_stage_context": life_stage_context,\n'
            '        "solar_calendar_note": solar_calendar_note,\n'
            '    }'
        ),
        "return dict에 solar_calendar_note",
    )

    # ── 3. entitlements free tier keep ──
    print("\n[3/8] app/services/entitlements.py")
    ok &= patch(
        "app/services/entitlements.py",
        (
            '    "year": {\n'
            '        "keep": {\n'
            '            "id", "title", "target_year", "pillar", "ten_god",\n'
            '            "name", "headline", "watch_for",\n'
            '        },\n'
            '        "locked_hint": ["body", "lean_into", "life_stage_context"],\n'
            '    },'
        ),
        (
            '    "year": {\n'
            '        "keep": {\n'
            '            "id", "title", "target_year", "pillar", "ten_god",\n'
            '            "name", "headline", "watch_for",\n'
            '            "solar_calendar_note",\n'
            '        },\n'
            '        "locked_hint": ["body", "lean_into", "life_stage_context"],\n'
            '    },'
        ),
        "free 티어 keep 확장",
    )

    # ── 4. frontend/types.ts ──
    print("\n[4/8] frontend/types.ts")
    ok &= patch(
        "frontend/types.ts",
        (
            'export interface YearSection extends ReportSectionBase {\n'
            '  id: "year";\n'
            '  target_year: number;\n'
            '  pillar: string;\n'
            '  pillar_name?: string;\n'
            '  pillar_name_traditional?: string;\n'
            '  ten_god: string;\n'
            '  name: string;\n'
            '  headline: string;\n'
            '  body?: string;\n'
            '  watch_for?: string;\n'
            '  lean_into?: string;\n'
        ),
        (
            'export interface YearSection extends ReportSectionBase {\n'
            '  id: "year";\n'
            '  target_year: number;\n'
            '  pillar: string;\n'
            '  pillar_name?: string;\n'
            '  pillar_name_traditional?: string;\n'
            '  ten_god: string;\n'
            '  name: string;\n'
            '  headline: string;\n'
            '  body?: string;\n'
            '  watch_for?: string;\n'
            '  lean_into?: string;\n'
            '  solar_calendar_note?: string;\n'
        ),
        "YearSection에 solar_calendar_note",
    )

    # ── 5. frontend YearSection.tsx ──
    print("\n[5/8] frontend/src/components/sections/YearSection.tsx")
    ok &= patch(
        "frontend/src/components/sections/YearSection.tsx",
        (
            '      <Text style={ss.metaText}>\n'
            '        {section.target_year}{section.pillar_name ? ` · ${section.pillar_name}` : ""}\n'
            '      </Text>\n'
            '      <Text style={ss.coreHero}>{section.name}</Text>'
        ),
        (
            '      <Text style={ss.metaText}>\n'
            '        {section.target_year}{section.pillar_name ? ` · ${section.pillar_name}` : ""}\n'
            '      </Text>\n'
            '      {section.solar_calendar_note && (\n'
            '        <Text style={[ss.metaText, { fontStyle: "italic", marginBottom: 8 }]}>\n'
            '          {section.solar_calendar_note}\n'
            '        </Text>\n'
            '      )}\n'
            '      <Text style={ss.coreHero}>{section.name}</Text>'
        ),
        "solar_calendar_note 표시",
    )

    # ── 6. tests/test_full_report.py ──
    print("\n[6/8] tests/test_full_report.py")
    ok &= append(
        "tests/test_full_report.py",
        '''
def test_year_section_has_solar_calendar_note_en():
    """year 섹션에 절기년 기준 안내가 포함되어야 함 (EN)."""
    report = _report_1974()
    year = report["sections"]["year"]
    note = year.get("solar_calendar_note", "")
    assert note, "EN solar_calendar_note 비어있음"
    assert "solar-term" in note.lower() or "lichun" in note.lower()
'''.strip(),
        marker="test_year_section_has_solar_calendar_note_en",
    )

    # ── 7. tests/test_ko_report.py ──
    print("\n[7/8] tests/test_ko_report.py")
    ok &= append(
        "tests/test_ko_report.py",
        '''
def test_ko_year_has_solar_calendar_note():
    """KO year 섹션의 절기년 안내가 한국어여야 함."""
    report = _ko_report_1974()
    year = report["sections"]["year"]
    note = year.get("solar_calendar_note", "")
    assert note, "KO solar_calendar_note 비어있음"
    assert "절기년" in note or "입춘" in note
    assert any("\\uac00" <= ch <= "\\ud7a3" for ch in note)


def test_ko_year_free_tier_keeps_solar_calendar_note():
    """free 티어에서도 절기년 안내는 노출되어야 함."""
    from app.services.entitlements import apply_entitlement_gate
    report = _ko_report_1974()
    gated = apply_entitlement_gate(report, tier="free")
    year = gated["sections"]["year"]
    assert "solar_calendar_note" in year
    assert year["solar_calendar_note"]
    # 반면 body/lean_into 는 잠금
    assert "body" not in year
'''.strip(),
        marker="test_ko_year_has_solar_calendar_note",
    )

    # ── 8. tests/test_report_api.py ──
    print("\n[8/8] tests/test_report_api.py")
    ok &= append(
        "tests/test_report_api.py",
        '''
def test_report_year_solar_calendar_note_present():
    """API year 섹션에 solar_calendar_note 가 항상 포함되어야 함 (free tier 포함)."""
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    payload["use_current_solar_year"] = True
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    year = resp.json()["report"]["sections"]["year"]
    assert "solar_calendar_note" in year
    assert year["solar_calendar_note"]
'''.strip(),
        marker="test_report_year_solar_calendar_note_present",
    )

    print("\n" + "=" * 60)
    print("✅ 완료" if ok else "❌ 일부 실패")
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())