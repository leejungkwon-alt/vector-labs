from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "sections" / "LuckyCodeSection.tsx"

if not p.exists():
    print("[ERR] 파일을 찾을 수 없습니다.")
else:
    t = p.read_text(encoding="utf-8")
    old = '>내 시조 모아보기 (25편)</Text>'
    new = '>{t("poem.viewCollection")} (25)</Text>'
    
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[OK] LuckyCodeSection.tsx 버튼 번역 완벽 적용!")
    elif new in t:
        print("[SKIP] 이미 번역이 적용되어 있습니다.")
    else:
        print("[ERR] 텍스트를 찾지 못했습니다. 파일 내용을 확인해 주세요.")
