import { create } from 'zustand';
import type { AuthResponse } from '../../types';
import { api, setAuthToken } from '../api/client';
import { storage } from './secureStore'; // 👈 새로 만든 래퍼 사용

const TOKEN_KEY = 'saju.access_token';
type User = AuthResponse['user'];

interface AuthState {
  user: User | null;
  ready: boolean;
  bootstrap: () => Promise<void>;
  linkAccount: (provider: "apple" | "google" | "kakao") => Promise<void>;
  signInAnonymous: () => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  ready: false,
  bootstrap: async () => {
    let t = await storage.getItem(TOKEN_KEY);

    // 1. 토큰이 없는 경우 -> 새 계정 생성
    if (!t) {
      try {
        const res = await api.anonymous();
        await storage.setItem(TOKEN_KEY, res.access_token);
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
        await storage.setItem(TOKEN_KEY, res.access_token);
        setAuthToken(res.access_token);
        set({ user: res.user, ready: true });
      } catch (e) {
        set({ ready: true });
      }
    }
  },
  linkAccount: async (provider: "apple" | "google" | "kakao") => {
    // [시뮬레이션] 실제 앱에서는 Apple/Google SDK에서 받은 진짜 토큰을 넣습니다.
    const mockToken = `mock:${provider}_${Math.random().toString(36).substring(2, 10)}`;
    const res = await api.linkProvider(provider, mockToken);
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
  },
  signInAnonymous: async () => {
    const res = await api.anonymous();
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
  },
  signOut: async () => {
    await storage.deleteItem(TOKEN_KEY);
    setAuthToken(null);
    set({ user: null });
  },
}));