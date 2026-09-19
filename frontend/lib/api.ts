// All requests go to OUR FastAPI backend only - never directly to law.go.kr.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiBlockedError extends Error {
  detail: string;
  constructor(detail: string) {
    super(detail);
    this.detail = detail;
  }
}

async function getJson<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiBlockedError(
      `백엔드(${API_URL})에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요.`
    );
  }
  if (res.status === 503) {
    const body = await res.json().catch(() => ({ detail: "데이터를 사용할 수 없습니다." }));
    throw new ApiBlockedError(body.detail);
  }
  if (!res.ok) {
    throw new ApiBlockedError(`API 오류 (${res.status}): ${path}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => getJson("/health"),
  summary: () => getJson("/api/v1/precedents/summary"),
  monthly: () => getJson("/api/v1/trends/monthly"),
  yearly: () => getJson("/api/v1/trends/yearly"),
  keywords: () => getJson("/api/v1/trends/keywords"),
  courts: () => getJson("/api/v1/trends/courts"),
  anomalies: () => getJson("/api/v1/anomalies"),
  decomposition: () => getJson("/api/v1/decomposition"),
  forecast: () => getJson("/api/v1/forecast"),
  insights: () => getJson("/api/v1/insights"),
  metadata: () => getJson("/api/v1/metadata"),
};
