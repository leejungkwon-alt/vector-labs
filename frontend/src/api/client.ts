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
import { Platform } from "react-native";


const BASE_URL: string = (() => {
  const fromEnv = process.env.EXPO_PUBLIC_API_BASE_URL;
  if (fromEnv) return fromEnv;
  if (typeof __DEV__ !== "undefined" && __DEV__) return "http://localhost:8000/api/v1";
  throw new Error(
    "[client] EXPO_PUBLIC_API_BASE_URL is not set. Set it in the build environment before bundling.",
  );
})();

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

  // 30초 타임아웃 설정
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
    // 502/404 등 HTML 응답이 와도 SyntaxError 로 터지지 않게 방어
    let body: any = null;
    if (text) {
      try { body = JSON.parse(text); } catch { body = null; }
    }

    if (!res.ok) {
      throw new ApiError(res.status, extractDetail(body, res.status));
    }
    return body as T;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if (err?.name === "AbortError") {
      throw new ApiError(408, "서버 응답 시간이 초과되었습니다. 네트워크 상태를 확인해주세요.");
    }
    // fetch 자체가 실패(서버 다운 / CORS / 오프라인) -> 브라우저는 그냥 TypeError("Failed to fetch")
    if (err instanceof TypeError) {
      throw new ApiError(0, "서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.");
    }
    throw err;
  }
}

// FastAPI 의 422 는 detail 이 객체 배열이라 String() 하면 "[object Object]" 가 된다.
function extractDetail(body: any, status: number): string {
  const d = body && (body.detail ?? body.message);
  if (Array.isArray(d)) {
    return d.map((x: any) => x?.msg ?? JSON.stringify(x)).join("\n");
  }
  if (d && typeof d === "object") return JSON.stringify(d);
  return d ? String(d) : `HTTP ${status}`;
}

export const api = {
  anonymous: () => request<AuthResponse>("/auth/anonymous", { method: "POST" }),
  createStarsInvoice: () => request<{ invoice_link: string }>("/billing/stars/invoice", { method: "POST" }),
  createStarsInvoiceOnetime: () => request<{ invoice_link: string }>("/billing/stars/invoice/onetime", { method: "POST" }),
  me: () => request<{ user: AuthResponse["user"] }>("/auth/me"),
  updateProfile: (payload: any) => request<any>("/auth/me/profile", { method: "PUT", body: JSON.stringify(payload) }),
  getMyProfile: () => request<any>("/auth/me/profile"),
  linkProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/link/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),
  loginProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/login/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),
  loginTelegram: (initData: string) => request<AuthResponse>("/auth/login/telegram", { method: "POST", body: JSON.stringify({ init_data: initData }) }),    checkout: (is_onetime = false) => request<{ url: string }>('/billing/checkout', { method: 'POST', body: JSON.stringify({ is_onetime }) }),
  getSharedCompatibility: (id: string) => request<{ compatibility: any }>(`/saju/compatibility/shared/${id}`),
  getPortalUrl: () => request<{ url: string }>("/billing/portal"),

  purchase: (product_id: string) => request<any>("/auth/me/purchase", { method: "POST", body: JSON.stringify({ product_id, receipt: "mock_valid_receipt", platform: Platform.OS }) }),
  deleteAccount: () => request<void>("/auth/me", { method: "DELETE" }),
  getPurchases: () => request<{ purchases: any[] }>("/billing/purchases"),
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