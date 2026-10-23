# save as: diagnose_frontend.py  (프로젝트 루트, C:\Users\lenovo\Desktop\SAJU)
#!/usr/bin/env python3
"""프론트엔드 3단계 대상 파일 위치·패턴 사전 확인. 출력은 파일로 저장."""
import io
from pathlib import Path

OUT = Path("diag_frontend.txt")
buf = io.StringIO()
def w(s=""): buf.write(str(s) + "\n")

ROOT = Path("frontend")
TARGETS = {
    "FIX-22 compatibility.tsx": ["app/(tabs)/compatibility.tsx", "app/compatibility.tsx", "src/screens/compatibility.tsx"],
    "FIX-22 birth-input.tsx":   ["app/birth-input.tsx", "src/screens/birth-input.tsx"],
    "FIX-21 PaymentModal.tsx":  ["src/components/PaymentModal.tsx", "components/PaymentModal.tsx"],
    "FIX-23 api/client.ts":     ["src/api/client.ts", "api/client.ts", "src/lib/client.ts", "lib/client.ts"],
    "FIX-24 _layout.tsx":       ["app/_layout.tsx", "src/app/_layout.tsx"],
    "FIX-25 index.tsx":         ["app/index.tsx", "src/app/index.tsx"],
    "FIX-26 SocialLoginModal":  ["src/components/SocialLoginModal.tsx", "components/SocialLoginModal.tsx"],
}

w("=" * 70); w("프론트엔드 대상 파일 위치 확인"); w(f"ROOT = {ROOT.resolve()}"); w("=" * 70)

resolved: dict[str, Path] = {}
for key, candidates in TARGETS.items():
    found = None
    for c in candidates:
        p = ROOT / c
        if p.exists():
            found = p; break
    if found is None:
        # rglob fallback
        name = candidates[0].split("/")[-1]
        for p in ROOT.rglob(name):
            if "node_modules" in p.parts: continue
            if ".bak." in p.name: continue
            found = p; break
    resolved[key] = found
    w(f"{'✅' if found else '❌'} {key:35}  {found if found else '(없음)'}")

w(); w("=" * 70); w("각 파일 내부 패턴 존재 여부"); w("=" * 70)
PATTERNS = {
    "FIX-22": ["offsetHours", "* 15", "tzOffset", "utcOffset"],
    "FIX-21": ["window.location.reload", "invalidateQueries", "bootstrap"],
    "FIX-23": ["http://", "https://", "run.app", "BASE_URL", "API_URL", "EXPO_PUBLIC_API_URL"],
    "FIX-24": ["tabBarIcon", "color as string", "color as any"],
    "FIX-25": ['console.log("[Boot]', "console.log('[Boot]"],
    "FIX-26": ["alert(", "Alert.alert", "Platform.OS", "from 'react-native'"],
}
for key, p in resolved.items():
    if not p: continue
    fid = key.split()[0]
    if fid not in PATTERNS: continue
    src = p.read_text(encoding="utf-8", errors="ignore")
    w(f"\n--- {key}  ({p}) ---")
    for pat in PATTERNS[fid]:
        cnt = src.count(pat)
        w(f"   {pat!r:40}  x{cnt}")

w(); w("=" * 70); w("npx 실행 위치 안내"); w("=" * 70)
w(f"  frontend/node_modules 존재? {(ROOT / 'node_modules').exists()}")
w(f"  frontend/package.json 존재? {(ROOT / 'package.json').exists()}")
w("  → npx tsc / npx expo 는 반드시 'cd frontend' 후 실행")

OUT.write_text(buf.getvalue(), encoding="utf-8")
print(f"✅ 저장: {OUT.resolve()}")
print("   Get-Content diag_frontend.txt")