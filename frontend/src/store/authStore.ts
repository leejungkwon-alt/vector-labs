import { create } from 'zustand';
import { Platform } from 'react-native';
import * as AppleAuthentication from 'expo-apple-authentication';
import * as AuthSession from 'expo-auth-session';
import * as Crypto from 'expo-crypto';
import * as WebBrowser from 'expo-web-browser';
import type { AuthResponse } from '../../types';
import { api, setAuthToken, ApiError } from '../api/client';
import { storage } from './secureStore';
import { useProfileStore } from "./profileStore";

declare var process: { env: Record<string, string | undefined> };

WebBrowser.maybeCompleteAuthSession();

const TOKEN_KEY = 'saju.access_token';
const GUEST_TOKEN_BACKUP_KEY = 'saju.guest_token_backup';

async function backupGuestToken(): Promise<void> {
  try {
    const existing = await storage.getItem(GUEST_TOKEN_BACKUP_KEY);
    if (existing) return;
    const current = await storage.getItem(TOKEN_KEY);
    if (current) await storage.setItem(GUEST_TOKEN_BACKUP_KEY, current);
  } catch (e) {
    console.warn('[backupGuestToken] failed:', e);
  }
}

type User = AuthResponse['user'];
type Provider = 'apple' | 'google' | 'kakao';

async function getAppleIdentityToken(): Promise<string> {
  const credential = await AppleAuthentication.signInAsync({
    requestedScopes: [
      AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
      AppleAuthentication.AppleAuthenticationScope.EMAIL,
    ],
  });
  if (!credential.identityToken) {
    throw new Error('Apple sign-in returned no identityToken');
  }
  return credential.identityToken;
}

async function getGoogleIdToken(): Promise<string> {
  const clientId = process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID;
  if (!clientId) {
    throw new Error('EXPO_PUBLIC_GOOGLE_CLIENT_ID is not set');
  }

  // 📱 앱(Android/iOS): 네이티브 구글 로그인
  if (Platform.OS !== 'web') {
    const { GoogleSignin } = require('@react-native-google-signin/google-signin');
    GoogleSignin.configure({ webClientId: clientId });
    await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
    
    // 💡 핵심 수정 1: 기존 로그인 세션을 지우거나(signOut) 또는 강제 프롬프트를 위해 
    // GoogleSignin.signIn() 호출 전에 아래와 같이 처리하여 매번 계정을 고르게 유도합니다.
    try {
      await GoogleSignin.signOut(); // 이전에 로그인된 구글 세션 캐시 초기화
    } catch (e) {
      // 세션이 없는 경우 무시
    }

    const res = await GoogleSignin.signIn();
    if (res?.type === 'cancelled') {
      throw new Error('Google sign-in was cancelled');
    }
    const idToken = res?.data?.idToken ?? res?.idToken;
    if (!idToken) {
      throw new Error('Google sign-in returned no idToken');
    }
    return idToken;
  }

  // 🌐 웹: 기존 방식 유지 + prompt 파라미터 추가
  const redirectUri = AuthSession.makeRedirectUri();
  const nonce = await Crypto.randomUUID();
  const request = new AuthSession.AuthRequest({
    clientId,
    redirectUri,
    responseType: AuthSession.ResponseType.IdToken,
    scopes: ['openid', 'profile', 'email'],
    // 💡 핵심 수정 2: 웹 AuthSession 요청 시 extraParams에 prompt 추가
    extraParams: { 
      nonce, 
      prompt: 'select_account' 
    },
    usePKCE: false,
  });
  const discovery = await AuthSession.fetchDiscoveryAsync('https://accounts.google.com');
  const result = await request.promptAsync(discovery);
  if (result.type !== 'success' || !result.params?.id_token) {
    throw new Error('Google sign-in was cancelled or returned no id_token');
  }
  return result.params.id_token;
}

async function getKakaoAccessToken(): Promise<string> {
  const clientId = process.env.EXPO_PUBLIC_KAKAO_CLIENT_ID;
  const clientSecret = process.env.EXPO_PUBLIC_KAKAO_CLIENT_SECRET;
  if (!clientId) {
    throw new Error('EXPO_PUBLIC_KAKAO_CLIENT_ID is not set');
  }
  const redirectUri = AuthSession.makeRedirectUri();
  const discovery: AuthSession.DiscoveryDocument = {
    authorizationEndpoint: 'https://kauth.kakao.com/oauth/authorize',
    tokenEndpoint: 'https://kauth.kakao.com/oauth/token',
  };
  const request = new AuthSession.AuthRequest({
    clientId,
    redirectUri,
    responseType: AuthSession.ResponseType.Code,
    scopes: ['profile_nickname', 'account_email'],
  });
  const result = await request.promptAsync(discovery);
  if (result.type !== 'success' || !result.params?.code) {
    throw new Error('Kakao sign-in was cancelled or returned no code');
  }
  const tokenResponse = await AuthSession.exchangeCodeAsync(
    {
      clientId,
      code: result.params.code,
      redirectUri,
      extraParams: clientSecret ? { client_secret: clientSecret } : {},
    },
    discovery,
  );
  if (!tokenResponse.accessToken) {
    throw new Error('Kakao token exchange failed');
  }
  return tokenResponse.accessToken;
}

