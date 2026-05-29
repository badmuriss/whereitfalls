from collections.abc import Iterable
from math import isfinite

from shapely.geometry import LineString, Point, mapping

from app.services.orbit import great_circle_distance_km
from app.services.sample_data import (
    BR_REGION_CENTERS,
    BRAZIL_ASSETS,
    GLOBAL_ASSETS,
    GLOBAL_RISK_ZONES,
)


def build_corridor_geojson(
    ground_track: list[tuple[float, float]],
    uncertainty_minutes: int,
) -> dict[str, object]:
    clean_track = [
        (lat, lon)
        for lat, lon in ground_track
        if isfinite(lat) and isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180
    ]
    lon_lat = [(lon, lat) for lat, lon in clean_track]
    if len(lon_lat) < 2:
        lon_lat = [(-48, -16), (-44, -12)]
    line = LineString(lon_lat)
    buffer_degrees = min(8.0, max(1.0, uncertainty_minutes / 60))
    polygon = line.buffer(buffer_degrees, cap_style="flat", join_style="round")
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(polygon),
                "properties": {
                    "kind": "risk_corridor",
                    "uncertainty_minutes": uncertainty_minutes,
                    "buffer_degrees": round(buffer_degrees, 2),
                },
            }
        ],
    }


def score_regions(
    ground_track: list[tuple[float, float]],
    prediction_id: str,
    norad_id: int,
    base_score: float,
) -> list[dict[str, object]]:
    scores: list[dict[str, object]] = []
    global_zones = {
        code: (float(zone["lat"]), float(zone["lon"]))
        for code, zone in GLOBAL_RISK_ZONES.items()
    }
    for region, center in {**global_zones, **BR_REGION_CENTERS}.items():
        zone = GLOBAL_RISK_ZONES.get(region)
        nearest = min(great_circle_distance_km(center, point) for point in ground_track)
        scale_km = 2600 if zone else 1400
        proximity = max(0.0, 1 - (nearest / scale_km))
        baseline = 0.28 if zone else 0.35
        score = round(min(1.0, base_score * (baseline + proximity)), 2)
        if score <= 0.05:
            continue
        candidate_assets = GLOBAL_ASSETS if zone else BRAZIL_ASSETS
        asset_radius_km = 1400 if zone else 900
        exposed_assets = []
        for asset in candidate_assets:
            if asset["region"] != region:
                continue
            asset_nearest = min(
                great_circle_distance_km((float(asset["lat"]), float(asset["lon"])), point)
                for point in ground_track
            )
            if asset_nearest < asset_radius_km:
                exposed_assets.append(str(asset["name"]))

        scores.append(
            {
                "region": region,
                "label": str(zone["label"]) if zone else region,
                "scope": str(zone["scope"]) if zone else "br_state",
                "lat": center[0],
                "lon": center[1],
                "score": score,
                "prediction_id": prediction_id,
                "norad_id": norad_id,
                "exposed_assets": exposed_assets,
            }
        )
    return sorted(scores, key=lambda item: item["score"], reverse=True)


def heatmap_features(region_scores: Iterable[dict[str, object]]) -> dict[str, object]:
    features = []
    for item in region_scores:
        if item.get("lat") is not None and item.get("lon") is not None:
            lat = float(item["lat"])
            lon = float(item["lon"])
        elif str(item["region"]) in BR_REGION_CENTERS:
            lat, lon = BR_REGION_CENTERS[str(item["region"])]
        else:
            zone = GLOBAL_RISK_ZONES[str(item["region"])]
            lat, lon = float(zone["lat"]), float(zone["lon"])
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(Point(lon, lat)),
                "properties": {
                    "region": item["region"],
                    "label": item.get("label", item["region"]),
                    "scope": item.get("scope", "global"),
                    "score": item["score"],
                    "prediction_id": item["prediction_id"],
                    "norad_id": item["norad_id"],
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}
