#!/usr/bin/env python3
"""
화면에 노출되는 아키타입 이름("태양")과 한자("丙寅")를
60일주 고유 이름("숲의 불꽃")으로 전면 교체합니다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CW = ROOT / "app" / "services" / "content_writer.py"
CORE_SECTION = ROOT / "frontend" / "src" / "components" / "sections" / "CoreSection.tsx"

def fix_backend():
    if not CW.exists():
        print("❌ content_writer.py를 찾을 수 없습니다.")
        return
        
    src = CW.read_text(encoding="utf-8")

    # 1. write_core_section: "archetype.name"을 "태양" 대신 "바위 위의 태양"으로 변경
    old_core = """    if content is None:
        intensities = arch.get("intensities") or {}
        content = intensities.get(intensity_key, default_intensity)

    # 2) intensity overlay(3개, 모든 일주 공통) 병합"""
    
    new_core = """    if content is None:
        intensities = arch.get("intensities") or {}
        content = intensities.get(intensity_key, default_intensity)

    display_name = content.get("name") if content_source == "pillar" else arch["name"]

    # 2) intensity overlay(3개, 모든 일주 공통) 병합"""
    src = src.replace(old_core, new_core)

    old_arch = """        "archetype": {
            "key": arch_key,
            "name": arch["name"],
            "tagline": content.get("tagline") or arch["tagline"],"""
            
    new_arch = """        "archetype": {
            "key": arch_key,
            "name": display_name,
            "tagline": content.get("tagline") or arch["tagline"],"""
    src = src.replace(old_arch, new_arch)

    # 2. write_chart_section: "당신의 네 가지 얼굴"의 "태양"을 각 일주별 고유 이름으로 변경
    old_chart = """        stem = pillar[0]
        arch_key = _STEM_TO_ARCH_KEY.get(stem, "UNKNOWN")
        elem_sig = _STEM_TO_ELEM_SIG.get(stem, "")
        arch_meta = arch_content.get(arch_key, {})
        meta = layer_meta.get(pos, {})
        arch_name = arch_meta.get("name", arch_key)
        narrative = pos_templates.get(pos, "{archetype}").format(archetype=arch_name)"""
    
    new_chart = """        stem = pillar[0]
        arch_key = _STEM_TO_ARCH_KEY.get(stem, "UNKNOWN")
        elem_sig = _STEM_TO_ELEM_SIG.get(stem, "")
        arch_meta = arch_content.get(arch_key, {})
        meta = layer_meta.get(pos, {})
        arch_name = arch_meta.get("name", arch_key)
        
        specific_name = arch_name
        if len(pillar) == 2:
            try:
                p_data = load_pack(lang, f"core_pillars/{pillar}")
                if p_data and p_data.get("name"):
                    specific_name = p_data["name"]
            except KeyError:
                pass

        narrative = pos_templates.get(pos, "{archetype}").format(archetype=specific_name)"""
    src = src.replace(old_chart, new_chart)

    old_append = """            "archetype": arch_name,"""
    new_append = """            "archetype": specific_name,"""
    src = src.replace(old_append, new_append)

    CW.write_text(src, encoding="utf-8")
    print("✅ 백엔드 content_writer.py 패치 완료 (아키타입 이름 교체)")

def fix_frontend():
    if not CORE_SECTION.exists():
        print("❌ CoreSection.tsx를 찾을 수 없습니다.")
        return
        
    src = CORE_SECTION.read_text(encoding="utf-8")
    
    # 3. CoreSection.tsx: "병인(丙寅)" 같은 한자 노출 부분 제거
    old_tsx = """      {section.pillar_name && (
        <Text style={[ss.metaText, { marginBottom: 8 }]}>
          {section.pillar_name}
          {section.pillar_name_traditional && (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>
              {" "}({section.pillar_name_traditional})
            </Text>
          )}
        </Text>
      )}"""
    
    new_tsx = """      {section.pillar_name && (
        <Text style={[ss.metaText, { marginBottom: 8 }]}>
          {section.pillar_name}
        </Text>
      )}"""
    
    if old_tsx in src:
        src = src.replace(old_tsx, new_tsx)
        CORE_SECTION.write_text(src, encoding="utf-8")
        print("✅ 프론트엔드 CoreSection.tsx 패치 완료 (한자 제거)")
    else:
        print("⚠️ CoreSection.tsx 패턴을 찾지 못했습니다 (이미 적용되었거나 코드가 다름).")

if __name__ == "__main__":
    print("=== 화면 노출 이름(태양, 丙寅) 교체 스크립트 ===")
    fix_backend()
    fix_frontend()
    print("\n패치 완료! 백엔드를 재시작하고, 다시 클라우드에 배포해야 반영됩니다.")