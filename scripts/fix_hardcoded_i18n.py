import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. 번역 키 추가 (locales/*.json)
translations = {
    "ko": {"poem": {"viewCollection": "내 시조 모아보기", "collection": "시조 컬렉션", "back": "돌아가기"}},
    "en": {"poem": {"viewCollection": "View My Collection", "collection": "Poem Collection", "back": "Back"}},
    "es": {"poem": {"viewCollection": "Ver mi colección", "collection": "Colección de poemas", "back": "Volver"}},
    "ja": {"poem": {"viewCollection": "コレクションを見る", "collection": "詩のコレクション", "back": "戻る"}},
    "zh_cn": {"poem": {"viewCollection": "查看我的收藏", "collection": "诗歌收藏", "back": "返回"}}
}

for lang, data in translations.items():
    p = ROOT / "frontend" / "src" / "locales" / f"{lang}.json"
    if not p.exists(): continue
    try:
        content = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        content = {}
    
    if "poem" not in content:
        content["poem"] = {}
    content["poem"].update(data["poem"])
    
    p.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {lang}.json 업데이트")

# 2. home.tsx 수정 (버튼 텍스트 i18n 적용)
p_home = ROOT / "frontend" / "app" / "(tabs)" / "home.tsx"
t_home = p_home.read_text(encoding="utf-8")
old_btn = '<Text style={{ color: colors.primary, fontWeight: "700" }}>내 시조 모아보기 (25편)</Text>'
new_btn = '<Text style={{ color: colors.primary, fontWeight: "700" }}>{t("poem.viewCollection")} (25)</Text>'
if old_btn in t_home:
    t_home = t_home.replace(old_btn, new_btn)
    p_home.write_text(t_home, encoding="utf-8")
    print("[OK] home.tsx 수정 완료 (버튼 번역 적용)")

# 3. collection.tsx 수정 (헤더/뒤로가기 i18n 적용)
p_col = ROOT / "frontend" / "app" / "collection.tsx"
t_col = p_col.read_text(encoding="utf-8")

# useT 임포트 추가
if "useT" not in t_col:
    t_col = t_col.replace(
        'import { usePoemStore } from "@/store/poemStore";',
        'import { usePoemStore } from "@/store/poemStore";\nimport { useT } from "@/i18n";'
    )

# useT 훅 추가
if "const t = useT();" not in t_col:
    t_col = t_col.replace(
        'const { collection, currentPoem } = usePoemStore();',
        'const { collection, currentPoem } = usePoemStore();\n  const t = useT();'
    )

# 텍스트 교체
t_col = t_col.replace('<Text style={styles.backText}>← Back</Text>', '<Text style={styles.backText}>← {t("poem.back")}</Text>')
t_col = t_col.replace('<Text style={styles.title}>Poem Collection</Text>', '<Text style={styles.title}>{t("poem.collection")}</Text>')
t_col = t_col.replace('Upgrade to see all 25 poems', '{t("common.upgradeToSeeAll", "Upgrade to see all 25 poems")}') # fallback

p_col.write_text(t_col, encoding="utf-8")
print("[OK] collection.tsx 수정 완료 (헤더/뒤로가기 번역 적용)")
