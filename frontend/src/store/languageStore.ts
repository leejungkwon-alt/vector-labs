// SAJU-PATCH:language-store
import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Localization from "expo-localization";

const LANG_KEY = "saju_language";
export type SupportedLang = "ko" | "en" | "ja" | "zh_cn" | "zh_tw";
const SUPPORTED: readonly SupportedLang[] = ["ko", "en", "ja", "zh_cn", "zh_tw"] as const;

function detectDeviceLang(): SupportedLang {
  const loc = Localization.getLocales()[0];
  const code = (loc?.languageCode ?? "ko").toLowerCase();
  if (code === "zh") {
    const region = (loc?.regionCode ?? "").toUpperCase();
    return ["TW", "HK", "MO"].includes(region) ? "zh_tw" : "zh_cn";
  }
  if (code === "ja") return "ja";
  if (code === "en") return "en";
  return "ko";
}

type LanguageState = {
  lang: SupportedLang;
  ready: boolean;
  loadLang: () => Promise<void>;
  setLang: (lang: SupportedLang) => Promise<void>;
};

export const useLanguageStore = create<LanguageState>((set) => ({
  lang: "ko",
  ready: false,
  loadLang: async () => {
    try {
      const saved = await AsyncStorage.getItem(LANG_KEY);
      if (saved && (SUPPORTED as readonly string[]).includes(saved)) {
        set({ lang: saved as SupportedLang, ready: true });
      } else {
        set({ lang: detectDeviceLang(), ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },
  setLang: async (newLang) => {
    await AsyncStorage.setItem(LANG_KEY, newLang);
    set({ lang: newLang });
  },
}));
