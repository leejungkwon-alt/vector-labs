// frontend/src/i18n.ts
import { useLanguageStore, SupportedLang } from "@/store/languageStore";
import ko from "./locales/ko.json";
import en from "./locales/en.json";

// 지원 언어 확장 시 여기에 추가 (ja, zh_cn, zh_tw는 이후 단계)
const RESOURCES: Record<string, any> = {
  ko,
  en,
};

// 점 표기법 지원: t("home.loading") → RESOURCES[lang].home.loading
function resolve(lang: string, key: string): string {
  const dict = RESOURCES[lang] ?? RESOURCES.en;
  const parts = key.split(".");
  let cur: any = dict;
  for (const p of parts) {
    if (cur == null) return key;
    cur = cur[p];
  }
  return typeof cur === "string" ? cur : key;
}

// 변수 치환: t("settings.loginSocial", { provider: "Apple" })
function format(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, k) =>
    vars[k] != null ? String(vars[k]) : `{${k}}`
  );
}

/**
 * 훅: useT()
 *   const t = useT();
 *   t("home.loading") // "Reading your life blueprint..."
 */
export function useT() {
  const lang = useLanguageStore((s) => s.lang);
  return (key: string, vars?: Record<string, string | number>): string => {
    const template = resolve(lang, key);
    return format(template, vars);
  };
}

/**
 * 훅: useLang()
 *   const { lang, setLang, availableLangs } = useLang();
 */
export function useLang() {
  const lang = useLanguageStore((s) => s.lang);
  const setLang = useLanguageStore((s) => s.setLang);
  const availableLangs: { key: SupportedLang; label: string }[] = [
    { key: "ko", label: "한국어" },
    { key: "en", label: "English" },
  ];
  return { lang, setLang, availableLangs };
}
// ---------------------------------------------------------------
// Date/Time helpers (locale-aware display for pickers)
// ---------------------------------------------------------------
export function formatPickerDate(d: Date, lang: string): string {
  if (lang === "ko") {
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
  }
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

export function formatPickerTime(d: Date): string {
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