interface AuthState {
  user: User | null;
  ready: boolean;
  authError: string | null;
  bootstrap: () => Promise<void>;
  linkAccount: (provider: Provider) => Promise<void>;
  signInWithProvider: (provider: Provider) => Promise<void>;
  loginWithTelegram: () => Promise<void>;
  signInAnonymous: () => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  ready: false,
  authError: null,
  bootstrap: async () => {
    const createAnonymous = async () => {
      const res = await api.anonymous();
      await storage.setItem(TOKEN_KEY, res.access_token);
      setAuthToken(res.access_token);
      set({ user: res.user, ready: true, authError: null });
    };

    try {
      const t = await storage.getItem(TOKEN_KEY);

      if (!t) {
        await createAnonymous();
        return;
      }

      setAuthToken(t);
      try {
        const me = await api.me();
        set({ user: me.user, ready: true, authError: null });
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) {
          await createAnonymous();
        } else {
          throw e;
        }
      }
    } catch (e: any) {
      console.warn('[auth] bootstrap failed:', e);
      set({ ready: true, authError: e?.detail ?? e?.message ?? 'auth failed' });
    }
  },
  linkAccount: async (provider: Provider) => {
    let providerToken: string;
    if (provider === 'apple') {
      if (Platform.OS !== 'ios') {
        throw new Error('Apple sign-in is only available on iOS');
      }
      providerToken = await getAppleIdentityToken();
    } else if (provider === 'google') {
      providerToken = await getGoogleIdToken();
    } else {
      providerToken = await getKakaoAccessToken();
    }
    let res;
    try {
      res = await api.linkProvider(provider, providerToken); // ⚠️ api/client.ts 확인 필요
    } catch (e: any) {
      if (e instanceof ApiError && e.status === 409) {
        res = await api.loginProvider(provider, providerToken); // ⚠️ api/client.ts 확인 필요
      } else {
        throw e;
      }
    }
    await backupGuestToken();
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
  
  loginWithTelegram: async () => {
    // 📱 앱 환경 방어 코드 추가
    if (Platform.OS !== 'web') {
      throw new Error("Telegram login is only available on Web");
    }
    
    const tg = (window as any).Telegram?.WebApp;
    if (!tg || !tg.initData) throw new Error("Telegram environment not found");
    
    const currentToken = await storage.getItem(TOKEN_KEY);
    const res = await api.loginTelegram(tg.initData);// ⚠️ api/client.ts 확인 필요
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user, ready: true });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
  signInWithProvider: async (provider: Provider) => {
    let providerToken: string;
    if (provider === 'apple') {
      if (Platform.OS !== 'ios') {
        throw new Error('Apple sign-in is only available on iOS');
      }
      providerToken = await getAppleIdentityToken();
    } else if (provider === 'google') {
      providerToken = await getGoogleIdToken();
    } else {
      providerToken = await getKakaoAccessToken();
    }
    const res = await api.loginProvider(provider, providerToken); // ⚠️ api/client.ts 확인 필요
    await backupGuestToken();
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
    try { await useProfileStore.getState().loadProfile(); } catch {}
  },
  signInAnonymous: async () => {
    const res = await api.anonymous();
    await storage.setItem(TOKEN_KEY, res.access_token);
    setAuthToken(res.access_token);
    set({ user: res.user });
  },
  signOut: async () => {
    setAuthToken(null);
    set({ user: null });
    try { await useProfileStore.getState().clearProfile(); } catch {}

    const backup = await storage.getItem(GUEST_TOKEN_BACKUP_KEY);
    if (backup) {
      try {
        setAuthToken(backup);
        const me = await api.me();
        await storage.setItem(TOKEN_KEY, backup);
        await storage.deleteItem(GUEST_TOKEN_BACKUP_KEY);
        set({ user: me.user, ready: true, authError: null });
        try { await useProfileStore.getState().loadProfile(); } catch {}
        return;
      } catch (e) {
        console.warn('[signOut] guest restore failed, falling back:', e);
        await storage.deleteItem(GUEST_TOKEN_BACKUP_KEY);
      }
    }

    try {
      await storage.deleteItem(TOKEN_KEY);
      const res = await api.anonymous();
      await storage.setItem(TOKEN_KEY, res.access_token);
      setAuthToken(res.access_token);
      set({ user: res.user, ready: true, authError: null });
      try { await useProfileStore.getState().loadProfile(); } catch {}
    } catch (e) {
      console.warn('[signOut] anonymous re-issue failed:', e);
    }
  },
}));