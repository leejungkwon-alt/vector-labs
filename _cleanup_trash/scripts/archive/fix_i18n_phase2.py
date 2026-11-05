#!/usr/bin/env python3
"""
Phase 2: 프론트엔드 i18n 인프라 확장 (ja, zh_cn, es).
- SupportedLang / LanguageCode 확장, zh_tw 제거
- i18n.ts: import, RESOURCES, availableLangs, formatPickerDate
- languageStore.ts: detectDeviceLang
- settings.tsx: 언어 버튼 배열
- locales/{ja,zh_cn,es}.json ← en.json 복제

실행 후 사용자가:
  cd frontend; npx tsc --noEmit; cd ..
  python -m pytest -q
  git add -A && git commit -m "feat(i18n): frontend support for (ja, zh_cn, es)"
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / "frontend"
LOCALES = FRONT / "src" / "locales"
BAK_SUFFIX = ".bak.p2"

errors = []
patched = []
skipped = []


def _dump_around(path: Path, needle: str, ctx: int = 6) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        return f"  (read error: {e})"
    for i, line in enumerate(lines):
        if needle and needle in line:
            lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
            out = []
            for j in range(lo, hi):
                mark = ">>" if j == i else "  "
                out.append(f"{mark} {j+1:>4}| {lines[j]}")
            return "\n".join(out)
    return f"  (no line containing {needle!r})"


def patch(path: Path, old: str, new: str, label: str) -> bool:
    if not path.exists():
        print(f"  [ERR] {path.relative_to(ROOT)} 없음")
        errors.append(label)
        return False
    src = path.read_text(encoding="utf-8")
    if new in src:
        print(f"  [SKIP] {label} (already)")
        skipped.append(label)
        return True
    if old not in src:
        print(f"  [ERR] {label}: 패턴 미발견")
        print(_dump_around(path, old.split("\n")[0][:40]))
        errors.append(label)
        return False
    bak = path.with_name(path.name + BAK_SUFFIX)
    if not bak.exists():
        shutil.copy2(path, bak)
    path.write_text(src.replace(old, new, 1), encoding="utf-8")
    print(f"  [OK] {label}")
    patched.append(label)
    return True


def copy_locale(src_lang: str, dst_lang: str) -> bool:
    src = LOCALES / f"{src_lang}.json"
    dst = LOCALES / f"{dst_lang}.json"
    if not src.exists():
        print(f"  [ERR] {src.relative_to(ROOT)} 없음")
        errors.append(f"copy {dst_lang}")
        return False
    if dst.exists():
        print(f"  [SKIP] {dst.name} 이미 존재")
        skipped.append(f"copy {dst_lang}")
        return True
    shutil.copy2(src, dst)
    print(f"  [OK] {dst.name} ← {src.name}")
    patched.append(f"copy {dst_lang}")
    return True


# ---- edits ----

def patch_language_store():
    p = FRONT / "src" / "store" / "languageStore.ts"
    old = '''export type SupportedLang = "ko" | "en" | "ja" | "zh_cn" | "zh_tw";
const SUPPORTED: readonly SupportedLang[] = ["ko", "en", "ja", "zh_cn", "zh_tw"] as const;

function detectDeviceLang(): SupportedLang {
  const loc = Localization.getLocales()[0];
  const code = (loc?.languageCode ?? "ko").toLowerCase();
  if (code === "zh") {
    const region = (loc?.regionCode ?? "").toUpperCase();
    return ["TW", "HK", "MO"].includes(region) ? "zh_tw" : "zh_cn";
  }
  if (code === "ja") return "ja";
  if (code === "en") return "en";
  return "ko";
}'''
    new = '''export type SupportedLang = "ko" | "en" | "ja" | "zh_cn" | "es";
const SUPPORTED: readonly SupportedLang[] = ["ko", "en", "ja", "zh_cn", "es"] as const;

function detectDeviceLang(): SupportedLang {
  const loc = Localization.getLocales()[0];
  const code = (loc?.languageCode ?? "ko").toLowerCase();
  // zh는 간체(zh_cn)로 통일. zh_tw 데이터팩은 API 계약에서 제외됨.
  if (code === "zh") return "zh_cn";
  if (code === "ja") return "ja";
  if (code === "es") return "es";
  if (code === "en") return "en";
  return "ko";
}'''
    patch(p, old, new, "languageStore.ts: SupportedLang + detectDeviceLang")


def patch_i18n_imports():
    p = FRONT / "src" / "i18n.ts"
    old = '''import ko from "./locales/ko.json";
import en from "./locales/en.json";'''
    new = '''import ko from "./locales/ko.json";
import en from "./locales/en.json";
import ja from "./locales/ja.json";
import zh_cn from "./locales/zh_cn.json";
import es from "./locales/es.json";'''
    patch(p, old, new, "i18n.ts: locale imports")


def patch_i18n_resources():
    p = FRONT / "src" / "i18n.ts"
    old = '''const RESOURCES: Record<string, any> = {
  ko,
  en,
};'''
    new = '''const RESOURCES: Record<string, any> = {
  ko,
  en,
  ja,
  zh_cn,
  es,
};'''
    patch(p, old, new, "i18n.ts: RESOURCES")


def patch_i18n_available():
    p = FRONT / "src" / "i18n.ts"
    old = '''  const availableLangs: { key: SupportedLang; label: string }[] = [
    { key: "ko", label: "한국어" },
    { key: "en", label: "English" },
  ];'''
    new = '''  const availableLangs: { key: SupportedLang; label: string }[] = [
    { key: "ko", label: "한국어" },
    { key: "en", label: "English" },
    { key: "ja", label: "日本語" },
    { key: "zh_cn", label: "简体中文" },
    { key: "es", label: "Español" },
  ];'''
    patch(p, old, new, "i18n.ts: availableLangs")


def patch_i18n_date_format():
    p = FRONT / "src" / "i18n.ts"
    old = '''export function formatPickerDate(d: Date, lang: string): string {
  if (lang === "ko") {
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
  }
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}'''
    new = '''export function formatPickerDate(d: Date, lang: string): string {
  if (lang === "ko") {
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
  }
  if (lang === "ja") {
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
  }
  if (lang === "zh_cn") {
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
  }
  if (lang === "es") {
    const meses = [
      "enero", "febrero", "marzo", "abril", "mayo", "junio",
      "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ];
    return `${d.getDate()} de ${meses[d.getMonth()]} de ${d.getFullYear()}`;
  }
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}'''
    patch(p, old, new, "i18n.ts: formatPickerDate (ja/zh_cn/es)")


def patch_types_language_code():
    p = FRONT / "types.ts"
    old = 'export type LanguageCode = "en" | "ko" | "ja" | "zh_cn" | "zh_tw";'
    new = 'export type LanguageCode = "en" | "ko" | "ja" | "zh_cn" | "es";'
    patch(p, old, new, "types.ts: LanguageCode")


def patch_settings_lang_buttons():
    p = FRONT / "app" / "(tabs)" / "settings.tsx"
    old = '''          {([
            { key: "ko", label: "한국어" },
            { key: "en", label: "English" },
            { key: "ja", label: "日本語" },
            { key: "zh_cn", label: "简体中文" },
            { key: "zh_tw", label: "繁體中文" },
          ] as { key: SupportedLang; label: string }[]).map((item) => ('''
    new = '''          {([
            { key: "ko", label: "한국어" },
            { key: "en", label: "English" },
            { key: "ja", label: "日本語" },
            { key: "zh_cn", label: "简体中文" },
            { key: "es", label: "Español" },
          ] as { key: SupportedLang; label: string }[]).map((item) => ('''
    patch(p, old, new, "settings.tsx: language button array")


# ---- scans ----

def scan_zh_tw() -> int:
    print("\n[verify] zh_tw 잔존 스캔")
    targets = [
        FRONT / "src" / "i18n.ts",
        FRONT / "src" / "store" / "languageStore.ts",
        FRONT / "types.ts",
        FRONT / "app" / "(tabs)" / "settings.tsx",
    ]
    total = 0
    for p in targets:
        if not p.exists():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "zh_tw" in line:
                print(f"  [ERR] {p.name}:{i}: {line.strip()}")
                total += 1
    if total == 0:
        print("  [OK] zh_tw 잔존 없음")
    return total


def scan_es() -> bool:
    print("\n[verify] es 반영 확인")
    targets = [
        FRONT / "src" / "i18n.ts",
        FRONT / "src" / "store" / "languageStore.ts",
        FRONT / "types.ts",
        FRONT / "app" / "(tabs)" / "settings.tsx",
    ]
    ok = True
    for p in targets:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        if '"es"' not in text and "'es'" not in text:
            print(f"  [ERR] {p.name}: 'es' 미발견")
            ok = False
    if ok:
        print("  [OK] 모든 대상 파일에 'es' 반영")
    return ok


def main() -> int:
    print("=" * 60)
    print("[Phase 2] 프론트엔드 i18n 인프라 (ja, zh_cn, es)")
    print("=" * 60)

    print("\n[1/5] 로케일 파일 복제 (en → ja, zh_cn, es)")
    copy_locale("en", "ja")
    copy_locale("en", "zh_cn")
    copy_locale("en", "es")

    print("\n[2/5] languageStore.ts")
    patch_language_store()

    print("\n[3/5] i18n.ts (4군데)")
    patch_i18n_imports()
    patch_i18n_resources()
    patch_i18n_available()
    patch_i18n_date_format()

    print("\n[4/5] types.ts")
    patch_types_language_code()

    print("\n[5/5] settings.tsx")
    patch_settings_lang_buttons()

    print("\n" + "=" * 60)
    print(f"결과: patched {len(patched)} / skipped {len(skipped)} / errors {len(errors)}")
    print("=" * 60)

    zh = scan_zh_tw()
    es_ok = scan_es()
    failed = len(errors) + zh + (0 if es_ok else 1)

    if failed == 0:
        print("\n[Phase 2 OK] 편집 완료. 다음 커맨드:")
        print("  cd frontend; npx tsc --noEmit; cd ..")
        print("  python -m pytest -q")
        print('  git add -A; git commit -m "feat(i18n): frontend (ja, zh_cn, es), drop zh_tw"')
        return 0
    print(f"\n[Phase 2 FAIL] 이슈 {failed}건 — 위 로그 확인")
    print("롤백: 각 파일 옆 *.bak.p2 를 원래 이름으로 덮어쓰기")
    return 1


if __name__ == "__main__":
    sys.exit(main())