export type Confidence = "low" | "medium" | "high";
export type ObjectType = "payload" | "rocket_body" | "debris";

export interface ReentrySummary {
  prediction_id: string;
  norad_id: number;
  name: string;
  type: ObjectType;
  country: string;
  predicted_reentry_utc: string;
  uncertainty_minutes: number;
  predicted_lat: number | null;
  predicted_lon: number | null;
  confidence: Confidence;
  max_region_score: number;
}

export interface ReentryListResponse {
  items: ReentrySummary[];
  total: number;
}

export type GroundTrackPoint = [lat: number, lon: number];

export interface ReentryDetail extends ReentrySummary {
  ground_track: GroundTrackPoint[];
  corridor_geojson: GeoJSONFeatureCollection;
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: Array<{
    type: "Feature";
    geometry: {
      type: string;
      coordinates: unknown;
    };
    properties: Record<string, unknown>;
  }>;
}

export interface RiskRegion {
  region: string;
  label?: string | null;
  scope?: string | null;
  lat?: number | null;
  lon?: number | null;
  score: number;
  prediction_id: string;
  norad_id: number;
  window_utc: [string, string];
  exposed_assets: string[];
}

export interface RiskResponse {
  items: RiskRegion[];
  total: number;
}

export interface SubscriptionResponse {
  id: string;
  channel: "email" | "webhook";
  target: {
    type: "region" | "bbox";
    region?: string | null;
    bbox?: [number, number, number, number] | null;
  };
  min_score: number;
  status: "active";
}

export interface AlertDispatchResponse {
  evaluated: number;
  matched: number;
  sent: number;
  events: Array<{
    subscription_id: string;
    prediction_id: string;
    region: string;
    score: number;
    status: string;
    provider: string | null;
    message_id: string | null;
    detail: string;
  }>;
}
