# scripts/patch_web_share_fix.py
from pathlib import Path
import sys
import difflib

PATH = Path("frontend/app/(tabs)/compatibility.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 웹 공유 블록을 PC/모바일 분기 + 안정적인 폴백으로 교체
old_block = '''      if (Platform.OS === "web") {
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

new_block = '''      if (Platform.OS === "web") {
        // PC(데스크톱)인지 확인 (모바일 웹은 navigator.userAgent로 구분)
        const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
        
        if (isMobile) {
          // 모바일 웹: Web Share API 시도
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
            console.log("Mobile Web Share failed, falling back to download.");
          }
        }

        // PC 브라우저 또는 모바일 공유 실패 시: 다운로드
        const link = document.createElement("a");
        link.href = uri;
        link.download = "gyeol-compatibility.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {'''

if new_block in src:
    print("⚠️ 이미 수정되어 있습니다."); sys.exit(0)
if old_block not in src:
    print("❌ 기존 웹 공유 블록을 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)

patched = src.replace(old_block, new_block, 1)

sys.stdout.writelines(difflib.unified_diff(
    src.splitlines(keepends=True),
    patched.splitlines(keepends=True),
    fromfile="before", tofile="after", n=2,
))

if "--apply" not in sys.argv:
    print("\n💡 dry-run. 적용: python scripts/patch_web_share_fix.py --apply")
    sys.exit(0)

PATH.write_text(patched, encoding="utf-8")
print("\n✅ PC/모바일 웹 공유 로직 분기 완료")