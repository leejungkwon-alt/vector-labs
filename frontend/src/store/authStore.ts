import { create } from 'zustand';
import { Platform } from 'react-native';
import * as AppleAuthentication from 'expo-apple-authentication';
import * as AuthSession from 'expo-auth-session';
import * as Crypto from 'expo-crypto';
import * as WebBrowser from 'expo-web-browser';
import type { AuthResponse } from '../../types';
import { api, setAuthToken } from '../api/client';
import { storage } from './secureStore';

declare var process: { env: Record<string, string | undefined> };

WebBrowser.maybeCompleteAuthSession();

const TOKEN_KEY = 'saju.access_token';
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
  const redirectUri = AuthSession.makeRedirectUri();
  const nonce = await Crypto.randomUUID();
  const request = new AuthSession.AuthRequest({
    clientId,
    redirectUri,
    responseType: AuthSession.ResponseType.IdToken,
    scopes: ['openid', 'profile', 'email'],
    extraParams: { nonce },
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
  bootstrap: () => Promise<void>;
  linkAccount: (provider: Provider) => Promise<void>;
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
    const res = await api.linkProvider(provider, providerToken);
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
