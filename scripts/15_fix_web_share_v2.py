import os
import re
import shutil
import subprocess

print("🚀 PC 웹 공유 로직을 '링크 복사'로 수정합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 웹 분기 로직 전체를 찾아서 교체
    old_logic = '''    } else {
      // 웹 환경에서도 링크 복사 or 공유
      if (Platform.OS === "web") {
        if (navigator.share) {
          await navigator.share({ title: "Gyeol Compatibility", url: shareUrl });
        } else {
          await navigator.clipboard.writeText(shareUrl);
          alert("공유 링크가 복사되었습니다! 친구에게 붙여넣기 해주세요.");
        }
        return;
      }
    }'''
    
    new_logic = '''    } else {
      // 웹 환경 분기
      if (Platform.OS === "web") {
        if (!shareUrl || shareUrl.includes("undefined")) {
          alert("공유 링크를 생성하지 못했습니다. 다시 시도해 주세요.");
          return;
        }
        
        const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
        
        if (isMobile && navigator.share) {
          try {
            await navigator.share({ title: "Gyeol Compatibility", url: shareUrl });
          } catch (e) {
            // 사용자가 공유 취소한 경우 무시
          }
        } else {
          // PC 웹은 무조건 링크 복사
          await navigator.clipboard.writeText(shareUrl);
          alert("공유 링크가 복사되었습니다! 친구에게 붙여넣기 해주세요.\\n\\n" + shareUrl);
        }
        return;
      }
    }'''

    if old_logic in content:
        content = content.replace(old_logic, new_logic)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ compatibility.tsx 수정 완료! (PC 웹은 링크 복사로 변경)")
    else:
        print("⚠️ 기존 로직 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")

    print("\n✨ 프론트엔드 배포를 위해 Git에 푸시합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "fix: PC 웹 공유 시 링크 복사로 변경"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
        print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
    except subprocess.CalledProcessError:
        print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ 파일을 찾을 수 없습니다.")
