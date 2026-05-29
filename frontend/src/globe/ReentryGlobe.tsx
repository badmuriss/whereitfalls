import { useEffect, useMemo, useRef, useState } from "react";
import Globe, { type GlobeMethods } from "react-globe.gl";
import * as THREE from "three";
import { feature } from "topojson-client";
import worldTopo from "world-atlas/countries-110m.json";

import type { ReentryDetail, RiskRegion } from "../api/types";
import { prefersReducedMotion } from "../lib/motion";
import { scoreToIndex, tierStyle } from "../lib/severity";

type TopoArg = Parameters<typeof feature>[0];
type GeomArg = Parameters<typeof feature>[1];

// países (vetor) para desenhar terra/fronteiras no globo — uma vez
const COUNTRY_FEATURES = (() => {
  const topo = worldTopo as unknown as TopoArg;
  const obj = (worldTopo as unknown as { objects: { countries: GeomArg } }).objects.countries;
  return (feature(topo, obj) as unknown as { features: object[] }).features;
})();

interface ReentryGlobeProps {
  focusedDetail: ReentryDetail | null;
  focusedRegions: RiskRegion[];
}

interface PointDatum {
  lat: number;
  lng: number;
  color: string;
  radius: number;
  alt: number;
  label: string;
}

/**
 * Globo 3D hero: órbita/ground-track do objeto varrendo o planeta + pulso no ponto de
 * impacto. Ilha client-only (three.js fica isolada aqui via React.lazy no App).
 */
export default function ReentryGlobe({ focusedDetail, focusedRegions }: ReentryGlobeProps) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const reduced = prefersReducedMotion();

  const leadTier = focusedRegions[0] ? tierStyle(focusedRegions[0].score) : undefined;
  const leadColor = leadTier?.color ?? "#3dd6c4";

  const globeMaterial = useMemo(
    () => new THREE.MeshPhongMaterial({ color: "#0a0f1c", emissive: "#05070f", emissiveIntensity: 0.9, shininess: 4 }),
    [],
  );

  // ground-track como uma única "path" varrendo o globo
  const pathsData = useMemo(() => {
    if (!focusedDetail?.ground_track?.length) return [];
    return [{ coords: focusedDetail.ground_track.map(([lat, lon]) => [lat, lon, 0.08]) }];
  }, [focusedDetail]);

  const pointsData = useMemo<PointDatum[]>(() => {
    return focusedRegions
      .filter((r) => r.lat != null && r.lon != null)
      .map((r) => {
        const t = tierStyle(r.score);
        return {
          lat: r.lat as number,
          lng: r.lon as number,
          color: t.color,
          radius: 0.7 + r.score * 0.9,
          alt: 0.02,
          label: `${r.label ?? r.region} · ${scoreToIndex(r.score)}/100`,
        };
      });
  }, [focusedRegions]);

  const ringsData = useMemo(() => {
    if (!focusedDetail) return [];
    const lat = focusedDetail.predicted_lat;
    const lon = focusedDetail.predicted_lon;
    if (lat == null || lon == null) return [];
    return [{ lat, lng: lon }];
  }, [focusedDetail]);

  // rótulos persistentes das regiões de maior risco — clareza sobre "o que é cada coisa"
  const labelsData = useMemo(() => {
    return focusedRegions
      .slice(0, 3)
      .filter((r) => r.lat != null && r.lon != null)
      .map((r) => ({
        lat: r.lat as number,
        lng: r.lon as number,
        text: `${r.region} ${scoreToIndex(r.score)}`,
        color: tierStyle(r.score).color,
      }));
  }, [focusedRegions]);

  // dimensionamento responsivo
  useEffect(() => {
    const node = wrapRef.current;
    if (!node) return;
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect;
      setSize({ w: Math.round(r.width), h: Math.round(r.height) });
    });
    ro.observe(node);
    return () => ro.disconnect();
  }, []);

  // controles + auto-rotação
  useEffect(() => {
    const g = globeRef.current;
    if (!g) return;
    const controls = g.controls();
    controls.enableZoom = true;
    controls.autoRotate = !reduced;
    controls.autoRotateSpeed = 0.6;
    controls.minDistance = 180;
    controls.maxDistance = 600;
    g.pointOfView({ altitude: 2.6 }, 0);
  }, [reduced, size.w]);

  // câmera viaja até o ponto de impacto ao focar
  useEffect(() => {
    const g = globeRef.current;
    if (!g || !focusedDetail) return;
    const lat = focusedDetail.predicted_lat ?? focusedRegions[0]?.lat;
    const lon = focusedDetail.predicted_lon ?? focusedRegions[0]?.lon;
    if (lat == null || lon == null) return;
    g.pointOfView({ lat, lng: lon, altitude: 2.1 }, reduced ? 0 : 1400);
  }, [focusedDetail, focusedRegions, reduced]);

  return (
    <div ref={wrapRef} className="reentry-globe">
      {size.w > 0 ? (
        <Globe
          ref={globeRef}
          width={size.w}
          height={size.h}
          rendererConfig={{ antialias: false, powerPreference: "high-performance" }}
          backgroundColor="rgba(0,0,0,0)"
          globeMaterial={globeMaterial}
          showAtmosphere
          atmosphereColor={leadColor}
          atmosphereAltitude={0.15}
          polygonsData={COUNTRY_FEATURES}
          polygonCapColor={() => "rgba(124,136,160,0.10)"}
          polygonSideColor={() => "rgba(124,136,160,0.04)"}
          polygonStrokeColor={() => "rgba(150,160,182,0.5)"}
          polygonAltitude={0.006}
          pathsData={pathsData}
          pathPoints="coords"
          pathPointLat={(p: number[]) => p[0]}
          pathPointLng={(p: number[]) => p[1]}
          pathPointAlt={(p: number[]) => p[2]}
          pathColor={() => [`${leadColor}00`, leadColor, `${leadColor}00`]}
          pathStroke={1.6}
          pathDashLength={0.35}
          pathDashGap={0.2}
          pathDashAnimateTime={reduced ? 0 : 5200}
          pathTransitionDuration={600}
          pointsData={pointsData}
          pointLat="lat"
          pointLng="lng"
          pointColor="color"
          pointAltitude="alt"
          pointRadius="radius"
          pointLabel="label"
          ringsData={ringsData}
          ringColor={() => (t: number) => {
            const a = Math.round((1 - t) * 255).toString(16).padStart(2, "0");
            return `${leadColor}${a}`;
          }}
          ringMaxRadius={5}
          ringPropagationSpeed={2.2}
          ringRepeatPeriod={reduced ? 0 : 900}
          labelsData={labelsData}
          labelLat="lat"
          labelLng="lng"
          labelText="text"
          labelColor="color"
          labelSize={1.1}
          labelDotRadius={0.4}
          labelAltitude={0.012}
          labelResolution={2}
        />
      ) : null}
      <div className="globe-legend" aria-hidden>
        <span><i className="gl-orbit" />órbita / ground-track</span>
        <span><i className="gl-region" />região em risco</span>
        <span><i className="gl-impact" />impacto previsto</span>
      </div>
    </div>
  );
}
