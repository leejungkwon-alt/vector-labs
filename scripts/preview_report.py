# scripts/preview_report.py
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report
from app.engine.daily_fortune import calculate_daily_range
from app.services.daily_writer import write_daily_section

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
RED = "\033[31m"
BG_GREEN = "\033[42m"

WIDTH = 78


def hr(char="─"):
    print(char * WIDTH)


def header(text):
    print()
    hr("═")
    print(f"{BOLD}{text}{RESET}")
    hr("═")


def section(title):
    print()
    hr("─")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    hr("─")


def para(text):
    print(f"  {text}")


def bullet(text, sym="•"):
    print(f"  {sym} {text}")


def render_chart(report):
    if "chart" not in report["sections"]:
        return
    chart = report["sections"]["chart"]
    section(chart["title"])
    print(f"  {DIM}{chart['hero']}{RESET}")
    print()
    for layer in chart["layers"]:
        marker = "← YOU" if layer["is_self"] else ""
        print(
            f"  {BOLD}{layer['label']}{RESET}  ·  "
            f"{layer['archetype']}  ·  {DIM}{layer['element']}{RESET}  "
            f"{GREEN}{marker}{RESET}"
        )
        print(f"    {DIM}{layer['role']}{RESET}")
        print(f"    {layer.get('narrative', '')}")
        print()
    for note in chart.get("notes", []):
        print(f"  {MAGENTA}※ {note}{RESET}")
    print()


def render_cover(report, lang):
    cover = report["cover"]
    arch = cover["archetype"]
    header(f"{arch['symbol']}  {arch['name']}  ·  {cover['intensity_label']}")
    print(f"  {DIM}{arch['tagline']}{RESET}")
    age_band = report["meta"].get("age_band")
    if age_band:
        if lang == "en":
            print(
                f"\n  {DIM}Age{RESET}: {BOLD}{age_band['age']}{RESET}  "
                f"{DIM}({age_band['key']}, target {age_band['target_year']}){RESET}"
            )
        else:
            print(
                f"\n  {DIM}나이{RESET}: {BOLD}{age_band['age']}세{RESET}  "
                f"{DIM}({age_band['key']}, target {age_band['target_year']}){RESET}"
            )


def render_summary_cards(report, lang="en"):
    section("Summary" if lang == "en" else "요약")
    for card in report["summary_cards"]:
        print(f"  {BOLD}{card['label']}{RESET}")
        print(f"    {YELLOW}{card['headline']}{RESET}")
        print(f"    {card['body']}")
        print()


def render_core(report, lang):
    core = report["sections"]["core"]
    section(core["title"])
    print(f"  {BOLD}{core['hero']}{RESET}")
    print()
    for p in core["narrative"]:
        para(p)
        print()
    shadow_label = "Shadows" if lang == "en" else "그림자 / Shadows"
    advice_label = "Advice" if lang == "en" else "조언 / Advice"
    print(f"  {MAGENTA}{shadow_label}:{RESET}")
    for s in core["shadows"]:
        bullet(s)
    print()
    print(f"  {GREEN}{advice_label}:{RESET}")
    for a in core["advice"]:
        bullet(a, "→")
    
    # 맞춤형 인사이트 추가
    insights = core.get("personalized_insights", [])
    if insights:
        label = "Personalized Insights" if lang == "en" else "맞춤형 통찰 / Insights"
        print()
        print(f"  {BOLD}{CYAN}{label}:{RESET}")
        for i in insights:
            para(i)


def render_energy(report, lang):
    energy = report["sections"]["energy"]
    section(energy["title"])
    print(f"  {BOLD}{energy['hero']}{RESET}")
    print()
    for block in energy["blocks"]:
        role = block["role"]
        marker = "★" if role == "dominant" else ("△" if role == "deficient" else "✕")
        print(f"  {marker} {BOLD}{block['name']}{RESET}")
        para(block["body"])
        print()


