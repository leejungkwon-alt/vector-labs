from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def create_relation_labels():
    p = ROOT / "frontend" / "src" / "utils" / "poemRelations.ts"
    p.parent.mkdir(parents=True, exist_ok=True)
    content = """export function getRelationLabel(relation: string | undefined, lang: string): string {
  const labels: Record<string, Record<string, string>> = {
    same: {
      ko: "같은 기운",
      en: "Same Energy",
      es: "Misma Energía",
      ja: "同じ気運",
      zh_cn: "同源能量",
    },
    generates_me: {
      ko: "나를 채워주는 기운",
      en: "Nourishing Energy",
      es: "Energía Nutricia",
      ja: "私を満たす気運",
      zh_cn: "滋养能量",
    },
    i_generate: {
      ko: "내가 뻗어 나가는 기운",
      en: "Creative Energy",
      es: "Energía Creativa",
      ja: "私が広がる気運",
      zh_cn: "创造能量",
    },
    i_control: {
      ko: "내가 다스리는 기운",
      en: "Controlling Energy",
      es: "Energía de Control",
      ja: "私が司る気運",
      zh_cn: "掌控能量",
    },
    controls_me: {
      ko: "나를 단련하는 기운",
      en: "Challenging Energy",
      es: "Energía Desafiante",
      ja: "私を鍛える気運",
      zh_cn: "历练能量",
    },
  };

  if (!relation) return "";
  const langKey = ["ko", "en", "es", "ja", "zh_cn"].includes(lang) ? lang : "en";
  return labels[relation]?.[langKey] || labels[relation]?.["en"] || relation;
}
"""
    p.write_text(content, encoding="utf-8")
    print("[OK] frontend/src/utils/poemRelations.ts 생성 완료")

def update_flip_card():
    p = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
    t = p.read_text(encoding="utf-8")
    
    if "getRelationLabel" not in t:
        t = t.replace(
            'import type { PoemCard } from "../../../types";',
            'import type { PoemCard } from "../../../types";\nimport { getRelationLabel } from "@/utils/poemRelations";'
        )
    
    t = t.replace(
        '{tt(lang, "오늘의 시조", "Poem of the Day")} · {poem.relation_kr}',
        '{tt(lang, "오늘의 시조", "Poem of the Day")} · {getRelationLabel(poem.relation, lang || "en")}'
    )
    
    p.write_text(t, encoding="utf-8")
    print("[OK] PoemFlipCard.tsx 수정 완료")

def update_collection():
    p = ROOT / "frontend" / "app" / "collection.tsx"
    t = p.read_text(encoding="utf-8")
    
    if "getRelationLabel" not in t:
        t = t.replace(
            'import { useAuthStore } from "@/store/authStore";',
            'import { useAuthStore } from "@/store/authStore";\nimport { getRelationLabel } from "@/utils/poemRelations";\nimport { useLanguageStore } from "@/store/languageStore";'
        )
    
    t = t.replace(
        'const { collection, currentPoem } = usePoemStore();',
        'const { collection, currentPoem } = usePoemStore();\n  const lang = useLanguageStore((s) => s.lang);'
    )
    
    t = t.replace(
        '<Text style={styles.cardRelation}>{poem.relation_kr}</Text>',
        '<Text style={styles.cardRelation}>{getRelationLabel(poem.relation, lang)}</Text>'
    )
    
    p.write_text(t, encoding="utf-8")
    print("[OK] collection.tsx 수정 완료")

if __name__ == "__main__":
    create_relation_labels()
    update_flip_card()
    update_collection()
