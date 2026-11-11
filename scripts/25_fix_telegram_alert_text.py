import os
import re
import shutil
import subprocess

print("🚀 텔레그램 안내 문구를 현실적으로 수정합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 downloadFile 로직 전체를 찾아서 단순 안내로 교체
    old_block = '''      // 💡 텔레그램 환경: downloadFile API로 저장 시도
      if (isTelegram) {
        try {
          if (typeof tg.downloadFile === "function") {
            const res = await fetch(uri);
            const blob = await res.blob();
            const blobUrl = URL.createObjectURL(blob);
            tg.downloadFile({ url: blobUrl, fileName: "gyeol-compatibility.png" });
            tg.showAlert("이미지 저장을 시작합니다!\\n저장이 안 되면 화면을 길게 눌러 저장해 주세요.");
            setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
            return;
          }
        } catch (e) {
          console.error("Telegram downloadFile failed", e);
        }
        // downloadFile 미지원 or 실패 시 안내
        tg.showAlert("이미지가 준비되었습니다.\\n화면을 길게 눌러 저장하거나 스크린샷을 찍어 주세요.");
        return;
      }'''
    
    new_block = '''      // 💡 텔레그램 환경: 이미지 저장이 불가능하므로 스크린샷 안내
      if (isTelegram) {
        tg.showAlert("텔레그램에서는 이미지 저장을 지원하지 않습니다.\\n\\n화면을 캡처(스크린샷)해서 친구에게 보내주세요!");
        return;
      }'''

    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 텔레그램 안내 문구 수정 완료!")
    else:
        print("⚠️ 기존 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")

    print("\n✨ 프론트엔드 배포를 위해 Git에 푸시합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "fix: 텔레그램 공유 시 스크린샷 안내로 변경"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
        print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
    except subprocess.CalledProcessError:
        print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ 파일을 찾을 수 없습니다.")