def render_lucky_code(report, lang):
    lc = report["sections"]["lucky_code"]
    section(lc["title"])
    print(f"  {BOLD}{lc['hero']}{RESET}")
    print()
    p = lc["power"]

    power_label = "Power" if lang == "en" else "핵심 에너지"
    support_label = "Support" if lang == "en" else "보조 에너지"
    domains_label = "Life Domains" if lang == "en" else "삶의 영역별 조언"
    watch_label = "Watch out" if lang == "en" else "주의"

    color_lbl = "Colors" if lang == "en" else "색상"
    num_lbl = "Numbers" if lang == "en" else "숫자"
    dir_lbl = "Directions" if lang == "en" else "방향"
    act_lbl = "Activities" if lang == "en" else "활동"
    prac_lbl = "Practices" if lang == "en" else "실천법"

    print(f"  {BOLD}{power_label} — {p['element']}{RESET}")
    print(f"    {color_lbl}: {', '.join(p['colors'])}")
    print(f"    {num_lbl}: {', '.join(map(str, p['numbers']))}")
    print(f"    {dir_lbl}: {', '.join(p['directions'])}")
    print(f"    {act_lbl}: {', '.join(p['activities'][:3])} …")
    print(f"    {prac_lbl}:")
    for x in p["practices"]:
        bullet(x, "→")

    s = lc["support"]
    print(f"\n  {BOLD}{support_label} — {s['element']}{RESET}")
    print(f"    {color_lbl}: {', '.join(s['colors'])}")

    p_domains = p.get("domains") or {}
    if p_domains:
        print()
        print(f"  {BOLD}{domains_label}{RESET}")
        domain_ko = {
            "career": "커리어", "wealth": "재물",
            "relationships": "관계", "learning": "배움",
            "everyday": "일상", "avoid": "피해야 할 것",
        }
        for key in ("career", "wealth", "relationships", "learning", "everyday"):
            val = p_domains.get(key)
            if val:
                label = domain_ko.get(key, key) if lang == "ko" else key
                print(f"    {DIM}{label}:{RESET} {val}")
        avoid = p_domains.get("avoid") or []
        if avoid:
            label = domain_ko.get("avoid", "avoid") if lang == "ko" else "avoid"
            print(f"    {RED}{label}:{RESET} {', '.join(avoid)}")

    if lc.get("watch_out"):
        names = [w["name"] for w in lc["watch_out"]]
        print(f"\n  {RED}{watch_label}:{RESET} {', '.join(names)}")


def render_health(report, lang):
    if "health" not in report["sections"]:
        return
    health = report["sections"]["health"]
    section(health["title"])
    print(f"  {BOLD}{health['hero']}{RESET}")
    print()
    for block in health["blocks"]:
        role = block["role"]
        marker = "★" if role == "dominant" else "△"
        o = block["organs"]
        print(f"  {marker} {BOLD}{block['name']}{RESET}  {DIM}({o['zang']}·{o['fu']}){RESET}")
        para(block["body"])
        print()
    if health.get("practices"):
        label = "Practices" if lang == "en" else "실천 / Practices"
        print(f"  {GREEN}{label}:{RESET}")
        for p in health["practices"][:5]:
            bullet(p, "→")


def render_age_band(report, lang):
    if "age_band" not in report["sections"]:
        return
    ab = report["sections"]["age_band"]
    if lang == "en":
        section(f"{ab['label']}  ·  Age {ab['age']}  (Life Stage)")
    else:
        section(f"{ab['label']}  ·  {ab['age']}세  (생애 단계)")
    print(f"  {BOLD}{ab['headline']}{RESET}")
    print()
    para(ab["body"])
    print()
    if ab.get("advice"):
        advice_label = "Advice" if lang == "en" else "조언 / Advice"
        print(f"  {GREEN}{advice_label}:{RESET}")
        for a in ab["advice"]:
            bullet(a, "→")


