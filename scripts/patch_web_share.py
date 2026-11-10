# scripts/patch_web_share.py
from pathlib import Path
import sys
import difflib

PATH = Path("frontend/app/(tabs)/compatibility.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 웹 다운로드 로직을 Web Share API + 폴백으로 교체
old_web_block = '''      if (Platform.OS === "web") {
        // 웹: 다운로드
        const link = document.createElement("a");
        link.href = uri;
        link.download = "gyeol-compatibility.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {'''

new_web_block = '''      if (Platform.OS === "web") {
        // 웹: Web Share API 시도 (모바일 브라우저 대응)
        try {
          const res = await fetch(uri);
          const blob = await res.blob();
          const file = new File([blob], "gyeol-compatibility.png", { type: "image/png" });
          
          if (navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({
              files: [file],
              title: "Gyeol Compatibility",
              text: "Check out our compatibility!",
            });
            return; // 공유 성공 시 종료
          }
        } catch (e) {
          console.log("Web Share API not available or failed, falling back to download.");
        }

        // 폴백: 다운로드 (PC 브라우저 등)
        const link = document.createElement("a");
        link.href = uri;
        link.download = "gyeol-compatibility.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {'''

if new_web_block in src:
    print("⚠️ 이미 패치되어 있습니다."); sys.exit(0)
if old_web_block not in src:
    print("❌ 기존 웹 로직을 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)

patched = src.replace(old_web_block, new_web_block, 1)

sys.stdout.writelines(difflib.unified_diff(
    src.splitlines(keepends=True),
    patched.splitlines(keepends=True),
    fromfile="before", tofile="after", n=2,
))

if "--apply" not in sys.argv:
    print("\n💡 dry-run. 적용: python scripts/patch_web_share.py --apply")
    sys.exit(0)

PATH.write_text(patched, encoding="utf-8")
print("\n✅ 웹 공유 로직 업그레이드 완료")