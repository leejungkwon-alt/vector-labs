import os
import re
import shutil
import subprocess

print("🚀 '공유 결과 웹페이지(대안 1)' 구현을 시작합니다...\n")

# =====================================================================
# 1. 백엔드: DB 스키마에 shared_compatibilities 테이블 추가
# =====================================================================
repo_path = "app/auth/repository.py"
if os.path.exists(repo_path):
    shutil.copy2(repo_path, repo_path + ".bak")
    with open(repo_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 테이블 생성문 추가 (stripe_events 테이블 뒤에)
    new_table = '''
      """
      CREATE TABLE IF NOT EXISTS shared_compatibilities (
          id TEXT PRIMARY KEY,
          result_data TEXT NOT NULL,
          created_at TEXT NOT NULL
      )
      """,
'''
    if "shared_compatibilities" not in content:
        content = content.replace(
            '      """\n      CREATE TABLE IF NOT EXISTS stripe_events (id TEXT PRIMARY KEY, type TEXT NOT NULL, processed_at TEXT NOT NULL)\n      """,',
            '      """\n      CREATE TABLE IF NOT EXISTS stripe_events (id TEXT PRIMARY KEY, type TEXT NOT NULL, processed_at TEXT NOT NULL)\n      """,\n' + new_table
        )
        print("✅ 1. DB 스키마: shared_compatibilities 테이블 추가 완료")
    else:
        print("ℹ️ 1. DB 스키마: shared_compatibilities 테이블이 이미 존재합니다.")

    # 메서드 추가 (set_tier 메서드 위에)
    methods = '''
    # ---- shared compatibility ----
    def save_shared_compatibility(self, result_data: str) -> str:
        """궁합 결과를 저장하고 고유 ID를 반환합니다."""
        import uuid
        share_id = uuid.uuid4().hex
        self._run(
            "INSERT INTO shared_compatibilities (id, result_data, created_at) VALUES (?, ?, ?)",
            (share_id, result_data, _now_iso()),
        )
        return share_id

    def get_shared_compatibility(self, share_id: str) -> Optional[dict]:
        """공유된 궁합 결과를 조회합니다."""
        return self._one(
            "SELECT * FROM shared_compatibilities WHERE id = ?", (share_id,)
        )

'''
    if "save_shared_compatibility" not in content:
        content = content.replace(
            "    def set_tier(self, user_id: str, tier: str) -> dict:",
            methods + "    def set_tier(self, user_id: str, tier: str) -> dict:"
        )
        print("✅ 1. DB 메서드: save/get_shared_compatibility 추가 완료")

    with open(repo_path, "w", encoding="utf-8") as f:
        f.write(content)

# =====================================================================
# 2. 백엔드: Pydantic 스키마 수정 (share_id 필드 추가)
# =====================================================================
schema_path = "app/schemas/compatibility.py"
if os.path.exists(schema_path):
    shutil.copy2(schema_path, schema_path + ".bak")
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "share_id" not in content:
        content = content.replace(
            "class CompatibilityResponse(BaseModel):\n    compatibility: Dict[str, Any]",
            "class CompatibilityResponse(BaseModel):\n    compatibility: Dict[str, Any]\n    share_id: Optional[str] = None"
        )
        # Optional import 추가
        if "from typing import Any, Dict" in content and "Optional" not in content:
            content = content.replace("from typing import Any, Dict", "from typing import Any, Dict, Optional")
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 2. Pydantic 스키마: share_id 필드 추가 완료")

# =====================================================================
# 3. 백엔드: compatibility.py 수정 (공유 API 추가 및 저장 로직)
# =====================================================================
compat_path = "app/api/v1/endpoints/compatibility.py"
if os.path.exists(compat_path):
    shutil.copy2(compat_path, compat_path + ".bak")
    with open(compat_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 api_compatibility 함수 반환부 수정 (share_id 추가)
    if "share_id" not in content:
        content = content.replace(
            '    return {"compatibility": response}',
            '    # 💡 결과를 DB에 저장하고 share_id 발급\n    import json\n    share_id = get_repository().save_shared_compatibility(json.dumps(response, ensure_ascii=False))\n    return {"compatibility": response, "share_id": share_id}'
        )
        print("✅ 3. POST /compatibility: share_id 발급 로직 추가 완료")

    # 공개 조회 API 추가 (파일 맨 아래에)
    if "/shared/{share_id}" not in content:
        public_api = '''

@router.get("/shared/{share_id}")
def get_shared_compatibility(share_id: str):
    """공유된 궁합 결과를 로그인 없이 조회합니다."""
    import json
    row = get_repository().get_shared_compatibility(share_id)
    if not row:
        raise HTTPException(status_code=404, detail="Shared compatibility not found.")
    return {"compatibility": json.loads(row["result_data"])}
'''
        content += public_api
        print("✅ 3. GET /compatibility/shared/{id}: 공개 조회 API 추가 완료")

    with open(compat_path, "w", encoding="utf-8") as f:
        f.write(content)

# =====================================================================
# 4. 프론트엔드: api/client.ts 수정
# =====================================================================
client_path = "frontend/src/api/client.ts"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "getSharedCompatibility" not in content:
        content = content.replace(
            "getPortalUrl: () =>",
            "getSharedCompatibility: (id: string) => request<{ compatibility: any }>(`/saju/compatibility/shared/${id}`),\n  getPortalUrl: () =>"
        )
        with open(client_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 4. api/client.ts: getSharedCompatibility 추가 완료")

# =====================================================================
# 5. 프론트엔드: 공유 결과 페이지 생성 (app/share/[id].tsx)
# =====================================================================
share_page_path = "frontend/app/share/[id].tsx"
os.makedirs("frontend/app/share", exist_ok=True)

share_page_content = '''import { useLocalSearchParams, router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { View, Text, ActivityIndicator, TouchableOpacity, ScrollView, StyleSheet, Platform } from "react-native";
import { api } from "@/api/client";
import { colors, spacing, radius } from "@/theme";

export default function SharedCompatibilityScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["shared-compat", id],
    queryFn: () => api.getSharedCompatibility(id as string),
    enabled: !!id,
  });

  const handleGoToApp = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg && tg.initData) {
      // 텔레그램 환경이면 봇 딥링크로 이동
      tg.openTelegramLink("https://t.me/my_vector_labs_bot?startapp=share");
    } else {
      // 웹 환경이면 메인으로 이동
      router.push("/");
    }
  };

  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  if (error || !data) return <View style={styles.center}><Text style={styles.errorText}>결과를 찾을 수 없습니다.</Text></View>;

  const compat = data.compatibility;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
        <Text style={styles.score}>{compat.overall_score || 0}점</Text>
        <Text style={styles.headline}>{compat.headline}</Text>
        <Text style={styles.body}>{compat.body}</Text>
        
        {compat.axes?.map((axis: any, idx: number) => (
          <View key={idx} style={styles.axisBox}>
            <Text style={styles.axisTitle}>{axis.title}</Text>
            <Text style={styles.axisDesc}>{axis.description}</Text>
          </View>
        ))}
      </View>
      
      <TouchableOpacity style={styles.ctaBtn} onPress={handleGoToApp}>
        <Text style={styles.ctaText}>나도 내 궁합 확인하러 가기</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg },
  errorText: { fontSize: 16, color: colors.textMuted },
  card: { backgroundColor: colors.surface, padding: 24, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, marginBottom: 24 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 16 },
  score: { fontSize: 56, fontWeight: "800", color: colors.primary, textAlign: "center", marginBottom: 8 },
  headline: { fontSize: 18, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 8 },
  body: { fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 },
  axisBox: { backgroundColor: colors.bg, padding: 16, borderRadius: radius.md, marginBottom: 12 },
  axisTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  axisDesc: { fontSize: 14, color: colors.text, lineHeight: 20 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});
'''
with open(share_page_path, "w", encoding="utf-8") as f:
    f.write(share_page_content)
print("✅ 5. 공유 결과 페이지 (app/share/[id].tsx) 생성 완료")

# =====================================================================
# 6. 프론트엔드: compatibility.tsx 공유 로직 수정
# =====================================================================
compat_tsx = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(compat_tsx):
    shutil.copy2(compat_tsx, compat_tsx + ".bak")
    with open(compat_tsx, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 텔레그램 분기 부분을 찾아서 링크 공유 로직으로 교체
    old_pattern = r"const tg = \(window as any\)\.Telegram\?\.WebApp;\n    if \(tg && tg\.platform !== \"unknown\"\) \{\n.*?return;\n    \}"
    
    new_logic = '''const tg = (window as any).Telegram?.WebApp;
    const isTelegram = !!tg?.platform && tg.platform !== "unknown";
    const shareUrl = `https://gyeol-blond.vercel.app/share/${data?.share_id}`;

    if (isTelegram) {
      const text = `내 궁합 결과 확인해 봐! 👇\\n${shareUrl}`;
      const telegramShareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(text)}`;
      tg.openTelegramLink(telegramShareUrl);
      return;
    } else {
      // 웹 환경에서도 링크 복사 or 공유
      if (Platform.OS === "web") {
        if (navigator.share) {
          await navigator.share({ title: "Gyeol Compatibility", url: shareUrl });
        } else {
          await navigator.clipboard.writeText(shareUrl);
          alert("공유 링크가 복사되었습니다! 친구에게 붙여넣기 해주세요.");
        }
        return;
      }
    }'''

    new_content, count = re.subn(old_pattern, new_logic, content, flags=re.DOTALL)
    if count > 0:
        with open(compat_tsx, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ 6. compatibility.tsx: 공유 로직 수정 완료")
    else:
        print("⚠️ 6. compatibility.tsx: 기존 텔레그램 분기 패턴을 찾지 못했습니다. 수동 확인 필요.")

# =====================================================================
# 7. 배포
# =====================================================================
print("\n7. 백엔드 배포 시작...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n8. 프론트엔드 배포를 위해 Git에 푸시합니다...")
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "feat: 공유 결과 웹페이지(대안 1) 구현"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("\n🎉 모든 작업이 완료되었습니다!")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패 (에러 확인 필요)")