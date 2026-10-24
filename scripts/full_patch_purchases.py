import re
import sqlite3
from pathlib import Path

print("🚀 시스템 통합 패치를 시작합니다...\n")

# ====================================================
# 1. 백엔드: DB 스키마에 'purchases' 테이블 추가 및 메서드 등록
# ====================================================
repo_path = Path("app/auth/repository.py")
repo_src = repo_path.read_text(encoding="utf-8")

if "CREATE TABLE IF NOT EXISTS purchases" not in repo_src:
    repo_src = repo_src.replace(
        """    CREATE TABLE IF NOT EXISTS telegram_subscribers (""",
        """    CREATE TABLE IF NOT EXISTS purchases (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        product_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        purchased_at TEXT NOT NULL
    )
    \"\"\",
    \"\"\"
    CREATE TABLE IF NOT EXISTS telegram_subscribers ("""
    )
    
    repo_src = repo_src.replace(
        "    # ---- push tokens ----",
        """    # ---- purchases ----
    def log_purchase(self, user_id: str, product_id: str, platform: str) -> dict:
        pid = uuid.uuid4().hex
        self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) VALUES (?, ?, ?, ?, ?)",
            (pid, user_id, product_id, platform, _now_iso())
        )
        return self._one("SELECT * FROM purchases WHERE id = ?", (pid,))

    def list_purchases(self, user_id: str) -> list:
        return self._all(
            "SELECT * FROM purchases WHERE user_id = ? ORDER BY purchased_at DESC",
            (user_id,),
        )

    # ---- push tokens ----"""
    )
    repo_path.write_text(repo_src, encoding="utf-8")
    print("✅ 1. 백엔드 DB에 결제 내역 테이블 추가 완료")

# ====================================================
# 2. 백엔드: IAP 결제 시 내역 저장 로직 추가
# ====================================================
iap_path = Path("app/services/iap.py")
iap_src = iap_path.read_text(encoding="utf-8")
if "repo.log_purchase" not in iap_src:
    iap_src = iap_src.replace(
        'repo.set_tier(user_id, "subscription")',
        'repo.set_tier(user_id, "subscription")\n            repo.log_purchase(user_id, product_id, platform)'
    )
    iap_src = iap_src.replace(
        'repo.grant_addon(user_id, "compatibility")',
        'repo.grant_addon(user_id, "compatibility")\n            repo.log_purchase(user_id, product_id, platform)'
    )
    iap_src = iap_src.replace(
        'repo.grant_addon(user_id, "deep_report")',
        'repo.grant_addon(user_id, "deep_report")\n            repo.log_purchase(user_id, product_id, platform)'
    )
    iap_path.write_text(iap_src, encoding="utf-8")
    print("✅ 2. 백엔드 결제 로직에 내역 기록 추가 완료")

# ====================================================
# 3. 백엔드: 결제 내역 조회 API 추가
# ====================================================
router_path = Path("app/auth/router.py")
router_src = router_path.read_text(encoding="utf-8")
if "/me/purchases" not in router_src:
    router_src = router_src.replace(
        '@router.get("/me/push-tokens")',
        '''@router.get("/me/purchases")
def list_my_purchases(user: dict = Depends(get_current_user)):
    return {"purchases": get_repository().list_purchases(user["id"])}

@router.get("/me/push-tokens")'''
    )
    router_path.write_text(router_src, encoding="utf-8")
    print("✅ 3. 백엔드 결제 내역 API 추가 완료")

# ====================================================
# 4. 프론트엔드: API 클라이언트에 내역 조회 함수 추가
# ====================================================
client_path = Path("frontend/src/api/client.ts")
client_src = client_path.read_text(encoding="utf-8")
if "getPurchases" not in client_src:
    client_src = client_src.replace(
        "  deleteAccount: () => request<void>(\"/auth/me\", { method: \"DELETE\" }),",
        "  deleteAccount: () => request<void>(\"/auth/me\", { method: \"DELETE\" }),\n  getPurchases: () => request<{ purchases: any[] }>(\"/auth/me/purchases\"),"
    )
    client_path.write_text(client_src, encoding="utf-8")
    print("✅ 4. 프론트엔드 API 클라이언트 연동 완료")

