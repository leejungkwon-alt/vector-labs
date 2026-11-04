from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"

t = p.read_text(encoding="utf-8")

# 1. useLanguageStore 임포트 추가 (lang prop이 없을 때 대비)
if "useLanguageStore" not in t:
    t = t.replace(
        'import { colors } from "@/theme";',
        'import { colors } from "@/theme";\nimport { useLanguageStore } from "@/store/languageStore";'
    )

# 2. 컴포넌트 내부에 언어 감지 및 번역 헬퍼 추가
old_head = '''  const [flipped, setFlipped] = useState(false);
  const anim = useRef(new Animated.Value(0)).current;'''
new_head = '''  const storeLang = useLanguageStore((s) => s.lang);
  const currentLang = lang || storeLang || "en";

  const getPoetName = (poet: string | undefined) => {
    if (!poet) return "";
    if (poet === "작자 미상" || poet === "미상" || poet === "Anonymous") {
      const map: Record<string, string> = {
        ko: "작자 미상",
        en: "Anonymous",
        ja: "作者不明",
        zh_cn: "佚名",
        es: "Anónimo"
      };
      return map[currentLang] || "Anonymous";
    }
    return poet;
  };

  const [flipped, setFlipped] = useState(false);
  const anim = useRef(new Animated.Value(0)).current;'''

t = t.replace(old_head, new_head)

# 3. 렌더링 부분에서 getPoetName 사용 및 lang 대신 currentLang 사용
t = t.replace(
    '{tt(lang, "오늘의 시조", "Poem of the Day")} · {getRelationLabel(poem.relation, lang || "en")}',
    '{tt(currentLang, "오늘의 시조", "Poem of the Day")} · {getRelationLabel(poem.relation, currentLang)}'
)

t = t.replace(
    '{poem.poet && <Text style={styles.poet}>- {poem.poet} -</Text>}',
    '{poem.poet && <Text style={styles.poet}>- {getPoetName(poem.poet)} -</Text>}'
)

# 나머지 tt(lang, ...) 도 currentLang 으로 통일
t = t.replace('tt(lang, ', 'tt(currentLang, ')

p.write_text(t, encoding="utf-8")
print("[OK] PoemFlipCard.tsx 수정 완료 (작자 미상 다국어 번역 적용)")
