import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api } from "../api/client";
import { api } from "@/api/client";

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
      // 1) 백엔드에서 현재 로그인 계정의 프로필 우선 조회
      try {
        const res = await api.getMyProfile();  // GET /auth/me/profile
        if (res) {
          set({ profile: res, ready: true });
          // 로컬 캐시도 동기화
          await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(res));
          return;
        }
      } catch (e: any) {
        // 404 = 아직 프로필 없음 → 캐시 시도
        // 401 = 로그인 안 됨 → 캐시 시도
        // 500/네트워크 → 캐시 fallback
      }
      // 2) 백엔드 실패 시 로컬 캐시 fallback
      const data = await AsyncStorage.getItem(PROFILE_KEY);
      if (data) {
        set({ profile: JSON.parse(data), ready: true });
      } else {
        set({ profile: null, ready: true });
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
