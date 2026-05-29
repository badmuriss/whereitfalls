import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useRef, useState } from "react";

import type { ReentryDetail, RiskRegion } from "../api/types";
import { prefersReducedMotion } from "../lib/motion";
import { scoreToIndex, tierStyle, type Tier } from "../lib/severity";

interface ReentryMapProps {
  contextRisks: RiskRegion[];
  focusedRegions: RiskRegion[];
  focusedDetail: ReentryDetail | null;
  loading: boolean;
}

const GLOBAL_CENTER: L.LatLngExpression = [6, -20];

// De-clutter: cada tier só ganha rótulo a partir de certo zoom (a região líder sempre).
const LABEL_ZOOM: Record<Tier, number> = {
  critical: 0,
  elevated: 3,
  attention: 5,
  monitor: 7,
};

/** Desembrulha longitudes para que pontos consecutivos nunca saltem >180° (anti-dateline). */
function unwrapLngs(points: [number, number][]): [number, number][] {
  if (!points.length) return [];
  const out: [number, number][] = [[points[0][0], points[0][1]]];
  for (let i = 1; i < points.length; i++) {
    let lon = points[i][1];
    const prev = out[i - 1][1];
    while (lon - prev > 180) lon -= 360;
    while (lon - prev < -180) lon += 360;
    out.push([points[i][0], lon]);
  }
  return out;
}

/** Trecho central da trilha (≈ época prevista) — o "vetor de descida" local, sem espaguete. */
function descentSegment(track: [number, number][]): [number, number][] {
  if (track.length < 2) return track;
  const mid = Math.floor(track.length / 2);
  const half = 6;
  const slice = track.slice(Math.max(0, mid - half), Math.min(track.length, mid + half + 1));
  return unwrapLngs(slice);
}