def render_sinsal(report, lang):
    if "sinsal" not in report["sections"]:
        return
    sinsal = report["sections"]["sinsal"]
    section(sinsal["title"])
    print(f"  {DIM}{sinsal['hero']}{RESET}")
    print()
    for item in sinsal["items"]:
        role = item.get("position_role") or item.get("position_label", "")
        role_disp = f" ({role})" if role else ""
        print(f"  {BOLD}{item['name']}{RESET}{DIM}{role_disp}{RESET}")
        print(f"    {item['headline']}")
        print(f"    {DIM}{item['body']}{RESET}")
        note = item.get("position_note", "")
        if note:
            print(f"    {DIM}{note}{RESET}")
        print(f"    {GREEN}→ {item['advice']}{RESET}")
        trad = item.get("name_traditional", "")
        if trad:
            print(f"    {DIM}전통 명칭 · {trad}{RESET}")
        print()


def render_mode_section(report, key, lang):
    sec = report["sections"][key]
    section(sec["title"])
    print(f"  {BOLD}{sec['headline']}{RESET}")
    print()
    parts = sec["body"].split("\n\n")
    for para_text in parts:
        if para_text.strip():
            print(f"  {para_text.strip()}")
            print()
    action_label = "Action" if lang == "en" else "액션"
    print(f"  {GREEN}{action_label}:{RESET}")
    bullet(sec["action"], "→")


def render_year(report, lang):
    if "year" not in report["sections"]:
        return
    year = report["sections"]["year"]
    section(year["title"])
    print(f"  {BOLD}{year['name']}  ({year['pillar']}, {year['target_year']}){RESET}")
    print(f"  {YELLOW}{year['headline']}{RESET}")
    print()
    para(year["body"])
    print()
    watch_label = "Watch for" if lang == "en" else "주의할 점"
    lean_label = "Lean into" if lang == "en" else "힘을 실어야 할 곳"
    print(f"  {MAGENTA}{watch_label}:{RESET} {year['watch_for']}")
    print(f"  {GREEN}{lean_label}:{RESET} {year['lean_into']}")

    ctx = year.get("life_stage_context")
    if ctx:
        print()
        ctx_label = "Life Stage" if lang == "en" else "생애 단계"
        print(f"  {BOLD}{ctx_label}{RESET} — {ctx['label']}  ({ctx['key']})")
        print(f"    {DIM}{ctx['headline']}{RESET}")


def render_monthly(report, lang):
    if "monthly" not in report["sections"]:
        return
    mo = report["sections"]["monthly"]
    section(mo["title"])
    print(f"  {DIM}{mo['hero']}{RESET}")
    print()

    grade_color = {
        "PEAK": GREEN + BOLD,
        "FAVORABLE": GREEN,
        "NEUTRAL": "",
        "CAUTION": YELLOW,
        "CHALLENGING": RED,
    }
    watch_label = "Watch" if lang == "en" else "주의"
    lean_label = "Lean" if lang == "en" else "집중"

    for item in mo["items"]:
        color = grade_color.get(item["grade"], "")
        ctx = item.get("grade_context", "")
        suffix = f"  {DIM}· {ctx}{RESET}" if ctx else ""
        print(
            f"  {BOLD}{item['approx_solar_month']}{RESET}  {item['pillar']}  "
            f"{color}{item['grade_label']}{RESET}{suffix}"
        )
        print(f"    {item['name']} — {item['headline']}")
        print(f"    {DIM}{item['body']}{RESET}")
        print(f"    {MAGENTA}{watch_label}:{RESET} {item['watch_for']}")
        print(f"    {GREEN}{lean_label}:{RESET} {item['lean_into']}")
        print()



