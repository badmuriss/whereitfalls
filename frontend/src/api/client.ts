import type {
  AlertDispatchResponse,
  GeoJSONFeatureCollection,
  ReentryDetail,
  ReentryListResponse,
  RiskResponse,
  SubscriptionResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8002";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getReentries(): Promise<ReentryListResponse> {
  return getJson<ReentryListResponse>("/v1/reentries");
}

export async function getRisk(): Promise<RiskResponse> {
  return getJson<RiskResponse>("/v1/risk?min_score=0.1");
}

export async function getReentryDetail(noradId: number): Promise<ReentryDetail> {
  return getJson<ReentryDetail>(`/v1/reentries/${noradId}`);
}

export async function getHeatmap(): Promise<GeoJSONFeatureCollection> {
  return getJson<GeoJSONFeatureCollection>("/v1/risk/heatmap");
}

export async function createEmailSubscription(input: {
  region: string;
  email: string;
  minScore: number;
}): Promise<SubscriptionResponse> {
  return postJson<SubscriptionResponse>("/v1/subscriptions", {
    channel: "email",
    target: { type: "region", region: input.region },
    min_score: input.minScore,
    email: input.email,
  });
}

export async function dispatchAlertDryRun(minScore = 0): Promise<AlertDispatchResponse> {
  return postJson<AlertDispatchResponse>("/v1/alerts/dispatch", {
    dry_run: true,
    min_score: minScore,
  });
}
