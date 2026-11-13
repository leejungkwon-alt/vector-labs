import json

print("🚀 app.json의 누락된 쉼표를 수정합니다...\n")

app_json_path = "app.json"
with open(app_json_path, "r", encoding="utf-8") as f:
    content = f.read()

# 누락된 쉼표 수정
content = content.replace('"expo-font"\n      "react-native-iap"', '"expo-font",\n      "react-native-iap"')

with open(app_json_path, "w", encoding="utf-8") as f:
    f.write(content)

# 수정 후 JSON 유효성 검사
try:
    with open(app_json_path, "r", encoding="utf-8") as f:
        json.load(f)
    print("✅ app.json 수정 완료! (JSON 형식 정상)")
except json.JSONDecodeError as e:
    print(f"❌ 여전히 JSON 에러가 있습니다: {e}")
