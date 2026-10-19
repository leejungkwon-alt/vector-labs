from pathlib import Path
import subprocess

BASE = Path.cwd()

# 1. 삭제할 파일 및 폴더 목록
FILES_TO_DELETE = [
    # Render 배포 관련
    "render.yaml",
    # 임시 배포 스크립트
    "scripts/fix_render_deploy.py",
    "scripts/migrate_to_fly.py",
    "scripts/patch_cloudrun_docker.py",
    "scripts/create_cloudrun_dockerfile.py",
    "scripts/fix_container_import.py",
    "scripts/fix_container_import_final.py",
    "scripts/fix_dockerignore_for_cloudrun.py",
    "scripts/update_to_cloudrun.py",
    "scripts/setup_telegram_proxy.py",
    # 임시 파일
    "secret.txt",
]

print("=" * 50)
print("  프로젝트 정리 시작")
print("=" * 50)

deleted_count = 0
for name in FILES_TO_DELETE:
    p = BASE / name
    if p.exists():
        p.unlink()
        print(f"🗑️ 삭제: {name}")
        deleted_count += 1
    else:
        print(f"⏭️ 건너뜀 (없음): {name}")

# 2. 백업 파일(*.bak*, *.broken*) 일괄 삭제
for pattern in ["*.bak*", "*.broken*"]:
    for p in BASE.rglob(pattern):
        try:
            p.unlink()
            print(f"🗑️ 삭제: {p.relative_to(BASE)}")
            deleted_count += 1
        except Exception:
            pass

# 3. 불필요한 폴더 삭제 (prompts는 유지)
FOLDERS_TO_DELETE = [
    "docs",
]
for name in FOLDERS_TO_DELETE:
    p = BASE / name
    if p.exists() and p.is_dir():
        import shutil
        shutil.rmtree(p)
        print(f"🗑️ 폴더 삭제: {name}")
        deleted_count += 1

print(f"\n✅ 총 {deleted_count}개 항목 정리 완료!")

# 4. .gitignore 최종 확인
GITIGNORE = BASE / ".gitignore"
content = GITIGNORE.read_text(encoding="utf-8")
if "render.yaml" not in content:
    content += "\n# Cloud Run 배포는 Dockerfile 사용 (render.yaml 불필요)\n"
    GITIGNORE.write_text(content, encoding="utf-8")
    print("✅ .gitignore에 정리 사항 반영")

# 5. 깃허브 푸시
print("\n[5] 깃허브 푸시")
try:
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: cleanup project after Cloud Run migration"],
        check=True,
    )
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ 깃허브 업로드 완료")
except subprocess.CalledProcessError:
    print("⚠️ 커밋할 변경 사항이 없거나 푸시에 실패했습니다.")

print("\n" + "=" * 50)
print("  🚀 정리 완료. Render 대시보드에서도 서비스를 삭제하세요.")
print("=" * 50)