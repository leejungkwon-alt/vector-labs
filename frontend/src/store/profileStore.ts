import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";

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
    await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    set({ profile });
  },
  clearProfile: async () => {
    await AsyncStorage.removeItem(PROFILE_KEY);
    set({ profile: null });
  },
}));
