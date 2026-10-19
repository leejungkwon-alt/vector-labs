from pathlib import Path
import subprocess

BASE = Path.cwd()

# 1. Dockerfile 및 .dockerignore 삭제 (Render가 Python 환경으로 자동 빌드하도록 유도)
for filename in ["Dockerfile", ".dockerignore"]:
    p = BASE / filename
    if p.exists():
        p.unlink()
        print(f"🗑️ {filename} 삭제됨 (Render Python 빌드 강제)")

# 2. requirements.txt 강제 추가 (깃허브에 반드시 올라가도록)
print("\n[2] requirements.txt 강제 스테이징")
subprocess.run(["git", "add", "-f", "requirements.txt"], check=True)

# 3. 변경사항 커밋 및 푸시
print("\n[3] 깃허브 푸시")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: remove Dockerfile and force add requirements.txt for Render"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n✅ 깃허브 업로드 완료!")
print("👉 이제 Render 대시보드로 돌아가서 [Manual Deploy] -> [Deploy latest commit]을 눌러주세요.")