from pathlib import Path

BASE = Path.cwd()
GITIGNORE = BASE / ".gitignore"

CLEAN_CONTENT = """# --- Python ---
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
_*.py

# --- 보안/로컬 자산 ---
.env
.env.*
!.env.example
*.log
data/auth.db
data/auth.db-journal
data/auth.db-wal
data/auth.db-shm

# --- OS / IDE ---
.DS_Store
.vscode/
.idea/

# --- Node.js / Frontend ---
node_modules/
frontend/node_modules/
tma/node_modules/
tma/dist/
dist/
.expo/

# --- Backups & Temporary Files ---
*.bak
*.bak_*
prompts/

# --- 로컬 전용 텍스트 (requirements.txt는 반드시 포함되도록 제외) ---
preview.txt
HANDOFF_*.txt
saju_complete_code.txt
"""

def main():
    print("=" * 50)
    print("  .gitignore 파일 정리")
    print("=" * 50)
    
    GITIGNORE.write_text(CLEAN_CONTENT, encoding="utf-8")
    print("✅ .gitignore 파일이 깔끔하게 재작성되었습니다.")
    print("✅ requirements.txt가 정상적으로 업로드되도록 수정되었습니다.")

if __name__ == "__main__":
    main()