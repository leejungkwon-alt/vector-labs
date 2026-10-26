from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

TEST1 = """

def test_year_section_has_solar_calendar_note_en():
    report = _report_1974()
    year = report["sections"]["year"]
    note = year.get("solar_calendar_note", "")
    assert note
    assert "solar-term" in note.lower() or "lichun" in note.lower()
"""

TEST2 = """

def test_ko_year_has_solar_calendar_note():
    report = _ko_report_1974()
    year = report["sections"]["year"]
    note = year.get("solar_calendar_note", "")
    assert note
    assert "\uc808\uae30\ub144" in note or "\uc785\ucd98" in note
    assert any("\uac00" <= ch <= "\ud7a3" for ch in note)


def test_ko_year_free_tier_keeps_solar_calendar_note():
    from app.services.entitlements import apply_entitlement_gate
    report = _ko_report_1974()
    gated = apply_entitlement_gate(report, tier="free")
    year = gated["sections"]["year"]
    assert "solar_calendar_note" in year
    assert year["solar_calendar_note"]
    assert "body" not in year
"""

TEST3 = """

def test_report_year_solar_calendar_note_present():
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    payload["use_current_solar_year"] = True
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    year = resp.json()["report"]["sections"]["year"]
    assert "solar_calendar_note" in year
    assert year["solar_calendar_note"]
"""

p = ROOT / "tests/test_full_report.py"
s = p.read_text(encoding="utf-8")
if "test_year_section_has_solar_calendar_note_en" not in s:
    p.write_text(s.rstrip() + TEST1 + "\n", encoding="utf-8"); print("  ok test_full_report")
else:
    print("  skip test_full_report")

p = ROOT / "tests/test_ko_report.py"
s = p.read_text(encoding="utf-8")
if "test_ko_year_has_solar_calendar_note" not in s:
    p.write_text(s.rstrip() + TEST2 + "\n", encoding="utf-8"); print("  ok test_ko_report")
else:
    print("  skip test_ko_report")

p = ROOT / "tests/test_report_api.py"
s = p.read_text(encoding="utf-8")
if "test_report_year_solar_calendar_note_present" not in s:
    p.write_text(s.rstrip() + TEST3 + "\n", encoding="utf-8"); print("  ok test_report_api")
else:
    print("  skip test_report_api")