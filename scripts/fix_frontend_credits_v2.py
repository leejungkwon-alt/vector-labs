import os
import shutil

def fix_home_tsx():
    filepath = "frontend/app/(tabs)/home.tsx"
    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return

    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. useAuthStore import 확인 (없으면 최상단에 추가)
    if "useAuthStore" not in content:
        content = "import { useAuthStore } from '@/store/authStore';\n" + content
        print("✅ useAuthStore import 추가 완료")

    # 2. useQuery가 끝나는 지점을 찾아서 그 밑에 useEffect 추가
    # 홈 코드에서 useQuery 블록의 끝부분인 "  });" 패턴을 찾습니다.
    old_pattern = """    enabled: !!profile && profileReady && ready,
    retry: false,
  });"""
    
    new_pattern = """    enabled: !!profile && profileReady && ready,
    retry: false,
  });

  // 🆕 리포트 데이터 로드 완료 후 크레딧(이용권) 잔액 갱신
  useEffect(() => {
    if (data) {
      useAuthStore.getState().bootstrap();
    }
  }, [data]);"""

    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ useQuery 하단에 크레딧 갱신용 useEffect 추가 완료")
    else:
        # 패턴이 약간 다를 경우를 대비한 2차 시도 (문자열 띄어쓰기 등)
        import re
        regex_pattern = r"enabled:\s*!!profile\s*&&\s*profileReady\s*&&\s*ready,\s*retry:\s*false,\s*\}\);"
        def repl(m):
            return m.group(0) + "\n\n  // 🆕 리포트 데이터 로드 완료 후 크레딧(이용권) 잔액 갱신\n  useEffect(() => {\n    if (data) {\n      useAuthStore.getState().bootstrap();\n    }\n  }, [data]);"
        
        new_content, count = re.subn(regex_pattern, repl, content)
        if count > 0:
            content = new_content
            print("✅ (정규식) useQuery 하단에 크레딧 갱신용 useEffect 추가 완료")
        else:
            print("⚠️ useQuery 종료 지점을 찾지 못했습니다. 수동 확인이 필요합니다.")
            return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

fix_home_tsx()