import type {
  AuthResponse,
  SajuRequest,
  SajuResponse,
  ReportRequest,
  ReportResponse,
  DailyResponse,
  CompatibilityRequest,
  CompatibilityResponse,
  PushTokenRequest,
} from "../../types";

// Cloud Run 백엔드 주소로 변경
const BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "https://vector-labs-api-787049663118.asia-northeast3.run.app/api/v1";

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
    this.name = "ApiError";
  }
}

let _token: string | null = null;
export function setAuthToken(t: string | null) {
  _token = t;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (_token) headers["Authorization"] = `Bearer ${_token}`;

  // 10초 타임아웃 설정
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (res.status === 204) return undefined as T;

    const text = await res.text();
    const body = text ? JSON.parse(text) : null;

    if (!res.ok) {
      const detail = (body && (body.detail ?? body.message)) ?? `HTTP ${res.status}`;
      throw new ApiError(res.status, String(detail));
    }
    return body as T;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new ApiError(408, "서버 응답 시간이 초과되었습니다. 네트워크 상태를 확인해주세요.");
    }
    throw err;
  }
}

export const api = {
  anonymous: () => request<AuthResponse>("/auth/anonymous", { method: "POST" }),
  me: () => request<{ user: AuthResponse["user"] }>("/auth/me"),
  updateProfile: (payload: any) => request<any>("/auth/me/profile", { method: "PUT", body: JSON.stringify(payload) }),
  linkProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/link/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),
  purchase: (product_id: string) => request<any>("/auth/me/purchase", { method: "POST", body: JSON.stringify({ product_id, receipt: "mock_valid_receipt" }) }),
  deleteAccount: () => request<void>("/auth/me", { method: "DELETE" }),
  calculate: (payload: SajuRequest) =>
    request<SajuResponse>("/saju/calculate", { method: "POST", body: JSON.stringify(payload) }),
  report: (payload: ReportRequest) =>
    request<ReportResponse>("/saju/report", { method: "POST", body: JSON.stringify(payload) }),
  daily: (payload: SajuRequest & { days?: number; target_date?: string; lang?: string }) =>
    request<DailyResponse>("/saju/daily", { method: "POST", body: JSON.stringify(payload) }),
  compatibility: (payload: CompatibilityRequest) =>
    request<CompatibilityResponse>("/saju/compatibility", { method: "POST", body: JSON.stringify(payload) }),
  registerPushToken: (payload: PushTokenRequest) =>
    request<{ registered: boolean; tokens: number }>("/auth/me/push-token", { method: "POST", body: JSON.stringify(payload) }),
};