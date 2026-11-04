from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "app" / "collection.tsx"

t = p.read_text(encoding="utf-8")

# 1. currentPoem 가져오기
old_import = 'const { collection } = usePoemStore();'
new_import = 'const { collection, currentPoem } = usePoemStore();'
t = t.replace(old_import, new_import)

# 2. 잠금 로직 수정 (오늘의 시조와 일치하면 무료)
old_locked = 'const locked = poem.tier === "premium" && !isPremium && i > 0;'
new_locked = '''const isMyDailyPoem = poem.id === currentPoem?.id;
          const locked = !isPremium && !isMyDailyPoem;'''
t = t.replace(old_locked, new_locked)

p.write_text(t, encoding="utf-8")
print("[OK] collection.tsx: 오늘의 시조(메인 카드)가 컬렉션에서도 열리도록 수정 완료")
