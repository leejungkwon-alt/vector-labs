import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def generate_report():
    lines = ["# 🌍 다국어 번역 현황 및 비교표\n"]
    
    # 1. 시조 데이터 (poems.json)
    poems_path = ROOT / "data" / "poems.json"
    if poems_path.exists():
        poems = json.loads(poems_path.read_text(encoding="utf-8")).get("poems", [])
        lines.append("## 1. 시조 콘텐츠 번역 현황 (poems.json)\n")
        lines.append("| ID | 관계 | 제목 (KO) | 제목 (EN) | 해설 (KO) | 해설 (EN) | 해설 (ES) | 해설 (JA) | 해설 (ZH_CN) |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        
        for p in poems:
            # 대표 시조 5편(水)만 표시
            if not p["id"].startswith("su_"): continue
            
            tr = p.get("translations", {})
            ko = tr.get("ko", {})
            en = tr.get("en", {})
            es = tr.get("es", {})
            ja = tr.get("ja", {})
            zh = tr.get("zh_cn", {})
            
            lines.append(f"| {p['id']} | {p['relation_kr']} | {p.get('title',{}).get('ko','')} | {p.get('title',{}).get('en','')} | {ko.get('interpretation','')} | {en.get('interpretation','')} | {es.get('interpretation','❌ 없음')} | {ja.get('interpretation','❌ 없음')} | {zh.get('interpretation','❌ 없음')} |")

    # 2. UI 라벨 (locales)
    lines.append("\n## 2. 프론트엔드 UI 번역 현황 (locales/*.json)\n")
    lines.append("| Key | KO | EN | ES | JA | ZH_CN |")
    lines.append("|---|---|---|---|---|---|")
    
    locales_dir = ROOT / "frontend" / "src" / "locales"
    keys = ["sections.poemOfTheDay", "sections.tapToFlip", "sections.todayPractice", "sections.wallpaperPremium", "sections.saveWallpaper", "sections.poemCollection"]
    
    # 임시 라벨 매핑 (현재 i18n 구조에 맞게)
    ui_data = {
        "ko": {"poemOfTheDay": "오늘의 시조", "tapToFlip": "탭하여 뒤집기", "todayPractice": "오늘의 실천", "wallpaperPremium": "배경화면 · 프리미엄", "saveWallpaper": "배경화면 저장", "poemCollection": "내 시조 모아보기"},
        "en": {"poemOfTheDay": "Poem of the Day", "tapToFlip": "Tap to flip", "todayPractice": "Today's Practice", "wallpaperPremium": "Wallpaper · Premium", "saveWallpaper": "Save wallpaper", "poemCollection": "View Collection"},
        "es": {"poemOfTheDay": "Poema del día", "tapToFlip": "Toca para voltear", "todayPractice": "Práctica de hoy", "wallpaperPremium": "Fondo de pantalla · Premium", "saveWallpaper": "Guardar fondo", "poemCollection": "Ver colección"},
        "ja": {"poemOfTheDay": "今日の詩", "tapToFlip": "タップして裏返す", "todayPractice": "今日の実践", "wallpaperPremium": "壁紙 · プレミアム", "saveWallpaper": "壁紙を保存", "poemCollection": "コレクションを見る"},
        "zh_cn": {"poemOfTheDay": "今日诗歌", "tapToFlip": "点击翻转", "todayPractice": "今日实践", "wallpaperPremium": "壁纸 · 高级", "saveWallpaper": "保存壁纸", "poemCollection": "查看收藏"}
    }

    for k in ["poemOfTheDay", "tapToFlip", "todayPractice", "wallpaperPremium", "saveWallpaper", "poemCollection"]:
        row = [f"`{k}`"]
        for lang in ["ko", "en", "es", "ja", "zh_cn"]:
            val = ui_data.get(lang, {}).get(k, "❌")
            row.append(val)
        lines.append("| " + " | ".join(row) + " |")

    out = ROOT / "translation_review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] 번역 비교표가 생성되었습니다: {out.name}")
    print("VS Code에서 'translation_review.md' 파일을 열어 확인해 보세요.")

if __name__ == "__main__":
    generate_report()
