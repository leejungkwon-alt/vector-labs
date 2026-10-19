"""콘텐츠 교차 중복 방지 테스트 (Daily vs Monthly vs Year)."""
from app.services.content.loader import load_pack

def _extract_sentences(pack, section, theme_list):
    sentences = set()
    for theme in theme_list:
        raw = pack.get(section, {}).get(theme)
        if not raw: continue
        variants = raw if isinstance(raw, list) else [raw]
        for v in variants:
            for field in ("headline", "body"):
                text = v.get(field, "")
                for s in text.replace(".", "|").replace("?", "|").replace("!", "|").split("|"):
                    s = s.strip().lower()
                    if len(s) > 15:
                        sentences.add(s)
    return sentences

def test_cross_content_no_overlap():
    """일운, 월운, 연운 간의 겹치는 문장이 없어야 함."""
    themes = [
        "TEN_GOD_FRIEND", "TEN_GOD_ROB_WEALTH", "TEN_GOD_EATING_GOD",
        "TEN_GOD_HURTING_OFFICER", "TEN_GOD_INDIRECT_WEALTH",
        "TEN_GOD_DIRECT_WEALTH", "TEN_GOD_SEVEN_KILLINGS",
        "TEN_GOD_DIRECT_OFFICER", "TEN_GOD_INDIRECT_RESOURCE",
        "TEN_GOD_DIRECT_RESOURCE"
    ]
    
    for lang in ("en", "ko"):
        daily = load_pack(lang, "daily")
        monthly = load_pack(lang, "monthly")
        year = load_pack(lang, "year")
        
        d_sents = _extract_sentences(daily, "DAILY_THEME_CONTENT", themes)
        m_sents = _extract_sentences(monthly, "MONTHLY_THEME_CONTENT", themes)
        y_sents = _extract_sentences(year, "YEAR_THEME_CONTENT", themes)
        
        assert not (d_sents & m_sents), f"[{lang}] Daily-Monthly overlap: {d_sents & m_sents}"
        assert not (d_sents & y_sents), f"[{lang}] Daily-Year overlap: {d_sents & y_sents}"
        assert not (m_sents & y_sents), f"[{lang}] Monthly-Year overlap: {m_sents & y_sents}"