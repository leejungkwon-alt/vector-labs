#!/usr/bin/env python3
"""
scripts/update_premium_renderer.py

확장된 프리미엄 콘텐츠 필드(patterns/compatibility/actions/red_flags)를
백엔드에서 반환하고, 프론트엔드에서 렌더링하도록 수정.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

def patch(rel_path, old, new, label, is_frontend=True):
    base = FRONTEND if is_frontend else ROOT
    p = base / rel_path
    if not p.exists():
        print(f"  [!!] {rel_path} 없음")
        return
    text = p.read_text(encoding="utf-8")
    if new in text:
        print(f"  [--] {label}: 이미 적용됨")
        return
    if old not in text:
        print(f"  [!!] {label}: 대상 문자열 불일치")
        return
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  [OK] {label}")

def main():
    print("=" * 60)
    print("  프리미엄 렌더러 업데이트")
    print("=" * 60)
    print()

    # 1. content_writer.py: write_premium_section 확장
    patch(
        "app/services/content_writer.py",
        '''    return {
        "id": section_name,
        "title": pack.get("SECTION_TITLE", section_name.title()),
        "mode": arch,
        "headline": content.get("headline", ""),
        "body": content.get("body", ""),
        "action": "꾸준한 기록과 실행이 필요합니다." if lang == "ko" else "Consistent action is required.",
    }''',
        '''    return {
        "id": section_name,
        "title": pack.get("SECTION_TITLE", section_name.title()),
        "mode": arch,
        "headline": content.get("headline", ""),
        "body": content.get("body", ""),
        "patterns": content.get("patterns", []),
        "compatibility": {
            "best_match": content.get("best_match", []),
            "best_reason": content.get("best_reason", ""),
            "challenging_match": content.get("challenging_match", []),
            "challenging_reason": content.get("challenging_reason", ""),
        },
        "actions": content.get("actions", []),
        "red_flags": content.get("red_flags", []),
    }''',
        "content_writer.py: write_premium_section 확장",
        is_frontend=False,
    )

    # 2. entitlements.py: 게이팅 규칙 확장
    patch(
        "app/services/entitlements.py",
        '''    "love": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "action"],
    },
    "career": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "action"],
    },
    "wealth": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "action"],
    },''',
        '''    "love": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },
    "career": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },
    "wealth": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },''',
        "entitlements.py: 게이팅 규칙 확장",
        is_frontend=False,
    )

    # 3. home.tsx: 확장 필드 렌더링
    patch(
        "app/(tabs)/home.tsx",
        '''                  {/* Premium Sections (Love, Career, Wealth) */}
                  {["love", "career", "wealth"].includes(key) && (
                    <View style={{ marginTop: 12, padding: 16, backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border }}>
                      <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22 }}>
                        프리미엄 결제 후 본문과 맞춤 액션 플랜을 확인하실 수 있습니다.
                      </Text>
                    </View>
                  )}''',
        '''                  {/* Premium Sections (Love, Career, Wealth) */}
                  {["love", "career", "wealth"].includes(key) && sec.patterns && sec.patterns.length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={styles.blockTitle}>관계 패턴</Text>
                      {sec.patterns.map((p: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>• {p}</Text>
                      ))}
                    </View>
                  )}
                  {["love", "career", "wealth"].includes(key) && sec.compatibility && (
                    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.surface, borderRadius: radius.md }}>
                      <Text style={styles.blockTitle}>궁합</Text>
                      <Text style={styles.paragraph}>최고의 궁합: {(sec.compatibility.best_match || []).join(", ")}</Text>
                      <Text style={{ fontSize: 14, color: colors.textMuted, marginBottom: 8 }}>{sec.compatibility.best_reason}</Text>
                      <Text style={styles.paragraph}>주의할 궁합: {(sec.compatibility.challenging_match || []).join(", ")}</Text>
                      <Text style={{ fontSize: 14, color: colors.textMuted }}>{sec.compatibility.challenging_reason}</Text>
                    </View>
                  )}
                  {["love", "career", "wealth"].includes(key) && sec.actions && sec.actions.length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={styles.blockTitle}>실천 가이드</Text>
                      {sec.actions.map((a: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>→ {a}</Text>
                      ))}
                    </View>
                  )}
                  {["love", "career", "wealth"].includes(key) && sec.red_flags && sec.red_flags.length > 0 && (
                    <View style={{ marginTop: 12, padding: 12, backgroundColor: "#FFF5F0", borderRadius: radius.md }}>
                      <Text style={[styles.blockTitle, { color: "#C2461F" }]}>주의할 점</Text>
                      {sec.red_flags.map((r: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>⚠ {r}</Text>
                      ))}
                    </View>
                  )}
                  {["love", "career", "wealth"].includes(key) && !sec.patterns && (
                    <View style={{ marginTop: 12, padding: 16, backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border }}>
                      <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22 }}>
                        프리미엄 결제 후 상세 분석을 확인하실 수 있습니다.
                      </Text>
                    </View>
                  )}''',
        "home.tsx: 프리미엄 확장 필드 렌더링",
    )

    print("\n[git] add → commit → push")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "feat: render expanded premium fields (patterns/compatibility/actions/red_flags)"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
        print("\n[done] 커밋 + 푸시 완료")
    except subprocess.CalledProcessError:
        print("\n[!!] git 커밋 실패")

if __name__ == "__main__":
    main()