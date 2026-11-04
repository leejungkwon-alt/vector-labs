export function getRelationLabel(relation: string | undefined, lang: string): string {
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
