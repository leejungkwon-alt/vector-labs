#!/usr/bin/env python3
"""
scripts/deepen_personalization.py

프리미엄 콘텐츠(love, career, wealth)에 다차원 개인화 엔진 적용.
사주의 아키타입 + 에너지 강도 + 주 오행 + 십성 모드를 조합하여
유저마다 완전히 다른 맞춤형 문단(personalized_insight)을 동적 생성합니다.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

def patch_file(rel_path, old, new, label, is_frontend=True):
    base = FRONTEND if is_frontend else ROOT
    p = base / rel_path
    if not p.exists():
        print(f"  [!!] {p} 없음")
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
    print("  다차원 개인화 엔진(Dynamic Personalization) 적용")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. content_writer.py 에 동적 개인화 텍스트 생성 로직 추가
    # ---------------------------------------------------------
    old_premium_func = '''def write_premium_section(profile: dict, lang: str, section_name: str) -> dict | None:
    try:
        pack = load_pack(lang, section_name)
    except KeyError:
        return None
        
    arch = profile["archetype"]["key"]
    content_map = pack.get("CONTENT", {})
    content = content_map.get(arch, {"headline": "Premium feature", "body": "Analyze your chart deeply."})
    
    return {
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
    }'''

    new_premium_func = '''def write_premium_section(profile: dict, lang: str, section_name: str) -> dict | None:
    try:
        pack = load_pack(lang, section_name)
    except KeyError:
        return None
        
    arch = profile["archetype"]["key"]
    content_map = pack.get("CONTENT", {})
    content = content_map.get(arch, {"headline": "Premium feature", "body": "Analyze your chart deeply."})
    
    # ----------------------------------------------------
    # 다차원 개인화 (Dynamic Personalization)
    # ----------------------------------------------------
    # 1. 에너지 강도 (신강/중화/신약)
    intensity = profile["archetype"].get("intensity", "BALANCED_CORE")
    # 2. 주 오행 (Dominant Element)
    dom_elems = profile.get("energy_signature", {}).get("dominant", [])
    dom_elem = dom_elems[0] if dom_elems else "BALANCED"
    # 3. 행동/재물/관계 모드
    work_mode = profile.get("work_mode", "THE_GENERALIST")
    money_mode = profile.get("money_mode", "THE_FLOW")
    bond_mode = profile.get("bond_mode", "THE_EMPATH")
    
    # 한글 개인화 문장 조합
    p_text_ko = "\\n\\n[당신의 사주를 깊이 읽은 맞춤 인사이트]\\n"
    
    # 강도별 수식어
    if intensity == "SELF_SOURCED":
        p_text_ko += "당신의 강한 '자기충전형' 에너지가 이 성향을 더욱 뚜렷하고 주도적으로 만듭니다. "
    elif intensity == "ENVIRONMENT_TUNED":
        p_text_ko += "당신의 '환경반응형' 기질로 인해, 주변 환경과 만나는 사람에 따라 이 성향이 깊게 발현됩니다. "
    else:
        p_text_ko += "당신의 균형 잡힌 '중심' 에너지가 이 성향을 안정적이고 조화롭게 이끕니다. "
        
    # 오행별 수식어
    elem_map_ko = {
        "GROWTH": "여기에 성장(木)의 기운이 더해져, 끊임없이 확장하고 새로운 방향을 개척하려는 욕구가 강하게 작용합니다.",
        "SPARK": "여기에 불꽃(火)의 뜨거운 기운이 더해져, 열정적이고 즉각적인 에너지로 이 성향을 밀어붙입니다.",
        "GROUND": "여기에 대지(土)의 안정적인 기운이 더해져, 신중하고 듬직하게 기반을 다지는 방향으로 발현됩니다.",
        "EDGE": "여기에 예리함(金)의 기운이 더해져, 명확한 기준과 날카로운 결단력으로 이 상황을 정리해 나갑니다.",
        "FLOW": "여기에 흐름(水)의 유연한 기운이 더해져, 상황에 맞춰 지혜롭고 유연하게 대처하는 힘이 생깁니다.",
    }
    p_text_ko += elem_map_ko.get(dom_elem, "")
    
    # 십성(모드)별 수식어 (섹션에 맞게 다르게 적용)
    if section_name == "love":
        mode_map = {"THE_TWIN": "특히 '동반자' 모드가 강해, 연인을 평생의 동료이자 동등한 파트너로 대우합니다.", "THE_RIVAL": "특히 '경쟁자' 모드가 강해, 서로 자극을 주고받으며 함께 성장하는 관계를 원합니다.", "THE_ALLY": "특히 '조력자' 모드가 강해, 한 번 맺은 인연을 끝까지 책임지고 헌신합니다."}
        p_text_ko += mode_map.get(bond_mode, "")
    elif section_name == "career":
        mode_map = {"THE_CREATOR": "특히 '창작자' 모드가 강해, 기존의 틀을 깨고 나만의 독창적인 결과물을 만들어내는 일에서 빛납니다.", "THE_OFFICER": "특히 '원칙주의자' 모드가 강해, 체계가 잡힌 조직에서 신뢰받는 핵심 인재로 성장합니다.", "THE_CHALLENGER": "특히 '도전자' 모드가 강해, 문제를 해결하고 위기를 돌파하는 리더의 기질이 있습니다."}
        p_text_ko += mode_map.get(work_mode, "")
    elif section_name == "wealth":
        mode_map = {"THE_OPERATOR": "특히 '운영자' 모드가 강해, 남들이 보지 못하는 기회를 포착해 과감하게 자산을 불려 나갑니다.", "THE_STEWARD": "특히 '관리자' 모드가 강해, 한 번 모은 자산을 안전하게 지키고 복리로 불려나가는 능력이 탁월합니다.", "THE_FLOW": "특히 '흐름' 모드가 강해, 얽매이지 않고 유연하게 돈의 흐름을 타고 자연스럽게 부를 끌어당깁니다."}
        p_text_ko += mode_map.get(money_mode, "")

    # 영어 (간단 버전)
    p_text_en = "\\n\\n[Personalized Insight]\\nBased on your chart, your energy is highly self-sourced and balanced with specific elements. " \\
                "This trait manifests uniquely in your life, aligning with your innate drive and specific mode."
    
    # 본문에 개인화 문장 병합
    final_body = content.get("body", "")
    if lang == "ko":
        final_body += p_text_ko
    else:
        final_body += p_text_en
    
    return {
        "id": section_name,
        "title": pack.get("SECTION_TITLE", section_name.title()),
        "mode": arch,
        "headline": content.get("headline", ""),
        "body": final_body,
        "patterns": content.get("patterns", []),
        "compatibility": {
            "best_match": content.get("best_match", []),
            "best_reason": content.get("best_reason", ""),
            "challenging_match": content.get("challenging_match", []),
            "challenging_reason": content.get("challenging_reason", ""),
        },
        "actions": content.get("actions", []),
        "red_flags": content.get("red_flags", []),
    }'''

    patch_file(
        "app/services/content_writer.py",
        old_premium_func,
        new_premium_func,
        "content_writer.py 다차원 개인화 엔진 적용",
        is_frontend=False
    )

    print("\n[git] add → commit → push")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "feat(personalization): dynamic content generation based on multi-dimensional saju data (intensity + element + ten gods)"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
        print("\n[done] 커밋 + 푸시 완료")
    except subprocess.CalledProcessError:
        print("\n[!!] git 커밋 실패")

if __name__ == "__main__":
    main()