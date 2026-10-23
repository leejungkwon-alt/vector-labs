import os
from pathlib import Path

# 🎯 "고등학생 수준"의 명확하고 논리적인 톤으로 번역하는 사전
REPLACEMENTS = {
    # --- [1] 추상적인 문장 번역 ---
    "관계에서는 '동반자', 일에서는 '도전자', 돈은 '흐름'처럼 다뤄요.": "당신은 관계에서는 서로 의지하는 '동반자'로, 일할 때는 목표를 향해 나아가는 '도전자'로 살아갑니다. 돈에 대해서는 집착하기보다는 자연스럽게 흘러가는 대로 받아들이는 편이에요.",
    "이 셋은 관계의 '함께하는 시간'과 돈의 '혼자만의 공간' 사이에서 흔들리고 있어요.": "당신은 사람들과 어울려 시간을 보내는 것과, 혼자만의 조용한 공간에서 쉬는 것 사이에서 종종 갈등을 겪습니다.",
    "여기에 돈의 '즉흥적 흐름' 쪽으로 마음이 기울어요.": "특히 돈과 관련해서는 계획을 세우기보다, 그때그때 끌리는 대로 즉흥적으로 쓰고 싶은 마음이 들 때가 많아요.",
    "그래서 당신은 '혼자 몰입하는 시간'과 '팀과 리듬을 맞추는 시간'이 둘 다 있어야 오래 갈 수 있어요. 둘 중 하나가 사라지면 금방 지쳐요.": "그래서 당신에게는 '온전히 혼자 집중하는 시간'과 '다른 사람들과 호흡을 맞추는 시간'이 둘 다 꼭 필요합니다. 이 둘 중 하나라도 부족하면 쉽게 지치거나 무기력해질 수 있어요.",

    # --- [2] 화면 캡처에 있던 문구 및 한자 ---
    "당신의 3개 모드가 만나는 지점": "당신의 숨겨진 세 가지 얼굴",
    "3개 모드가 만나는 지점": "숨겨진 세 가지 얼굴",
    "무인 대운(戊寅)": "새로운 도전의 시기",
    "戊寅": "새로운 도전의 시기", 
    "戊戌": "성장과 결실의 달",
    "현대 대운": "현재 인생의 큰 흐름",
    "대운": "인생의 큰 흐름",
    "소운": "작은 흐름",

    # --- [3] 기타 사주 전문용어 ---
    "세운(歲運)": "올해의 운세", "세운": "올해의 운세",
    "월운(月運)": "이번 달의 운세", "월운": "이번 달의 운세",
    "일진(日辰)": "오늘의 기운", "일진": "오늘의 기운",
    "천간(天干)": "타고난 기질", "천간": "타고난 기질",
    "지지(地支)": "환경적 특성", "지지": "환경적 특성",
    "십신(十神)": "관계와 역할", "십신": "관계와 역할",
    "용신(用神)": "나에게 힘이 되는 요소", "용신": "나에게 힘이 되는 요소",
    "희신(喜神)": "나를 도와주는 요소", "희신": "나를 도와주는 요소",
    "기신(忌神)": "주의해야 할 요소", "기신": "주의해야 할 요소",
    "합(合)": "조화", "충(沖)": "갈등과 변화", "형(刑)": "내적 갈등", "파(破)": "계획의 차질",
}

# 🔍 검사할 파일 확장자
TARGET_EXTENSIONS = {'.json', '.py', '.tsx', '.ts', '.js', '.jsx'}

# 🚫 무시할 폴더
IGNORE_DIRS = {'node_modules', '.git', 'venv', '__pycache__', 'backups', 'build', '.expo', 'tests'}

def process_files():
    print("🚀 앱 전체 텍스트 자동 번역을 시작합니다...\n")
    count = 0
    
    # 긴 문장 우선 치환
    sorted_keys = sorted(REPLACEMENTS.keys(), key=len, reverse=True)

    # 스크립트 자기 자신의 파일명
    current_script_name = os.path.basename(__file__)

    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            path = Path(root) / file
            
            # 🔥 자기 자신(스크립트)은 번역하지 않도록 제외
            if file == current_script_name:
                continue
                
            if path.suffix not in TARGET_EXTENSIONS:
                continue

            try:
                content = path.read_text(encoding='utf-8')
                original_content = content

                for old_word in sorted_keys:
                    content = content.replace(old_word, REPLACEMENTS[old_word])

                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    print(f"✅ 수정 완료: {path}")
                    count += 1
            except Exception as e:
                print(f"⚠️ 읽기 실패 (건너뜀): {path} - {e}")

    print(f"\n🎉 총 {count}개의 파일이 성공적으로 수정되었습니다!")

if __name__ == "__main__":
    process_files()