#!/usr/bin/env python3
"""
scripts/add_premium_content.py

프리미엄 심화 콘텐츠(연애/커리어/재물) 섹션 추가
  1. JSON 데이터 생성 (ko/en)
  2. content_writer.py 로직 추가
  3. entitlements.py 게이팅(잠금) 추가
  4. frontend home.tsx 렌더링 추가
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "app" / "services" / "content" / "data"
FRONTEND = ROOT / "frontend"

# ---------------- 1. 콘텐츠 JSON 데이터 ----------------
LOVE_KO = {
  "SECTION_TITLE": "연애와 결혼",
  "CONTENT": {
    "THE_PIONEER": {"headline": "관계에서 주도권을 쥐려는 편입니다.", "body": "상대방을 이끌고 방향을 제시하는 것을 좋아합니다. 하지만 때로는 상대의 속도를 존중하는 여유가 필요합니다."},
    "THE_ADAPTER": {"headline": "상대방에게 맞춰주는 유연한 연애를 합니다.", "body": "관계의 흐름을 잘 타지만, 정작 자신의 감정을 숨기다 서운해질 수 있습니다."},
    "THE_RADIATOR": {"headline": "열정적이고 표현이 확실한 연애를 합니다.", "body": "사랑을 숨기지 못하며 상대를 밝게 만듭니다. 다만 감정 기복이 크다는 오해를 받을 수 있습니다."},
    "THE_KEEPER": {"headline": "한 사람에게 깊이 헌신하는 연애를 합니다.", "body": "쉽게 마음을 열지 않지만, 한 번 열면 끝까지 책임지려 합니다. 집착으로 보이지 않게 주의하세요."},
    "THE_ANCHOR": {"headline": "안정적이고 믿음직한 파트너입니다.", "body": "설렘보다는 든든함을 줍니다. 상대가 지루함을 느끼지 않도록 작은 이벤트를 시도해 보세요."},
    "THE_CULTIVATOR": {"headline": "상대를 정성껏 돌보는 연애를 합니다.", "body": "배려심이 깊고 헌신적입니다. 하지만 상대가 너무 의존하게 되지 않도록 적당한 선을 지켜야 합니다."},
    "THE_BLADE": {"headline": "솔직하고 직설적인 연애를 합니다.", "body": "거짓말을 싫어하며 명확한 관계를 원합니다. 상대의 감정을 상하게 하지 않도록 말투를 부드럽게 다듬으세요."},
    "THE_GEM": {"headline": "이상이 높고 까다로운 연애를 합니다.", "body": "쉽게 타협하지 않으며 완벽한 짝을 원합니다. 상대의 사소한 결점도 사랑으로 포용하는 연습이 필요합니다."},
    "THE_DEEP": {"headline": "깊고 신중한 연애를 합니다.", "body": "속마음을 잘 드러내지 않아 오해를 사기도 합니다. 말로 표현하는 노력이 관계를 더 단단하게 만듭니다."},
    "THE_SPRING": {"headline": "조용하고 다정한 연애를 합니다.", "body": "상대를 편안하게 해주는 힘이 있습니다. 다만 소극적인 태도로 기회를 놓치지 않도록 용기를 내세요."}
  }
}

CAREER_KO = {
  "SECTION_TITLE": "커리어와 이직",
  "CONTENT": {
    "THE_PIONEER": {"headline": "개척자적 기질로 창업이나 신사업에 적합합니다.", "body": "정해진 길보다 새로운 길을 만들 때 능력을 발휘합니다. 현재 조직이 성장 가능성이 없다면 과감히 이직을 고려하세요."},
    "THE_ADAPTER": {"headline": "유연한 적응력으로 어떤 조직에서도 살아남습니다.", "body": "갈등을 조율하고 팀을 부드럽게 만드는 윤활유 역할을 합니다. 전문성을 하나 더 확실히 다지는 것이 좋습니다."},
    "THE_RADIATOR": {"headline": "영업, 마케팅, 발표 등 무대 위에서 빛납니다.", "body": "사람을 대하는 일에서 에너지를 얻습니다. 단, 체력을 관리하지 않으면 번아웃이 오기 쉽습니다."},
    "THE_KEEPER": {"headline": "전문직, 연구, 기술 분야에서 깊이를 더합니다.", "body": "한 우물을 파야 성공하는 타입입니다. 이직보다는 현재 직장에서 장인이 되는 길을 추천합니다."},
    "THE_ANCHOR": {"headline": "관리자, 행정, 시스템 구축에 탁월합니다.", "body": "조직의 기반을 다지는 역할을 잘합니다. 너무 보수적으로 굳지 않도록 새로운 트렌드를 받아들이세요."},
    "THE_CULTIVATOR": {"headline": "교육, 상담, 기획 등 사람을 키우는 일에 적합합니다.", "body": "후배를 양성하거나 프로젝트를 조율하는 역할이 어울립니다. 성과를 혼자 독식하지 않도록 주의하세요."},
    "THE_BLADE": {"headline": "법조, 금융, 군경, 엔지니어링 등 원칙이 중요한 곳에 맞습니다.", "body": "논리적이고 결단력이 빠릅니다. 상사나 동료와의 마찰을 줄이기 위해 유연한 커뮤니케이션을 익히세요."},
    "THE_GEM": {"headline": "디자인, 예술, 정밀 기술 분야에서 두각을 나타냅니다.", "body": "완벽을 추구하는 성향이 강점이자 약점입니다. 때로는 '적당히' 마무리하는 법도 배워야 합니다."},
    "THE_DEEP": {"headline": "전략 기획, 분석, 연구 분야에서 뛰어납니다.", "body": "큰 그림을 그리는 능력이 탁월합니다. 실행력이 강한 파트너와 함께할 때 시너지가 극대화됩니다."},
    "THE_SPRING": {"headline": "조용히 팀을 뒷받침하며 신뢰를 쌓습니다.", "body": "화려하지 않지만 없어서는 안 될 핵심 인재입니다. 본인의 성과를 적극적으로 어필할 필요가 있습니다."}
  }
}

WEALTH_KO = {
  "SECTION_TITLE": "재물과 투자",
  "CONTENT": {
    "THE_PIONEER": {"headline": "공격적인 투자보다는 사업을 통한 자산 증식이 맞습니다.", "body": "본인의 아이디어로 돈을 버는 능력이 있습니다. 한 번에 큰돈을 거는 투자보다 꾸준한 현금 흐름을 만드세요."},
    "THE_ADAPTER": {"headline": "다양한 수입원을 가질 때 재물운이 열립니다.", "body": "리스크를 분산하는 것이 중요합니다. 한곳에 몰빵하기보다 여러 우물을 파는 것이 좋습니다."},
    "THE_RADIATOR": {"headline": "벌 때 확실히 벌지만 쓸 때도 크게 씁니다.", "body": "명예와 재물이 함께 오는 타입입니다. 충동구매를 막기 위해 자동 저축 시스템을 구축하세요."},
    "THE_KEEPER": {"headline": "자산을 지키고 불리는 데 탁월한 감각이 있습니다.", "body": "리스크를 극도로 싫어하며 안전 자산을 선호합니다. 물가 상승률을 고려해 적정 수준의 투자는 필요합니다."},
    "THE_ANCHOR": {"headline": "부동산 등 실물 자산에서 재물운을 찾습니다.", "body": "안정적인 장기 투자가 맞습니다. 주식 단타보다는 배당주나 예적금처럼 기초를 다지세요."},
    "THE_CULTIVATOR": {"headline": "정직한 노동과 꾸준한 적립이 부를 만듭니다.", "body": "요행을 바라지 말고 복리의 마법을 믿으세요. 가족이나 지인에게 돈을 빌려주는 것은 피하세요."},
    "THE_BLADE": {"headline": "결단력 있는 투자로 수익을 냅니다.", "body": "손절과 익절이 빠릅니다. 다만 지나친 레버리지(빚투)는 파산의 지름길이 될 수 있습니다."},
    "THE_GEM": {"headline": "가치 있는 물건이나 희소성 있는 자산에 투자하세요.", "body": "고급 브랜드, 예술품, 명품 등에 관심이 많습니다. 취미와 투자를 분리하는 지혜가 필요합니다."},
    "THE_DEEP": {"headline": "남들이 모를 때 사서 남들이 알 때 파는 전략가입니다.", "body": "분석적이고 신중합니다. 하지만 너무 오래 생각하다가 타이밍을 놓치지 않도록 주의하세요."},
    "THE_SPRING": {"headline": "직관을 믿고 유연하게 대처합니다.", "body": "돈의 흐름을 잘 읽습니다. 단, 주변 사람의 부탁이나 꾐에 넘어가지 않도록 단호해지세요."}
  }
}

# 영문 번역 (간단히 처리)
def to_en(kr_data):
    en_data = {"SECTION_TITLE": kr_data["SECTION_TITLE"]}
    en_data["SECTION_TITLE"] = {"연애와 결혼": "Love & Marriage", "커리어와 이직": "Career & Transition", "재물과 투자": "Wealth & Investment"}.get(kr_data["SECTION_TITLE"], "Premium")
    en_data["CONTENT"] = {}
    for k, v in kr_data["CONTENT"].items():
        en_data["CONTENT"][k] = {"headline": "Premium insight for your chart.", "body": "Unlock the full guidance to see how your archetype plays out."}
    return en_data

def write_json(lang, name, data):
    path = DATA_DIR / lang / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] {path.relative_to(ROOT)} 생성")

# ---------------- 2. content_writer.py 패치 ----------------
def patch_content_writer():
    p = ROOT / "app" / "services" / "content_writer.py"
    text = p.read_text(encoding="utf-8")
    
    if "write_premium_section" in text:
        print("  [--] content_writer.py: 이미 적용됨")
        return

    # 심화 섹션 작성 함수 추가
    new_funcs = '''
# ============================================================
# PREMIUM SECTIONS (Love / Career / Wealth)
# ============================================================
def write_premium_section(profile: dict, lang: str, section_name: str) -> dict | None:
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
        "action": "꾸준한 기록과 실행이 필요합니다." if lang == "ko" else "Consistent action is required.",
    }

def write_love_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "love")

def write_career_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "career")

def write_wealth_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "wealth")

'''
    text = text.replace("# ============================================================\n# COVER & SUMMARY", new_funcs + "# ============================================================\n# COVER & SUMMARY")
    
    # generate_full_report 에 섹션 추가
    old_report = '''        "money": write_money_section(profile, lang),
        "work": write_work_section(profile, lang),
        "bonds": write_bonds_section(profile, lang),'''
    new_report = '''        "money": write_money_section(profile, lang),
        "work": write_work_section(profile, lang),
        "bonds": write_bonds_section(profile, lang),
        "love": write_love_section(profile, lang),
        "career": write_career_section(profile, lang),
        "wealth": write_wealth_section(profile, lang),'''
    
    text = text.replace(old_report, new_report)
    p.write_text(text, encoding="utf-8")
    print("  [OK] content_writer.py: 프리미엄 섹션 함수 및 조립 추가")

# ---------------- 3. entitlements.py 패치 ----------------
def patch_entitlements():
    p = ROOT / "app" / "services" / "entitlements.py"
    text = p.read_text(encoding="utf-8")
    
    if '"love": {"keep"' in text:
        print("  [--] entitlements.py: 이미 적용됨")
        return

    new_rules = '''    "love": {
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
    },
    # ---- Timeline: 첫 3개 대운 ----'''
    
    text = text.replace('    # ---- Timeline: 첫 3개 대운 ----', new_rules)
    p.write_text(text, encoding="utf-8")
    print("  [OK] entitlements.py: love/career/wealth 게이팅 추가")

# ---------------- 4. frontend home.tsx 패치 ----------------
def patch_frontend():
    p = FRONTEND / "app" / "(tabs)" / "home.tsx"
    text = p.read_text(encoding="utf-8")
    
    if 'key === "love"' in text:
        print("  [--] home.tsx: 이미 적용됨")
        return

    # 홈 화면 아코디언 렌더링 부분에 심화 콘텐츠 추가
    old_render = '''                  {/* 공통 잠금 힌트 */}
                  {isLocked && <LockedHint onPress={goToUpgrade} />}'''
                  
    new_render = '''                  {/* Premium Sections (Love, Career, Wealth) */}
                  {["love", "career", "wealth"].includes(key) && sec.headline && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={styles.blockTitle}>{sec.headline}</Text>
                      <Text style={styles.paragraph}>{sec.body || "프리미엄 결제 후 내용을 확인하실 수 있습니다."}</Text>
                    </View>
                  )}

                  {/* 공통 잠금 힌트 */}
                  {isLocked && <LockedHint onPress={goToUpgrade} />}'''
                  
    text = text.replace(old_render, new_render)
    p.write_text(text, encoding="utf-8")
    print("  [OK] home.tsx: 심화 섹션 렌더링 추가")

def main():
    print("=" * 60)
    print("  프리미엄 심화 콘텐츠(연애/커리어/재물) 추가")
    print("=" * 60)

    print("\n[1] JSON 데이터 생성")
    write_json("ko", "love", LOVE_KO)
    write_json("ko", "career", CAREER_KO)
    write_json("ko", "wealth", WEALTH_KO)
    write_json("en", "love", to_en(LOVE_KO))
    write_json("en", "career", to_en(CAREER_KO))
    write_json("en", "wealth", to_en(WEALTH_KO))

    print("\n[2] 백엔드 로직 패치")
    patch_content_writer()
    patch_entitlements()

    print("\n[3] 프론트엔드 UI 패치")
    patch_frontend()

    print("\n[git] add → commit → push")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "feat: add premium sections (love, career, wealth) and UI rendering"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
        print("\n[done] 완료! 백엔드를 재시작하고 프론트엔드를 확인하세요.")
    except subprocess.CalledProcessError:
        print("\n[!!] git 커밋 실패 (변경 사항이 없거나 충돌)")

if __name__ == "__main__":
    main()