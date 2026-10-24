import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/app/(tabs)/daily.tsx")

def main():
    if not FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {FILE}")
        return

    src = FILE.read_text(encoding="utf-8")

    # 1. PaymentModal import 추가
    if "PaymentModal" not in src:
        src = src.replace(
            'import { useProfileStore } from "@/store/profileStore";',
            'import { useProfileStore } from "@/store/profileStore";\nimport { PaymentModal } from "@/components/PaymentModal";\nimport { useState } from "react";'
        )
        # 만약 import 위치가 다르다면 가장 첫 번째 import 뒤에 넣습니다.
        if "PaymentModal" not in src:
            src = src.replace(
                'import { useQuery } from "@tanstack/react-query";',
                'import { useQuery } from "@tanstack/react-query";\nimport { useState } from "react";\nimport { PaymentModal } from "@/components/PaymentModal";'
            )

    # 2. showPayment 상태 추가
    if "const [showPayment, setShowPayment] = useState(false);" not in src:
        src = src.replace(
            '  const user = useAuthStore((s) => s.user);',
            '  const user = useAuthStore((s) => s.user);\n  const [showPayment, setShowPayment] = useState(false);'
        )

    # 3. 403 에러(구독자 전용) 화면 내 버튼 라우팅을 모달 띄우기로 변경
    src = src.replace(
        'onPress={() => router.push("/(tabs)/settings")}',
        'onPress={() => setShowPayment(true)}'
    )

    # 4. 403 에러 화면 컴포넌트 안에 PaymentModal 렌더링 추가
    old_forbidden_block = """          <TouchableOpacity style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} onPress={() => setShowPayment(true)}>
            <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 업그레이드</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }"""
    
    new_forbidden_block = """          <TouchableOpacity style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} onPress={() => setShowPayment(true)}>
            <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 업그레이드</Text>
          </TouchableOpacity>
        </View>
        
        <PaymentModal visible={showPayment} onClose={() => setShowPayment(false)} />
      </View>
    );
  }"""
    
    src = src.replace(old_forbidden_block, new_forbidden_block)

    # 저장
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = FILE.with_suffix(f".tsx.bak.{ts}")
    shutil.copy2(FILE, bak)
    FILE.write_text(src, encoding="utf-8")
    
    print("✅ daily.tsx 결제 모달 직통 연결 완료!")
    print("   - [프리미엄 업그레이드] 버튼 클릭 시 화면 이동 없이 즉시 결제 모달 팝업")
    print(f"📦 백업 파일: {bak.name}")

if __name__ == "__main__":
    main()
