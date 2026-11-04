import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. home.tsx 버튼 번역
p_home = ROOT / "frontend" / "app" / "(tabs)" / "home.tsx"
t_home = p_home.read_text(encoding="utf-8")
if "내 시조 모아보기" in t_home:
    t_home = re.sub(r'내 시조 모아보기\s*\(25편\)', '{t("poem.viewCollection")} (25)', t_home)
    p_home.write_text(t_home, encoding="utf-8")
    print("[OK] home.tsx 버튼 번역 적용")
else:
    print("[SKIP] home.tsx 이미 적용됨")

# 2. PoemFlipCard.tsx tt 함수 번역 확장
p_flip = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
t_flip = p_flip.read_text(encoding="utf-8")

old_tt = '''function tt(lang: string | undefined, ko: string, en: string): string {
  return lang === "ko" ? ko : en;
}'''

new_tt = '''const LANG_MAP: Record<string, Record<string, string>> = {
  es: {
    "오늘의 시조": "Poema del Día",
    "탭하여 뒤집기 →": "Toca para voltear →",
    "← 탭하여 돌아가기": "← Toca para volver",
    "오늘의 실천": "Práctica de Hoy",
    "배경화면 · 프리미엄": "Fondo de pantalla · Premium",
    "배경화면 저장": "Guardar fondo"
  },
  ja: {
    "오늘의 시조": "今日の詩",
    "탭하여 뒤집기 →": "タップして裏返す →",
    "← 탭하여 돌아가기": "← タップして戻る",
    "오늘의 실천": "今日の実践",
    "배경화면 · 프리미엄": "壁紙 · プレミアム",
    "배경화면 저장": "壁紙を保存"
  },
  zh_cn: {
    "오늘의 시조": "今日诗歌",
    "탭하여 뒤집기 →": "点击翻转 →",
    "← 탭하여 돌아가기": "← 点击返回",
    "오늘의 실천": "今日实践",
    "배경화면 · 프리미엄": "壁纸 · 高级",
    "배경화면 저장": "保存壁纸"
  }
};

function tt(lang: string | undefined, ko: string, en: string): string {
  const l = lang || "en";
  if (l === "ko") return ko;
  if (l === "en") return en;
  return LANG_MAP[l]?.[ko] || en;
}'''

if old_tt in t_flip:
    t_flip = t_flip.replace(old_tt, new_tt)
    p_flip.write_text(t_flip, encoding="utf-8")
    print("[OK] PoemFlipCard.tsx tt 함수 다국어 확장")
else:
    print("[SKIP] PoemFlipCard.tsx 이미 적용됨 또는 앵커 없음")
