from datetime import UTC, datetime, timedelta

from app.models.domain import Confidence, ObjectType

DEMO_REENTRIES = [
    {
        "prediction_id": "tip-48274-20260602T143500Z",
        "norad_id": 48274,
        "name": "CZ-5B R/B",
        "type": ObjectType.rocket_body,
        "country": "PRC",
        "predicted_reentry_utc": datetime(2026, 6, 2, 14, 35, tzinfo=UTC),
        "uncertainty_minutes": 120,
        "predicted_lat": -12.7,
        "predicted_lon": -45.2,
        "confidence": Confidence.medium,
        "max_region_score": 0.78,
        "tle": (
            "1 48274U 21035B   21122.75616741  .01234567  00000-0  12345-2 0  9991",
            "2 48274  41.4682 149.0913 0012345 122.3318 237.8872 16.04880000 12345",
        ),
    },
    {
        "prediction_id": "tip-60231-20260604T092000Z",
        "norad_id": 60231,
        "name": "STARLINK-31908",
        "type": ObjectType.payload,
        "country": "US",
        "predicted_reentry_utc": datetime(2026, 6, 4, 9, 20, tzinfo=UTC),
        "uncertainty_minutes": 180,
        "predicted_lat": -3.4,
        "predicted_lon": -38.6,
        "confidence": Confidence.low,
        "max_region_score": 0.54,
        "tle": (
            "1 60231U 24111A   26150.12500000  .00420100  00000-0  89230-3 0  9998",
            "2 60231  53.2161  41.3127 0001183  83.4491 276.6642 15.97822345 45678",
        ),
    },
    {
        "prediction_id": "tip-33591-20260607T221500Z",
        "norad_id": 33591,
        "name": "ARIANE 5 DEB",
        "type": ObjectType.debris,
        "country": "ESA",
        "predicted_reentry_utc": datetime(2026, 6, 7, 22, 15, tzinfo=UTC),
        "uncertainty_minutes": 90,
        "predicted_lat": -22.9,
        "predicted_lon": -43.2,
        "confidence": Confidence.high,
        "max_region_score": 0.66,
        "tle": (
            "1 33591U 09005C   26150.50000000  .00201020  00000-0  71200-3 0  9993",
            "2 33591   7.0122 205.1188 0021021 318.1101  41.8394 15.89100231 65432",
        ),
    },
]

BRAZIL_ASSETS = [
    {"name": "SBBR Brasilia Intl", "region": "DF", "lat": -15.8697, "lon": -47.9208, "weight": 0.9},
    {"name": "SBGR Guarulhos", "region": "SP", "lat": -23.4356, "lon": -46.4731, "weight": 1.0},
    {"name": "SBGL Galeao", "region": "RJ", "lat": -22.8099, "lon": -43.2506, "weight": 0.95},
    {"name": "SBFZ Fortaleza", "region": "CE", "lat": -3.7763, "lon": -38.5326, "weight": 0.75},
    {"name": "SBSV Salvador", "region": "BA", "lat": -12.9086, "lon": -38.3225, "weight": 0.78},
]

GLOBAL_RISK_ZONES = {
    "ATL-N": {"label": "Atlântico Norte", "lat": 20.0, "lon": -45.0, "scope": "ocean"},
    "ATL-S": {"label": "Atlântico Sul", "lat": -22.0, "lon": -25.0, "scope": "ocean"},
    "PAC-N": {"label": "Pacífico Norte", "lat": 25.0, "lon": -155.0, "scope": "ocean"},
    "PAC-S": {"label": "Pacífico Sul", "lat": -25.0, "lon": -135.0, "scope": "ocean"},
    "IND-O": {"label": "Oceano Índico", "lat": -18.0, "lon": 80.0, "scope": "ocean"},
    "SA-E": {"label": "América do Sul Leste", "lat": -15.0, "lon": -47.0, "scope": "land"},
    "NA-E": {"label": "América do Norte Leste", "lat": 38.0, "lon": -78.0, "scope": "land"},
    "EU-W": {"label": "Europa Ocidental", "lat": 48.0, "lon": 2.0, "scope": "land"},
    "AF-W": {"label": "África Ocidental", "lat": 8.0, "lon": -3.0, "scope": "land"},
    "AS-SE": {"label": "Sudeste Asiático", "lat": 10.0, "lon": 105.0, "scope": "land"},
    "AU-E": {"label": "Austrália Leste", "lat": -28.0, "lon": 145.0, "scope": "land"},
}

GLOBAL_ASSETS = [
    {"name": "North Atlantic air routes", "region": "ATL-N", "lat": 20.0, "lon": -45.0},
    {"name": "South Atlantic air routes", "region": "ATL-S", "lat": -22.0, "lon": -25.0},
    {"name": "Trans-Pacific corridors", "region": "PAC-N", "lat": 25.0, "lon": -155.0},
    {"name": "South Pacific maritime lanes", "region": "PAC-S", "lat": -25.0, "lon": -135.0},
    {"name": "Indian Ocean maritime lanes", "region": "IND-O", "lat": -18.0, "lon": 80.0},
    {"name": "South America aviation cluster", "region": "SA-E", "lat": -15.0, "lon": -47.0},
    {"name": "US East Coast aviation cluster", "region": "NA-E", "lat": 38.0, "lon": -78.0},
    {"name": "Western Europe aviation cluster", "region": "EU-W", "lat": 48.0, "lon": 2.0},
    {"name": "West Africa aviation corridor", "region": "AF-W", "lat": 8.0, "lon": -3.0},
    {"name": "Southeast Asia aviation cluster", "region": "AS-SE", "lat": 10.0, "lon": 105.0},
    {"name": "Australia East Coast aviation cluster", "region": "AU-E", "lat": -28.0, "lon": 145.0},
]

BR_REGION_CENTERS = {
    "DF": (-15.8, -47.9),
    "SP": (-23.5, -46.6),
    "RJ": (-22.9, -43.2),
    "CE": (-3.7, -38.5),
    "BA": (-12.9, -38.5),
    "GO": (-16.7, -49.3),
}


def utc_window(epoch: datetime, uncertainty_minutes: int) -> tuple[datetime, datetime]:
    delta = timedelta(minutes=uncertainty_minutes)
    return epoch - delta, epoch + delta
