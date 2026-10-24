#!/usr/bin/env python3
"""
scripts/fix_core_hanja.py
CoreSection.tsx에서 한자(pillar_name_traditional)가 노출되는 구문을 제거합니다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "frontend" / "src" / "components" / "sections" / "CoreSection.tsx"

def main():
    if not FILE.exists():
        print("❌ CoreSection.tsx 파일을 찾을 수 없습니다.")
        return

    src = FILE.read_text(encoding="utf-8")

    old_block = """      {section.pillar_name && (
        <Text style={[ss.metaText, { marginBottom: 8 }]}>
          {section.pillar_name}
          {section.pillar_name_traditional && (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>
              {" "}({section.pillar_name_traditional})
            </Text>
          )}
        </Text>
      )}"""

    new_block = """      {section.pillar_name && (
        <Text style={[ss.metaText, { marginBottom: 8 }]}>
          {section.pillar_name}
        </Text>
      )}"""

    if old_block in src:
        src = src.replace(old_block, new_block)
        FILE.write_text(src, encoding="utf-8")
        print("✅ CoreSection.tsx 한자 노출 제거 완료!")
    else:
        # 혹시 이전에 다른 스크립트로 인해 코드가 살짝 다를 수 있으므로 fallback 처리
        if "section.pillar_name_traditional" in src:
            # 정규식으로 <Text> 안의 traditional 출력 부분만 삭제
            import re
            src = re.sub(r'\{section\.pillar_name_traditional\s*&&\s*\(\s*<Text[^>]*>\s*\{"\s*"\}\(\{section\.pillar_name_traditional\}\)\s*</Text>\s*\)\}', '', src)
            FILE.write_text(src, encoding="utf-8")
            print("✅ CoreSection.tsx 한자 노출 제거 완료 (Fallback 패치 적용)!")
        else:
            print("⚠️ 이미 패치되었거나, 패턴을 찾을 수 없습니다. 코드를 확인해주세요.")

if __name__ == "__main__":
    main()