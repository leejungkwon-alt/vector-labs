#!/usr/bin/env python3
"""
scripts/apply_handoff_step3.py

Handoff Step 3 — App Store / Play Store compliance patches.

  [PATCH 1] frontend/app.json
      expo.ios.privacyManifests 병합 (루트 ./app.json 참조, bundleIdentifier 유지)
  [PATCH 2] frontend/src/components/CrisisBanner.tsx (신규)
  [PATCH 3] frontend/app/(tabs)/home.tsx  → <CrisisBanner crisis={report.crisis_resources} />
  [PATCH 4] frontend/app/(tabs)/daily.tsx → <CrisisBanner />  (fallback only)

Usage:
  python scripts/apply_handoff_step3.py           # dry-run
  python scripts/apply_handoff_step3.py --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FE = ROOT / "frontend"
FE_APP = FE / "app.json"
ROOT_APP = ROOT / "app.json"
HOME = FE / "app" / "(tabs)" / "home.tsx"
DAILY = FE / "app" / "(tabs)" / "daily.tsx"
BANNER = FE / "src" / "components" / "CrisisBanner.tsx"


# ---------------------------------------------------------------------------
# CrisisBanner.tsx content
# ---------------------------------------------------------------------------
BANNER_TSX = r'''// frontend/src/components/CrisisBanner.tsx
// SAJU-COMPLIANCE: 자살예방/위기 리소스 배너. App Store 5.1.1 / Play 정책 대응.
import { View, Text, TouchableOpacity, Linking, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "@/theme";
import { useLanguageStore } from "@/store/languageStore";
import { useT } from "@/i18n";

type CrisisResource = { hotline?: string; phone?: string; url?: string };

type Pack = { title: string; body: string; fallback: string; find: string };

const FALLBACKS: Record<string, Pack> = {
  ko: {
    title: "도움이 필요하시면",
    body: "위기 상황이라면 {hotline} ({phone})에 연락하세요.",
    fallback: "위기 상황이라면 지역 자살예방 핫라인에 연락하세요.",
    find: "지역별 핫라인 찾기",
  },
  en: {
    title: "If you need support",
    body: "In crisis, contact {hotline} ({phone}).",
    fallback: "If you are in crisis, contact a local suicide prevention hotline.",
    find: "Find a helpline",
  },
  ja: {
    title: "サポートが必要なとき",
    body: "危機的な状況なら {hotline}（{phone}）にご連絡ください。",
    fallback: "危機的な状況なら地域の自殺予防ホットラインにご連絡ください。",
    find: "地域のホットラインを探す",
  },
  zh_cn: {
    title: "如果您需要帮助",
    body: "如遇危机，请联系 {hotline}（{phone}）。",
    fallback: "如遇危机，请联系当地的自杀预防热线。",
    find: "查找当地热线",
  },
  es: {
    title: "Si necesitas apoyo",
    body: "En crisis, contacta {hotline} ({phone}).",
    fallback: "Si estás en crisis, contacta con una línea de prevención del suicidio local.",
    find: "Buscar una línea de ayuda",
  },
};

function pick(lang: string, key: keyof Pack): string {
  const pack = FALLBACKS[lang] ?? FALLBACKS.en;
  return pack[key];
}

export function CrisisBanner({ crisis }: { crisis?: CrisisResource }) {
  const lang = useLanguageStore((s) => s.lang);
  const t = useT();

  const tr = (key: string, fbKey: keyof Pack): string => {
    const fromI18n = t(`crisis.${key}`);
    if (!fromI18n || fromI18n === `crisis.${key}`) return pick(lang, fbKey);
    return fromI18n;
  };

  const phone = crisis?.phone;
  const hotline = crisis?.hotline;
  const url = crisis?.url || "https://findahelpline.com/";

  const title = tr("title", "title");
  const fallbackText = tr("fallback", "fallback");
  const findText = tr("findHelpline", "find");

  const bodyText =
    hotline && phone
      ? pick(lang, "body").replace("{hotline}", hotline).replace("{phone}", phone)
      : fallbackText;

  return (
    <View style={styles.box}>
      <View style={styles.header}>
        <Ionicons name="heart-circle" size={20} color="#8B1E1E" />
        <Text style={styles.title}>{title}</Text>
      </View>
      <Text style={styles.body}>{bodyText}</Text>
      {phone ? (
        <TouchableOpacity
          style={styles.callButton}
          onPress={() => Linking.openURL(`tel:${phone}`)}
        >
          <Ionicons name="call" size={16} color="#FFFFFF" />
          <Text style={styles.callButtonText}>{phone}</Text>
        </TouchableOpacity>
      ) : null}
      <TouchableOpacity
        style={styles.linkButton}
        onPress={() => Linking.openURL(url)}
      >
        <Text style={styles.linkText}>{findText}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    margin: spacing.lg,
    marginBottom: 0,
    padding: spacing.md,
    backgroundColor: "#FDF2F2",
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: "#F5C2C2",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  title: {
    fontSize: 14,
    fontWeight: "700",
    color: "#8B1E1E",
    marginLeft: 6,
  },
  body: {
    fontSize: 13,
    color: "#4A1A1A",
    lineHeight: 20,
    marginBottom: 10,
  },
  callButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#B91C1C",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: radius.sm,
    marginBottom: 6,
  },
  callButtonText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 14,
    marginLeft: 6,
  },
  linkButton: {
    paddingVertical: 6,
    alignItems: "center",
  },
  linkText: {
    fontSize: 12,
    color: "#8B1E1E",
    textDecorationLine: "underline",
  },
});
'''


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def plan_app_json() -> str:
    if not ROOT_APP.exists():
        return "  [P1] SKIP  루트 ./app.json 없음 (privacyManifests 원본 없음)"
    if not FE_APP.exists():
        return f"  [P1] ERR   {FE_APP.relative_to(ROOT)} 없음"
    root = json.loads(read_text(ROOT_APP))
    fe = json.loads(read_text(FE_APP))
    pm = root.get("expo", {}).get("ios", {}).get("privacyManifests")
    if not pm:
        return "  [P1] SKIP  루트 app.json 에 privacyManifests 없음"
    if fe.get("expo", {}).get("ios", {}).get("privacyManifests"):
        return "  [P1] SKIP  frontend/app.json 이미 privacyManifests 있음"
    return "  [P1] PATCH frontend/app.json ← expo.ios.privacyManifests 병합"


def plan_banner() -> str:
    if BANNER.exists():
        return "  [P2] SKIP  CrisisBanner.tsx 이미 존재"
    return "  [P2] CREATE frontend/src/components/CrisisBanner.tsx"


def plan_home() -> str:
    if not HOME.exists():
        return "  [P3] ERR   home.tsx 없음"
    text = read_text(HOME)
    if "CrisisBanner" in text:
        return "  [P3] SKIP  home.tsx 이미 마운트됨"
    if 'import { useProfileStore } from "@/store/profileStore";' not in text:
        return "  [P3] ERR   home.tsx import marker 없음"
    if "      <View style={styles.disclaimerBox}>" not in text:
        return "  [P3] ERR   home.tsx disclaimer anchor 없음"
    return "  [P3] PATCH home.tsx ← import + <CrisisBanner crisis={report.crisis_resources} />"


def plan_daily() -> str:
    if not DAILY.exists():
        return "  [P4] ERR   daily.tsx 없음"
    text = read_text(DAILY)
    if "CrisisBanner" in text:
        return "  [P4] SKIP  daily.tsx 이미 마운트됨"
    if 'import { PaymentModal } from "@/components/PaymentModal";' not in text:
        return "  [P4] ERR   daily.tsx import marker 없음"
    if "    </ScrollView>" not in text:
        return "  [P4] ERR   daily.tsx </ScrollView> anchor 없음"
    return "  [P4] PATCH daily.tsx ← import + <CrisisBanner /> (fallback)"


def show_plan(apply: bool) -> None:
    print("=" * 72)
    print(f"  apply_handoff_step3  ({'APPLY' if apply else 'DRY-RUN'})")
    print("=" * 72)
    print(plan_app_json())
    print(plan_banner())
    print(plan_home())
    print(plan_daily())


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------
def apply_app_json() -> None:
    if not (ROOT_APP.exists() and FE_APP.exists()):
        print("  [P1] skip (missing input)")
        return
    root = json.loads(read_text(ROOT_APP))
    fe = json.loads(read_text(FE_APP))
    pm = root.get("expo", {}).get("ios", {}).get("privacyManifests")
    if not pm:
        print("  [P1] skip (no privacyManifests in root)")
        return
    ios = fe.setdefault("expo", {}).setdefault("ios", {})
    if ios.get("privacyManifests"):
        print("  [P1] skip (already present)")
        return
    ios["privacyManifests"] = pm
    text = json.dumps(fe, ensure_ascii=False, indent=2) + "\n"
    write_text(FE_APP, text)
    print("  [P1] patched frontend/app.json")


def apply_banner() -> None:
    if BANNER.exists():
        print("  [P2] skip (exists)")
        return
    write_text(BANNER, BANNER_TSX)
    print("  [P2] created frontend/src/components/CrisisBanner.tsx")


def apply_home() -> None:
    text = read_text(HOME)
    if "CrisisBanner" in text:
        print("  [P3] skip (already mounted)")
        return
    marker = 'import { useProfileStore } from "@/store/profileStore";'
    text = text.replace(
        marker,
        marker + '\nimport { CrisisBanner } from "@/components/CrisisBanner";',
        1,
    )
    anchor = "      <View style={styles.disclaimerBox}>"
    text = text.replace(
        anchor,
        "      <CrisisBanner crisis={(report as any).crisis_resources} />\n" + anchor,
        1,
    )
    write_text(HOME, text)
    print("  [P3] patched home.tsx")


def apply_daily() -> None:
    text = read_text(DAILY)
    if "CrisisBanner" in text:
        print("  [P4] skip (already mounted)")
        return
    marker = 'import { PaymentModal } from "@/components/PaymentModal";'
    text = text.replace(
        marker,
        marker + '\nimport { CrisisBanner } from "@/components/CrisisBanner";',
        1,
    )
    anchor = "    </ScrollView>"
    text = text.replace(
        anchor,
        "      <CrisisBanner />\n" + anchor,
        1,
    )
    write_text(DAILY, text)
    print("  [P4] patched daily.tsx")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    show_plan(args.apply)
    print("-" * 72)
    if not args.apply:
        print("  dry-run 완료 → --apply 로 적용")
        print("=" * 72)
        return 0

    apply_app_json()
    apply_banner()
    apply_home()
    apply_daily()
    print("-" * 72)
    print("  apply 완료")
    print("  다음:")
    print("    python -m pytest -q")
    print("    python scripts/verify_i18n.py")
    print("    python scripts/verify_i18n_tone.py")
    print("    cd frontend ; npx tsc --noEmit")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())