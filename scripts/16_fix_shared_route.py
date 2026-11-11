import os
import shutil
import subprocess

print("🚀 공유 결과 조회 API의 백엔드 경로를 수정합니다...\n")

compat_path = "app/api/v1/endpoints/compatibility.py"
if os.path.exists(compat_path):
    shutil.copy2(compat_path, compat_path + ".bak")
    with open(compat_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 라우트를 프론트엔드가 호출하는 주소와 일치하도록 변경
    old_route = '@router.get("/shared/{share_id}")'
    new_route = '@router.get("/compatibility/shared/{share_id}")'
    
    if old_route in content:
        content = content.replace(old_route, new_route)
        with open(compat_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 라우트 경로 수정 완료: /shared/{id} -> /compatibility/shared/{id}")
    else:
        print("⚠️ 기존 라우트 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")

    print("\n✨ 백엔드 배포를 위해 Cloud Run에 배포합니다...")
    subprocess.run(".\\deploy.ps1", shell=True)
else:
    print("❌ 파일을 찾을 수 없습니다.")
