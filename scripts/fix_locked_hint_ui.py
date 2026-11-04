import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "sections" / "shared.tsx"

if not p.exists():
    print("[ERR] shared.tsx 파일을 찾을 수 없습니다.")
else:
    t = p.read_text(encoding="utf-8")

    # useT 임포트가 없으면 추가
    if "useT" not in t:
        t = 'import { useT } from "@/i18n";\n' + t

    # 깔끔한 LockedHint 컴포넌트 (아이콘 없음)
    clean_hint = """
export function LockedHint({ onPress }: { onPress: () => void }) {
  const t = useT();
  return (
    <View style={{ alignItems: "center", padding: 24, backgroundColor: "#FDF2F2", borderRadius: 12, marginTop: 16, borderWidth: 1, borderColor: "#F5D6D6" }}>
      <Text style={{ fontSize: 14, color: "#A04040", marginBottom: 12, textAlign: "center", lineHeight: 20 }}>
        {t("sections.deeperAnalysis", "Deeper analysis and personalized insights are ready for you.")}
      </Text>
      <TouchableOpacity onPress={onPress} style={{ backgroundColor: "#E55A38", paddingHorizontal: 20, paddingVertical: 10, borderRadius: 24 }}>
        <Text style={{ color: "#FFF", fontWeight: "700", fontSize: 14 }}>
          {t("sections.viewFullReport", "View Full Report")}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
"""

    # 기존 LockedHint 함수 교체
    pattern = re.compile(r'export\s+function\s+LockedHint\([^)]*\)\s*\{.*?\n\}', re.DOTALL)
    if pattern.search(t):
        t = pattern.sub(clean_hint, t)
        p.write_text(t, encoding="utf-8")
        print("[OK] LockedHint 컴포넌트를 아이콘 없는 깔끔한 버전으로 교체 완료")
    else:
        pattern2 = re.compile(r'export\s+const\s+LockedHint\s*=\s*\([^)]*\)\s*=>\s*\(.*?\);', re.DOTALL)
        if pattern2.search(t):
            t = pattern2.sub(clean_hint, t)
            p.write_text(t, encoding="utf-8")
            print("[OK] LockedHint 컴포넌트를 아이콘 없는 깔끔한 버전으로 교체 완료")
        else:
            print("[ERR] LockedHint 컴포넌트를 찾을 수 없습니다. shared.tsx를 수동으로 확인해주세요.")
