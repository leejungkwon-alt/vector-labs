import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api } from "../api/client";

const PROFILE_KEY = "saju_profile";

interface ProfileState {
  profile: any | null;
  ready: boolean;
  loadProfile: () => Promise<void>;
  saveProfile: (profile: any) => Promise<void>;
  clearProfile: () => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: null,
  ready: false,
  loadProfile: async () => {
    try {
      const data = await AsyncStorage.getItem(PROFILE_KEY);
      if (data) {
        set({ profile: JSON.parse(data), ready: true });
      } else {
        set({ ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },
  saveProfile: async (profile: any) => {
    // 1. 로컬 저장 (오프라인/새로고침 대비)
    await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    set({ profile });

    // 2. 서버 동기화 (에러가 나도 로컬은 유지)
    try {
      await api.updateProfile(profile);
    } catch (e) {
      console.warn("Server profile sync failed (using local cache):", e);
    }
  },
  clearProfile: async () => {
    await AsyncStorage.removeItem(PROFILE_KEY);
    set({ profile: null });
  },
}));
