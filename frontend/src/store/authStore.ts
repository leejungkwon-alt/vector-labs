import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import type { AuthResponse } from "../../types";
import { api, setAuthToken } from "../api/client";

const TOKEN_KEY = "saju.access_token";
type User = AuthResponse["user"];

interface AuthState {
  user: User | null;
  ready: boolean;
  bootstrap: () => Promise<void>;
  signInAnonymous: () => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  ready: false,
  bootstrap: async () => {
    let t = await SecureStore.getItemAsync(TOKEN_KEY);
    
    // 1. 토큰이 아예 없는 경우 -> 새 계정 생성
    if (!t) {
      try {
        const res = await api.anonymous();
        await SecureStore.setItemAsync(TOKEN_KEY, res.access_token);
        setAuthToken(res.access_token);
        set({ user: res.user, ready: true });
      } catch (e) {
        set({ ready: true });
      }
      return;
    }

    // 2. 토큰이 있는 경우 -> 유효성 검사
    setAuthToken(t);
    try {
      const me = await api.me();
      set({ user: me.user, ready: true });
    } catch {
      // 토큰이 만료되었으면 새로 생성
      try {
        const res = await api.anonymous();
        await SecureStore.setItemAsync(TOKEN_KEY, res.access_token);
        setAuthToken(res.access_token);
        set({ user: res.user, ready: true });
      } catch (e) {
        set({ ready: true });
      }
    }
  },
  signInAnonymous: async () => {
    const res = await api.anonymous();
    await SecureStore.setItemAsync(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
  },
  signOut: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setAuthToken(null);
    set({ user: null });
  },
}));
