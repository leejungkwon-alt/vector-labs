#!/usr/bin/env python3
"""
Step 1 (P0): 세운·월운 입춘 반영.
- target_year 는 절기년 계약 유지
- use_current_solar_year=true → 서버가 오늘 기준 절기년 계산
- mutual exclusion: 422
- 백엔드 + 프론트 + 테스트 동시 적용
- 각 파일마다 .bak.solar_year 백업
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────
def patch(path_rel: str, old: str, new: str, label: str) -> bool:
    p = ROOT / path_rel
    if not p.exists():
        print(f"  ❌ {path_rel} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if old not in src:
        # 이미 적용됐는지 확인
        if new.split("\n")[0] in src:
            print(f"  ⏭  {label} (already)")
            return True
        print(f"  ❌ {label}: 패턴 미발견")
        print(f"     찾는 문자열: {old[:80]!r}")
        return False
    (p.parent / (p.name + ".bak.solar_year")).write_text(src, encoding="utf-8")
    p.write_text(src.replace(old, new, 1), encoding="utf-8")
    print(f"  ✅ {label}")
    return True


def append(path_rel: str, block: str, marker: str) -> bool:
    p = ROOT / path_rel
    if not p.exists():
        print(f"  ❌ {path_rel} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if marker in src:
        print(f"  ⏭  {path_rel} (already has {marker!r})")
        return True
    (p.parent / (p.name + ".bak.solar_year")).write_text(src, encoding="utf-8")
    p.write_text(src.rstrip() + "\n\n\n" + block.strip() + "\n", encoding="utf-8")
    print(f"  ✅ append {path_rel}")
    return True


def main() -> int:
    print("=" * 60)
    print("[Step 1] 세운·월운 입춘 반영")
    print("=" * 60)
    ok = True

    # ── 1. app/engine/luck.py — current_solar_year 헬퍼 ──
    print("\n[1/9] app/engine/luck.py")
    ok &= patch(
        "app/engine/luck.py",
        "from app.engine.pillars import get_year_pillar, get_month_pillar, EARTHLY_BRANCHES",
        (
            "from datetime import datetime, timezone\n"
            "from zoneinfo import ZoneInfo, ZoneInfoNotFoundError\n"
            "\n"
            "from app.engine.pillars import get_year_pillar, get_month_pillar, EARTHLY_BRANCHES"
        ),
        "imports 추가",
    )
    ok &= append(
        "app/engine/luck.py",
        '''
def current_solar_year(
    tz_str: str = "Asia/Seoul",
    now: datetime | None = None,
) -> int:
    """
    주어진 시각(기본: 지금) 기준 절기년(입춘 기준)을 반환.

    - 2026-01-15 KST → 2025 (乙巳)
    - 2026-03-15 KST → 2026 (丙午)

    Args:
        tz_str: 유저 로컬 타임존. 잘못된 값은 Asia/Seoul로 폴백.
        now: 테스트/재현용 기준 시각. None이면 지금.
    """
    from app.engine.solar_terms import determine_solar_year_and_month

    try:
        tz = ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, ValueError):
        tz = ZoneInfo("Asia/Seoul")

    ref = now if now is not None else datetime.now(tz)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=tz)
    utc = ref.astimezone(timezone.utc)
    solar_year, _ = determine_solar_year_and_month(utc)
    return solar_year
'''.strip(),
        marker="def current_solar_year",
    )

    # ── 2. app/schemas/saju.py — use_current_solar_year 필드 + validator ──
    print("\n[2/9] app/schemas/saju.py")
    ok &= patch(
        "app/schemas/saju.py",
        (
            '    target_year: Optional[int] = Field(\n'
            '        default=None, examples=[2026], description="운세 조회 대상 연도 (올해의 흐름/이번 달의 흐름)"\n'
            '    )'
        ),
        (
            '    target_year: Optional[int] = Field(\n'
            '        default=None, examples=[2026], description="운세 조회 대상 절기년 (입춘~입춘). 올해의 흐름/이번 달의 흐름."\n'
            '    )\n'
            '    use_current_solar_year: bool = Field(\n'
            '        default=False,\n'
            '        description=(\n'
            '            "true면 요청 시점(now) 기준 절기년(입춘 기준)을 자동 계산하여 "\n'
            '            "year/monthly 섹션을 채운다. target_year와 동시 지정 불가."\n'
            '        ),\n'
            '    )'
        ),
        "use_current_solar_year 필드 추가",
    )
    # mutual exclusion validator: validate_birth_time_combination 뒤에 삽입
    ok &= patch(
        "app/schemas/saju.py",
        (
            '            raise ValueError(\n'
            '                f"birth_time must be omitted when birth_time_mode=\'{mode}\'."\n'
            '            )\n'
            '        return self\n'
        ),
        (
            '            raise ValueError(\n'
            '                f"birth_time must be omitted when birth_time_mode=\'{mode}\'."\n'
            '            )\n'
            '        return self\n'
            '\n'
            '    @model_validator(mode="after")\n'
            '    def validate_year_mode(self):\n'
            '        if self.target_year is not None and self.use_current_solar_year:\n'
            '            raise ValueError(\n'
            '                "target_year and use_current_solar_year are mutually exclusive."\n'
            '            )\n'
            '        return self\n'
        ),
        "validate_year_mode validator 추가",
    )

    # ── 3. app/engine/calculator.py — 시그니처 + 로직 ──
    print("\n[3/9] app/engine/calculator.py")
    ok &= patch(
        "app/engine/calculator.py",
        (
            '    target_year=None,\n'
            '    dst_fold=None,\n'
            '    birth_location=None,\n'
            '):'
        ),
        (
            '    target_year=None,\n'
            '    dst_fold=None,\n'
            '    birth_location=None,\n'
            '    use_current_solar_year=False,\n'
            '):'
        ),
        "시그니처에 use_current_solar_year 추가",
    )
    ok &= patch(
        "app/engine/calculator.py",
        (
            '    luck_info = None\n'
            '    if target_year is not None:\n'
            '        annual = calculate_annual_luck(target_year)\n'
            '        monthly = calculate_monthly_lucks(target_year)\n'
        ),
        (
            '    # ---- 세운 기준 절기년 결정 (입춘 반영) ----\n'
            '    if use_current_solar_year:\n'
            '        from app.engine.luck import current_solar_year\n'
            '        effective_solar_year = current_solar_year(timezone_str)\n'
            '    elif target_year is not None:\n'
            '        effective_solar_year = target_year\n'
            '    else:\n'
            '        effective_solar_year = None\n'
            '\n'
            '    luck_info = None\n'
            '    if effective_solar_year is not None:\n'
            '        annual = calculate_annual_luck(effective_solar_year)\n'
            '        monthly = calculate_monthly_lucks(effective_solar_year)\n'
        ),
        "effective_solar_year 계산 + luck_info 조건 변경",
    )
    ok &= patch(
        "app/engine/calculator.py",
        (
            '        luck_info = {\n'
            '            "target_year": target_year,\n'
            '            "annual_luck": {**annual, "ten_god": annual_stem_god},\n'
            '            "monthly_lucks": monthly,\n'
            '        }'
        ),
        (
            '        luck_info = {\n'
            '            "target_year": effective_solar_year,\n'
            '            "annual_luck": {**annual, "ten_god": annual_stem_god},\n'
            '            "monthly_lucks": monthly,\n'
            '        }'
        ),
        "luck_info.target_year = effective_solar_year",
    )

    # ── 4. app/api/v1/endpoints/report.py — pass-through ──
    print("\n[4/9] app/api/v1/endpoints/report.py")
    ok &= patch(
        "app/api/v1/endpoints/report.py",
        (
            '            target_year=payload.target_year,\n'
            '            dst_fold=payload.dst_fold,\n'
            '            birth_location=payload.birth_location,\n'
            '        )'
        ),
        (
            '            target_year=payload.target_year,\n'
            '            use_current_solar_year=payload.use_current_solar_year,\n'
            '            dst_fold=payload.dst_fold,\n'
            '            birth_location=payload.birth_location,\n'
            '        )'
        ),
        "report → calculate_saju pass-through",
    )

    # ── 5. app/api/v1/endpoints/saju.py — pass-through ──
    print("\n[5/9] app/api/v1/endpoints/saju.py")
    ok &= patch(
        "app/api/v1/endpoints/saju.py",
        (
            '            target_year=payload.target_year,\n'
            '            dst_fold=payload.dst_fold, \n'
            '            birth_location=payload.birth_location, \n'
            '        )'
        ),
        (
            '            target_year=payload.target_year,\n'
            '            use_current_solar_year=payload.use_current_solar_year,\n'
            '            dst_fold=payload.dst_fold, \n'
            '            birth_location=payload.birth_location, \n'
            '        )'
        ),
        "saju → calculate_saju pass-through",
    )

    # ── 6. frontend/types.ts — 타입 추가 ──
    print("\n[6/9] frontend/types.ts")
    ok &= patch(
        "frontend/types.ts",
        (
            '  target_year?: number | null;\n'
            '  birth_location?: string | null;\n'
            '  dst_fold?: 0 | 1 | null;\n'
            '}'
        ),
        (
            '  target_year?: number | null;\n'
            '  use_current_solar_year?: boolean;\n'
            '  birth_location?: string | null;\n'
            '  dst_fold?: 0 | 1 | null;\n'
            '}'
        ),
        "SajuRequest에 use_current_solar_year 추가",
    )

    # ── 7. frontend/app/(tabs)/home.tsx — 쿼리 변경 ──
    print("\n[7/9] frontend/app/(tabs)/home.tsx")
    ok &= patch(
        "frontend/app/(tabs)/home.tsx",
        (
            '    queryFn: () =>\n'
            '      api.report({ ...profile, target_year: new Date().getFullYear(), lang }),'
        ),
        (
            '    queryFn: () =>\n'
            '      api.report({ ...profile, use_current_solar_year: true, lang }),'
        ),
        "home → use_current_solar_year: true",
    )

    # ── 8. tests/test_luck.py — 입춘 경계 테스트 추가 ──
    print("\n[8/9] tests/test_luck.py")
    ok &= append(
        "tests/test_luck.py",
        '''
# ==== current_solar_year (입춘 기준 절기년) ====

from datetime import datetime, timedelta, timezone
from app.engine.luck import current_solar_year

_KST = timezone(timedelta(hours=9))


def test_current_solar_year_before_lichun():
    """1월 15일은 아직 전년도 절기년 (입춘 전)."""
    now = datetime(2026, 1, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2025


def test_current_solar_year_after_lichun():
    """3월 15일은 해당 연도 절기년."""
    now = datetime(2026, 3, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2026


def test_current_solar_year_jan_1():
    """1월 1일은 확실히 전년도."""
    now = datetime(2026, 1, 1, 0, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2025


def test_current_solar_year_dec_31():
    """12월 31일은 해당 연도 절기년."""
    now = datetime(2026, 12, 31, 23, 59, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2026


def test_current_solar_year_invalid_tz_falls_back():
    """잘못된 tz는 Asia/Seoul로 폴백 (예외 없이)."""
    now = datetime(2026, 1, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Invalid/Zone", now=now) == 2025
'''.strip(),
        marker="test_current_solar_year_before_lichun",
    )

    # ── 9. tests/test_report_api.py — 엔드포인트 테스트 추가 ──
    print("\n[9/9] tests/test_report_api.py")
    ok &= append(
        "tests/test_report_api.py",
        '''
# ==== use_current_solar_year (입춘 반영) ====

def test_report_use_current_solar_year_january(monkeypatch):
    """1월 요청 시 절기년이 전년도로 계산되어야 함."""
    import app.engine.luck as luck_mod
    monkeypatch.setattr(luck_mod, "current_solar_year", lambda tz_str="Asia/Seoul": 2025)

    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    payload["use_current_solar_year"] = True
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    year = resp.json()["report"]["sections"]["year"]
    assert year["target_year"] == 2025


def test_report_use_current_solar_year_march(monkeypatch):
    """3월 요청 시 절기년이 해당 연도로 계산되어야 함."""
    import app.engine.luck as luck_mod
    monkeypatch.setattr(luck_mod, "current_solar_year", lambda tz_str="Asia/Seoul": 2026)

    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    payload["use_current_solar_year"] = True
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    year = resp.json()["report"]["sections"]["year"]
    assert year["target_year"] == 2026


def test_report_target_year_still_works():
    """기존 target_year=2026 계약 유지."""
    payload = {**BASE_PAYLOAD, "target_year": 2026}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    year = resp.json()["report"]["sections"]["year"]
    assert year["target_year"] == 2026


def test_report_mutual_exclusion_422():
    """target_year와 use_current_solar_year 동시 지정 → 422."""
    payload = {**BASE_PAYLOAD, "target_year": 2026, "use_current_solar_year": True}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 422


def test_report_neither_year_yields_no_section():
    """둘 다 없으면 기존처럼 year 섹션 없음."""
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    assert "year" not in resp.json()["report"]["sections"]
'''.strip(),
        marker="test_report_use_current_solar_year_january",
    )

    print("\n" + "=" * 60)
    print("✅ 모든 패치 적용" if ok else "❌ 일부 패치 실패 — 로그 확인")
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())