def render_daily(profile, lang, target_date=None):
    """일운(Daily) 7일치 출력"""
    if target_date is None:
        target_date = date.today()

    day_stem = profile["archetype"]["stem"]

    # yongsin_info 는 dict 이어야 함 (daewoon_score._element_score 계약)
    lc = profile["lucky_code"]
    yongsin_info = {
        "yongsin": lc.get("power_element", ""),
        "huisin":  lc.get("support_element", ""),
        "gisin":   lc.get("watch_out_elements", []),
    }

    try:
        items = calculate_daily_range(target_date, 7, day_stem, yongsin_info)
        sec = write_daily_section(items, lang=lang)
    except Exception as e:
        print(f"  ❌ 일운 생성 실패: {e}")
        return

    section(sec.get("title") or ("Daily" if lang == "en" else "일운"))
    print(f"  {DIM}{sec.get('hero', '')}{RESET}")
    print()

    grade_color = {
        "PEAK": GREEN + BOLD,
        "FAVORABLE": GREEN,
        "NEUTRAL": "",
        "CAUTION": YELLOW,
        "CHALLENGING": RED,
    }
    watch_label = "Watch" if lang == "en" else "주의"
    lean_label  = "Lean"  if lang == "en" else "집중"

    for item in sec["items"]:
        color = grade_color.get(item.get("grade", ""), "")
        is_today = (item.get("date") == target_date.isoformat())
        today_marker = f"{BG_GREEN}{BOLD} TODAY {RESET}" if is_today else "       "

        print(
            f" {today_marker} {BOLD}{item.get('date', '')}{RESET}  "
            f"{item.get('day_pillar', '')}  "
            f"{color}{item.get('grade_label', '')}{RESET}"
        )
        print(f"    {item.get('name', '')} — {item.get('headline', '')}")
        body_text = item.get('body', '')
        for para in body_text.split("\n\n"):
            if para.strip():
                print(f"    {DIM}{para.strip()}{RESET}")
        print(f"    {MAGENTA}{watch_label}:{RESET} {item.get('watch_for', '')}")
        print(f"    {GREEN}{lean_label}:{RESET} {item.get('lean_into', '')}")
        print()


def render_timeline(report, lang="en"):
    import unicodedata

    def pad(s, width):
        # 한글은 2칸, 영문은 1칸으로 계산해서 정렬
        w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
        return s + " " * max(0, width - w)

    tl = report["sections"]["timeline"]
    section(tl["title"])
    print(f"  {DIM}{tl['hero']}{RESET}")
    print()

    grade_labels = {
        "en": {
            "PEAK": "Peak", "FAVORABLE": "Favorable", "NEUTRAL": "Neutral",
            "CAUTION": "Caution", "CHALLENGING": "Challenging",
        },
        "ko": {
            "PEAK": "대길", "FAVORABLE": "순풍", "NEUTRAL": "중립",
            "CAUTION": "주의", "CHALLENGING": "무거움",
        },
    }.get(lang, {})

    for item in tl["items"]:
        grade = item["grade"]
        label = grade_labels.get(grade, grade)
        color = {
            "PEAK": GREEN + BOLD,
            "FAVORABLE": GREEN,
            "NEUTRAL": "",
            "CAUTION": YELLOW,
            "CHALLENGING": RED,
        }.get(grade, "")
        ages = f"{item['ages'][0]:>2}–{item['ages'][1]:<3}"
        score = f"{item['score']:+.1f}"
        now_marker = f"{BG_GREEN}{BOLD} NOW {RESET}" if item.get("is_current") else "     "
        print(
            f" {now_marker} {ages}  {item['pillar']}  "
            f"{color}{pad(label, 12)}{RESET} {DIM}{score}{RESET}  {item['blurb']}"
        )

def render_disclaimer(report):
    print()
    hr("─")
    print(f"  {DIM}{report['disclaimer']}{RESET}")
    hr("─")


