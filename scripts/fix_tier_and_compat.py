import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

# ====================================================
# 1. 백엔드 DB: 현재 유저에게 'compatibility' 애드온 강제 부여
# ====================================================
DB_PATH = Path("data/auth.db")

def grant_compat():
    if not DB_PATH.exists():
        print("❌ DB 파일이 없습니다.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 가장 최근 유저 찾기
    cur.execute("SELECT id FROM users ORDER BY created_at DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        uid = row[0]
        cur.execute(
            "INSERT INTO user_addons (user_id, addon, granted_at) VALUES (?, 'compatibility', datetime('now')) ON CONFLICT DO NOTHING",
            (uid,)
        )
        conn.commit()
        print(f"✅ 백엔드 DB: 유저({uid[:8]}...)에게 궁합 애드온 부여 완료!")
    conn.close()

# ====================================================
# 2. 프론트엔드: Settings UI 등급 라벨 정확히 수정
# ====================================================
FILE = Path("frontend/app/(tabs)/settings.tsx")

def patch_settings():
    if not FILE.exists():
        print("❌ settings.tsx를 찾을 수 없습니다.")
        return
    src = FILE.read_text(encoding="utf-8")
    
    # 등급 표시 라벨 로직 수정
    old_label = '{user?.tier === "free" ? "무료 회원 (Free)" : "프리미엄 구독자 (Premium)"}'
    new_label = '''{
              user?.tier === "free" ? "무료 회원 (Free)" :
              user?.tier === "subscription" ? "구독자 (Subscription)" :
              user?.tier === "premium" ? "프리미엄 회원 (Premium)" : user?.tier
            }'''

    if old_label in src:
        src = src.replace(old_label, new_label)
        
        # 백업 및 저장
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = FILE.with_suffix(f".tsx.bak.{ts}")
        shutil.copy2(FILE, bak)
        FILE.write_text(src, encoding="utf-8")
        print(f"✅ 프론트엔드: UI 등급 라벨 수정 완료! (백업: {bak.name})")
    else:
        print("⚠️ 이미 수정되었거나 패턴을 찾지 못했습니다.")

if __name__ == "__main__":
    grant_compat()
    patch_settings()
