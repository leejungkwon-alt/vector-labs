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

const BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

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

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });

  if (res.status === 204) return undefined as T;

  const text = await res.text();
  const body = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const detail = (body && (body.detail ?? body.message)) ?? `HTTP ${res.status}`;
    throw new ApiError(res.status, String(detail));
  }
  return body as T;
}

export const api = {
  anonymous: () => request<AuthResponse>("/auth/anonymous", { method: "POST" }),
  me: () => request<{ user: AuthResponse["user"] }>("/auth/me"),
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