export function ReentryMap({ contextRisks, focusedRegions, focusedDetail, loading }: ReentryMapProps) {
  const nodeRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const staticLayer = useRef<L.LayerGroup | null>(null);
  const animLayer = useRef<L.LayerGroup | null>(null);
  const rafRef = useRef<number | null>(null);
  const [zoom, setZoom] = useState(3);

  // init once
  useEffect(() => {
    if (!nodeRef.current || mapRef.current) return;
    const map = L.map(nodeRef.current, {
      center: GLOBAL_CENTER,
      zoom: 3,
      minZoom: 2,
      maxZoom: 8,
      zoomControl: true,
      attributionControl: true,
      worldCopyJump: false,
      preferCanvas: true,
    });
    map.zoomControl.setPosition("bottomright");
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(map);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png", {
      subdomains: "abcd",
      maxZoom: 19,
      opacity: 0.5,
    }).addTo(map);
    map.setMaxBounds([[-85, -210], [85, 210]]);
    map.on("zoomend", () => setZoom(map.getZoom()));
    mapRef.current = map;
    staticLayer.current = L.layerGroup().addTo(map);
    animLayer.current = L.layerGroup().addTo(map);
    return () => {
      map.remove();
      mapRef.current = null;
      staticLayer.current = null;
      animLayer.current = null;
    };
  }, []);

  // static draw: context dots, corridor, region markers, impact
  useEffect(() => {
    const layer = staticLayer.current;
    const map = mapRef.current;
    if (!layer || !map) return;
    layer.clearLayers();

    const focusedKeys = new Set(focusedRegions.map((r) => r.region));
    const leadTier = focusedRegions[0] ? tierStyle(focusedRegions[0].score) : undefined;

    // contexto global — pontinhos esmaecidos, sem rótulo
    contextRisks.forEach((risk) => {
      if (focusedKeys.has(risk.region)) return;
      if (risk.lat == null || risk.lon == null) return;
      L.circleMarker([risk.lat, risk.lon], {
        radius: 2.5,
        stroke: false,
        fillColor: tierStyle(risk.score).color,
        fillOpacity: 0.28,
        interactive: false,
      }).addTo(layer);
    });

    // corredor de risco = faixa de latitudes sobrevoadas na janela. Como a janela cobre
    // muitas órbitas, o objeto cruza todas as longitudes → banda contínua (não recortada).
    if (focusedDetail?.ground_track?.length && leadTier) {
      const lats = focusedDetail.ground_track.map((p) => p[0]).filter((v) => Number.isFinite(v));
      if (lats.length) {
        const pad = 6;
        const latMin = Math.max(-84, Math.min(...lats) - pad);
        const latMax = Math.min(84, Math.max(...lats) + pad);
        L.rectangle([[latMin, -180], [latMax, 180]], {
          stroke: true,
          color: leadTier.color,
          weight: 1,
          opacity: 0.4,
          fillColor: leadTier.color,
          fillOpacity: 0.08,
          interactive: false,
        }).addTo(layer);
      }
    }

    // regiões do evento focado — badge (de-clutter por zoom) ou dot
    focusedRegions.forEach((risk, idx) => {
      if (risk.lat == null || risk.lon == null) return;
      const t = tierStyle(risk.score);
      const isLead = idx === 0;
      const showLabel = isLead || zoom >= LABEL_ZOOM[t.tier];
      if (showLabel) {
        L.marker([risk.lat, risk.lon], {
          icon: L.divIcon({
            className: `rmk rmk--${t.tier}${isLead ? " rmk--lead" : ""}`,
            html: `<b>${risk.region}</b><i>${scoreToIndex(risk.score)}</i>`,
            iconSize: [58, 26],
            iconAnchor: [29, 13],
          }),
          keyboard: false,
        })
          .bindTooltip(`${risk.label ?? risk.region} · ${t.label} · índice ${scoreToIndex(risk.score)}/100`, {
            direction: "top",
            opacity: 0.96,
          })
          .addTo(layer);
      } else {
        L.circleMarker([risk.lat, risk.lon], {
          radius: 5,
          stroke: true,
          color: t.color,
          weight: 1.4,
          fillColor: t.color,
          fillOpacity: 0.45,
        })
          .bindTooltip(`${risk.label ?? risk.region} · índice ${scoreToIndex(risk.score)}/100`, {
            direction: "top",
            opacity: 0.96,
          })
          .addTo(layer);
      }
    });

    // ponto de impacto previsto (na época central)
    if (focusedDetail && leadTier) {
      const lat = focusedDetail.predicted_lat;
      const lon = focusedDetail.predicted_lon;
      const track = focusedDetail.ground_track;
      const impact = lat != null && lon != null ? [lat, lon] : track[Math.floor(track.length / 2)];
      if (impact) {
        L.marker(impact as L.LatLngExpression, {
          icon: L.divIcon({
            className: `impact-pulse impact-pulse--${leadTier.tier}`,
            html: `<span></span>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13],
          }),
          interactive: false,
          keyboard: false,
        }).addTo(layer);
      }
    }
  }, [contextRisks, focusedRegions, focusedDetail, zoom]);

  // fit aos pontos REAIS (regiões em risco + impacto), não à trilha multi-órbita —
  // assim o enquadramento é estável e significativo em qualquer proporção de tela.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.invalidateSize();
    const pts: L.LatLngTuple[] = [];
    focusedRegions.forEach((r) => {
      if (r.lat != null && r.lon != null) pts.push([r.lat, r.lon]);
    });
    if (focusedDetail?.predicted_lat != null && focusedDetail?.predicted_lon != null) {
      pts.push([focusedDetail.predicted_lat, focusedDetail.predicted_lon]);
    }
    if (pts.length === 0) {
      map.flyTo(GLOBAL_CENTER, 2, { duration: 0.5 });
      return;
    }
    if (pts.length === 1) {
      map.flyTo(pts[0], 4, { duration: 0.7 });
      return;
    }
    map.flyToBounds(L.latLngBounds(pts).pad(0.25), { duration: 0.7, maxZoom: 4 });
  }, [focusedRegions, focusedDetail]);

  // sweep comet along the descent segment
  useEffect(() => {
    const layer = animLayer.current;
    if (!layer) return;
    layer.clearLayers();
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;

    const track = focusedDetail?.ground_track;
    const leadTier = focusedRegions[0] ? tierStyle(focusedRegions[0].score) : undefined;
    if (!track || track.length < 2 || !leadTier) return;
    const seg = descentSegment(track);
    if (seg.length < 2) return;

    // trilha de descida (linha local, brilhante)
    L.polyline(seg as L.LatLngExpression[], {
      color: leadTier.color,
      weight: 2,
      opacity: 0.75,
      dashArray: "2 6",
      interactive: false,
    }).addTo(layer);

    const comet = L.marker(seg[0] as L.LatLngExpression, {
      icon: L.divIcon({ className: `comet comet--${leadTier.tier}`, html: "<span></span>", iconSize: [14, 14], iconAnchor: [7, 7] }),
      interactive: false,
      keyboard: false,
    }).addTo(layer);

    // distância acumulada para param por comprimento de arco
    const segDist: number[] = [];
    let total = 0;
    for (let i = 1; i < seg.length; i++) {
      const d = Math.hypot(seg[i][0] - seg[i - 1][0], seg[i][1] - seg[i - 1][1]);
      segDist.push(d);
      total += d;
    }
    const posAt = (t: number): [number, number] => {
      const target = t * total;
      let acc = 0;
      for (let i = 0; i < segDist.length; i++) {
        if (acc + segDist[i] >= target) {
          const f = segDist[i] ? (target - acc) / segDist[i] : 0;
          return [seg[i][0] + (seg[i + 1][0] - seg[i][0]) * f, seg[i][1] + (seg[i + 1][1] - seg[i][1]) * f];
        }
        acc += segDist[i];
      }
      return seg[seg.length - 1];
    };

    if (prefersReducedMotion()) {
      comet.setLatLng(seg[seg.length - 1] as L.LatLngExpression);
      return;
    }

    const DURATION = 5200;
    let start: number | null = null;
    const tick = (ts: number) => {
      if (start == null) start = ts;
      const t = ((ts - start) % DURATION) / DURATION;
      comet.setLatLng(posAt(t) as L.LatLngExpression);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    };
  }, [focusedDetail, focusedRegions]);

  return (
    <div className="reentry-map" aria-label="Mapa do corredor de risco de reentrada" aria-busy={loading}>
      <div ref={nodeRef} className="reentry-map__canvas" />
    </div>
  );
}
