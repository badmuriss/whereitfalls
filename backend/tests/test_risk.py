from app.services.risk import build_corridor_geojson, heatmap_features, score_regions


def test_corridor_geojson_wraps_track_as_feature_collection() -> None:
    track = [(-15.8, -47.9), (-12.7, -45.2), (-3.7, -38.5)]
    geojson = build_corridor_geojson(track, uncertainty_minutes=120)

    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"
    assert geojson["features"][0]["properties"]["uncertainty_minutes"] == 120


def test_region_scores_are_sorted_and_bounded() -> None:
    track = [(-15.8, -47.9), (-12.7, -45.2), (-3.7, -38.5)]
    scores = score_regions(track, "tip-test", 12345, 0.78)

    assert scores
    assert scores == sorted(scores, key=lambda item: item["score"], reverse=True)
    assert all(0 <= item["score"] <= 1 for item in scores)
    assert all("lat" in item and "lon" in item and "scope" in item for item in scores)


def test_global_ocean_zone_scores_without_brazil_proximity() -> None:
    track = [(18.0, -44.0), (20.0, -45.0), (22.0, -46.0)]
    scores = score_regions(track, "tip-atl", 98765, 0.72)

    assert scores[0]["region"] == "ATL-N"
    assert scores[0]["scope"] == "ocean"
    assert scores[0]["score"] > 0.5


def test_heatmap_features_are_geojson_points() -> None:
    features = heatmap_features(
        [
            {
                "region": "ATL-N",
                "label": "Atlântico Norte",
                "scope": "ocean",
                "lat": 20.0,
                "lon": -45.0,
                "score": 0.8,
                "prediction_id": "p1",
                "norad_id": 1,
            }
        ]
    )

    assert features["type"] == "FeatureCollection"
    assert features["features"][0]["geometry"]["type"] == "Point"
    assert features["features"][0]["properties"]["scope"] == "ocean"