# ====================================================
# 5. 프론트엔드: Settings 화면에 결제 내역 UI 추가
# ====================================================
settings_path = Path("frontend/app/(tabs)/settings.tsx")
settings_src = settings_path.read_text(encoding="utf-8")

# import 추가
if 'import { useQuery } from "@tanstack/react-query";' not in settings_src:
    settings_src = settings_src.replace(
        'import { useLanguageStore, SupportedLang } from "@/store/languageStore";',
        'import { useLanguageStore, SupportedLang } from "@/store/languageStore";\nimport { useQuery } from "@tanstack/react-query";'
    )

# useQuery 추가
if "const { data: purchaseData } = useQuery" not in settings_src:
    settings_src = settings_src.replace(
        '  const [showLogin, setShowLogin] = useState(false);',
        '''  const { data: purchaseData } = useQuery({
    queryKey: ["purchases", user?.id],
    queryFn: () => api.getPurchases(),
    enabled: !!user,
  });

  const [showLogin, setShowLogin] = useState(false);'''
    )

# UI 렌더링 추가 (구독 관리 박스 아래에 삽입)
if "결제 내역 (Payment History)" not in settings_src:
    settings_src = settings_src.replace(
        '      {/* 4. 계정 액션 */}',
        '''      {/* 3.5 결제 내역 (영수증) */}
      {purchaseData?.purchases && purchaseData.purchases.length > 0 && (
        <View style={styles.profileBox}>
          <Text style={styles.sectionTitle}>결제 내역 (Payment History)</Text>
          {purchaseData.purchases.map((p: any, i: number) => (
            <View key={i} style={[styles.row, { borderBottomWidth: i === purchaseData.purchases.length - 1 ? 0 : 1, borderBottomColor: colors.border, paddingBottom: 10, marginBottom: 10 }]}>
              <View>
                <Text style={{ fontSize: 14, fontWeight: "600", color: colors.text }}>
                  {p.product_id === "sub_monthly_299" ? "월간 구독권" : 
                   p.product_id === "addon_compat_199" ? "궁합 애드온" :
                   p.product_id === "addon_deep_099" ? "심화 리포트" : p.product_id}
                </Text>
                <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
                  {new Date(p.purchased_at).toLocaleString()} · {p.platform.toUpperCase()}
                </Text>
              </View>
              <Text style={{ fontSize: 15, fontWeight: "700", color: colors.primary }}>
                {p.product_id === "sub_monthly_299" ? "$2.99" : 
                 p.product_id === "addon_compat_199" ? "$1.99" :
                 p.product_id === "addon_deep_099" ? "$0.99" : "-"}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* 4. 계정 액션 */}'''
    )
settings_path.write_text(settings_src, encoding="utf-8")
print("✅ 5. 프론트엔드 설정 화면에 '결제 내역' UI 추가 완료")

# ====================================================
# 6. 보너스: 궁합 테스트를 위해 모든 로컬 유저에게 애드온 강제 부여
# ====================================================
DB_PATH = Path("data/auth.db")
if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users")
    users = cur.fetchall()
    for u in users:
        cur.execute(
            "INSERT INTO user_addons (user_id, addon, granted_at) VALUES (?, 'compatibility', datetime('now')) ON CONFLICT DO NOTHING",
            (u[0],)
        )
    conn.commit()
    conn.close()
    print("✅ 6. 로컬 DB의 모든 유저에게 '궁합(compatibility)' 애드온 강제 부여 완료 (테스트용)")

print("\n🎉 모든 패치가 완료되었습니다!")
print("⚠️ 백엔드 서버(uvicorn)와 프론트엔드(npx expo)를 모두 재시작해주세요.")
