import os
import re
import shutil

print("🚀 구매 내역(Purchase History) 기능 추가를 시작합니다...\n")

# 1. 백엔드: billing.py에 조회 API 추가
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "@router.get(\"/purchases\")" not in content:
        endpoint_code = '''

@router.get("/purchases")
async def get_purchases(user: dict = Depends(get_current_user)):
    """유저의 결제(구매) 내역을 반환합니다."""
    repo = get_repository()
    purchases = repo.list_purchases(user["id"])
    return {"purchases": purchases}
'''
        content += endpoint_code
        with open(billing_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 백엔드: /billing/purchases API 추가 완료")
    else:
        print("ℹ️ 백엔드: /billing/purchases API가 이미 존재합니다.")

# 2. 프론트엔드: types.ts에 Purchase 타입 추가
types_path = "frontend/types.ts"
if os.path.exists(types_path):
    shutil.copy2(types_path, types_path + ".bak")
    with open(types_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "export interface Purchase" not in content:
        type_code = '''
export interface Purchase {
  id: string;
  user_id: string;
  product_id: string;
  platform: string;
  purchased_at: string;
}
'''
        content += type_code
        with open(types_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 프론트엔드: Purchase 타입 추가 완료")

# 3. 프론트엔드: api/client.ts에 getPurchases 함수 추가
client_path = "frontend/src/api/client.ts"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "getPurchases:" not in content:
        # getPortalUrl 근처에 추가
        pattern = r"(getPortalUrl:\s*\(\)\s*=>[^\n]+,)"
        replacement = r"\1\n  getPurchases: () => request<{ purchases: any[] }>('/billing/purchases'),"
        
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            with open(client_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ 프론트엔드: api.getPurchases 함수 추가 완료")
        else:
            print("⚠️ api.getPurchases 함수 추가 실패 (getPortalUrl 패턴 불일치)")

# 4. 프론트엔드: settings.tsx UI 연동
settings_path = "frontend/app/(tabs)/settings.tsx"
if os.path.exists(settings_path):
    shutil.copy2(settings_path, settings_path + ".bak")
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1) Import 추가
    if "getPurchases" not in content and "useState" in content:
        # useState는 이미 있음. Purchase 타입 임포트
        if "import type { Purchase }" not in content:
            content = content.replace("import { api } from \"@/api/client\";", "import { api } from \"@/api/client\";\nimport type { Purchase } from \"../../../types\";")

    # 2) State 추가
    if "const [purchases, setPurchases] = useState<Purchase[]>([]);" not in content:
        content = content.replace(
            "const [showPayment, setShowPayment] = useState(false);",
            "const [showPayment, setShowPayment] = useState(false);\n  const [purchases, setPurchases] = useState<Purchase[]>([]);"
        )

    # 3) useEffect 데이터 fetch 추가
    if "api.getPurchases()" not in content:
        fetch_code = '''
  useEffect(() => {
    if (user) {
      api.getPurchases().then((res) => {
        if (res && res.purchases) setPurchases(res.purchases);
      }).catch((e) => console.warn("Failed to load purchases", e));
    }
  }, [user]);
'''
        content = content.replace(
            "useEffect(() => {",
            fetch_code + "\n  useEffect(() => {"
        )

    # 4) UI 렌더링 추가 (계정 액션 위에 추가)
    if "구매 내역" not in content:
        ui_code = '''
      {/* 구매 내역 */}
      {purchases.length > 0 && (
        <View style={styles.profileBox}>
          <Text style={styles.sectionTitle}>구매 내역</Text>
          {purchases.map((item) => (
            <View key={item.id} style={styles.row}>
              <Text style={styles.label}>
                {item.product_id === "stars_onetime" ? "1회 이용권 (150 Stars)" : 
                 item.product_id === "stars_sub" ? "프리미엄 구독 (400 Stars)" : 
                 item.product_id}
              </Text>
              <Text style={styles.value}>
                {new Date(item.purchased_at).toLocaleDateString()}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* 4. 계정 액션 */}
'''
        content = content.replace("      {/* 4. 계정 액션 */}", ui_code)

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드: settings.tsx 구매 내역 UI 및 데이터 로딩 로직 추가 완료")

print("\n✨ 모든 수정이 완료되었습니다!")
print("1. 백엔드 배포: .\\deploy.ps1")
print("2. 프론트엔드 배포: git add . && git commit -m 'feat: 구매 내역 추가' && git push")