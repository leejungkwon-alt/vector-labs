import os
import re
import shutil
import subprocess

print("🚀 공유 기능을 완벽하게 원상 복구(이미지 다운로드)합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 handleShare 함수 전체를 찾아서 원래 코드로 교체
    pattern = r"const handleShare = async \(\) => \{[\s\S]*?\n  \};"
    
    original_code = '''const handleShare = async () => {
    try {
      if (!shareRef.current) return;
      const uri = await captureRef(shareRef, { format: "png", quality: 1 });
      
      if (Platform.OS === "web") {
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

        // PC 웹이거나 모바일 웹 공유 실패 시 다운로드
        const link = document.createElement("a");
        link.href = uri;
        link.download = "gyeol-compatibility.png";
        link.click();
      } else {
        // 네이티브 앱 (iOS/Android) 로직은 필요시 추가
      }
    } catch (e) {
      console.error("Share failed", e);
    }
  };'''

    new_content, count = re.subn(pattern, original_code, content)
    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ compatibility.tsx 공유 함수 원상 복구 완료!")
    else:
        print("⚠️ 기존 handleShare 함수를 찾지 못했습니다. 수동 확인 필요.")

    print("\n✨ 프론트엔드 배포를 위해 Git에 푸시합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "revert: 공유 기능 완벽 원상 복구 (이미지 다운로드)"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
        print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
    except subprocess.CalledProcessError:
        print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ 파일을 찾을 수 없습니다.")
