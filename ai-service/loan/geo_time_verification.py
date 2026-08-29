from datetime import datetime, timezone, timedelta
from math import radians, sin, cos, sqrt, atan2
from typing import Optional


# =========================================================
# INDIA STANDARD TIME
# =========================================================

IST = timezone(
    timedelta(
        hours=5,
        minutes=30
    )
)


# =========================================================
# HAVERSINE DISTANCE
# =========================================================

def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)

    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1_rad)
        * cos(lat2_rad)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


# =========================================================
# GEO + TIME VERIFICATION
# =========================================================

def verify_geo_time(

    latitude: Optional[float],

    longitude: Optional[float],

    captured_at: Optional[str],

    metadata_valid: bool,

    geo_verified: bool,

    expected_latitude: Optional[float] = None,

    expected_longitude: Optional[float] = None,

    allowed_distance_km: float = 25.0

) -> dict:

    risk_score = 0

    reasons = []

    distance_km = None

    capture_time_utc = None


    # =====================================================
    # 1. METADATA VALIDATION
    # =====================================================

    if not metadata_valid:

        risk_score += 40

        reasons.append(
            "Evidence metadata validation failed"
        )


    # =====================================================
    # 2. GEO VERIFICATION FLAG
    # =====================================================

    if not geo_verified:

        risk_score += 40

        reasons.append(
            "Evidence geo-location verification failed"
        )


    # =====================================================
    # 3. COORDINATE PRESENCE
    # =====================================================

    if latitude is None or longitude is None:

        risk_score += 30

        reasons.append(
            "GPS coordinates are missing"
        )

    else:

        # -------------------------------------------------
        # LATITUDE RANGE
        # -------------------------------------------------

        if not (-90 <= latitude <= 90):

            risk_score += 50

            reasons.append(
                "Invalid latitude detected"
            )

        # -------------------------------------------------
        # LONGITUDE RANGE
        # -------------------------------------------------

        if not (-180 <= longitude <= 180):

            risk_score += 50

            reasons.append(
                "Invalid longitude detected"
            )


    # =====================================================
    # 4. EXPECTED LOCATION DISTANCE CHECK
    # =====================================================

    if (
        latitude is not None
        and longitude is not None
        and expected_latitude is not None
        and expected_longitude is not None
    ):

        try:

            distance_km = haversine_distance_km(

                latitude,
                longitude,

                expected_latitude,
                expected_longitude
            )

            if distance_km > allowed_distance_km:

                risk_score += 35

                reasons.append(

                    f"Evidence was captured "
                    f"{distance_km:.2f} km "
                    f"away from the expected location"
                )

            else:

                reasons.append(

                    f"Evidence location is within "
                    f"{distance_km:.2f} km "
                    f"of the expected location"
                )

        except Exception as exc:

            risk_score += 20

            reasons.append(
                f"Unable to calculate location distance: {exc}"
            )


    # =====================================================
    # 5. TIMESTAMP CHECK
    # =====================================================

    if not captured_at:

        risk_score += 25

        reasons.append(
            "Capture timestamp is missing"
        )

    else:

        try:

            # -------------------------------------------------
            # PARSE ISO TIMESTAMP
            #
            # Example:
            # 2026-08-18T16:10:00
            # 2026-08-18T16:10:00+05:30
            # 2026-08-18T10:40:00Z
            # -------------------------------------------------

            capture_time = datetime.fromisoformat(

                captured_at.replace(
                    "Z",
                    "+00:00"
                )
            )


            # -------------------------------------------------
            # IMPORTANT FIX
            #
            # Spring currently sends:
            #
            # 2026-08-18T16:10:00
            #
            # with no timezone.
            #
            # Since the prototype is running in India,
            # treat a timezone-less timestamp as IST.
            # -------------------------------------------------

            if capture_time.tzinfo is None:

                capture_time = capture_time.replace(
                    tzinfo=IST
                )


            # -------------------------------------------------
            # CONVERT TO UTC FOR COMPARISON
            # -------------------------------------------------

            capture_time_utc = (
                capture_time.astimezone(
                    timezone.utc
                )
            )

            current_time_utc = datetime.now(
                timezone.utc
            )


            # -------------------------------------------------
            # SMALL CLOCK-SKEW ALLOWANCE
            # -------------------------------------------------

            future_tolerance = timedelta(
                minutes=5
            )


            # -------------------------------------------------
            # FUTURE TIMESTAMP
            # -------------------------------------------------

            if (
                capture_time_utc
                >
                current_time_utc
                +
                future_tolerance
            ):

                risk_score += 35

                reasons.append(
                    "Evidence capture timestamp is in the future"
                )

            else:

                reasons.append(
                    "Evidence capture timestamp is valid"
                )


            # -------------------------------------------------
            # OPTIONAL AGE CHECK
            #
            # Very old photos may indicate reused evidence.
            # For prototype: older than 180 days gets risk.
            # -------------------------------------------------

            age = (
                current_time_utc
                -
                capture_time_utc
            )

            if age.days > 180:

                risk_score += 20

                reasons.append(
                    "Evidence appears to be older than 180 days"
                )


        except ValueError:

            risk_score += 30

            reasons.append(
                "Invalid capture timestamp format"
            )

        except Exception as exc:

            risk_score += 25

            reasons.append(
                f"Timestamp verification failed: {exc}"
            )


    # =====================================================
    # 6. LIMIT RISK SCORE
    # =====================================================

    risk_score = min(
        risk_score,
        100
    )


    # =====================================================
    # 7. FINAL GEO/TIME CLASSIFICATION
    # =====================================================

    if risk_score >= 60:

        result = "SUSPICIOUS"

    elif risk_score >= 30:

        result = "REVIEW"

    else:

        result = "VALID"


    # =====================================================
    # 8. DEFAULT SUCCESS REASON
    # =====================================================

    if not reasons:

        reasons.append(
            "Geo-location, timestamp and metadata checks passed"
        )


    # =====================================================
    # 9. RESPONSE
    # =====================================================

    return {

        "result":
            result,

        "risk_score":
            risk_score,

        "distance_km":
            (
                round(
                    distance_km,
                    2
                )
                if distance_km is not None
                else None
            ),

        "captured_at_utc":
            (
                capture_time_utc.isoformat()
                if capture_time_utc
                else None
            ),

        "reason":
            "; ".join(
                reasons
            )
    }