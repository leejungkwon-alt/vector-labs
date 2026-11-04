from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fix_entitlements():
    p = ROOT / "app" / "services" / "entitlements.py"
    t = p.read_text(encoding="utf-8")
    old = '"locked_fields": {"wallpaper_image", "collection"},'
    new = '"locked_fields": {"wallpaper_image"},'
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[OK] entitlements.py: collection 잠금 해제")
    else:
        print("[SKIP] entitlements.py: 이미 수정되었거나 앵커를 찾을 수 없음")

def fix_home_fallback():
    p = ROOT / "frontend" / "app" / "(tabs)" / "home.tsx"
    t = p.read_text(encoding="utf-8")
    old = 'const collection = (poem as any).collection || [];'
    new = 'const collection = (poem as any).collection && (poem as any).collection.length > 0 ? (poem as any).collection : [poem];'
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[OK] home.tsx: fallback 추가 완료")
    else:
        print("[SKIP] home.tsx: 이미 수정되었거나 앵커를 찾을 수 없음")

if __name__ == "__main__":
    fix_entitlements()
    fix_home_fallback()
