import json

print("🚀 app.json에서 react-native-iap 플러그인을 제거합니다...\n")

app_json_path = "app.json"
with open(app_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# plugins 배열에서 "react-native-iap" 제거
expo = data.get("expo", {})
plugins = expo.get("plugins", [])
if "react-native-iap" in plugins:
    plugins.remove("react-native-iap")
    expo["plugins"] = plugins
    data["expo"] = expo
    with open(app_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ app.json에서 react-native-iap 플러그인 제거 완료!")
else:
    print("ℹ️ plugins 배열에 react-native-iap가 없습니다.")

# JSON 유효성 검사
try:
    with open(app_json_path, "r", encoding="utf-8") as f:
        json.load(f)
    print("✅ app.json JSON 형식 정상!")
except json.JSONDecodeError as e:
    print(f"❌ JSON 에러: {e}")
