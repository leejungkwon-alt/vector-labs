# scripts/patch_malgun_gothic.py
from pathlib import Path
import re
import sys

# ==========================================
# 1. _layout.tsx 수정 (이전 폰트 로딩 제거 및 웹 전역 CSS 주입)
# ==========================================
layout_path = Path("frontend/app/_layout.tsx")
if layout_path.exists():
    src = layout_path.read_text(encoding="utf-8")
    
    # 1-1. 이전 붓글씨 관련 import 및 useFonts 제거
    src = re.sub(r'import \{ useFonts \} from [\'"]expo-font[\'"];\n?', '', src)
    src = re.sub(r'import \{ NanumBrushScript_400Regular \} from [\'"]@expo-google-fonts/nanum-brush-script[\'"];\n?', '', src)
    src = re.sub(r'const \[fontsLoaded\] = useFonts\(\{[\s\S]*?\}\);\n?', '', src)
    src = re.sub(r'if \(!fontsLoaded\) \{\s*return null;\s*\}\n?', '', src)
    
    # 1-2. 웹 전역 폰트(맑은 고딕) 적용을 위한 useEffect 추가
    if "Malgun Gothic" not in src:
        font_effect = '''
  useEffect(() => {
    if (typeof document !== "undefined" && Platform.OS === "web") {
      const style = document.createElement("style");
      style.innerHTML = `
        body, div, span, p, h1, h2, h3, h4, h5, h6, input, textarea, button, a, li, label {
          font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif !important;
        }
      `;
      document.head.appendChild(style);
      return () => { document.head.removeChild(style); };
    }
  }, []);
'''
        # useEffect import 확인 및 추가
        if "useEffect" not in src:
            src = src.replace("import React", "import React, { useEffect }", 1)
            if "import React" not in src:
                src = "import { useEffect } from 'react';\n" + src
        
        # 컴포넌트 최상단(return 문 위)에 삽입
        match = re.search(r'(export default function\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*\{)', src)
        if match:
            src = src[:match.end()] + font_effect + src[match.end():]
            print("✅ _layout.tsx 웹 전역 폰트(맑은 고딕) 적용 완료")

    layout_path.write_text(src, encoding="utf-8")

# ==========================================
# 2. index.tsx 수정 ("결" 글씨 맑은 고딕으로 변경)
# ==========================================
index_path = Path("frontend/app/index.tsx")
if index_path.exists():
    src = index_path.read_text(encoding="utf-8")
    
    # 2-1. BRUSH_FONT 상수를 맑은 고딕으로 변경
    old_font_pattern = r'const BRUSH_FONT = (Platform\.select\(\{.*?\}\)|"NanumBrushScript_400Regular"|.*?);'
    new_font = 'const BRUSH_FONT = "Malgun Gothic";' # 텔레그램 웹뷰에서도 적용되도록
    
    src = re.sub(old_font_pattern, new_font, src, count=1)
    
    # 2-2. "결" 텍스트 스타일에 볼드(굵기) 강화 (맑은 고딕의 특징 살리기)
    src = src.replace('fontSize: 132,\n    lineHeight: 160,', 'fontSize: 132,\n    lineHeight: 160,\n    fontWeight: "900",')
    
    index_path.write_text(src, encoding="utf-8")
    print("✅ index.tsx '결' 로고 폰트 변경 완료")