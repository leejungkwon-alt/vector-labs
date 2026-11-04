import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = f".bak_phase2_3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 1. poems.json 업데이트 (poet, commentary 추가)
def update_poems():
    path = ROOT / "data" / "poems.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    
    commentaries_ko = {
        "same": "이 시조는 같은 기운이 서로를 마주했을 때의 공명을 노래합니다. 두 힘이 부딪히지 않고 하나의 결로 흐르는 모습이 인상적입니다.",
        "generates_me": "나를 살찌우는 기운이 바깥에서 들어오는 상황을 그립니다. 보이지 않는 곳에서 나를 돕는 힘에 대한 감사를 담고 있습니다.",
        "i_generate": "내 안의 기운이 세상으로 뻗어 나가 꽃피는 과정을 노래합니다. 창조와 표현의 기쁨이 시조의 가락에 묻어납니다.",
        "i_control": "내가 가진 힘으로 세상을 다스리고 정돈하는 모습을 보여줍니다. 중심을 잡고 나아가는 단단한 의지가 느껴집니다.",
        "controls_me": "바깥의 강한 힘이 나를 누르고 다듬는 상황을 노래합니다. 고통스럽지만 결국 나를 단단하게 만드는 성장의 과정을 담고 있습니다."
    }
    commentaries_en = {
        "same": "This sijo sings of the resonance when two forces of the same element meet. They flow as one grain without clashing.",
        "generates_me": "It depicts a nourishing force entering from the outside. The poem carries gratitude for the unseen power that supports you.",
        "i_generate": "Your inner energy reaches out into the world and blossoms. The joy of creation and expression flows through the rhythm.",
        "i_control": "It shows your power governing and organizing the world around you. A firm will to hold your center is felt.",
        "controls_me": "An external force presses and refines you. It captures the painful yet ultimately strengthening process of growth."
    }

    for poem in data.get("poems", []):
        rel = poem.get("relation", "")
        # 작가 정보 추가 (현재는 미상으로 처리)
        poem["poet"] = "미상 (Anonymous)"
        
        if "translations" not in poem:
            poem["translations"] = {}
        
        for lang in ["ko", "en"]:
            if lang not in poem["translations"]:
                poem["translations"][lang] = {}
        
        # 해설(commentary) 추가
        if "commentary" not in poem["translations"]["ko"]:
            poem["translations"]["ko"]["commentary"] = commentaries_ko.get(rel, "")
        if "commentary" not in poem["translations"]["en"]:
            poem["translations"]["en"]["commentary"] = commentaries_en.get(rel, "")

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] data/poems.json 업데이트 (작가, 해설 추가)")

# 2. content_writer.py 업데이트
def update_content_writer():
    path = ROOT / "app" / "services" / "content_writer.py"
    text = path.read_text(encoding="utf-8")
    
    old_ret = '''        "title": title,
        "sijo_ko": match.get("sijo_ko", ""),
        "romanization": match.get("romanization", ""),
        "interpretation": tr.get("interpretation", ""),'''
    new_ret = '''        "title": title,
        "poet": match.get("poet", "미상"),
        "sijo_ko": match.get("sijo_ko", ""),
        "romanization": match.get("romanization", ""),
        "commentary": tr.get("commentary", ""),
        "interpretation": tr.get("interpretation", ""),'''
    
    if old_ret in text and '"poet"' not in text:
        text = text.replace(old_ret, new_ret)
        path.write_text(text, encoding="utf-8")
        print("[OK] app/services/content_writer.py 업데이트 (poet, commentary 반환)")
    else:
        print("[SKIP] content_writer.py 이미 업데이트됨")

# 3. types.ts 업데이트
def update_types():
    path = ROOT / "frontend" / "types.ts"
    text = path.read_text(encoding="utf-8")
    old_type = '''  title: string;
  sijo_ko: string;
  romanization: string;
  interpretation: string;'''
    new_type = '''  title: string;
  poet?: string;
  sijo_ko: string;
  romanization: string;
  commentary?: string;
  interpretation: string;'''
    
    if "poet?: string;" not in text:
        text = text.replace(old_type, new_type)
        path.write_text(text, encoding="utf-8")
        print("[OK] frontend/types.ts 업데이트 (PoemCard 타입 확장)")

# 4. PoemFlipCard.tsx 업데이트 (UI 반영)
def update_flipcard():
    path = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
    text = path.read_text(encoding="utf-8")
    
    # 카드 높이 증가 (텍스트가 많아지므로)
    text = text.replace("const FACE_HEIGHT = 480;", "const FACE_HEIGHT = 560;")
    
    old_back = '''            <Text style={styles.title}>{poem.title}</Text>
            <Text style={styles.romanization}>{poem.romanization}</Text>
            <View style={styles.divider} />
            <Text style={styles.interpretation}>{poem.interpretation}</Text>'''
    new_back = '''            <Text style={styles.title}>{poem.title}</Text>
            {poem.poet && <Text style={styles.poet}>- {poem.poet} -</Text>}
            <Text style={styles.romanization}>{poem.romanization}</Text>
            <View style={styles.divider} />
            {poem.commentary ? <Text style={styles.commentary}>{poem.commentary}</Text> : null}
            <View style={styles.divider} />
            <Text style={styles.interpretation}>{poem.interpretation}</Text>'''
            
    if old_back in text:
        text = text.replace(old_back, new_back)
        
    old_styles = '''  title: { fontSize: 22, fontWeight: "600", textAlign: "center", color: C.text, marginBottom: 8 },
  romanization:'''
    new_styles = '''  title: { fontSize: 22, fontWeight: "600", textAlign: "center", color: C.text, marginBottom: 4 },
  poet: { fontSize: 14, textAlign: "center", color: C.accent, marginBottom: 8, fontStyle: "italic" },
  commentary: { fontSize: 14, lineHeight: 22, color: C.text, fontStyle: "italic", marginBottom: 8 },
  romanization:'''
    if old_styles in text:
        text = text.replace(old_styles, new_styles)
        
    path.write_text(text, encoding="utf-8")
    print("[OK] frontend/src/components/poem/PoemFlipCard.tsx 업데이트 (시인 및 해설 렌더링)")

if __name__ == "__main__":
    update_poems()
    update_content_writer()
    update_types()
    update_flipcard()