def build_report(birth_date, birth_time, birth_time_mode, gender, target_year, lang, city, longitude, timezone_str):
    kwargs = dict(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_time_mode=birth_time_mode,
        correction_mode="lmt",
        jasi_boundary=23,
        gender=gender,
    )
    if city:
        kwargs["birth_location"] = city
    else:
        kwargs["longitude"] = longitude
        kwargs["timezone_str"] = timezone_str
    if target_year:
        kwargs["target_year"] = target_year

    result = calculate_saju(**kwargs)
    profile = build_semantic_profile(result)
    return result, profile, generate_full_report(profile, lang=lang)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("birth_date")
    p.add_argument("birth_time", nargs="?", default=None)
    p.add_argument(
        "--birth-time-mode",
        default="exact",
        choices=["exact", "noon", "day_only"],
    )
    p.add_argument("--gender", default="M", choices=["M", "F"])
    p.add_argument("--target-year", type=int, default=None)
    p.add_argument("--daily-date", default=None, help="일운 기준일 (YYYY-MM-DD)")
    p.add_argument("--lang", default="ko", choices=["en", "ko", "ja", "zh_cn", "zh_tw", "both", "all"])
    p.add_argument("--city", default=None)
    p.add_argument("--longitude", type=float, default=126.9780)
    p.add_argument("--timezone", default="Asia/Seoul")
    args = p.parse_args()

    if args.lang == "both":
        langs = ["en", "ko"]
    elif args.lang == "all":
        langs = ["en", "ko", "ja", "zh_cn"]
    else:
        langs = [args.lang]
    result, _, _ = build_report(
        args.birth_date, args.birth_time, args.birth_time_mode, args.gender,
        args.target_year, "en", args.city, args.longitude, args.timezone,
    )

    print()
    hr("═")
    print(f"{BOLD}{args.birth_date}  {args.birth_time}  ({args.gender}){RESET}")
    if args.city:
        print(f"  city: {args.city}  |  region: {result.get('region')}")
    hr("═")

    pillars_label = "Four Pillars" if args.lang == "en" else "四柱"
    hp = result.get('hour_pillar') or "—"
    print(
        f"  {pillars_label}   "
        f"{result['year_pillar']}  {result['month_pillar']}  "
        f"{result['day_pillar']}  {hp}"
    )
    if args.lang in ("ko", "both"):
        from app.services.template_interpreter import HANJA_TO_HANGUL
        readings = "  ".join(
            "".join(HANJA_TO_HANGUL.get(c, c) for c in p)
            for p in (
                result["year_pillar"], result["month_pillar"],
                result["day_pillar"], result.get("hour_pillar") or "",
            )
        )
        print(f"  읽기          {readings}")
    print(f"  LMT    {result['solar_adjusted_time']}")
    print(f"  UTC    {result['birth_instant_utc']}")

    for lang in langs:
        _, profile, report = build_report(
            args.birth_date, args.birth_time, args.birth_time_mode, args.gender,
            args.target_year, lang, args.city, args.longitude, args.timezone,
        )
        header(f"[{lang.upper()}]")
        render_chart(report)
        render_cover(report, lang)
        render_summary_cards(report, lang)
        render_core(report, lang)
        render_energy(report, lang)
        render_lucky_code(report, lang)
        render_health(report, lang)
        render_age_band(report, lang)
        render_sinsal(report, lang)
        render_mode_section(report, "money", lang)
        render_mode_section(report, "work", lang)
        render_mode_section(report, "bonds", lang)
        render_year(report, lang)
        render_monthly(report, lang)

        # ===== 일운 출력 (7일) =====
        try:
            from datetime import datetime as _dt
            _target_date = None
            if getattr(args, "daily_date", None):
                _target_date = _dt.strptime(args.daily_date, "%Y-%m-%d").date()
            render_daily(profile, lang, _target_date)
        except Exception as _e:
            print(f"  ⚠️ 일운 출력 실패: {_e}")

        render_timeline(report, lang)
        render_disclaimer(report)


if __name__ == "__main__":
    main()