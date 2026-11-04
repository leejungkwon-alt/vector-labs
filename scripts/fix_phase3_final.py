from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fix_deploy_ps1():
    p = ROOT / "deploy.ps1"
    if not p.exists():
        print("[ERR] deploy.ps1 not found")
        return
    t = p.read_text(encoding="utf-8")
    if "SAJU_DB_PATH" in t:
        print("[SKIP] deploy.ps1 already has SAJU_DB_PATH")
        return
    old = '--allow-unauthenticated --quiet'
    new = '--allow-unauthenticated --quiet --update-env-vars="SAJU_DB_PATH=/tmp/auth.db"'
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[OK] deploy.ps1 patched (SAJU_DB_PATH added)")
    else:
        print("[ERR] deploy.ps1 anchor not found")

def fix_collection_tsx():
    p = ROOT / "frontend" / "app" / "collection.tsx"
    t = p.read_text(encoding="utf-8")
    if "i > 0" in t:
        print("[SKIP] collection.tsx already patched")
        return
    old = 'const locked = poem.tier === "premium" && !isPremium;'
    new = 'const locked = poem.tier === "premium" && !isPremium && i > 0;'
    if old in t:
        t = t.replace(old, new)
        p.write_text(t, encoding="utf-8")
        print("[OK] collection.tsx patched (first item unlocked)")
    else:
        print("[ERR] collection.tsx anchor not found")

if __name__ == "__main__":
    fix_deploy_ps1()
    fix_collection_tsx()
